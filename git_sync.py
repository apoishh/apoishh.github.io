"""
Auto-publishes the site to GitHub while start.bat is running.

When anything in the project changes (new photos, edits to config.js, ...)
and then stays unchanged for QUIET_SECONDS, it commits everything and pushes.
GitHub Pages then updates the live site in 1-2 minutes.

It also pulls from GitHub every few minutes, so the daily YouTube refresh
made on GitHub doesn't clash with your changes.

Originals and RAW photos are never uploaded (see .gitignore).
"""
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).parent
QUIET_SECONDS = 60  # wait this long after the last change before publishing
CHECK_EVERY = 10
PULL_EVERY = 300


def git(*args):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def log(msg):
    print(time.strftime("[%H:%M:%S]"), msg, flush=True)


def changes():
    """Changed files plus their modification times, to notice ongoing edits."""
    _, out = git("status", "--porcelain", "--untracked-files=all")
    if not out:
        return None
    snap = []
    for line in out.splitlines():
        path = ROOT / line[3:].strip('"').split(" -> ")[-1]
        snap.append((line, path.stat().st_mtime if path.exists() else 0))
    return tuple(snap)


def summary(snap):
    photos = sum(1 for line, _ in snap if "/web/" in line and line[:2].strip() in ("??", "A"))
    removed = sum(1 for line, _ in snap if "/web/" in line and "D" in line[:2])
    other = sum(1 for line, _ in snap if "/web/" not in line and "photos.js" not in line)
    parts = []
    if photos:
        parts.append(f"add {photos} photo{'s' * (photos != 1)}")
    if removed:
        parts.append(f"remove {removed} photo{'s' * (removed != 1)}")
    if other:
        parts.append(f"edit {other} file{'s' * (other != 1)}")
    return "Update site: " + (", ".join(parts) or "changes")


def pull():
    code, out = git("pull", "--rebase", "origin", "main")
    if code != 0:
        git("rebase", "--abort")
        log("Couldn't pull from GitHub: " + (out.splitlines()[-1] if out else "unknown error"))
        log("Open GitHub Desktop to sort it out. Auto-publish keeps trying.")
        return False
    return True


def publish(snap):
    msg = summary(snap)
    git("add", "-A")
    code, out = git("commit", "-m", msg)
    if code != 0 and "nothing to commit" not in out:
        log("Commit failed: " + out)
        return
    if not pull():
        return
    code, out = git("push", "origin", "HEAD:main")
    if code == 0:
        log(f"Published to GitHub ({msg}). Live in 1-2 minutes.")
    else:
        log("Push failed (will retry): " + out.splitlines()[-1])


def unpushed():
    code, out = git("rev-list", "--count", "origin/main..HEAD")
    return code == 0 and out.isdigit() and int(out) > 0


def run():
    code, _ = git("remote", "get-url", "origin")
    if code != 0:
        log("Auto-publish off: this folder isn't connected to GitHub yet.")
        return
    log(f"Auto-publish on: changes go to GitHub {QUIET_SECONDS}s after you stop editing.")
    last_snap, changed_at, last_pull = None, time.time(), 0
    while True:
        try:
            snap = changes()
            if snap != last_snap:
                last_snap, changed_at = snap, time.time()
            elif snap and time.time() - changed_at >= QUIET_SECONDS:
                publish(snap)
                last_snap, last_pull = changes(), time.time()
            elif not snap and time.time() - last_pull >= PULL_EVERY:
                git("fetch", "-q", "origin")
                if unpushed():  # an earlier push failed - retry
                    code, out = git("push", "origin", "HEAD:main")
                    if code == 0:
                        log("Published earlier changes to GitHub.")
                pull()
                last_pull = time.time()
        except Exception as e:
            log(f"Auto-publish error: {e}")
        time.sleep(CHECK_EVERY)


def publish_now():
    """Publish immediately (used by publish.bat)."""
    import update_photos
    update_photos.build()  # make sure new photos are processed first
    snap = changes()
    if snap:
        publish(snap)
    elif unpushed():
        code, out = git("push", "origin", "HEAD:main")
        log("Published to GitHub." if code == 0 else "Push failed: " + out)
    else:
        log("Nothing new to publish - the site is up to date.")


if __name__ == "__main__":
    import sys
    try:
        publish_now() if "--now" in sys.argv else run()
    except KeyboardInterrupt:
        pass
