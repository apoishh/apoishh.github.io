# Photography Portfolio

Plain HTML/CSS/JS — no build step, no frameworks.

## Edit the site
Everything lives in **`js/config.js`**: your name, links, pages, photos and videos.

1. Drop full-size photos into `photos/preconvo/`, `photos/travel/`, etc.
2. Run:
   ```bash
   python update_photos.py
   ```
   This makes web-sized copies in each folder's `web/` subfolder (~18 MB → ~300 KB)
   and writes `js/photos.js` with each photo's shape.
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
Loads your public GitHub repos live (newest-updated first, the newest one
featured). Forks and repos listed in `hide` (in `config.js`) are left out.
Each card shows every language the repo uses (with percentages).
Descriptions come from `descriptions` in `config.js`, or from the repo's
description on GitHub if it isn't listed there. Repos with GitHub Pages get an
"Open live" button automatically. The "Coding activity" graph is your GitHub
contribution calendar for the last 12 months (via a free public mirror,
github-contributions-api.jogruber.de, since GitHub only offers it to signed-in apps).

## Add a page
Copy a block in `pages` and give it a new `id` and `title`. Types: `gallery`, `videos`, `about`.

## Preview locally (with auto-updating photos)
Double-click **`start.bat`** (or run `python serve.py`). It opens the site at
http://localhost:8080 and watches `photos/`: drop photos into a folder, delete
or replace them, then refresh the page. Keep the window open while you work.

## Publish (free)
See **[PUBLISHING.md](PUBLISHING.md)**: GitHub Pages setup, updating, and custom domain.
