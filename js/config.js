/* ==========================================================================
   SITE CONFIG — this is the only file you need to edit to update the site.
   ==========================================================================

   ADDING PHOTOS
   1. Put your full-size photos in the matching folder, e.g. photos/travel/
   2. Run:  python update_photos.py
      It makes fast web-sized copies and records each photo's shape.
   3. Point the gallery at that folder with  folder: "travel"
   Photos show in file-name order and keep their original ratio.
   Optional captions:  captions: { "DSC09340": "Class of 2026" }

   ADDING A NEW PAGE
   Copy one of the blocks in "pages" and change the id / title.
   type: "gallery" -> photo grid
   type: "videos"  -> YouTube embeds
   type: "about"   -> text + portrait + contact links
   ========================================================================== */

// Temporary placeholder images so you can see the layout. Delete this helper
// (and the demo(...) calls below) once you add your own photos.
function demo(seed, count) {
  const sizes = [[1200, 1500], [1200, 1500], [1500, 1000], [1200, 1500]];
  return Array.from({ length: count }, (_, i) => {
    const [w, h] = sizes[i % sizes.length];
    return { src: `https://picsum.photos/seed/${seed}${i}/${w}/${h}`, w, h };
  });
}

const SITE = {
  name: "APOISHH",
  tagline: "Photography", // small line under your name
  instagram: "https://instagram.com/apoishh",
  youtubeChannel: "https://www.youtube.com/@apoishhh",
  github: "https://github.com/apoishh",
  email: "redrazzor728@gmail.com",

  // Message form on the About page. Get a free key at https://web3forms.com
  // (enter your email, the key arrives in your inbox) and paste it here.
  // Until then, "Send" opens the visitor's email app instead.
  web3formsKey: "",

  // The first page is the home page.
  pages: [
    {
      id: "preconvo",
      title: "Pre-Convo",
      type: "gallery",
      folder: "preconvo",
    },
    {
      id: "travel",
      title: "Travel",
      type: "gallery",
      folder: "travel",
      photos: demo("travel", 12), // shown until photos/travel has photos
    },
    {
      id: "projects",
      title: "Projects",
      type: "github",
      // Loaded live from GitHub: newest-updated project first.
      // Tip: add a description (and a website link) to a repo on GitHub
      // and it shows up here automatically.
      user: "apoishh",
      hide: ["apoishh.github.io"], // repos to leave out (this website itself)
      showForks: false,
      // Where "Open live" goes (and what the preview screenshot shows) when it
      // isn't the repo's normal GitHub Pages address or website link.
      live: {
        "monkey-money": "https://apoishh.github.io/monkey-money/docs/",
      },
      // Short descriptions shown on the cards (by repo name). Repos not listed
      // here use the description from GitHub (repo page -> About -> gear icon).
      descriptions: {
        "monkey-money": "A personal-finance kit for Malaysia built on Excel and Python. Drop in Maybank / CIMB statement PDFs to import spending automatically, check the tracker against real bank balances, and explore spending, investments and future plans in a local dashboard. Everything runs on your own PC.",
        "snake-rush": "An arcade take on classic Snake: eat, grow and don't crash. Grab power-ups like 2× points, slow-mo, ghost mode and a food magnet, then chase a spot on the online leaderboard.",
        "Apoishh-Portfolio": "My first portfolio website, built from scratch to show my skills, projects and experience as a developer.",
        "The-Simon-Game": "A web version of the classic Simon memory game. Watch the colour sequence, repeat it, and see how long you can keep up as it grows.",
        "learning-html-resume": "A resume page built with plain HTML while learning the basics of page structure.",
        "Learning-understanding-github-experimental": "A sandbox repo for learning how Git and GitHub work: commits, branches and history.",
      },
    },
    {
      id: "youtube",
      title: "YouTube",
      type: "videos",
      // Filled in automatically from youtubeChannel (latest + 4 most viewed)
      // by update_videos.py, which serve.py runs for you.
    },
    {
      id: "about",
      title: "About / Contact",
      type: "about",
      folder: "about", // uses the newest photo in photos/about
      text: [
        "Hi, I'm Apoishh — a beginner, part-time photographer who loves taking travel photos.",
        "I'm always open to trying new stuff and saying yes to the next adventure. Along the way I also shoot pre-convo sessions for graduates.",
        "Got a trip, a shoot or an idea in mind? Get in touch below.",
      ],
    },
  ],
};
