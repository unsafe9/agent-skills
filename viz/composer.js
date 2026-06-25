
  // ---- decisions + bottom prompt composer (no-op without #composer) ----
  // build.py assembles this in after the engine; it stays inert on a page that
  // emits no #composer, so it costs nothing when unused.
  const composer = document.getElementById('composer');
  if (composer) {
    const preview = document.getElementById('prompt-preview');
    const copyBtn = document.getElementById('copy-btn');
    const build = () => {
      const parts = [];
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
