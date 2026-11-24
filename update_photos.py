"""
Makes the site pick up whatever photos are in the photos/ folders.

    python update_photos.py           run once
    python update_photos.py --watch   keep running; re-run whenever photos are
                                      added, removed or replaced

For every folder in photos/ (e.g. photos/preconvo, photos/travel) it:
  1. makes a web-sized copy of each original in photos/<folder>/web/
     (2000px long edge, fixed rotation, so the site loads fast)
  2. writes js/photos.js with each photo's size, so the grid keeps
     every photo's real ratio.

Place sections: make subfolders, e.g. photos/travel/Bromo, photos/travel/Turkey.
Each becomes its own section on that page, titled with the folder name.

Order:
  - Pages in BY_DATE_TAKEN (Travel): trips ordered by when you went there
    (most recent trip first), and photos inside a trip in the order you took them.
    Uses the date the camera stored in each photo.
  - Other pages (Pre-Convo): most recently added photo first.
Set NEWEST_FIRST = False below to flip both to oldest first.

RAW files (.ARW, .CR2, .NEF, ...) work too. If a RAW and a JPG share a name
(DSC0001.ARW + DSC0001.JPG) the JPG is used, so your edits win.

Needs:  pip install pillow rawpy
"""
from pathlib import Path
import io
import json
import sys
import time
from PIL import Image, ImageOps

ROOT = Path(__file__).parent
PHOTOS = ROOT / "photos"
OUT_JS = ROOT / "js" / "photos.js"
LONG_EDGE = 2000
QUALITY = 82
NEWEST_FIRST = True
BY_DATE_TAKEN = {"travel"}  # pages ordered by the date photos were taken
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}
RAW_EXTS = {".arw", ".cr2", ".cr3", ".nef", ".raf", ".rw2", ".orf", ".dng", ".pef", ".srw"}


def added_time(p):
    st = p.stat()
    # On Windows st_ctime is when the file was created in this folder.
    return getattr(st, "st_birthtime", st.st_ctime)


_taken_cache = {}


def taken_time(p):
    """When the photo was taken, from the camera's EXIF data.
    Falls back to the file's modified time (usually the shoot date too)."""
    st = p.stat()
    key = (str(p), st.st_mtime, st.st_size)
    if key in _taken_cache:
        return _taken_cache[key]
    stamp = None
    try:
        if p.suffix.lower() in RAW_EXTS:
            import rawpy
            with rawpy.imread(str(p)) as raw:
                thumb = raw.extract_thumb()
                exif = Image.open(io.BytesIO(thumb.data)).getexif()
        else:
            with Image.open(p) as im:
                exif = im.getexif()
        text = exif.get_ifd(0x8769).get(36867) or exif.get(306)  # DateTimeOriginal / DateTime
        if text:
            stamp = time.mktime(time.strptime(text.strip()[:19], "%Y:%m:%d %H:%M:%S"))
    except Exception:
        pass
    _taken_cache[key] = stamp or st.st_mtime
    return _taken_cache[key]


def by_date_taken(folder):
    return folder.relative_to(PHOTOS).parts[0] in BY_DATE_TAKEN


def originals_in(folder):
    files = [p for p in folder.iterdir()
             if p.is_file() and p.suffix.lower() in EXTS | RAW_EXTS]
    # one photo per name; prefer the JPG/edited file over the RAW
    by_stem = {}
    for p in files:
        cur = by_stem.get(p.stem.lower())
        if cur is None or (cur.suffix.lower() in RAW_EXTS and p.suffix.lower() in EXTS):
            by_stem[p.stem.lower()] = p
    if by_date_taken(folder):
        # a trip reads like a story: first shot to last
        return sorted(by_stem.values(), key=lambda p: (taken_time(p), p.name),
                      reverse=not NEWEST_FIRST)
    return sorted(by_stem.values(), key=lambda p: (added_time(p), p.name),
                  reverse=NEWEST_FIRST)


