
  // ---- column focus/dim: click a candidate header to read one column at a time ----
  const grid = document.querySelector('.cmp-grid');
  if (grid) {
    // map each .cand header + every .cell to its 0-based candidate column index
    const cols = new Map();   // candIndex -> [elements]
    const cands = [];
    let col = -1;
    [...grid.children].forEach(el => {
      if (el.classList.contains('cmp-corner') || el.classList.contains('crit')) { col = -1; return; }
      col++;
      if (!cols.has(col)) cols.set(col, []);
      cols.get(col).push(el);
      if (el.classList.contains('cand')) cands.push({ el, col });
    });
    let focused = -1;
    const apply = () => {
      cols.forEach((els, c) => {
        const dim = focused !== -1 && c !== focused;
        els.forEach(el => el.classList.toggle('cmp-dim', dim));
      });
    };
    cands.forEach(({ el, col }) => el.addEventListener('click', () => {
      focused = focused === col ? -1 : col;   // toggle off when re-clicked
      apply();
    }));
  }
