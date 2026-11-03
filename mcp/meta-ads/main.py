#!/usr/bin/env python3
"""
Meta Ads MCP Server
Direct connection to Meta Graph API for campaign management,
creative uploads, ad launching, and performance insights.

v2: self-refreshing access token, retries with backoff, friendly errors,
pagination, check_connection/set_access_token tools.
"""

import asyncio
import json
import os
import stat
import time
from pathlib import Path
from typing import Optional

import httpx
from fastmcp import FastMCP

GRAPH_VERSION = "v25.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_VERSION}"
VIDEO_URL = f"https://graph-video.facebook.com/{GRAPH_VERSION}"
CHARACTER_LIMIT = 25_000

# Token lifecycle: Meta long-lived user tokens last ~60 days. A still-valid
# token can be exchanged for a fresh 60-day one (fb_exchange_token), so this
# server refreshes itself as long as it gets used at least once every 60 days.
TOKEN_FILE = Path(__file__).with_name(".token.json")
REFRESH_INTERVAL_SECONDS = 7 * 24 * 3600  # proactive refresh weekly

# Meta error codes worth retrying: 1/2 transient, 4/17/32/613 rate limits
RETRYABLE_CODES = {1, 2, 4, 17, 32, 613}
RETRY_DELAYS = [2, 8]

mcp = FastMCP("meta-ads")


# ── Token management ──────────────────────────────────────────────────────────

