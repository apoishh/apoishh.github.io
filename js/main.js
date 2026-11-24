(function () {
  const $ = (id) => document.getElementById(id);
  const content = $("content");
  const sidebar = $("sidebar");
  const year = new Date().getFullYear();

  const ICONS = {
    instagram: '<svg viewBox="0 0 24 24"><path d="M12 2.2c3.2 0 3.6 0 4.8.1 3.3.1 4.8 1.7 4.9 4.9.1 1.3.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 3.2-1.7 4.8-4.9 4.9-1.3.1-1.6.1-4.8.1s-3.6 0-4.8-.1c-3.3-.1-4.8-1.7-4.9-4.9C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.8C2.4 3.9 3.9 2.4 7.2 2.3 8.4 2.2 8.8 2.2 12 2.2zM12 0C8.7 0 8.3 0 7.1.1 2.7.3.3 2.7.1 7.1 0 8.3 0 8.7 0 12s0 3.7.1 4.9c.2 4.4 2.6 6.8 7 7 1.2.1 1.6.1 4.9.1s3.7 0 4.9-.1c4.4-.2 6.8-2.6 7-7 .1-1.2.1-1.6.1-4.9s0-3.7-.1-4.9c-.2-4.4-2.6-6.8-7-7C15.7 0 15.3 0 12 0zm0 5.8a6.2 6.2 0 100 12.4 6.2 6.2 0 000-12.4zM12 16a4 4 0 110-8 4 4 0 010 8zm6.4-11.8a1.4 1.4 0 100 2.9 1.4 1.4 0 000-2.9z"/></svg>',
    youtube: '<svg viewBox="0 0 24 24"><path d="M23.5 6.2a3 3 0 00-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5A3 3 0 00.5 6.2 31 31 0 000 12a31 31 0 00.5 5.8 3 3 0 002.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 002.1-2.1A31 31 0 0024 12a31 31 0 00-.5-5.8zM9.6 15.6V8.4l6.2 3.6-6.2 3.6z"/></svg>',
  };

  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const norm = (p) => (typeof p === "string" ? { src: p, caption: "" } : p);

  /* ---------- Sidebar ---------- */
  $("brand").innerHTML = `<span>${esc(SITE.name)}</span><span>${esc(SITE.tagline)}</span>`;
  $("brand").href = "#/" + SITE.pages[0].id;
  $("subtitle").innerHTML = esc(SITE.subtitle);
  $("nav").innerHTML = SITE.pages
    .map((p) => `<a href="#/${esc(p.id)}" data-id="${esc(p.id)}">${esc(p.title)}</a>`)
    .join("");
  $("socials").innerHTML = [
    SITE.instagram && `<a href="${esc(SITE.instagram)}" target="_blank" rel="noopener" aria-label="Instagram">${ICONS.instagram}</a>`,
    SITE.youtubeChannel && `<a href="${esc(SITE.youtubeChannel)}" target="_blank" rel="noopener" aria-label="YouTube">${ICONS.youtube}</a>`,
  ].filter(Boolean).join("");
  $("copyright").innerHTML = `&copy; ${year} ${esc(SITE.name)}<br>All rights reserved`;

  $("menuToggle").addEventListener("click", () => {
    const open = sidebar.classList.toggle("open");
    $("menuToggle").setAttribute("aria-expanded", open);
    document.body.style.overflow = open ? "hidden" : "";
  });
  $("nav").addEventListener("click", () => {
    sidebar.classList.remove("open");
    document.body.style.overflow = "";
  });

  /* ---------- Lazy fade-in ---------- */
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      const img = e.target;
      img.src = img.dataset.src;
      io.unobserve(img);
    });
  }, { rootMargin: "400px 0px" });

  /* ---------- Masonry grid ---------- */
  // Each photo goes into whichever column is currently shortest, so every
  // photo keeps its own ratio and there are no gaps.
  function masonry(photos, altText) {
    const tiles = photos.map((p, i) => {
      const a = document.createElement("a");
      a.className = "tile";
      a.href = p.src;
      a.dataset.index = i;
      a.style.aspectRatio = p.w && p.h ? `${p.w} / ${p.h}` : "4 / 5";
      a.innerHTML = `<img data-src="${esc(p.src)}" alt="${esc(p.caption || altText)}">`;
      const img = a.firstChild;
      img.addEventListener("load", () => {
        if (!p.w) { p.w = img.naturalWidth; p.h = img.naturalHeight; a.style.aspectRatio = `${p.w} / ${p.h}`; }
        a.classList.add("loaded");
      });
      io.observe(img);
      return a;
    });

    const grid = document.createElement("div");
    grid.className = "grid";
    let cols = 0;
    const layout = () => {
      // 1 column on phones, 2 on laptops, 3 on wide monitors
      const w = window.innerWidth;
      const n = w <= 760 ? 1 : w < 1500 ? 2 : 3;
      if (n === cols) return;
      cols = n;
      const columns = Array.from({ length: n }, () => {
        const c = document.createElement("div");
        c.className = "col";
        return c;
      });
      const heights = new Array(n).fill(0);
      tiles.forEach((t, i) => {
        const k = heights.indexOf(Math.min(...heights));
        columns[k].appendChild(t);
        const p = photos[i];
        heights[k] += p.w && p.h ? p.h / p.w : 1.25;
      });
      grid.replaceChildren(...columns);
    };
    grid.addEventListener("click", (e) => {
      const tile = e.target.closest(".tile");
      if (!tile) return;
      e.preventDefault();
      openLightbox(photos, +tile.dataset.index);
    });
    return { grid, layout };
  }

  /* ---------- Renderers ---------- */
  const renderers = {
    gallery(page) {
      const all = typeof PHOTOS !== "undefined" ? PHOTOS : {};
      const prep = (list) => list.map((p) => {
        p = norm(p);
        const key = p.src.split("/").pop().replace(/\.[^.]+$/, "");
        return { ...p, caption: p.caption || (page.captions || {})[key] || "" };
      });
      // "bromo" -> "Bromo", "krabi-2025" -> "Krabi 2025"; "Cappadocia, Turkey" stays as is
      const prettify = (name) => {
        const s = name.replace(/[-_]+/g, " ").trim();
        return s === s.toLowerCase() ? s.replace(/\b\w/g, (c) => c.toUpperCase()) : s;
      };

      // Place sections come from subfolders, e.g. photos/travel/bromo
      const sections = Object.keys(all)
        .filter((k) => page.folder && k.startsWith(page.folder + "/"))
        .map((k) => ({ title: prettify(k.split("/").pop()), photos: prep(all[k]) }));
      const loose = prep((all[page.folder] || []).length ? all[page.folder] : sections.length ? [] : page.photos || []);
      if (loose.length) sections.push({ title: sections.length ? "Other" : "", photos: loose });

      const layouts = [];
      const frag = document.createDocumentFragment();
      if (sections.length > 1) {
        const nav = document.createElement("nav");
        nav.className = "place-nav";
        sections.forEach((s, i) => {
          const b = document.createElement("button");
          b.textContent = s.title;
          b.onclick = () => document.getElementById(`place-${i}`).scrollIntoView({ behavior: "smooth" });
          nav.appendChild(b);
        });
        frag.appendChild(nav);
      }
      sections.forEach((s, i) => {
        const sec = document.createElement("section");
        sec.className = "place";
        sec.id = `place-${i}`;
        if (s.title) {
          sec.innerHTML = `<h2 class="place-title">${esc(s.title)}<span>${s.photos.length}</span></h2>`;
        }
        const { grid, layout } = masonry(s.photos, page.title);
        sec.appendChild(grid);
        frag.appendChild(sec);
        layouts.push(layout);
      });
      content.replaceChildren(frag);
      layouts.forEach((f) => f());
      window.onresize = () => layouts.forEach((f) => f());
    },

    videos(page) {
      const data = typeof VIDEOS !== "undefined" ? VIDEOS : { latest: null, popular: page.videos || [] };
      const views = (n) => (n ? `${Number(n).toLocaleString()} view${n == 1 ? "" : "s"}` : "");
      const card = (v) => `
        <div class="video">
          <div class="video-frame">
            <iframe src="https://www.youtube-nocookie.com/embed/${esc(v.id)}" title="${esc(v.title)}" loading="lazy"
              allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
          </div>
          <h2>${esc(v.title)}</h2>
          <p class="video-meta">${views(v.views)}</p>
        </div>`;
      content.innerHTML = `
        <div class="video-layout">
          ${data.latest ? `<section class="video-latest">
            <p class="section-label">Latest upload</p>${card(data.latest)}
            ${SITE.youtubeChannel ? `<a class="channel-link" href="${esc(SITE.youtubeChannel)}" target="_blank" rel="noopener">See all videos on YouTube &rarr;</a>` : ""}
          </section>` : ""}
          ${data.popular.length ? `<section>
            <p class="section-label">Most watched</p>
            <div class="video-grid">${data.popular.map(card).join("")}</div>
          </section>` : ""}
        </div>`;
    },

    about(page) {
      const fromFolder = typeof PHOTOS !== "undefined" && PHOTOS[page.folder];
      const portrait = (fromFolder && fromFolder[0] && fromFolder[0].src) || page.portrait;
      content.innerHTML = `
        <div class="about">
          ${portrait ? `<img src="${esc(portrait)}" alt="${esc(SITE.name)}">` : "<div></div>"}
          <div class="about-text">
            ${page.text.map((t) => `<p>${esc(t)}</p>`).join("")}
            <div class="contact">
              ${SITE.email ? `<a href="mailto:${esc(SITE.email)}">${esc(SITE.email)}</a>` : ""}
              ${SITE.instagram ? `<a href="${esc(SITE.instagram)}" target="_blank" rel="noopener">Instagram</a>` : ""}
              ${SITE.youtubeChannel ? `<a href="${esc(SITE.youtubeChannel)}" target="_blank" rel="noopener">YouTube</a>` : ""}
            </div>
            ${SITE.email || SITE.web3formsKey ? `
            <form class="message-form" id="messageForm" novalidate>
              <p class="section-label">Send me a message</p>
              <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off">
              <label>Name<input name="name" required autocomplete="name"></label>
              <label>Email<input name="email" type="email" required autocomplete="email"></label>
              <label>Message<textarea name="message" rows="5" required></textarea></label>
              <button type="submit">Send</button>
              <p class="form-status" id="formStatus" role="status"></p>
            </form>` : ""}
          </div>
        </div>`;
      const form = $("messageForm");
      if (form) form.addEventListener("submit", sendMessage);
    },
  };

  /* ---------- Message form ---------- */
  async function sendMessage(e) {
    e.preventDefault();
    const form = e.target, status = $("formStatus"), button = form.querySelector("button");
    const data = Object.fromEntries(new FormData(form));
    if (data.botcheck) return; // spam bot filled the hidden box
    if (!data.name.trim() || !data.message.trim() || !form.email.checkValidity() || !data.email) {
      status.textContent = "Please fill in your name, a valid email and a message.";
      status.className = "form-status error";
      return;
    }

    // No form service set up yet: open the visitor's email app instead.
    if (!SITE.web3formsKey) {
      const subject = encodeURIComponent(`Message from ${data.name} via your portfolio`);
      const body = encodeURIComponent(`${data.message}\n\n${data.name}\n${data.email}`);
      location.href = `mailto:${SITE.email}?subject=${subject}&body=${body}`;
      return;
    }

    button.disabled = true;
    status.textContent = "Sending…";
    status.className = "form-status";
    try {
      const res = await fetch("https://api.web3forms.com/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({
          access_key: SITE.web3formsKey,
          subject: `New message from ${data.name} (portfolio)`,
          from_name: "Portfolio website",
          name: data.name,
          email: data.email,
          message: data.message,
        }),
      });
      const json = await res.json();
      if (!json.success) throw new Error(json.message);
      form.reset();
      status.textContent = "Thanks! Your message was sent. I'll get back to you soon.";
    } catch (err) {
      status.textContent = `Couldn't send right now. Please email me at ${SITE.email}.`;
      status.className = "form-status error";
    } finally {
      button.disabled = false;
    }
  }

  /* ---------- Router ---------- */
  function route() {
    const id = location.hash.replace(/^#\/?/, "");
    const page = SITE.pages.find((p) => p.id === id) || SITE.pages[0];
    document.title = `${page.title} — ${SITE.name}`;
    document.querySelectorAll(".nav a").forEach((a) =>
      a.classList.toggle("active", a.dataset.id === page.id));
    content.style.animation = "none";
    void content.offsetWidth;
    content.style.animation = "";
    window.onresize = null;
    (renderers[page.type] || renderers.gallery)(page);
    window.scrollTo(0, 0);
  }
  window.addEventListener("hashchange", route);
  route();

  /* ---------- Lightbox ---------- */
  const lb = $("lightbox"), lbImg = $("lbImg");
  let list = [], idx = 0;

  function show(i) {
    idx = (i + list.length) % list.length;
    lbImg.src = list[idx].src;
    lbImg.alt = list[idx].caption || "";
    $("lbCaption").textContent = list[idx].caption || "";
    $("lbCount").textContent = `${idx + 1} / ${list.length}`;
    [list[idx + 1], list[idx - 1]].forEach((p) => p && (new Image().src = p.src));
  }
  function openLightbox(photos, i) {
    list = photos;
    lb.hidden = false;
    document.body.style.overflow = "hidden";
    show(i);
  }
  function closeLightbox() {
    lb.hidden = true;
    document.body.style.overflow = "";
  }
  $("lbClose").onclick = closeLightbox;
  $("lbPrev").onclick = () => show(idx - 1);
  $("lbNext").onclick = () => show(idx + 1);
  lb.addEventListener("click", (e) => { if (e.target === lb) closeLightbox(); });
  document.addEventListener("keydown", (e) => {
    if (lb.hidden) return;
    if (e.key === "Escape") closeLightbox();
    if (e.key === "ArrowLeft") show(idx - 1);
    if (e.key === "ArrowRight") show(idx + 1);
  });
  let touchX = null;
  lb.addEventListener("touchstart", (e) => (touchX = e.touches[0].clientX), { passive: true });
  lb.addEventListener("touchend", (e) => {
    if (touchX === null) return;
    const dx = e.changedTouches[0].clientX - touchX;
    if (Math.abs(dx) > 50) show(idx + (dx < 0 ? 1 : -1));
    touchX = null;
  });
})();
