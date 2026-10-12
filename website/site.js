/* GLOSSKN — shared site script: catalogue, header/footer, cart, product pages, 3D tilt. */
(() => {
const A = "assets/";
const CATALOG = {
  cleanse: {
    name: "Power Cleanse - Make-up Removing Face Wash", short: "Power Cleanse", page: "power-cleanse.html", price: 1299,
    sub: "Make-up removing face wash · 100 ml", gallery: [1, 2, 3, 4, 5, 6].map(i => `${A}cleanse-${i}.webp`), threeD: true,
    chips: ["Gentle on eyes", "Eyelash friendly", "pH balanced", "Made in India"],
    desc: ["An all-in-one makeup-removing face wash for women who want effective cleansing without a complicated routine. Removes makeup, sunscreen, dirt and daily buildup in one wash. No separate ritual. No cotton pads. No unnecessary rubbing.", "Massage. Rinse. Done."],
    love: ["Removes makeup + cleanses, one easy wash", "Designed for comfortable cleansing around the eyes", "Helps minimise unnecessary rubbing", "Gentle, non-stripping, soft & fresh finish", "Ideal for busy routines and travel"],
    powered: "Squalane · Moringa · Rice Extract · Gentle Cleansing System",
    how: ["Massage: take a few pumps and massage gently over a damp face.", "Rinse: rinse thoroughly."],
  },
  melt: {
    name: "Power Melt - Face Cleansing Balm", short: "Power Melt", page: "power-melt.html", price: 1099,
    sub: "Cleansing balm · 60 g", gallery: [1, 2, 3, 4, 5, 6].map(i => `${A}melt-${i}.webp`),
    chips: ["Non-comedogenic", "Eyelash conditioning", "No greasy residue", "Made in India"],
    desc: ["A silky cleansing balm designed to melt away makeup, sunscreen and daily buildup effortlessly.", "Massage. Melt. Wipe.", "As you massage, the balm transforms into a silky oil that helps lift stubborn makeup while reducing the need for excessive rubbing. Wipe away to reveal skin that feels clean, soft and nourished — without a heavy greasy residue."],
    love: ["Melts long-wear and stubborn makeup, helps reduce rubbing", "Wipe-off convenience, no heavy greasy after-feel", "Nourishing oil blend", "Hygienic tube packaging, easy to carry and travel with", "Perfect for tired nights and on-the-go cleansing"],
    powered: "Plum Kernel Oil · Jojoba Oil · Squalane",
    how: ["Massage: take a small amount and massage gently over dry skin.", "Wipe: wipe away with a soft tissue or damp cloth."],
  },
  duo: {
    name: "Power Series Combo - Double Cleansing Duo (Melt + Cleanse)", short: "Power Series Combo", page: "power-series-combo.html", price: 1820, was: 2032, badges: ["Best Seller", "-10%"],
    sub: "Power Melt + Power Cleanse", gallery: [`${A}duo-1.webp`, `${A}duo-2.webp`, `${A}cleanse-2.webp`, `${A}melt-2.webp`, `${A}cleanse-3.webp`, `${A}melt-3.webp`],
    chips: ["Two formats", "One philosophy", "Made in India"],
    desc: ["One routine does not fit every day. Sometimes you want to wash and go. Sometimes you want to melt, wipe and unwind. That is why the Power Cleansing Duo gives you two different ways to reset your skin."],
    blocks: [["Power Cleanse", "For when you want: Makeup removal + cleansing in one wash.", "Massage. Rinse. Done."], ["Power Melt", "For when you want: A silky, wipe-off makeup removal experience.", "Massage. Melt. Wipe."]],
    outro: ["Use them according to your lifestyle — not because beauty needs more steps.", "Two formats. One philosophy.", "Make cleansing easier."],
  },
  gift: {
    name: "Power Reset Gifting Edition", short: "Power Reset Gift Box", page: "power-reset-gift-box.html", price: 2086, was: 2455, badges: ["-15%"],
    sub: "Power Cleanse + Power Melt + Power Bands", gallery: [1, 2, 3].map(i => `${A}gift-${i}.webp`), engraving: true,
    chips: ["Ready to gift", "Custom engraving available"],
    desc: ["Give her something she will actually use - easier self-care. The Power Reset Gift Box brings together two of GLOSSKN's signature cleansing experiences in a beautifully curated gift."],
    inside: ["Power Cleanse: the face wash that removes makeup too.", "Power Melt: the cleansing balm that melts away makeup effortlessly.", "Power Bands: designed to keep hair back and water off the wrists for a cleaner, more comfortable cleansing ritual."],
    outro: ["Why It Makes The Perfect Gift: because the best gifts do more than look beautiful. They make everyday life a little better.", "Perfect for: Birthdays · Bridesmaids · Weddings · Festive Gifting · Thank You Gifts · Travel · Corporate Gifting · Self-care · Just Because", "Thoughtful gifting, made effortless."],
  },
  bands: {
    name: "Power Bands: Wrist and Head Bands for Skin Care", short: "Power Bands", page: "power-bands.html", price: 380, was: 423, badges: ["-10%"],
    sub: "1 headband + 2 wrist bands", gallery: [`${A}bands-1.webp`, `${A}bands-2.webp`],
    chips: ["Reusable", "Washable", "Stretch-fit"],
    desc: ["Say goodbye to wet sleeves and messy hair. The GLOSSKN Power Bands set includes a plush skincare headband and absorbent wrist wash bands designed to keep you dry while you cleanse. Made from ultra-soft, stretch-fit fabric, these bands catch water drips before they run down your arms, making your face washing routine mess-free and effortless. Reusable and washable, they are the essential accessory for cleansing, applying face masks, or doing your makeup."],
    love: ["Designed to keep hair and sleeves dry during your skincare ritual.", "Made from soft, absorbent fabric that gently catches drips and splashes.", "Comfortable, stretch-fit for all face shapes and wrists.", "Reusable, washable, and kind to even the most sensitive skin.", "Perfect for cleansing, masking, or makeup days.", "A small touch of calm to elevate your everyday care."],
  },
};
CATALOG.cleanse.alt = CATALOG.cleanse.gallery[1]; CATALOG.melt.alt = CATALOG.melt.gallery[1]; CATALOG.duo.alt = CATALOG.duo.gallery[1];
CATALOG.gift.alt = CATALOG.gift.gallery[1]; CATALOG.bands.alt = CATALOG.bands.gallery[1];
const FREE_SHIP = 250;
window.GLOSSKN = { CATALOG };

const $ = (s, r = document) => r.querySelector(s);
const rs = n => "Rs. " + n.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const priceHTML = p => `${rs(p.price)}${p.was ? `<s>${rs(p.was)}</s>` : ""}`;
const keep = { get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch { return d; } }, set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} } };
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
const fine = matchMedia("(pointer: fine)").matches && !reduce;
const plus = `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M8 3v10M3 8h10"/></svg>`;
const here = (location.pathname.split("/").pop() || "index.html");

