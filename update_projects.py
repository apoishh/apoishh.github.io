"""
Builds the Projects page data from your public GitHub repos.

    python update_projects.py          new projects / previews older than a week
    python update_projects.py --all    retake every preview screenshot

Saves js/projects.js (each repo's name, languages, live link, ...) so visitors'
browsers never call GitHub themselves. GitHub only allows 60 calls an hour per
internet address, which a shared campus or office network uses up fast.
For repos with a live site it also opens the site in a hidden browser
(Edge on Windows, Chrome on Linux) and saves a screenshot in previews/.
The daily GitHub job runs this, so new projects show up within a day.
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
OUT_JS = ROOT / "js" / "projects.js"
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
    forks = bool(re.search(r'showForks:\s*true', block))
    return user, hidden, overrides, forks


def github(path):
    req = urllib.request.Request(f"https://api.github.com/{path}", headers={
        "Accept": "application/vnd.github+json", "User-Agent": "portfolio-projects"})
    token = os.environ.get("GITHUB_TOKEN")  # set in the daily GitHub job: higher limit
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    return json.load(urllib.request.urlopen(req, timeout=30))


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
    return None


def screenshot(browser, url, dest):
    with tempfile.TemporaryDirectory() as tmp:
        png = Path(tmp) / "shot.png"
        subprocess.run([
            browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--mute-audio",
            "--no-first-run", "--no-default-browser-check", f"--user-data-dir={tmp}/profile",
            f"--window-size={WIDTH},{HEIGHT}", "--virtual-time-budget=8000",
            f"--screenshot={png}", url,
        ] + (["--no-sandbox"] if sys.platform.startswith("linux") else []),
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        if not png.exists():
            raise RuntimeError("browser made no screenshot")
        with Image.open(png) as im:
            im = im.convert("RGB")
            im = im.resize((SAVE_WIDTH, round(im.height * SAVE_WIDTH / im.width)), Image.LANCZOS)
            im.save(dest, "JPEG", quality=80, optimize=True, progressive=True)
            return im.size


def main():
    user, hidden, overrides, forks = settings()
    old = {}
    if OUT_JS.exists():
        text = OUT_JS.read_text(encoding="utf-8")
        old = {p["name"]: p.get("preview") for p in json.loads(text[text.index("["):text.rindex("]") + 1])}

    repos = [r for r in github(f"users/{user}/repos?per_page=100")
             if (forks or not r["fork"]) and not r["archived"] and r["name"].lower() not in hidden]
    repos.sort(key=lambda r: r["pushed_at"], reverse=True)

    browser = find_browser()
    if not browser:
        print("  no Edge or Chrome found - keeping old screenshots")
    OUT_DIR.mkdir(exist_ok=True)
    projects, now = [], time.time()
    for r in repos:
        name = r["name"]
        # the one place that decides a repo's live site
        live = (overrides.get(name) or r["homepage"]
                or (f"https://{user}.github.io/{name}/" if r["has_pages"] else ""))
        try:
            languages = github(f"repos/{user}/{name}/languages")
        except Exception:
            languages = {r["language"]: 1} if r["language"] else {}

        preview, prev, dest = None, old.get(name), OUT_DIR / f"{name}.jpg"
        if live:
            fresh = (prev and dest.exists() and prev.get("url") == live
                     and now - prev.get("taken", 0) < MAX_AGE_DAYS * 86400)
            if fresh and "--all" not in sys.argv:
                preview = prev
            elif browser:
                try:
                    w, h = screenshot(browser, live, dest)
                    preview = {"src": f"previews/{name}.jpg", "w": w, "h": h, "url": live, "taken": int(now)}
                    print("  preview", name)
                except Exception as e:
                    print(f"  couldn't preview {name}: {e}")
            if not preview and prev and dest.exists():
                preview = prev  # keep the last good screenshot

        projects.append({
            "name": name, "url": r["html_url"], "description": r["description"],
            "pushed": r["pushed_at"], "stars": r["stargazers_count"],
            "live": live, "languages": languages, "preview": preview,
        })

    keep = {p["name"] for p in projects if p["preview"]}
    for f in OUT_DIR.glob("*.jpg"):  # projects that no longer have a live site
        if f.stem not in keep:
            f.unlink()
    OUT_JS.write_text(
        "// Generated by update_projects.py - don't edit by hand.\n"
        "const PROJECTS = " + json.dumps(projects, indent=2, ensure_ascii=False) + ";\n",
        encoding="utf-8")
    print(f"projects: {len(projects)} ({len(keep)} with a preview)")


if __name__ == "__main__":
    main()
