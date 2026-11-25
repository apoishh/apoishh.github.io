"""
Takes a screenshot of each project's live website for the Projects page.

    python update_previews.py          only new projects / previews older than a week
    python update_previews.py --all    retake every preview

Finds your public GitHub repos that have a live site (GitHub Pages or a
website link), opens each one in a hidden browser (Edge on Windows, Chrome
on Linux), and saves previews/<repo>.jpg plus js/previews.js.
The daily GitHub job runs this too, so new projects get a preview within a day.
Needs:  pip install pillow
"""
from pathlib import Path
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

from PIL import Image

ROOT = Path(__file__).parent
CONFIG = ROOT / "js" / "config.js"
OUT_DIR = ROOT / "previews"
OUT_JS = ROOT / "js" / "previews.js"
MAX_AGE_DAYS = 7
WIDTH, HEIGHT = 1440, 900   # browser window size for the screenshot
SAVE_WIDTH = 1200


def settings():
    text = CONFIG.read_text(encoding="utf-8")
    block = text[text.find('type: "github"'):]
    user = re.search(r'user:\s*"([^"]+)"', block).group(1)
    hide = re.search(r'hide:\s*\[([^\]]*)\]', block)
    hidden = {h.lower() for h in re.findall(r'"([^"]+)"', hide.group(1))} if hide else set()
    live = re.search(r'live:\s*\{([^}]*)\}', block)
    overrides = dict(re.findall(r'"([^"]+)"\s*:\s*"([^"]+)"', live.group(1))) if live else {}
    return user, hidden, overrides


def find_browser():
    candidates = [
        os.environ.get("BROWSER_PATH", ""),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        shutil.which("google-chrome") or "", shutil.which("chromium") or "",
        shutil.which("chromium-browser") or "", shutil.which("microsoft-edge") or "",
    ]
    for c in candidates:
        if c and Path(c).exists():
            return c
    raise SystemExit("No Edge or Chrome found for taking screenshots.")


def live_sites(user, hidden, overrides):
    req = urllib.request.Request(
        f"https://api.github.com/users/{user}/repos?per_page=100",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "portfolio-previews"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    repos = json.load(urllib.request.urlopen(req, timeout=30))
    sites = {}
    for r in repos:
        if r["fork"] or r["archived"] or r["name"].lower() in hidden:
            continue
        url = (overrides.get(r["name"]) or r["homepage"]
               or (f"https://{user}.github.io/{r['name']}/" if r["has_pages"] else ""))
        if url:
            sites[r["name"]] = url
    return sites


def screenshot(browser, url, dest):
    with tempfile.TemporaryDirectory() as tmp:
        png = Path(tmp) / "shot.png"
        subprocess.run([
            browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--mute-audio",
            "--no-first-run", "--no-default-browser-check", f"--user-data-dir={tmp}/profile",
            f"--window-size={WIDTH},{HEIGHT}", "--virtual-time-budget=8000",
            f"--screenshot={png}", url,
        ] + (["--no-sandbox"] if sys.platform.startswith("linux") else []), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        if not png.exists():
            raise RuntimeError("browser made no screenshot")
        with Image.open(png) as im:
            im = im.convert("RGB")
            im = im.resize((SAVE_WIDTH, round(im.height * SAVE_WIDTH / im.width)), Image.LANCZOS)
            im.save(dest, "JPEG", quality=80, optimize=True, progressive=True)
            return im.size


def main():
    user, hidden, overrides = settings()
    old = {}
    if OUT_JS.exists():
        text = OUT_JS.read_text(encoding="utf-8")
        old = json.loads(text[text.index("{"):text.rindex("}") + 1])
    sites = live_sites(user, hidden, overrides)
    browser = find_browser()
    OUT_DIR.mkdir(exist_ok=True)
    result, now = {}, time.time()
    for name, url in sites.items():
        prev = old.get(name)
        dest = OUT_DIR / f"{name}.jpg"
        fresh = prev and dest.exists() and prev.get("url") == url and now - prev.get("taken", 0) < MAX_AGE_DAYS * 86400
        if fresh and "--all" not in sys.argv:
            result[name] = prev
            continue
        try:
            w, h = screenshot(browser, url, dest)
            result[name] = {"src": f"previews/{name}.jpg", "w": w, "h": h, "url": url, "taken": int(now)}
            print("  preview", name)
        except Exception as e:
            print(f"  couldn't preview {name}: {e}")
            if prev and dest.exists():
                result[name] = prev
    for f in OUT_DIR.glob("*.jpg"):  # projects that no longer have a live site
        if f.stem not in result:
            f.unlink()
    OUT_JS.write_text(
        "// Generated by update_previews.py - don't edit by hand.\n"
        "const PREVIEWS = " + json.dumps(result, indent=2) + ";\n", encoding="utf-8")
    print(f"previews: {len(result)} project{'s' * (len(result) != 1)}")


if __name__ == "__main__":
    main()