/* ---------- header + footer + drawer ---------- */
const hdr = $("#site-header");
if (hdr) hdr.outerHTML = `
<div class="announce">Clean Beauty · Cruelty-Free · Made in India</div>
<header class="header" id="header">
  <div class="wrap header-in">
    <nav class="nav" aria-label="Main">
      <div class="dd"><button type="button" aria-haspopup="true">Cleansers</button>
        <div class="dd-menu"><a href="power-cleanse.html">Power Cleanse</a><a href="power-melt.html">Power Melt</a><a href="power-series-combo.html">Power Series Combo</a><a href="power-bands.html">Power Bands</a></div></div>
      <a href="power-reset-gift-box.html" ${here === "power-reset-gift-box.html" ? 'aria-current="page"' : ""}>Gift Sets</a>
      <a href="index.html#featured">Shop All</a>
      <a href="our-story.html" ${here === "our-story.html" ? 'aria-current="page"' : ""}>Our Story</a>
    </nav>
    <button class="ibtn menu-btn" id="menuBtn" aria-label="Open menu" aria-expanded="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><path d="M3 7h18M3 12h18M3 17h18"/></svg></button>
    <a class="brand" href="index.html" aria-label="GLOSSKN home"><img src="${A}logo.png" alt="GLOSSKN"></a>
    <div class="icons">
      <a class="ibtn hide-sm" href="https://glosskn.com/search" target="_blank" rel="noopener" aria-label="Search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></svg></a>
      <a class="ibtn hide-sm" href="https://glosskn.com/account" target="_blank" rel="noopener" aria-label="Account"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4"><circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/></svg></a>
      <button class="ibtn" id="cartBtn" aria-label="Open cart"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"><path d="M4 7h16l-1.4 12.2a2 2 0 0 1-2 1.8H7.4a2 2 0 0 1-2-1.8Z"/><path d="M9 10V6a3 3 0 0 1 6 0v4"/></svg><span class="count" id="count">0</span></button>
    </div>
  </div>
  <nav class="mnav" id="mnav" aria-label="Mobile" hidden>
    <a href="power-cleanse.html" class="sub">Power Cleanse</a><a href="power-melt.html" class="sub">Power Melt</a><a href="power-series-combo.html" class="sub">Power Series Combo</a><a href="power-bands.html" class="sub">Power Bands</a>
    <a href="power-reset-gift-box.html">Gift Sets</a><a href="index.html#featured">Shop All</a><a href="our-story.html">Our Story</a>
  </nav>
</header>`;
const ftr = $("#site-footer");
if (ftr) ftr.outerHTML = `
<section class="faq" id="faq">
  <div class="wrap faq-grid">
    <h2 class="h3 reveal">Discover more in our <span class="it">FAQs</span></h2>
    <div>
      <details><summary>Is Power Cleanse safe to use around the eyes?</summary><p>Yes. Power Cleanse is designed for comfortable cleansing around the eyes and is eyelash friendly. Massage gently over a damp face, including the eye area, and rinse thoroughly.</p></details>
      <details><summary>What is the difference between Power Cleanse and Power Melt?</summary><p>Power Cleanse removes makeup and cleanses in one wash: massage, rinse, done. Power Melt is a silky balm that turns into oil to lift long-wear and waterproof makeup: massage, melt, wipe. Use them according to your lifestyle, or together as the Power Series Combo.</p></details>
      <details><summary>What is the skin barrier?</summary><p>Think of your skin barrier as your skin’s personal bodyguard. It is the outermost layer of your skin, made up of skin cells (like bricks) and lipids (like mortar). It locks in moisture, protects against pollution, bacteria and UV rays, and keeps skin balanced.</p></details>
      <details><summary>What are the signs of a damaged skin barrier?</summary><p>Redness or inflammation, dry or flaky skin, itching or burning, breakouts or increased sensitivity, and skin that feels tight even after moisturising.</p></details>
      <details><summary>How do I repair and protect it?</summary><p>Switch to gentle, hydrating cleansers, use a moisturiser rich in ceramides and fatty acids, avoid over-exfoliating, and always wear sunscreen during the day.</p></details>
    </div>
  </div>
</section>
<section class="club">
  <div class="wrap">
    <h2 class="h3">Join the GLOSSKN <span class="it">Club</span></h2>
    <p>Subscribe for store updates and discounts.</p>
    <form id="club" novalidate><label for="clubEmail" style="position:absolute;left:-9999px">Email</label><input id="clubEmail" type="email" placeholder="Enter your email" autocomplete="email"><button class="btn" type="submit">Join</button></form>
    <p class="msg" id="clubMsg" role="status"></p>
    <small>By subscribing you agree to the Terms of Use &amp; Privacy Policy.</small>
  </div>
</section>
<footer class="footer">
  <div class="wrap">
    <div class="ft">
      <div><p class="lead">Glosskn is more than mere beauty care, it’s a way to Own your Radiance. Powered by trust, empathy and innovation, we create one-stop routines with no-compromise ingredients, making beauty truly uncomplicated.</p></div>
      <div><h4>Shop</h4><ul><li><a href="power-cleanse.html">Power Cleanse</a></li><li><a href="power-melt.html">Power Melt</a></li><li><a href="power-series-combo.html">Power Series Combo</a></li><li><a href="power-bands.html">Accessories</a></li></ul></div>
      <div><h4>Gifting</h4><ul><li><a href="power-reset-gift-box.html">Power Reset Gift Box</a></li><li><a href="power-reset-gift-box.html">Custom engraving</a></li><li><a href="our-story.html">Our Story</a></li></ul></div>
      <div><h4>Help</h4><ul><li><a href="https://glosskn.com/policies/shipping-policy" target="_blank" rel="noopener">Shipping Policy</a></li><li><a href="https://glosskn.com/policies/refund-policy" target="_blank" rel="noopener">Returns &amp; Refunds</a></li><li><a href="https://glosskn.com/policies/privacy-policy" target="_blank" rel="noopener">Privacy Policy</a></li><li><a href="https://glosskn.com/pages/contact" target="_blank" rel="noopener">Contact us</a></li></ul></div>
    </div>
    <p style="margin-top:30px;font-size:var(--t-sm)">For gifting enquiries write to us at <b style="font-weight:500;user-select:all">hello@glosskn.com</b></p>
    <div class="ft-base">
      <div class="social"><a href="https://www.instagram.com/glosskndaily/" target="_blank" rel="noopener" aria-label="Instagram"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".8" fill="currentColor"/></svg></a></div>
      <span>© 2026, GLOSSKN. All Rights Reserved.</span>
    </div>
  </div>
</footer>
<div class="scrim" id="scrim"></div>
<aside class="drawer" id="drawer" aria-label="Your cart" aria-hidden="true">
  <div class="dh"><h2 id="cartTitle">Your Cart (0)</h2><button class="ibtn" id="closeCart" aria-label="Close cart"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="m6 6 12 12M18 6 6 18"/></svg></button></div>
  <div class="ship"><span id="shipMsg"></span><div class="bar"><i id="shipBar"></i></div></div>
  <div class="db" id="cartBody"></div>
  <div class="df"><div class="tot"><span>Subtotal</span><span id="subtotal">Rs. 0.00</span></div><small>Taxes and shipping calculated at checkout.</small>
    <div class="two"><a class="btn btn-line" href="https://glosskn.com/cart" target="_blank" rel="noopener">View cart</a><button class="btn btn-dark" type="button" id="checkout">Check out</button></div></div>
</aside>
<div class="toast" id="toast" role="status"></div>`;

