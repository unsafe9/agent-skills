
  const body = document.body;
  const deck = document.getElementById('deck');
  const slides = [...deck.querySelectorAll('.slide')];
  const counter = document.getElementById('counter');
  const bar = document.getElementById('bar');
  const modeBtn = document.getElementById('modeBtn');
  let current = 0;

  const clamp = n => Math.max(0, Math.min(slides.length - 1, n));
  const isScroll = () => body.classList.contains('mode-scroll');

  function paint(){
    counter.textContent = `${current + 1} / ${slides.length}`;
    slides.forEach((s, i) => s.classList.toggle('active', i === current));
    document.querySelectorAll('.ov-item').forEach((el, i) => el.classList.toggle('cur', i === current));
    if (!isScroll()) bar.style.width = ((current + 1) / slides.length * 100) + '%';
  }

  function goto(n, push){
    current = clamp(n);
    if (isScroll()) slides[current].scrollIntoView({ behavior: push === false ? 'auto' : 'smooth', block: 'start' });
    paint();
    if (push !== false) history.replaceState(null, '', '#' + (current + 1));
  }
  const next = () => goto(current + 1);
  const prev = () => goto(current - 1);

  // scroll mode: derive current slide + progress from scroll position
  addEventListener('scroll', () => {
    if (!isScroll()) return;
    const mid = scrollY + innerHeight * 0.4;
    let idx = 0;
    slides.forEach((s, i) => { if (s.offsetTop <= mid) idx = i; });
    current = idx;
    const max = document.documentElement.scrollHeight - innerHeight;
    bar.style.width = (max > 0 ? scrollY / max * 100 : 0) + '%';
    counter.textContent = `${current + 1} / ${slides.length}`;
    document.querySelectorAll('.ov-item').forEach((el, i) => el.classList.toggle('cur', i === current));
  }, { passive: true });

  function setMode(mode){
    body.classList.toggle('mode-scroll', mode === 'scroll');
    body.classList.toggle('mode-slides', mode === 'slides');
    modeBtn.textContent = mode === 'scroll' ? '⇅ scroll' : '▭ slides';
    paint();
    goto(current, false);
  }
  const toggleMode = () => setMode(isScroll() ? 'slides' : 'scroll');

  let overview = false;
  function toggleOverview(force){
    overview = force === undefined ? !overview : force;
    body.classList.toggle('overview', overview);
  }
  const toggleNotes = () => body.classList.toggle('show-notes');

  addEventListener('keydown', e => {
    if (e.target.matches('input, textarea')) return;
    const k = e.key;
    if (['ArrowRight', 'PageDown', ' ', 'ArrowDown'].includes(k)) { e.preventDefault(); overview ? toggleOverview(false) : next(); }
    else if (['ArrowLeft', 'PageUp', 'ArrowUp'].includes(k)) { e.preventDefault(); prev(); }
    else if (k === 'Home') { e.preventDefault(); goto(0); }
    else if (k === 'End') { e.preventDefault(); goto(slides.length - 1); }
    else if (k === 'o' || k === 'O') toggleOverview();
    else if (k === 'Escape') toggleOverview(false);
    else if (k === 'm' || k === 'M') toggleMode();
    else if (k === 'n' || k === 'N') toggleNotes();
  });

  // click zones — slide mode only (scroll mode owns the scroll)
  deck.addEventListener('click', e => {
    if (overview || isScroll() || getSelection().toString()) return;
    if (e.target.closest('a, button, pre, code, table, input, textarea, svg')) return;
    (e.clientX > innerWidth * 0.5) ? next() : prev();
  });

  // overview grid from slide titles
  const ov = document.getElementById('overview');
  slides.forEach((s, i) => {
    const t = s.dataset.title || s.querySelector('h1,h2')?.textContent || `Slide ${i + 1}`;
    const item = document.createElement('button');
    item.className = 'ov-item';
    item.innerHTML = `<span class="ov-num">${i + 1}</span><span class="ov-t"></span>`;
    item.querySelector('.ov-t').textContent = t;
    item.onclick = () => { toggleOverview(false); goto(i, false); };
    ov.appendChild(item);
  });

  // init: honor the <body> default mode, restore position from hash
  if (!isScroll() && !body.classList.contains('mode-slides')) body.classList.add('mode-scroll');
  const startN = parseInt(location.hash.slice(1)) - 1;
  current = Number.isInteger(startN) && startN >= 0 ? clamp(startN) : 0;
  setMode(isScroll() ? 'scroll' : 'slides');
