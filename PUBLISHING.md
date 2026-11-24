# Putting the site online (GitHub Pages, free)

The project is already a Git repository with everything committed. Only the
small web copies of your photos are included. Originals and RAWs stay on your PC.

## One-time setup (~10 minutes)

1. **Create a GitHub account** at https://github.com/signup
   Pick your username carefully: the free address will be `https://<username>.github.io`.

2. **Install GitHub Desktop** from https://desktop.github.com and sign in.

3. **Add this folder:** File → *Add local repository* → choose this
   `Website portfolio` folder.

4. **Publish it:** click **Publish repository**.
   - Name: `<your-username>.github.io` (exactly, e.g. `apoishh.github.io`)
     so the site lives at `https://<username>.github.io`.
   - **Untick "Keep this code private"**: free GitHub Pages needs a public repo.
     Visitors can see the site's files on GitHub, which is normal for a portfolio.
     Your originals and RAWs are never uploaded.

5. **Turn on Pages:** on github.com open the repo → **Settings → Pages** →
   Source: *Deploy from a branch* → Branch: `main`, folder `/ (root)` → Save.
   After 1–2 minutes the site is live at `https://<username>.github.io`.

6. **Allow the daily YouTube refresh:** repo → **Settings → Actions → General** →
   Workflow permissions → *Read and write permissions* → Save.
   To test it now: **Actions** tab → *Update YouTube videos* → **Run workflow**.

## Updating the site later (automatic)

1. Double-click `start.bat` and leave its window open.
2. Drop new photos into the folders, or edit `js/config.js`.
3. About a minute after you stop making changes, they're committed and pushed
   to GitHub automatically. The window shows "Published to GitHub".
   The live site updates 1–2 minutes later.

Notes:
- It only publishes while `start.bat` is running. Changes made while it's
  closed get published the next time you start it.
- Want to edit without publishing yet? Run `python serve.py --no-sync` instead.
- The first push may open a GitHub sign-in window. Sign in once and it's remembered.
- If the window says it couldn't pull or push, open GitHub Desktop to see why.

## Publish right now (manual)

Double-click **`publish.bat`**. It processes any new photos and pushes to
GitHub immediately, with no 60-second wait. It works whether or not `start.bat`
is open. GitHub Desktop (**Commit to main** → **Push origin**) works too.

## Don't see your changes on the live site?
Browsers keep GitHub Pages files for up to 10 minutes. Press **Ctrl+F5**
on the site to force a fresh copy.

## Custom domain (e.g. apoishh.com)

1. Buy the domain from a registrar (Cloudflare, Namecheap, Porkbun, ...).
   Usually around US$10–15 a year for .com.
2. In the registrar's **DNS settings**, add these records:

   | Type  | Name  | Value                   |
   |-------|-------|-------------------------|
   | A     | @     | 185.199.108.153         |
   | A     | @     | 185.199.109.153         |
   | A     | @     | 185.199.110.153         |
   | A     | @     | 185.199.111.153         |
   | CNAME | www   | `<username>.github.io`  |

3. On GitHub: repo → **Settings → Pages → Custom domain** → enter `apoishh.com` → Save.
   (This creates a `CNAME` file in the repo. Pull it in GitHub Desktop.)
4. Once the check passes (can take up to a few hours), tick **Enforce HTTPS**.

## Good to know
- GitHub pauses scheduled jobs on repos with no activity for 60 days. If the
  YouTube page stops updating, push anything or run the workflow by hand.
- YouTube sometimes blocks requests from GitHub's servers. If a refresh
  fails, the site just keeps the last list. You can run
  `python update_videos.py` on your PC and push.