/* header behaviour */
const mnav = $("#mnav"), menuBtn = $("#menuBtn");
menuBtn?.addEventListener("click", () => { mnav.hidden = !mnav.hidden; menuBtn.setAttribute("aria-expanded", String(!mnav.hidden)); });
mnav?.addEventListener("click", e => { if (e.target.closest("a")) { mnav.hidden = true; menuBtn.setAttribute("aria-expanded", "false"); } });

/* toast */
let tt; function toast(msg) { const t = $("#toast"); t.textContent = msg; t.classList.add("show"); clearTimeout(tt); tt = setTimeout(() => t.classList.remove("show"), 2600); }

/* ---------- cart ---------- */
let cart = keep.get("glosskn-cart-v3", { lines: [], wrap: false, note: "" });
const drawer = $("#drawer"), scrim = $("#scrim");
const openCart = () => { drawer.classList.add("open"); scrim.classList.add("open"); drawer.setAttribute("aria-hidden", "false"); $("#closeCart").focus(); };
const closeCart = () => { drawer.classList.remove("open"); scrim.classList.remove("open"); drawer.setAttribute("aria-hidden", "true"); };
$("#cartBtn")?.addEventListener("click", openCart); $("#closeCart")?.addEventListener("click", closeCart); scrim?.addEventListener("click", closeCart);
addEventListener("keydown", e => { if (e.key === "Escape") { closeCart(); const z = $(".zoom"); if (z) z.remove(); } });
function renderCart() {
  if (!drawer) return;
  const lines = cart.lines.filter(l => CATALOG[l.id] && l.q > 0);
  const n = lines.reduce((a, l) => a + l.q, 0), sub = lines.reduce((a, l) => a + CATALOG[l.id].price * l.q, 0);
  $("#count").textContent = n; $("#cartTitle").textContent = `Your Cart (${n})`; $("#subtotal").textContent = rs(sub);
  const left = Math.max(0, FREE_SHIP - sub);
  $("#shipMsg").innerHTML = left > 0 ? `Spend <b style="font-weight:500">${rs(left)}</b> more for free shipping` : "Congratulations! Your order qualifies for free shipping";
  $("#shipBar").style.width = Math.min(100, sub / FREE_SHIP * 100) + "%";
  const body = $("#cartBody");
  if (!lines.length) { body.innerHTML = `<div class="empty"><p>Your cart is empty</p><a class="btn" href="index.html#featured">Continue shopping</a></div>`; return; }
  const up = ["bands", "melt", "cleanse"].find(id => !lines.some(l => l.id === id));
  body.innerHTML = lines.map((l, i) => { const p = CATALOG[l.id]; return `<div class="ln"><img src="${p.gallery[0]}" alt=""><div><h3>${p.name}</h3>${l.engrave ? `<small>Engraving: “${l.engrave.replace(/</g, "&lt;")}”</small>` : ""}
    <div class="qty"><button type="button" data-q="${i}" data-d="-1" aria-label="Decrease">−</button><span>${l.q}</span><button type="button" data-q="${i}" data-d="1" aria-label="Increase">+</button></div></div>
    <div style="text-align:right"><span class="price" style="font-size:var(--t-sm)">${rs(p.price * l.q)}</span><br><button class="rm" type="button" data-rm="${i}">Remove</button></div></div>`; }).join("") +
    (up ? `<div style="display:grid;gap:10px"><span class="eyebrow">Buy it with</span><div class="up"><img src="${CATALOG[up].gallery[0]}" alt=""><div><h4>${CATALOG[up].short}</h4><span class="price" style="font-size:var(--t-sm)">${rs(CATALOG[up].price)}</span></div><button type="button" data-add="${up}" aria-label="Add ${CATALOG[up].short}">${plus}</button></div></div>` : "") +
    `<label class="opt"><input type="checkbox" id="wrapOpt" ${cart.wrap ? "checked" : ""}> Gift wrap this order</label>
     <label for="noteBox" style="font-size:var(--t-sm)">Add order note</label><textarea class="note-box" id="noteBox" placeholder="How can we help you?"></textarea>`;
  $("#noteBox").value = cart.note;
  $("#wrapOpt").onchange = e => { cart.wrap = e.target.checked; keep.set("glosskn-cart-v3", cart); };
  $("#noteBox").oninput = e => { cart.note = e.target.value; keep.set("glosskn-cart-v3", cart); };
}
$("#cartBody")?.addEventListener("click", e => {
  const b = e.target.closest("button"); if (!b || b.dataset.add) return;
  if (b.dataset.q) cart.lines[+b.dataset.q].q = Math.max(0, cart.lines[+b.dataset.q].q + +b.dataset.d);
  else if (b.dataset.rm) cart.lines.splice(+b.dataset.rm, 1);
  cart.lines = cart.lines.filter(l => l.q > 0); keep.set("glosskn-cart-v3", cart); renderCart();
});
function addToCart(id, q = 1, engrave = "") {
  const ex = cart.lines.find(l => l.id === id && (l.engrave || "") === engrave);
  if (ex) ex.q += q; else cart.lines.push({ id, q, engrave });
  keep.set("glosskn-cart-v3", cart); renderCart();
  const c = $("#count"); c.classList.add("pop"); setTimeout(() => c.classList.remove("pop"), 350);
  dispatchEvent(new CustomEvent("glosskn:add", { detail: id })); openCart();
}
window.GLOSSKN.addToCart = addToCart;
document.addEventListener("click", e => { const b = e.target.closest("[data-add]"); if (b) { e.preventDefault(); addToCart(b.dataset.add); } });
$("#checkout")?.addEventListener("click", () => toast("Design prototype: checkout runs on your Shopify store."));
renderCart();

