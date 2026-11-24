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
  tagline: "Portfolio",
  subtitle: "Pre-Convo & Travel",
  instagram: "https://instagram.com/apoishh",
  youtubeChannel: "https://www.youtube.com/@apoishhh",
  email: "redrazzor728@gmail.com",

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
