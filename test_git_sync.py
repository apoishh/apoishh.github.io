"""Self-check for the publish list.  Run:  python test_git_sync.py"""
from git_sync import describe, summary

# git status lines as git prints them (some start with a space)
snap = tuple((line, 0) for line in [
    " M js/config.js",
    "?? photos/travel/Bali/web/DSC0001.jpg",
    "?? photos/travel/Bali/thumb/DSC0001.jpg",
    " D photos/preconvo/web/DSC0002.jpg",
    " M js/photos.js",
    "?? secret.pdf",
] + [f"?? photos/travel/Bali/web/IMG{i}.jpg" for i in range(10)])

text = describe(snap)
assert "   ~ js/config.js" in text, text            # first letter not cut off
assert "   + secret.pdf" in text, text              # non-photo files always shown
assert "   + travel/Bali/DSC0001.jpg" in text, text # photos shown by place
assert "thumb" not in text and "photos.js" not in text, text  # generated files hidden
assert "... and 4 more photos" in text, text        # only the photo list is shortened
assert summary(snap) == "Update site: add 11 photos, remove 1 photo, edit 2 files", summary(snap)
print("ok")