/* club */
$("#club")?.addEventListener("submit", e => { e.preventDefault(); const v = $("#clubEmail").value.trim();
  $("#clubMsg").textContent = /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v) ? "Welcome to the GLOSSKN Club." : "Enter a valid email, like name@example.com."; });

/* ---------- product cards + 3D tilt ---------- */
function cardHTML(id) {
  const p = CATALOG[id];
  return `<article class="card">
    <div class="tile" data-tilt>
      <a class="cover" href="${p.page}" aria-label="${p.short}"></a>
      ${p.badges ? `<span class="badges">${p.badges.map((b, i) => `<span class="badge ${p.badges.length > 1 && !i ? "" : "l"}">${b}</span>`).join("")}</span>` : ""}
      <img src="${p.gallery[0]}" alt="${p.short}"><img class="alt" src="${p.alt}" alt="" loading="lazy"><span class="glare"></span>
      <button class="quick" type="button" data-add="${id}">Add to cart</button>
    </div>
    <a href="${p.page}" style="text-decoration:none"><h3>${p.name}</h3></a><p class="price">${priceHTML(p)}</p>
  </article>`;
}
window.GLOSSKN.cardHTML = cardHTML;
function bindTilt(root = document) {
  if (!fine) return;
  root.querySelectorAll("[data-tilt]").forEach(el => {
    if (el.dataset.bound) return; el.dataset.bound = 1;
    const g = el.querySelector(".glare"), k = +(el.dataset.tilt || 10);
    el.addEventListener("pointermove", e => {
      const r = el.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
      el.style.transform = `perspective(900px) rotateY(${(x - .5) * k}deg) rotateX(${(.5 - y) * k}deg) translateZ(12px)`;
      if (g) { g.style.setProperty("--gx", x * 100 + "%"); g.style.setProperty("--gy", y * 100 + "%"); }
    });
    el.addEventListener("pointerleave", () => { el.style.transform = ""; });
  });
}
window.GLOSSKN.bindTilt = bindTilt;

