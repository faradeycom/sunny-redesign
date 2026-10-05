(function () {
  // мобільне меню
  document.querySelectorAll('[data-burger]').forEach(function (b) {
    b.addEventListener('click', function () { document.body.classList.toggle('nav-open'); });
  });

  // слайдер на головній (дизайн А)
  var slides = document.querySelectorAll('.hslides .slide'), dots = document.querySelectorAll('.hslides .dots button'), cur = 0, timer;
  function show(k) {
    cur = (k + slides.length) % slides.length;
    slides.forEach(function (s, i) { s.classList.toggle('on', i === cur); });
    dots.forEach(function (d, i) { d.classList.toggle('on', i === cur); });
  }
  if (slides.length > 1) {
    dots.forEach(function (d, i) { d.addEventListener('click', function () { show(i); clearInterval(timer); }); });
    if (!matchMedia('(prefers-reduced-motion: reduce)').matches) timer = setInterval(function () { show(cur + 1); }, 6000);
  }

  // демо-форми
  document.querySelectorAll('form[data-demo]').forEach(function (f) {
    f.addEventListener('submit', function (ev) { ev.preventDefault(); var ok = f.querySelector('.ok'); if (ok) ok.hidden = false; f.reset(); });
  });

  // калькулятор: цін на сайті немає, тому показуємо площу і передаємо менеджеру
  document.querySelectorAll('form[data-calc]').forEach(function (f) {
    f.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var v = f.querySelectorAll('input'), w = +v[0].value, h = +v[1].value, out = f.querySelector('.out');
      var area = (w * h / 10000).toFixed(2);
      out.hidden = false;
      out.innerHTML = '<b>' + f.querySelector('select').value + '</b>, ' + w + ' × ' + h + ' см — площа ' + area + ' м². Точну вартість підготує менеджер: <a href="tel:+380663948374">+38 066-394-83-74</a>.';
    });
  });

  // модальне вікно сервісів
  var modal = document.getElementById('svc');
  document.querySelectorAll('[data-open]').forEach(function (a) {
    a.addEventListener('click', function (ev) {
      if (!modal || !modal.showModal) return;
      ev.preventDefault();
      modal.querySelectorAll('.mpanel').forEach(function (p) { p.hidden = p.dataset.panel !== a.dataset.open; });
      modal.querySelectorAll('.ok,.out').forEach(function (o) { o.hidden = true; });
      modal.showModal();
    });
  });
  if (modal) {
    modal.addEventListener('click', function (ev) { if (ev.target === modal || ev.target.hasAttribute('data-close')) modal.close(); });
  }

  // пошук салонів
  var finder = document.querySelector('[data-finder]');
  if (finder && window.SHOPS) {
    var PAUSE = /\(?\s*ТИМЧАСОВО НЕ ПРАЦЮЄМО\s*\)?/i;
    var OFFICIAL = /шоу-?рум|оф(\.|іційн\S*)\s*(дилер|представ)|офіційне представництво|Офіс ТМ Sunny|Sunny ?Store/i;
    var esc = function (s) { return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
    var norm = function (s) { return s.toLowerCase().replace(/[ʼ'’]/g, "'"); };
    var linkify = function (t) {
      var h = esc(t);
      h = h.replace(/[\w.+-]+@[\w-]+\.[\w.]+/g, function (m) { return '<a href="mailto:' + m + '">' + m + '</a>'; });
      return h.replace(/(\+?38\s?)?\(?0\d{2,4}\)?[\s-]?\d[\d\s-]{4,12}\d/g, function (m) {
        var d = m.replace(/\D/g, ''), n = d.length === 10 ? '38' + d : d;
        return n.length === 12 ? '<a class="tel" href="tel:+' + n + '">' + m.trim() + '</a>' : m;
      });
    };
    var shops = [];
    SHOPS.forEach(function (R) {
      R.p.forEach(function (P) {
        var paused = PAUSE.test(P.c), city = P.c.replace(PAUSE, '').trim();
        P.s.forEach(function (t) { shops.push({ r: R.r, c: city, paused: paused, t: t, off: OFFICIAL.test(t) }); });
      });
    });
    var q = finder.querySelector('input'), sel = finder.querySelector('select'), list = finder.querySelector('.flist');
    var draw = function () {
      var t = norm(q.value), r = sel.value;
      var res = shops.filter(function (s) { return (!r || s.r === r) && (!t || norm(s.r + ' ' + s.c + ' ' + s.t).indexOf(t) > -1); });
      res.sort(function (a, b) { return (b.off - a.off) || (a.paused - b.paused); });
      list.innerHTML = res.length ? res.map(function (s) {
        return '<div class="shop' + (s.off ? ' official' : '') + (s.paused ? ' paused' : '') + '"><div class="sc">' + esc(s.c) + ' <small>' + esc(s.r) + '</small>' +
          (s.off ? '<span class="badge">Офіційний</span>' : '') + (s.paused ? '<span class="badge grey">Тимчасово не працює</span>' : '') +
          '</div><p>' + linkify(s.t) + '</p></div>';
      }).join('') : '<p class="empty">Нічого не знайдено. Зателефонуйте в оптовий відділ — підкажемо найближчий салон.</p>';
    };
    q.addEventListener('input', draw); sel.addEventListener('change', draw); draw();
  }
})();
