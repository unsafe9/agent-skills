
  document.body.classList.add('js');
  const bar = document.getElementById('bar');
  const sections = [...document.querySelectorAll('section[data-nav]')];

  // side dot nav
  const nav = document.querySelector('nav.dots');
  sections.forEach((s, i) => {
    if (!s.id) s.id = 'sec-' + i;
    const a = document.createElement('a');
    a.href = '#' + s.id; a.title = s.dataset.nav;
    nav.appendChild(a);
  });
  const dots = [...nav.children];

  function onScroll(){
    const max = document.documentElement.scrollHeight - innerHeight;
    bar.style.width = (max > 0 ? scrollY / max * 100 : 0) + '%';
    const mid = scrollY + innerHeight * 0.4;
    let cur = 0;
    sections.forEach((s, i) => { if (s.offsetTop <= mid) cur = i; });
    dots.forEach((d, i) => d.classList.toggle('on', i === cur));
  }
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // fade-in on enter
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
  }), { threshold: 0.12 });
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));