/* ---------- product page ---------- */
const PID = document.body.dataset.product;
if (PID && CATALOG[PID]) {
  const p = CATALOG[PID], root = $("#product");
  const slides = p.gallery.map((src, i) => `<div><img src="${src}" alt="${p.short} image ${i + 1}" ${i ? 'loading="lazy"' : ""}></div>`);
  const thumbs = p.gallery.map((src, i) => `<button type="button" data-i="${i}" aria-label="Show image ${i + 1}"><img src="${src}" alt="" loading="lazy"></button>`);
  if (p.threeD) {
    slides.splice(1, 0, `<div class="s3d" id="s3d"><span class="hint">Drag to rotate</span></div>`);
    thumbs.splice(1, 0, `<button type="button" data-i="1" class="t3d" aria-label="View in 3D"><span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><path d="M12 3 4 7.5v9L12 21l8-4.5v-9L12 3Z"/><path d="m4 7.5 8 4.5 8-4.5M12 12v9"/></svg><br>3D</span></button>`);
  }
  const N = slides.length;
  const list = arr => `<ul>${arr.map(x => `<li>${x}</li>`).join("")}</ul>`;
  const save = p.was ? Math.round((1 - p.price / p.was) * 100) : 0;
  root.innerHTML = `
    <nav class="crumbs wrap" aria-label="Breadcrumb"><a href="index.html">Home</a> / <a href="index.html#featured">Shop</a> / <span>${p.short}</span></nav>
    <div class="wrap pdp">
      <div>
        <div class="gallery">
          <div class="thumbs" role="tablist" aria-label="Product images">${thumbs.join("")}</div>
          <div class="stage" id="stage">
            <div class="slides" id="slides">${slides.join("")}</div>
            <button class="nav-arrow prev" type="button" id="gPrev" aria-label="Previous image"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M10 3 5 8l5 5"/></svg></button>
            <button class="nav-arrow next" type="button" id="gNext" aria-label="Next image"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6"><path d="m6 3 5 5-5 5"/></svg></button>
          </div>
        </div>
        <div class="dots" id="dots">${Array.from({ length: N }, (_, i) => `<i class="${i ? "" : "on"}"></i>`).join("")}</div>
      </div>
      <div class="info">
        <span class="eyebrow">GLOSSKN</span>
        <h1>${p.name}</h1>
        <p class="sub">${p.sub}</p>
        <div class="pricebig price">${rs(p.price)}${p.was ? `<s>${rs(p.was)}</s><span class="save">Save ${save}%</span>` : ""}</div>
        <p class="tax">Taxes included. Shipping calculated at checkout.</p>
        ${p.chips ? `<ul class="chips">${p.chips.map(c => `<li>${c}</li>`).join("")}</ul>` : ""}
        ${p.engraving ? `<div class="variant"><span class="eyebrow">Edition</span><div class="opts">
            <input type="radio" name="ed" id="edA" value="" checked><label class="o" for="edA">Classic</label>
            <input type="radio" name="ed" id="edB" value="eng"><label class="o" for="edB">With custom engraving</label></div>
            <div id="engWrap" hidden><label for="engText" class="eyebrow" style="display:block;margin:6px 0 8px">Name or message (up to 20 characters)</label><input class="engrave-in" id="engText" maxlength="20" placeholder="e.g. For Anaya"></div></div>` : ""}
        <div class="buy">
          <div class="qty" role="group" aria-label="Quantity"><button type="button" id="qMinus" aria-label="Decrease quantity">−</button><output id="qVal">1</output><button type="button" id="qPlus" aria-label="Increase quantity">+</button></div>
          <button class="btn" type="button" id="addMain">Add to cart</button>
        </div>
        <button class="btn btn-dark buy-now" type="button" id="buyNow">Buy it now</button>
        <div class="acc">
          <details open><summary>Description</summary><div class="body">${p.desc.map(x => `<p>${x}</p>`).join("")}
            ${p.blocks ? p.blocks.map(b => `<p><b style="font-weight:500;letter-spacing:.06em;text-transform:uppercase">${b[0]}</b><br>${b[1]}<br><span class="it">${b[2]}</span></p>`).join("") : ""}
            ${p.inside ? `<p><b style="font-weight:500">Inside:</b></p>${list(p.inside)}` : ""}
            ${p.outro ? p.outro.map(x => `<p>${x}</p>`).join("") : ""}</div></details>
          ${p.love ? `<details><summary>Why you'll love it</summary><div class="body">${list(p.love)}</div></details>` : ""}
          ${p.powered ? `<details><summary>Powered with</summary><div class="body"><p>${p.powered}</p></div></details>` : ""}
          ${p.how ? `<details><summary>How to use</summary><div class="body">${list(p.how)}</div></details>` : ""}
          <details><summary>Shipping &amp; returns</summary><div class="body"><p>Free shipping on orders over ${rs(FREE_SHIP)}. See our <a href="https://glosskn.com/policies/shipping-policy" target="_blank" rel="noopener">shipping</a> and <a href="https://glosskn.com/policies/refund-policy" target="_blank" rel="noopener">returns</a> policies.</p></div></details>
        </div>
      </div>
    </div>
    <section class="pair wrap"><h2 class="h3">Pairs well <span class="it">with</span></h2><div class="pair-grid" id="pairGrid"></div></section>
    <div class="sticky-buy" id="stickyBuy"><img src="${p.gallery[0]}" alt=""><div><b>${p.short}</b><span class="price">${rs(p.price)}</span></div><button class="btn" type="button" data-add="${PID}">Add to cart</button></div>`;
  document.title = `${p.short} | GLOSSKN`;
  // gallery
  const sl = $("#slides"), th = [...document.querySelectorAll(".thumbs button")], dots = [...document.querySelectorAll("#dots i")];
  let cur = 0;
  const go = i => { cur = (i + N) % N; sl.scrollTo({ left: sl.clientWidth * cur, behavior: reduce ? "auto" : "smooth" }); };
  const mark = () => { th.forEach((b, i) => b.setAttribute("aria-current", String(i === cur))); dots.forEach((d, i) => d.classList.toggle("on", i === cur)); if (p.threeD && cur === 1) dispatchEvent(new Event("glosskn:3d")); };
  sl.addEventListener("scroll", () => { const i = Math.round(sl.scrollLeft / sl.clientWidth); if (i !== cur) { cur = i; mark(); } }, { passive: true });
  th.forEach(b => b.addEventListener("click", () => { go(+b.dataset.i); cur = +b.dataset.i; mark(); }));
  $("#gPrev").onclick = () => { go(cur - 1); mark(); }; $("#gNext").onclick = () => { go(cur + 1); mark(); };
  mark();
  sl.addEventListener("click", e => { const im = e.target.closest("img"); if (!im) return;
    const z = document.createElement("div"); z.className = "zoom"; z.innerHTML = `<img src="${im.src}" alt="${im.alt}">`; z.onclick = () => z.remove(); document.body.appendChild(z); });
  // 3D tilt of the main stage
  if (fine) { const st = $("#stage"); st.addEventListener("pointermove", e => { if (e.target.closest(".s3d")) return; const r = st.getBoundingClientRect(); const im = st.querySelectorAll(".slides > div")[cur]?.querySelector("img"); if (!im) return;
    im.style.transform = `scale(1.04) rotateY(${((e.clientX - r.left) / r.width - .5) * 6}deg) rotateX(${(.5 - (e.clientY - r.top) / r.height) * 6}deg)`; });
    st.addEventListener("pointerleave", () => st.querySelectorAll(".slides img").forEach(i => i.style.transform = "")); }
  // buy
  let q = 1;
  $("#qMinus").onclick = () => { q = Math.max(1, q - 1); $("#qVal").textContent = q; };
  $("#qPlus").onclick = () => { q = Math.min(9, q + 1); $("#qVal").textContent = q; };
  const engr = () => { if (!p.engraving || !$("#edB").checked) return ""; return $("#engText").value.trim(); };
  if (p.engraving) document.querySelectorAll('input[name="ed"]').forEach(r => r.onchange = () => { $("#engWrap").hidden = !$("#edB").checked; if (!$("#engWrap").hidden) $("#engText").focus(); });
  const add = () => { if (p.engraving && $("#edB").checked && !engr()) { toast("Add the name or message to engrave."); $("#engText").focus(); return false; } addToCart(PID, q, engr()); return true; };
  $("#addMain").onclick = add;
  $("#buyNow").onclick = () => { if (add()) toast("Design prototype: checkout runs on your Shopify store."); };
  // pairs
  $("#pairGrid").innerHTML = Object.keys(CATALOG).filter(k => k !== PID).slice(0, 4).map(window.GLOSSKN.cardHTML).join("");
  bindTilt();
  // sticky mobile buy bar after the main buy button scrolls away
  const sb = $("#stickyBuy");
  new IntersectionObserver(([e]) => sb.classList.toggle("show", !e.isIntersecting && e.boundingClientRect.top < 0)).observe($("#addMain"));
}

bindTilt();
})();
