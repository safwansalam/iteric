/* IT Eric – subtle, professional GSAP animations
   Needs: gsap + ScrollTrigger (loaded in base.html). Safe if they fail to load. */
(function () {
  if (!window.gsap || !window.ScrollTrigger) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  gsap.registerPlugin(ScrollTrigger);
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var EASE = 'power3.out';
  /* explicit start/end values (fromTo) so CSS transitions on buttons/cards can't confuse GSAP */
  function rise(targets, y, vars) {
    vars = vars || {};
    vars.opacity = 1; vars.y = 0;
    if (!vars.ease) vars.ease = EASE;
    vars.clearProps = 'transform,opacity';
    return gsap.fromTo(targets, { opacity: 0, y: y }, vars);
  }

  /* ---------- thin scroll-progress bar at the very top ---------- */
  var bar = document.createElement('div');
  bar.style.cssText = 'position:fixed;top:0;left:0;height:3px;width:100%;z-index:2000;transform-origin:0 50%;' +
    'background:linear-gradient(90deg,#2457d6,#7c3aed,#e6007e);pointer-events:none';
  document.body.appendChild(bar);
  gsap.set(bar, { scaleX: 0 });
  gsap.to(bar, { scaleX: 1, ease: 'none',
    scrollTrigger: { trigger: document.documentElement, start: 'top top', end: 'bottom bottom', scrub: 0.3 } });

  /* ---------- HOME hero ---------- */
  var hero = $('.lp-hero');
  if (hero) {
    var h1 = $('h1', hero);
    if (h1) {                                   // headline: each line slides up from a mask
      var lines = h1.innerHTML.split(/<br\s*\/?>/i);
      h1.innerHTML = lines.map(function (l) {
        return '<span class="ln" style="display:block;overflow:hidden;padding-bottom:.1em;margin-bottom:-.1em">' +
               '<span class="in" style="display:block">' + l + '</span></span>';
      }).join('');
    }
    var tl = gsap.timeline({ defaults: { ease: EASE } });
    tl.fromTo('.lp-hero .in', { yPercent: 110 }, { yPercent: 0, duration: 1, stagger: 0.12, clearProps: 'transform' })
      .add(rise('.lp-hero .lead', 24, { duration: 0.8 }), '-=0.6')
      .add(rise('.lp-hero .lp-btn', 20, { duration: 0.7, stagger: 0.1 }), '-=0.55')
      .add(rise('.lp-hero .lp-checks > *', 14, { duration: 0.6, stagger: 0.08 }), '-=0.5')
      .fromTo('.lp-hero-art svg', { y: 50, opacity: 0, scale: 0.94 }, { y: 0, opacity: 1, scale: 1, duration: 1.2 }, 0.15)
      .fromTo('.lp-hero-art .lp-chip', { opacity: 0 }, { opacity: 1, duration: 0.8, stagger: 0.2, clearProps: 'opacity' }, '-=0.5');
    tl.eventCallback('onComplete', function () {   // gentle idle float of the monitor
      gsap.to('.lp-hero-art svg', { y: -8, duration: 3.2, ease: 'sine.inOut', yoyo: true, repeat: -1 });
    });
    gsap.to('.lp-skyline', { yPercent: 12, ease: 'none',
      scrollTrigger: { trigger: hero, start: 'top top', end: 'bottom top', scrub: true } });
  }

  /* ---------- inner-page title banners (Products, Brands, About) ---------- */
  var head = $('.page-head') || $('.ab-hero');
  if (head) {
    rise($$('h1, h2, p, .lp-eyebrow', head).slice(0, 5), 26, { duration: 0.9, stagger: 0.1, delay: 0.1 });
  }

  /* ---------- section headings ---------- */
  $$('.text-center.mb-5').forEach(function (box) {
    rise(box.children, 28, { duration: 0.8, stagger: 0.12,
      scrollTrigger: { trigger: box, start: 'top 85%', once: true } });
  });

  /* ---------- groups of cards: fade up in a gentle stagger ---------- */
  var groups = ['.lp-brand-row a', '.lp-cat', '.lp-product', '.lp-branch', '.lp-why', '.ab-stat', '.ab-svc',
                '.product-card', '.brand-tile', '.brand-chip', '.cat-pill'];
  groups.forEach(function (sel) {
    var els = $$(sel);
    if (!els.length) return;
    gsap.set(els, { opacity: 0, y: 34 });
    ScrollTrigger.batch(els, {
      start: 'top 92%', once: true,
      onEnter: function (batch) {
        gsap.to(batch, { opacity: 1, y: 0, duration: 0.7, ease: EASE, stagger: 0.07,
          clearProps: 'transform,opacity' });   // hand control back to CSS hover effects
      }
    });
  });

  /* ---------- count-up numbers ---------- */
  $$('.lp-stat .num, .ab-stat .n').forEach(function (el) {
    var m = el.textContent.trim().match(/^(\d+)(.*)$/);
    if (!m) return;
    var target = parseInt(m[1], 10), suffix = m[2], obj = { v: 0 };
    el.textContent = '0' + suffix;
    gsap.to(obj, { v: target, duration: 1.6, ease: 'power2.out',
      scrollTrigger: { trigger: el, start: 'top 90%', once: true },
      onUpdate: function () { el.textContent = Math.round(obj.v) + suffix; } });
  });

  /* ---------- call-to-action + contact blocks ---------- */
  ['.lp-cta', '.lp-contact', '.ab-close', '.ab-quote', '.ab-serve', '.ab-mv'].forEach(function (sel) {
    $$(sel).forEach(function (el) {
      rise(el, 40, { duration: 0.9, scrollTrigger: { trigger: el, start: 'top 88%', once: true } });
    });
  });

  window.addEventListener('load', function () { ScrollTrigger.refresh(); });
})();