# Photography Portfolio

Plain HTML/CSS/JS — no build step, no frameworks.

## Edit the site
Everything lives in **`js/config.js`**: your name, links, pages, photos and videos.

1. Open `start.bat` and drop full-size photos into `photos/preconvo/`, `photos/travel/<place>/`, etc.
2. It makes two copies of each photo automatically (or run `python update_photos.py`):
   `web/` (2000px, ~300 KB) for the full-screen view and `thumb/` (800px) for
   the grid, and writes `js/photos.js` with each photo's shape.
   File types it can't read (like iPhone `.HEIC`) are listed as "skipped".
3. Make sure the gallery in `config.js` has `folder: "<folder name>"`.

Photos keep their original ratio (portrait and landscape mixed) in a two-column
masonry grid, **newest added first**. For oldest first, set `NEWEST_FIRST = False`
in `update_photos.py`.

**Place sections:** make a subfolder per place, e.g. `photos/travel/Bromo`,
`photos/travel/Krabi 2025`. Each becomes its own titled section on the page,
with jump links at the top.

**Travel order** uses the date the camera stored in each photo: most recent
trip first, and photos inside a trip in the order you took them. Other pages
show the most recently added photos first. (`BY_DATE_TAKEN` in `update_photos.py`.)

RAW files (.ARW, .CR2, .NEF, .DNG, ...) work too: the script uses the camera's
built-in full-size preview. If a RAW and a JPG share a name, the JPG wins.
Needs `pip install pillow rawpy`.

## YouTube page
Shows your latest upload + your 4 most-viewed videos from `youtubeChannel` in
`config.js`. Once online, GitHub refreshes it daily
(`.github/workflows/update-videos.yml`). To refresh by hand run
`python update_videos.py`. Needs `pip install yt-dlp`.

## Projects page
Shows your public GitHub repos (newest-updated first, the newest one featured)
from `js/projects.js`, which `update_projects.py` builds. The daily GitHub job
runs it, so new projects appear within a day; run `python update_projects.py`
from a normal Windows window to update right away. Visitors' browsers never
call GitHub (its limit is 60 calls an hour per internet address).
Forks and repos listed in `hide` (in `config.js`) are left out.
Each card shows every language the repo uses (with percentages).
Descriptions come from `descriptions` in `config.js`, or from the repo's
description on GitHub if it isn't listed there. Repos with GitHub Pages get an
"Open live" button automatically (fix the address in `live` in `config.js`
if it's wrong), plus a screenshot preview and a bigger tile.

Check the publish list still works: `python test_git_sync.py`.

The "Coding activity" graph is your GitHub
contribution calendar for the last 12 months (via a free public mirror,
github-contributions-api.jogruber.de, since GitHub only offers it to signed-in apps).

## Add a page
Copy a block in `pages` and give it a new `id` and `title`. Types: `gallery`, `github`, `videos`, `about`.

## Preview locally (with auto-updating photos)
Double-click **`start.bat`** (or run `python serve.py`). It opens the site at
http://localhost:8080 and watches `photos/`: drop photos into a folder, delete
or replace them, then refresh the page. Keep the window open while you work.

## Publish (free)
See **[PUBLISHING.md](PUBLISHING.md)**: GitHub Pages setup, updating, and custom domain.
