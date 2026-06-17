
  // ---- optional step highlight: walk numbered steps, lighting matching SVG groups ----
  // No [data-step] anywhere → fully static figure, this whole block no-ops.
  const stepLis = [...document.querySelectorAll('.steps li[data-step]')];
  if (stepLis.length) {
    const steps = [...new Set(stepLis.map(li => li.dataset.step))].sort((a, b) => a - b);
    const stages = [...document.querySelectorAll('.stage')];
    stages.forEach(s => s.classList.add('stepping'));
    let idx = -1;
    const paint = () => {
      const cur = idx === -1 ? null : steps[idx];
      stepLis.forEach(li => li.classList.toggle('on', li.dataset.step === cur));
      document.querySelectorAll('.stage [data-step]').forEach(g =>
        g.classList.toggle('lit', cur !== null && g.dataset.step === cur));
    };
    const go = n => { idx = Math.max(0, Math.min(steps.length - 1, n)); paint(); };
    stepLis.forEach(li => li.addEventListener('click', () => go(steps.indexOf(li.dataset.step))));
    addEventListener('keydown', e => {
      if (e.target.matches('input, textarea')) return;
      if (['ArrowRight', ' ', 'ArrowDown'].includes(e.key)) { e.preventDefault(); go(idx + 1); }
      else if (['ArrowLeft', 'ArrowUp'].includes(e.key)) { e.preventDefault(); go(idx - 1); }
    });
    paint();
  }
