#!/usr/bin/env python3
"""Render carousel slides to 1080x1350 PNGs in YOUR brand palette, via a
headless Chromium browser (Chrome, Edge, or Brave — whichever is installed).

Usage:
  python3 render-carousel.py palette.json slides.json output_folder   -> PNGs
  python3 render-carousel.py palette.json slides.json preview.html    -> one-page mockup

If the third argument ends in .html you get a single preview page showing
every slide at true proportions, for approval BEFORE rendering. Anything
else is treated as a folder and the finished PNGs land there.

palette.json — REQUIRED keys:
  {"handle": "@yourhandle",
   "background": "#F5EDE3",      light slide background
   "text": "#3D2314",            main text color on light slides
   "accent": "#C4714A",          the brand pop color (eyebrows, rules, CTA slide)
   "soft": "#F0DEDA",            a soft/tint tone (decorative circle, quote band)
   "serif_font": "Georgia, serif",
   "sans_font": "'Avenir Next', Avenir, 'Segoe UI', sans-serif"}
Optional keys (derived from the required ones when missing):
  accent_deep, divider, quote_border, footer, dark_bg, dark_text, dark_muted,
  cta_bg, cta_text, cta_soft, cta_muted

slides.json is a list of slide objects. Types and fields:
  {"type": "hook",      "eyebrow": "...", "headline": "...", "swipe": "Keep going"}
  {"type": "truth",     "eyebrow": "...", "serif": "...", "body": "..."}
  {"type": "punch",     "text": "..."}
  {"type": "checklist", "eyebrow": "...", "items": ["...", "...", "..."]}
  {"type": "quote",     "text": "..."}
  {"type": "cta",       "headline": "...", "body": "...", "button": "..."}

A single-slide slides.json makes a static post (the slide number is dropped
from the footer automatically). Line breaks in any field: use \\n.
Browser not found? Set the CHROME_PATH environment variable to your
Chrome/Edge/Brave executable and run again.
"""
import json, os, platform, shutil, subprocess, sys, tempfile, html

REQUIRED = ["handle", "background", "text", "accent", "soft", "serif_font", "sans_font"]


