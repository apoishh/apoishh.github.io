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

## Updating the site later

1. Double-click `start.bat` and drop new photos into the folders.
   Check them at http://localhost:8080.
2. Open GitHub Desktop. Your changes are listed. Type a short summary
   (e.g. "Add Japan photos") → **Commit to main** → **Push origin**.
3. The live site updates in 1–2 minutes.

If GitHub Desktop says there are new changes on GitHub (from the daily YouTube
refresh), click **Pull origin** first, then push.

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
