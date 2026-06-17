
  // ---- decisions + bottom prompt composer (shared by every interactive style; no-op without #composer) ----
  // The matrix pick-row branch is compare-only and self-skips elsewhere, so this
  // one block serves scroll / slides / compare / diagram identically. build.py
  // assembles it in after each engine; it is never duplicated per engine.
  const composer = document.getElementById('composer');
  if (composer) {
    const preview = document.getElementById('prompt-preview');
    const copyBtn = document.getElementById('copy-btn');
    const build = () => {
      const parts = [];
      // compare's matrix pick row (flat .option set under each column); null elsewhere
      const pickRow = document.querySelector('.cell--pick')?.closest('.cmp-grid');
      if (pickRow) {
        const sel = pickRow.querySelector('.cell--pick .option.sel') || pickRow.querySelector('.cell--pick .option.pick');
        if (sel) parts.push(sel.dataset.frag || sel.textContent.trim());
      }
      document.querySelectorAll('.decision').forEach(d => {
        const sel = d.querySelector('.option.sel') || d.querySelector('.option.pick');
        if (sel) parts.push(sel.dataset.frag || sel.textContent.trim());
      });
      document.querySelectorAll('.ask-input').forEach(i => {
        const v = i.value.trim();
        if (v) parts.push((i.dataset.frag || '{v}').replace('{v}', v));
      });
      return [composer.dataset.lead, parts.join(', '), composer.dataset.tail].filter(Boolean).join(' ');
    };
    const refresh = () => { preview.textContent = build(); };
    // compare pick row: a flat set of .option buttons (one per column), mutually exclusive
    const picks = [...document.querySelectorAll('.cell--pick .option')];
    if (picks.length) {
      const lean = picks.find(p => p.classList.contains('pick'));
      if (lean) lean.classList.add('sel');
      picks.forEach(opt => opt.addEventListener('click', () => {
        picks.forEach(o => o.classList.remove('sel'));
        opt.classList.add('sel'); refresh();
      }));
    }
    document.querySelectorAll('.decision').forEach(d => {
      const pick = d.querySelector('.option.pick');
      if (pick) pick.classList.add('sel');
      d.querySelectorAll('.option').forEach(opt => opt.addEventListener('click', () => {
        d.querySelectorAll('.option').forEach(o => o.classList.remove('sel'));
        opt.classList.add('sel'); refresh();
      }));
    });
    document.querySelectorAll('.ask-input').forEach(i => i.addEventListener('input', refresh));
    copyBtn.addEventListener('click', async () => {
      const text = build();
      try { await navigator.clipboard.writeText(text); }
      catch { const t = document.createElement('textarea'); t.value = text; document.body.appendChild(t); t.select(); document.execCommand('copy'); t.remove(); }
      const old = copyBtn.textContent; copyBtn.textContent = copyBtn.dataset.done || 'Copied ✓';
      setTimeout(() => copyBtn.textContent = old, 1400);
    });
    refresh();
  }