def _read_token_file() -> dict:
    try:
        return json.loads(TOKEN_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _write_token_file(token: str) -> None:
    TOKEN_FILE.write_text(json.dumps({"access_token": token, "refreshed_at": int(time.time())}))
    TOKEN_FILE.chmod(stat.S_IRUSR | stat.S_IWUSR)


def _token() -> str:
    # The token file (written by refreshes and set_access_token) wins over the
    # env seed from ~/.claude.json, since it's always the most recent.
    file_token = _read_token_file().get("access_token")
    if file_token:
        return file_token
    token = os.environ.get("META_ACCESS_TOKEN")
    if not token:
        raise ValueError("META_ACCESS_TOKEN environment variable is not set.")
    return token


def _app_credentials() -> Optional[tuple]:
    app_id = os.environ.get("META_APP_ID")
    app_secret = os.environ.get("META_APP_SECRET")
    return (app_id, app_secret) if app_id and app_secret else None


async def _exchange(current_token: str) -> Optional[str]:
    """Trade a still-valid long-lived token for a fresh 60-day one."""
    creds = _app_credentials()
    if not creds:
        return None
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            r = await client.get(f"{BASE_URL}/oauth/access_token", params={
                "grant_type": "fb_exchange_token",
                "client_id": creds[0],
                "client_secret": creds[1],
                "fb_exchange_token": current_token,
            })
            new_token = r.json().get("access_token")
        except httpx.RequestError:
            return None
    if new_token:
        _write_token_file(new_token)
        return new_token
    return None


async def _maybe_refresh() -> None:
    """Weekly proactive refresh so the token never reaches its 60-day expiry."""
    state = _read_token_file()
    if time.time() - state.get("refreshed_at", 0) < REFRESH_INTERVAL_SECONDS:
        return
    refreshed = await _exchange(_token())
    if refreshed is None and not state:
        # Nothing exchangeable yet; stamp the env token so we don't retry
        # the exchange on every single request.
        try:
            _write_token_file(_token())
        except ValueError:
            pass


async def _recover_token() -> Optional[str]:
    """The active token was rejected. Try every token we know about."""
    candidates = []
    file_token = _read_token_file().get("access_token")
    env_token = os.environ.get("META_ACCESS_TOKEN")
    if file_token:
        candidates.append(file_token)
    if env_token and env_token != file_token:
        candidates.append(env_token)  # a fresh one may have been pasted into the config file
    for candidate in candidates:
        refreshed = await _exchange(candidate)
        if refreshed:
            return refreshed
    return None


TOKEN_EXPIRED_HELP = (
    "Meta access token is expired or revoked and could not be auto-refreshed. "
    "Fix: generate a new long-lived token (Meta Business Suite or Graph API Explorer "
    "with ads_read + ads_management), then call the set_access_token tool with it. "
    "That stores it in meta-mcp/.token.json and the server keeps it fresh from there."
)


# ── Error translation ─────────────────────────────────────────────────────────

def _parse_error(response: httpx.Response) -> dict:
    try:
        return response.json().get("error", {})
    except json.JSONDecodeError:
        return {}


def _friendly_error(response: httpx.Response) -> str:
    err = _parse_error(response)
    code = err.get("code")
    message = err.get("message", response.text[:300])
    detail = err.get("error_user_msg") or ""
    if code == 190:
        return f"AUTH FAILED (code 190): {message}\n{TOKEN_EXPIRED_HELP}"
    if code in (10, 200, 294):
        return (f"PERMISSION ERROR (code {code}): {message} "
                "The token is valid but missing access to this object. Check that the token "
                "was generated by a user with access to this ad account.")
    if code in RETRYABLE_CODES:
        return (f"RATE LIMITED (code {code}): {message} "
                "Meta is throttling. Wait a few minutes and try again; batch fewer calls.")
    return f"Meta API error (HTTP {response.status_code}, code {code}): {message} {detail}".strip()


# ── HTTP core ─────────────────────────────────────────────────────────────────

def _truncate(data) -> str:
    text = json.dumps(data, indent=2) if not isinstance(data, str) else data
    if len(text) > CHARACTER_LIMIT:
        return text[:CHARACTER_LIMIT] + "\n\n[Truncated — narrow your query for more detail]"
    return text


async def _request(method: str, url: str, params: dict = None, data: dict = None,
                   files: dict = None, timeout: int = 60) -> httpx.Response:
    """One HTTP call with token injection, auth recovery, and backoff retries."""
    await _maybe_refresh()
    token = _token()
    attempt = 0
    auth_retried = False
    while True:
        p = dict(params or {})
        d = dict(data or {})
        (p if method == "GET" else d)["access_token"] = token
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                r = await client.request(method, url, params=p, data=d or None, files=files)
            except httpx.RequestError as e:
                if attempt < len(RETRY_DELAYS):
                    await asyncio.sleep(RETRY_DELAYS[attempt])
                    attempt += 1
                    continue
                raise
        if r.status_code < 400:
            return r
        err = _parse_error(r)
        if err.get("code") == 190 and not auth_retried:
            auth_retried = True
            recovered = await _recover_token()
            if recovered:
                token = recovered
                continue
            return r
        if (err.get("code") in RETRYABLE_CODES or r.status_code >= 500) and attempt < len(RETRY_DELAYS):
            await asyncio.sleep(RETRY_DELAYS[attempt])
            attempt += 1
            continue
        return r


async def _get(path: str, params: dict = None) -> str:
    try:
        r = await _request("GET", f"{BASE_URL}/{path}", params=params)
    except httpx.RequestError as e:
        return f"Network error reaching Meta after retries: {e}"
    if r.status_code >= 400:
        return _friendly_error(r)
    return _truncate(r.json())


async def _get_paged(path: str, params: dict = None, max_pages: int = 4) -> str:
    """GET that follows paging.next so lists aren't silently cut at one page."""
    rows, page_url, page_params = [], f"{BASE_URL}/{path}", dict(params or {})
    for _ in range(max_pages):
        try:
            r = await _request("GET", page_url, params=page_params)
        except httpx.RequestError as e:
            return f"Network error reaching Meta after retries: {e}"
        if r.status_code >= 400:
            return _friendly_error(r)
        payload = r.json()
        rows.extend(payload.get("data", []))
        next_url = payload.get("paging", {}).get("next")
        if not next_url:
            return _truncate({"data": rows})
        page_url, page_params = next_url, {}  # next already carries query + token
    return _truncate({"data": rows, "note": f"Stopped after {max_pages} pages; more may exist."})


async def _post(path: str, data: dict = None) -> str:
    try:
        r = await _request("POST", f"{BASE_URL}/{path}", data=data)
    except httpx.RequestError as e:
        return f"Network error reaching Meta after retries: {e}"
    if r.status_code >= 400:
        return _friendly_error(r)
    return _truncate(r.json())


# ── Connection health ─────────────────────────────────────────────────────────

@mcp.tool()
async def check_connection() -> str:
    """
    Verify the Meta connection: token validity, expiry date, scopes, and ad
    account access. Run this first when anything Meta-related misbehaves.
    """
    creds = _app_credentials()
    if not creds:
        return "META_APP_ID / META_APP_SECRET not set; cannot inspect the token."
    try:
        r = await _request("GET", f"{BASE_URL}/debug_token",
                           params={"input_token": _token(),
                                   "access_token": f"{creds[0]}|{creds[1]}"})
    except httpx.RequestError as e:
        return f"Network error reaching Meta: {e}"
    info = r.json().get("data", {})
    expires = info.get("expires_at", 0)
    days_left = round((expires - time.time()) / 86400, 1) if expires else None
    state = _read_token_file()
    report = {
        "token_valid": info.get("is_valid", False),
        "token_expires_in_days": days_left if expires else "never",
        "scopes": info.get("scopes", []),
        "token_source": ".token.json (self-refreshing)" if state.get("access_token") else "env (~/.claude.json seed)",
        "last_auto_refresh": time.strftime("%Y-%m-%d", time.localtime(state["refreshed_at"])) if state.get("refreshed_at") else "never",
        "graph_api_version": GRAPH_VERSION,
    }
    if not info.get("is_valid", False):
        report["fix"] = TOKEN_EXPIRED_HELP
        return _truncate(report)
    accounts = await _get("me/adaccounts", {"fields": "id,name,account_status"})
    report["ad_accounts"] = "reachable" if '"data"' in accounts else accounts
    return _truncate(report)


@mcp.tool()
async def set_access_token(token: str) -> str:
    """
    Store a new Meta access token. Validates it, exchanges it for a long-lived
    60-day token, and saves it to .token.json where the server keeps it fresh
    automatically. Use when check_connection reports an expired/invalid token.
    """
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(f"{BASE_URL}/me", params={"access_token": token})
    if r.status_code >= 400:
        return f"That token was rejected by Meta: {_friendly_error(r)}"
    long_lived = await _exchange(token)
    if long_lived:
        return "Token accepted, exchanged for a long-lived 60-day token, and saved. Auto-refresh will keep it alive."
    _write_token_file(token)
    return ("Token accepted and saved, but the long-lived exchange failed "
            "(check META_APP_ID/META_APP_SECRET). It will work until its natural expiry.")


# ── Ad Accounts ───────────────────────────────────────────────────────────────

@mcp.tool()
async def get_ad_accounts() -> str:
    """List all Meta ad accounts accessible by the current user."""
    return await _get_paged("me/adaccounts", {
        "fields": "id,name,account_status,amount_spent,currency,balance"
    })


# ── Campaigns ─────────────────────────────────────────────────────────────────

@mcp.tool()
async def get_campaigns(account_id: str, status: str = "") -> str:
    """
    Get campaigns for an ad account.
    account_id: format act_XXXXXXXXX
    status: ACTIVE, PAUSED, ARCHIVED, or empty for all
    """
    params = {
        "fields": "id,name,objective,status,daily_budget,lifetime_budget,start_time,stop_time,created_time"
    }
    if status:
        params["effective_status"] = json.dumps([status])
    return await _get_paged(f"{account_id}/campaigns", params)


@mcp.tool()
async def create_campaign(
    account_id: str,
    name: str,
    objective: str,
    daily_budget: int,
    status: str = "PAUSED"
) -> str:
    """
    Create a new campaign.
    account_id: format act_XXXXXXXXX
    objective: OUTCOME_LEADS, OUTCOME_TRAFFIC, OUTCOME_ENGAGEMENT, OUTCOME_SALES, OUTCOME_AWARENESS
    daily_budget: in cents (e.g. 2000 = $20.00)
    status: ACTIVE or PAUSED (default PAUSED)
    """
    return await _post(f"{account_id}/campaigns", {
        "name": name,
        "objective": objective,
        "status": status,
        "daily_budget": str(daily_budget),
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "special_ad_categories": "[]",
    })


@mcp.tool()
async def update_campaign(
    campaign_id: str,
    status: str = "",
    daily_budget: int = 0,
    name: str = ""
) -> str:
    """Update a campaign's status, daily budget, or name."""
    data = {}
    if status:
        data["status"] = status
    if daily_budget:
        data["daily_budget"] = str(daily_budget)
    if name:
        data["name"] = name
    return await _post(campaign_id, data)


# ── Ad Sets ───────────────────────────────────────────────────────────────────

@mcp.tool()
async def get_adsets(campaign_id: str) -> str:
    """Get all ad sets for a campaign."""
    return await _get_paged(f"{campaign_id}/adsets", {
        "fields": "id,name,status,daily_budget,targeting,optimization_goal,billing_event,start_time,end_time"
    })


@mcp.tool()
async def create_adset(
    account_id: str,
    campaign_id: str,
    name: str,
    daily_budget: int,
    optimization_goal: str,
    billing_event: str,
    targeting_json: str,
    start_time: str = "",
    status: str = "PAUSED"
) -> str:
    """
    Create an ad set.
    account_id: format act_XXXXXXXXX
    daily_budget: in cents
    optimization_goal: LEAD_GENERATION, LINK_CLICKS, IMPRESSIONS, OFFSITE_CONVERSIONS
    billing_event: IMPRESSIONS or LINK_CLICKS
    targeting_json: JSON string of targeting spec
    start_time: ISO 8601, e.g. 2026-06-10T08:00:00-0700
    """
    data = {
        "name": name,
        "campaign_id": campaign_id,
        "daily_budget": str(daily_budget),
        "optimization_goal": optimization_goal,
        "billing_event": billing_event,
        "targeting": targeting_json,
        "status": status,
    }
    if start_time:
        data["start_time"] = start_time
    return await _post(f"{account_id}/adsets", data)


@mcp.tool()
async def update_adset(adset_id: str, status: str = "", daily_budget: int = 0) -> str:
    """Update an ad set's status or daily budget."""
    data = {}
    if status:
        data["status"] = status
    if daily_budget:
        data["daily_budget"] = str(daily_budget)
    return await _post(adset_id, data)


# ── Ads ───────────────────────────────────────────────────────────────────────

@mcp.tool()
async def get_ads(adset_id: str) -> str:
    """Get all ads in an ad set."""
    return await _get_paged(f"{adset_id}/ads", {
        "fields": "id,name,status,creative,adset_id,campaign_id,created_time"
    })


@mcp.tool()
async def create_ad(
    account_id: str,
    adset_id: str,
    name: str,
    creative_id: str,
    status: str = "PAUSED"
) -> str:
    """
    Create an ad by linking a creative to an ad set.
    account_id: format act_XXXXXXXXX
    creative_id: ID from create_video_ad_creative or create_image_ad_creative
    """
    return await _post(f"{account_id}/ads", {
        "name": name,
        "adset_id": adset_id,
        "creative": json.dumps({"creative_id": creative_id}),
        "status": status,
    })


@mcp.tool()
async def update_ad(ad_id: str, status: str) -> str:
    """Update an ad's status. status: ACTIVE, PAUSED, ARCHIVED, DELETED"""
    return await _post(ad_id, {"status": status})


# ── Ad Creatives ──────────────────────────────────────────────────────────────

@mcp.tool()
async def get_ad_creatives(account_id: str) -> str:
    """List ad creatives for an account."""
    return await _get_paged(f"{account_id}/adcreatives", {
        "fields": "id,name,title,body,object_story_spec,video_id,image_hash,status"
    })


@mcp.tool()
async def create_video_ad_creative(
    account_id: str,
    name: str,
    page_id: str,
    video_id: str,
    message: str,
    title: str,
    call_to_action_type: str,
    link_url: str,
    thumbnail_url: str = ""
) -> str:
    """
    Create a video ad creative.
    account_id: format act_XXXXXXXXX
    page_id: your Facebook Page ID
    video_id: from upload_video
    message: post caption/body text
    title: headline below the video
    call_to_action_type: LEARN_MORE, SIGN_UP, WATCH_MORE, DOWNLOAD, GET_OFFER
    link_url: destination URL
    thumbnail_url: optional custom thumbnail URL
    """
    video_data: dict = {
        "video_id": video_id,
        "message": message,
        "title": title,
        "call_to_action": json.dumps({
            "type": call_to_action_type,
            "value": {"link": link_url}
        })
    }
    if thumbnail_url:
        video_data["image_url"] = thumbnail_url

    return await _post(f"{account_id}/adcreatives", {
        "name": name,
        "object_story_spec": json.dumps({
            "page_id": page_id,
            "video_data": video_data
        }),
    })


@mcp.tool()
async def create_image_ad_creative(
    account_id: str,
    name: str,
    page_id: str,
    image_hash: str,
    message: str,
    link_url: str,
    call_to_action_type: str = "LEARN_MORE",
    headline: str = "",
    description: str = ""
) -> str:
    """
    Create an image ad creative.
    image_hash: from upload_image
    """
    link_data: dict = {
        "message": message,
        "link": link_url,
        "image_hash": image_hash,
        "call_to_action": json.dumps({
            "type": call_to_action_type,
            "value": {"link": link_url}
        })
    }
    if headline:
        link_data["name"] = headline
    if description:
        link_data["description"] = description

    return await _post(f"{account_id}/adcreatives", {
        "name": name,
        "object_story_spec": json.dumps({
            "page_id": page_id,
            "link_data": link_data
        }),
    })


# ── Video Upload ──────────────────────────────────────────────────────────────

@mcp.tool()
async def upload_video(account_id: str, video_path: str, title: str = "") -> str:
    """
    Upload a video file to Meta using chunked upload.
    account_id: format act_XXXXXXXXX
    video_path: absolute path to the video file on disk
    Returns video_id to use in create_video_ad_creative.
    """
    if not os.path.exists(video_path):
        return f"Error: File not found at {video_path}"

    file_size = os.path.getsize(video_path)

    try:
        # Initialize upload session
        init_data = {"upload_phase": "start", "file_size": str(file_size)}
        if title:
            init_data["title"] = title
        r = await _request("POST", f"{VIDEO_URL}/{account_id}/videos",
                           data=init_data, timeout=300)
        if r.status_code >= 400:
            return _friendly_error(r)
        init_result = r.json()

        upload_session_id = init_result.get("upload_session_id")
        video_id = init_result.get("video_id")

        if not upload_session_id:
            return _truncate(init_result)

        # Transfer in 10MB chunks
        chunk_size = 10 * 1024 * 1024
        start_offset = 0

        with open(video_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break

                r = await _request(
                    "POST", f"{VIDEO_URL}/{account_id}/videos",
                    data={
                        "upload_phase": "transfer",
                        "upload_session_id": upload_session_id,
                        "start_offset": str(start_offset),
                    },
                    files={"video_file_chunk": ("chunk", chunk, "application/octet-stream")},
                    timeout=300,
                )
                if r.status_code >= 400:
                    return _friendly_error(r)
                result = r.json()
                start_offset = int(result.get("start_offset", start_offset + len(chunk)))

                if start_offset >= file_size:
                    break

        # Finish upload
        r = await _request("POST", f"{VIDEO_URL}/{account_id}/videos",
                           data={"upload_phase": "finish",
                                 "upload_session_id": upload_session_id},
                           timeout=300)
        if r.status_code >= 400:
            return _friendly_error(r)
    except httpx.RequestError as e:
        return f"Network error during video upload: {e}"

    return json.dumps({"video_id": video_id, "status": "uploaded"})


# ── Image Upload ──────────────────────────────────────────────────────────────

@mcp.tool()
async def upload_image(account_id: str, image_path: str) -> str:
    """
    Upload an image to a Meta ad account.
    image_path: absolute path to the image file on disk
    Returns image_hash to use in create_image_ad_creative.
    """
    if not os.path.exists(image_path):
        return f"Error: File not found at {image_path}"

    filename = os.path.basename(image_path)

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    try:
        r = await _request("POST", f"{BASE_URL}/{account_id}/adimages",
                           files={"filename": (filename, image_bytes)}, timeout=120)
    except httpx.RequestError as e:
        return f"Network error during image upload: {e}"
    if r.status_code >= 400:
        return _friendly_error(r)
    return _truncate(r.json())


# ── Insights ──────────────────────────────────────────────────────────────────

@mcp.tool()
async def get_insights(
    object_id: str,
    since: str,
    until: str,
    level: str = "ad",
    breakdown: str = ""
) -> str:
    """
    Get performance insights for an account, campaign, ad set, or ad.
    object_id: account ID (act_XXX), campaign ID, adset ID, or ad ID
    since/until: YYYY-MM-DD
    level: account, campaign, adset, ad
    breakdown: optional — age, gender, country, device_platform, publisher_platform
    """
    params = {
        "fields": ("campaign_name,adset_name,ad_name,impressions,clicks,spend,ctr,cpc,cpm,"
                   "reach,frequency,inline_link_clicks,inline_link_click_ctr,"
                   "cost_per_inline_link_click,actions,cost_per_action_type,cpp"),
        "time_range": json.dumps({"since": since, "until": until}),
        "level": level,
        "limit": 100,
    }
    if breakdown:
        params["breakdowns"] = breakdown
    return await _get_paged(f"{object_id}/insights", params)


# ── Pages & Audiences ─────────────────────────────────────────────────────────

@mcp.tool()
async def get_pages() -> str:
    """Get Facebook Pages connected to this account."""
    return await _get_paged("me/accounts", {"fields": "id,name,category,fan_count"})


@mcp.tool()
async def get_custom_audiences(account_id: str) -> str:
    """List custom audiences for an ad account."""
    return await _get_paged(f"{account_id}/customaudiences", {
        "fields": "id,name,subtype,approximate_count,description"
    })


if __name__ == "__main__":
    mcp.run()
