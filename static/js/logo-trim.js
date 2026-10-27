/* IT Eric – crops the empty space around brand logos in the browser,
   so every logo fills its box and looks the same size (no need to edit the image files). */
(function () {
  var SEL = '.bs-item img, .lp-brand-row img, .ab-brand-tile img, .brand-tile img, .brand-chip img, .brand-logo img, ' +
            '.product-brand-logo, .lp-product .body img';

  function trim(img) {
    var src = img.currentSrc || img.src;
    if (!src || img.getAttribute('data-trimmed')) return;
    var im = new Image();
    im.crossOrigin = 'anonymous';
    im.onload = function () {
      try {
        var w = im.naturalWidth, h = im.naturalHeight;
        if (!w || !h) return;
        var s = Math.min(1, 800 / Math.max(w, h));
        var cw = Math.max(1, Math.round(w * s)), ch = Math.max(1, Math.round(h * s));
        var c = document.createElement('canvas'); c.width = cw; c.height = ch;
        var ctx = c.getContext('2d'); ctx.drawImage(im, 0, 0, cw, ch);
        var d = ctx.getImageData(0, 0, cw, ch).data;
        var x0 = cw, y0 = ch, x1 = -1, y1 = -1, x, y, i;
        for (y = 0; y < ch; y++) {
          for (x = 0; x < cw; x++) {
            i = (y * cw + x) * 4;
            if (d[i + 3] > 25 && (d[i] < 238 || d[i + 1] < 238 || d[i + 2] < 238)) {
              if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y;
            }
          }
        }
        if (x1 < 0) return;                       // blank image: leave it alone
        var pad = 2;
        x0 = Math.max(0, x0 - pad); y0 = Math.max(0, y0 - pad);
        x1 = Math.min(cw - 1, x1 + pad); y1 = Math.min(ch - 1, y1 + pad);
        var tw = x1 - x0 + 1, th = y1 - y0 + 1;
        if (tw >= cw - 2 && th >= ch - 2) { img.setAttribute('data-trimmed', '1'); return; }   // already tight
        var o = document.createElement('canvas'); o.width = tw; o.height = th;
        o.getContext('2d').drawImage(c, x0, y0, tw, th, 0, 0, tw, th);
        img.src = o.toDataURL('image/png');
        img.setAttribute('data-trimmed', '1');
      } catch (e) { /* cross-origin image: keep the original */ }
    };
    im.src = src;
  }

  function run() { Array.prototype.forEach.call(document.querySelectorAll(SEL), trim); }
  if (document.readyState === 'complete') run(); else window.addEventListener('load', run);
})();