def open_image(src):
    if src.suffix.lower() not in RAW_EXTS:
        return ImageOps.exif_transpose(Image.open(src))
    import rawpy  # pip install rawpy
    with rawpy.imread(str(src)) as raw:
        flip = raw.sizes.flip
        try:
            thumb = raw.extract_thumb()  # camera's own full-size JPEG preview
            if thumb.format != rawpy.ThumbFormat.JPEG:
                raise ValueError("no JPEG preview")
            im = Image.open(io.BytesIO(thumb.data))
            if im.getexif().get(0x0112, 1) != 1:
                return ImageOps.exif_transpose(im)
            if min(im.size) < 1000:
                raise ValueError("preview too small")
            rotate = {3: 180, 5: 90, 6: 270}.get(flip)
            return im.rotate(rotate, expand=True) if rotate else im
        except Exception:
            return Image.fromarray(raw.postprocess(use_camera_wb=True))


def photo_folders():
    """photos/<page> and any place subfolders, e.g. photos/travel/bromo."""
    return sorted(p for p in PHOTOS.rglob("*")
                  if p.is_dir() and "web" not in p.relative_to(PHOTOS).parts)


def build():
    result, newest = {}, {}
    for folder in photo_folders():
        originals = originals_in(folder)
        web_dir = folder / "web"
        items = []
        if originals:
            web_dir.mkdir(exist_ok=True)
        for src in originals:
            dst = web_dir / (src.stem + ".jpg")
            try:
                if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
                    im = open_image(src).convert("RGB")
                    im.thumbnail((LONG_EDGE, LONG_EDGE), Image.LANCZOS)
                    im.save(dst, "JPEG", quality=QUALITY, optimize=True, progressive=True)
                    print("  made", dst.relative_to(ROOT))
                with Image.open(dst) as im:
                    w, h = im.size
            except Exception as e:  # half-copied or broken file: skip, retry next time
                print(f"  skipped {src.name}: {e}")
                continue
            items.append({"src": dst.relative_to(ROOT).as_posix(), "w": w, "h": h})

        # remove web copies whose original was deleted
        if web_dir.exists():
            keep = {src.stem.lower() for src in originals}
            for old in web_dir.glob("*.jpg"):
                if old.stem.lower() not in keep:
                    old.unlink()
                    print("  removed", old.relative_to(ROOT))

        if items:
            key = folder.relative_to(PHOTOS).as_posix()  # e.g. "travel/bromo"
            result[key] = items
            stamp = taken_time if by_date_taken(folder) else added_time
            newest[key] = max(stamp(p) for p in originals)
            print(f"  {key}: {len(items)} photos")

    # Pages in name order; place sections inside a page newest first
    # (latest trip for Travel, latest added for other pages).
    def order(key):
        top, *rest = key.split("/")
        return (top, bool(rest), -newest[key] if NEWEST_FIRST else newest[key])
    result = {k: result[k] for k in sorted(result, key=order)}

    OUT_JS.write_text(
        "// Generated by update_photos.py - don't edit by hand.\n"
        "const PHOTOS = " + json.dumps(result, indent=2) + ";\n",
        encoding="utf-8",
    )
    print(time.strftime("[%H:%M:%S]"), "site photos updated")


def snapshot():
    """Names, sizes and times of every original, to spot changes."""
    snap = []
    for folder in photo_folders():
        for p in originals_in(folder):
            st = p.stat()
            snap.append((str(p), st.st_size, st.st_mtime))
    return snap


def watch(interval=2):
    print("Watching photos/ for changes. Leave this running; Ctrl+C to stop.")
    build()
    built, prev = snapshot(), None
    while True:
        time.sleep(interval)
        now = snapshot()
        # wait until files stop changing (big photos take a moment to copy)
        if now == prev and now != built:
            build()
            built = now
        prev = now


if __name__ == "__main__":
    try:
        watch() if "--watch" in sys.argv else build()
    except KeyboardInterrupt:
        pass
