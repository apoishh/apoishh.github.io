"""
Publishes the site to GitHub from the start.bat window.

When anything in the project changes (new photos, edits to config.js, ...)
and then stays unchanged for QUIET_SECONDS, it lists what changed and asks
"Publish to GitHub now?". Type y + Enter to publish, n to wait.
You can also type p + Enter at any time to publish straight away.
GitHub Pages then updates the live site in 1-2 minutes.

It also pulls from GitHub every few minutes, so the daily YouTube refresh
made on GitHub doesn't clash with your changes.

Originals and RAW photos are never uploaded (see .gitignore).
"""
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).parent
QUIET_SECONDS = 20  # wait this long after the last change before asking
CHECK_EVERY = 2
PULL_EVERY = 300


def git(*args):
    # stdin=DEVNULL: git must not share the window's keyboard input, which the
    # prompt reader is waiting on (on Windows that would freeze both).
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True,
                       stdin=subprocess.DEVNULL)
    # rstrip only: git status lines can start with a space (" M file")
    return r.returncode, (r.stdout + r.stderr).rstrip()


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


def describe(snap):
    """Readable list of what changed, for the confirm question."""
    names = []
    for line, _ in snap:
        path = line[3:].strip('"').split(" -> ")[-1]
        if path == "js/photos.js":
            continue
        sign = "-" if "D" in line[:2] else "+" if line[:2].strip() in ("??", "A") else "~"
        if "/web/" in path:  # show the photo as "travel/Bromo/DSC0001.jpg"
            path = path.replace("photos/", "", 1).replace("/web/", "/")
        names.append(f"   {sign} {path}")
    more = len(names) - 8
    return "\n".join(names[:8] + ([f"   ... and {more} more"] if more > 0 else []))


def _read_keys(q):
    """Collect what's typed into the start.bat window."""
    for line in sys.stdin:
        q.put(line.strip().lower())


def run():
    code, _ = git("remote", "get-url", "origin")
    if code != 0:
        log("Publishing off: this folder isn't connected to GitHub yet.")
        return
    print("\n  Publishing: you'll be asked before anything goes online.")
    print("  Type  p  + Enter at any time to publish right away.\n", flush=True)
    keys = queue.Queue()
    threading.Thread(target=_read_keys, args=(keys,), daemon=True).start()

    last_snap, changed_at, last_pull = None, time.time(), 0
    asked = None      # the changes we're currently asking about
    declined = None   # changes you said "n" to - don't ask again until something new
    while True:
        try:
            snap = changes()
            if snap != last_snap:
                last_snap, changed_at = snap, time.time()
                if asked and snap != asked:
                    asked = None  # more changes arrived; ask again once they settle

            # answers / commands typed in the window
            while not keys.empty():
                key = keys.get()
                if key in ("p", "y", "yes", "publish") and (snap or unpushed()):
                    if snap:
                        publish(snap)
                    else:
                        code, out = git("push", "origin", "HEAD:main")
                        log("Published to GitHub." if code == 0 else "Push failed: " + out)
                    last_snap, asked, declined, last_pull = changes(), None, None, time.time()
                    snap = last_snap
                elif key in ("p", "y", "yes", "publish"):
                    log("Nothing new to publish - the site is up to date.")
                elif key in ("n", "no") and asked:
                    declined, asked = asked, None
                    log("OK, not published. I'll ask again after your next change (or type p).")

            if snap and not asked and snap != declined and time.time() - changed_at >= QUIET_SECONDS:
                asked = snap
                print(f"\n{time.strftime('[%H:%M:%S]')} Changes ready to publish ({summary(snap)[13:]}):")
                print(describe(snap))
                print("   Publish to GitHub now?  Type  y + Enter  (or  n  to wait)\n", flush=True)
            elif not snap and time.time() - last_pull >= PULL_EVERY:
                git("fetch", "-q", "origin")
                if unpushed():
                    log("You have published-but-not-uploaded changes. Type p + Enter to upload them.")
                pull()
                last_pull = time.time()
        except Exception as e:
            log(f"Publish error: {e}")
        time.sleep(CHECK_EVERY)


def publish_now():
    """Publish immediately: python git_sync.py --now"""
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
    try:
        publish_now() if "--now" in sys.argv else run()
    except KeyboardInterrupt:
        pass