def find_browser():
    if os.environ.get("CHROME_PATH") and os.path.exists(os.environ["CHROME_PATH"]):
        return os.environ["CHROME_PATH"]
    system = platform.system()
    candidates = []
    if system == "Darwin":
        candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
    elif system == "Windows":
        for env in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
            base = os.environ.get(env)
            if not base:
                continue
            candidates += [
                os.path.join(base, "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(base, "Microsoft", "Edge", "Application", "msedge.exe"),
                os.path.join(base, "BraveSoftware", "Brave-Browser", "Application", "brave.exe"),
            ]
    else:
        for name in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge", "brave-browser"):
            path = shutil.which(name)
            if path:
                candidates.append(path)
    for path in candidates:
        if os.path.exists(path):
            return path
    raise SystemExit(
        "No Chromium browser found (Chrome, Edge, or Brave). Install one, or set\n"
        "the CHROME_PATH environment variable to the browser executable and rerun."
    )


def mix(hex_a, hex_b, t):
    """Blend two #RRGGBB colors; t=0 -> a, t=1 -> b."""
    a = [int(hex_a.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(hex_b.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


def load_palette(path):
    p = json.load(open(path))
    missing = [k for k in REQUIRED if k not in p]
    if missing:
        raise SystemExit(f"palette.json is missing required keys: {', '.join(missing)}")
    bg, txt, acc, soft = p["background"], p["text"], p["accent"], p["soft"]
    p.setdefault("accent_deep", mix(acc, txt, 0.25))
    p.setdefault("divider", mix(bg, txt, 0.15))
    p.setdefault("quote_border", mix(soft, acc, 0.35))
    p.setdefault("footer", mix(txt, bg, 0.35))
    p.setdefault("dark_bg", txt)
    p.setdefault("dark_text", bg)
    p.setdefault("dark_muted", mix(txt, bg, 0.55))
    p.setdefault("cta_bg", acc)
    p.setdefault("cta_text", "#FFFFFF")
    p.setdefault("cta_soft", mix(acc, "#FFFFFF", 0.85))
    p.setdefault("cta_muted", mix(acc, "#FFFFFF", 0.6))
    return p


def css(p):
    return f"""
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html, body {{ width: 1080px; height: 1350px; overflow: hidden; }}
  body {{ background: {p['background']}; color: {p['text']}; font-family: {p['sans_font']};
         position: relative; padding: 96px; display: flex; flex-direction: column; justify-content: center; }}
  .foot {{ position: absolute; bottom: 60px; left: 96px; right: 96px; display: flex;
          justify-content: space-between; font-size: 26px; font-weight: 600;
          letter-spacing: .14em; text-transform: uppercase; color: {p['footer']}; }}
  .eyebrow {{ font-size: 30px; font-weight: 600; letter-spacing: .16em; text-transform: uppercase;
             color: {p['accent']}; margin-bottom: 36px; }}
  .rule {{ width: 120px; height: 8px; background: {p['accent']}; margin-bottom: 48px; }}
  /* hook */
  .circle {{ position: absolute; width: 600px; height: 600px; border-radius: 50%;
            background: {p['soft']}; top: -210px; right: -210px; }}
  .ring {{ position: absolute; width: 150px; height: 150px; border-radius: 50%;
          border: 7px solid {p['accent']}; top: 265px; right: 120px; }}
  .hook-h {{ font-family: {p['serif_font']}; font-size: 96px; line-height: 1.1; position: relative; }}
  .swipe {{ margin-top: 54px; font-size: 32px; font-weight: 600; letter-spacing: .1em;
           text-transform: uppercase; color: {p['accent_deep']}; position: relative; }}
  /* truth */
  .truth-serif {{ font-family: {p['serif_font']}; font-size: 62px; line-height: 1.3; margin-bottom: 36px; }}
  .body {{ font-size: 42px; line-height: 1.5; }}
  /* punch */
  body.punch {{ background: {p['dark_bg']}; color: {p['dark_text']}; align-items: center; text-align: center; }}
  body.punch .rule {{ margin-left: auto; margin-right: auto; }}
  .punch-t {{ font-family: {p['serif_font']}; font-size: 76px; line-height: 1.2; }}
  body.punch .foot {{ color: {p['dark_muted']}; }}
  /* checklist */
  .item {{ display: flex; gap: 32px; align-items: flex-start; padding: 34px 0; border-bottom: 2px solid {p['divider']}; }}
  .item:last-of-type {{ border-bottom: none; }}
  .tick {{ flex: 0 0 auto; width: 40px; height: 40px; border: 5px solid {p['accent']}; border-radius: 4px; margin-top: 8px; }}
  .item p {{ font-size: 42px; line-height: 1.45; }}
  /* quote */
  .band {{ background: {p['soft']}; border-left: 12px solid {p['quote_border']}; border-radius: 0 8px 8px 0; padding: 64px 56px; }}
  .band p {{ font-family: {p['serif_font']}; font-style: italic; font-size: 58px; line-height: 1.35; }}
  /* cta */
  body.cta {{ background: {p['cta_bg']}; color: {p['cta_text']}; align-items: center; text-align: center; }}
  .cta-h {{ font-family: {p['serif_font']}; font-size: 75px; line-height: 1.15; }}
  .cta-b {{ font-size: 42px; line-height: 1.5; color: {p['cta_soft']}; margin-top: 36px; }}
  .ghost {{ margin-top: 60px; border: 6px solid {p['cta_text']}; border-radius: 8px; padding: 28px 64px;
           font-size: 38px; font-weight: 600; display: inline-block; }}
  body.cta .foot {{ color: {p['cta_muted']}; }}
"""


def esc(s):
    return html.escape(str(s), quote=False).replace("\\n", "<br>").replace("\n", "<br>")


def build(slide, n, total, p):
    t = slide["type"]
    number = f"{n:02d}" if total > 1 else ""
    foot = f'<div class="foot"><span>{esc(p["handle"])}</span><span>{number}</span></div>'
    cls = ""
    if t == "hook":
        inner = (f'<div class="circle"></div><div class="ring"></div>'
                 f'<p class="eyebrow" style="position:relative">{esc(slide["eyebrow"])}</p>'
                 f'<p class="hook-h">{esc(slide["headline"])}</p>'
                 f'<p class="swipe">{esc(slide.get("swipe", "Keep going"))} &rsaquo;</p>')
    elif t == "truth":
        inner = (f'<p class="eyebrow">{esc(slide["eyebrow"])}</p><div class="rule"></div>'
                 f'<p class="truth-serif">{esc(slide["serif"])}</p>'
                 f'<p class="body">{esc(slide["body"])}</p>')
    elif t == "punch":
        cls = "punch"
        inner = f'<div class="rule"></div><p class="punch-t">{esc(slide["text"])}</p>'
    elif t == "checklist":
        items = "".join(f'<div class="item"><span class="tick"></span><p>{esc(i)}</p></div>'
                        for i in slide["items"][:3])
        inner = f'<p class="eyebrow">{esc(slide["eyebrow"])}</p><div class="rule"></div>{items}'
    elif t == "quote":
        inner = f'<div class="band"><p>{esc(slide["text"])}</p></div>'
    elif t == "cta":
        cls = "cta"
        inner = (f'<p class="cta-h">{esc(slide["headline"])}</p>'
                 f'<p class="cta-b">{esc(slide["body"])}</p>'
                 f'<span class="ghost">{esc(slide.get("button", "It is in my bio"))}</span>')
    else:
        raise SystemExit(f"Unknown slide type: {t}")
    return (f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{css(p)}</style></head>'
            f'<body class="{cls}">{inner}{foot}</body></html>')


def write_preview(pages, out, p):
    """One self-contained page: every slide at true proportions, scaled down."""
    scale = 0.32
    w, h = int(1080 * scale), int(1350 * scale)
    cards = []
    for n, page in enumerate(pages, 1):
        cards.append(
            f'<figure><div class="frame" style="width:{w}px;height:{h}px">'
            f'<iframe srcdoc="{html.escape(page, quote=True)}" '
            f'style="width:1080px;height:1350px;border:0;transform:scale({scale});transform-origin:0 0"></iframe>'
            f'</div><figcaption>Slide {n:02d}</figcaption></figure>')
    doc = (f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>Carousel mockup</title><style>'
           f'body{{margin:0;padding:36px;background:#1E1E1E;color:#EEE;'
           f'font-family:{p["sans_font"]}}} h1{{font-size:20px;font-weight:600;margin:0 0 6px}}'
           f'p.note{{font-size:14px;color:#AAA;margin:0 0 28px}}'
           f'.grid{{display:flex;flex-wrap:wrap;gap:22px}}'
           f'figure{{margin:0}} .frame{{overflow:hidden;border-radius:8px;'
           f'box-shadow:0 4px 18px rgba(0,0,0,.5)}}'
           f'figcaption{{font-size:12px;color:#AAA;margin-top:8px;text-align:center}}'
           f'</style></head><body><h1>Carousel mockup</h1>'
           f'<p class="note">True proportions, scaled down. The finished PNGs render at 1080 x 1350.</p>'
           f'<div class="grid">{"".join(cards)}</div></body></html>')
    open(out, "w").write(doc)
    print(f"wrote mockup {out}")


def main():
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    palette = load_palette(sys.argv[1])
    slides = json.load(open(sys.argv[2]))
    target = sys.argv[3]
    pages = [build(s, n, len(slides), palette) for n, s in enumerate(slides, 1)]

    if target.lower().endswith(".html"):
        write_preview(pages, target, palette)
        return

    browser = find_browser()
    os.makedirs(target, exist_ok=True)
    for n, page in enumerate(pages, 1):
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
            f.write(page)
            path = f.name
        out = os.path.join(target, f"slide-{n:02d}.png")
        subprocess.run([browser, "--headless", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", "--window-size=1080,1350",
                        f"--screenshot={out}", f"file://{path}"],
                       check=True, capture_output=True)
        os.unlink(path)
        print(f"rendered {out}")


if __name__ == "__main__":
    main()
