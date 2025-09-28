---
fecha-creación: {{ fecha_actual.strftime("%d/%m/%Y) }}
source: {{ source }}
doi: {{ doi }}
title: "{{ title }}"
abstract: |
{{ abstract_formatted }}
primera-revisión:
segunda-revisión:
estado: obtenido-motor
tags:
  - paper
  - primera-sin-revisar
  - segunda-sin-revisar
---

> [!primera-wrap]+ ① **Primera revisión** 
> `INPUT[inlineSelect(option(aprobado, '🟢 aprobado'), option(rechazado, '🔴 rechazado')):primera-revisión]`

> [!segunda-wrap]+ ② **Segunda revisión** 
> `INPUT[inlineSelect(option(aprobado, '🟢 aprobado'), option(rechazado, '🔴 rechazado')):segunda-revisión]`

```meta-bind-js-view
{primera-revisión} as p1
{segunda-revisión} as p2
save to {tags}
hidden
---
const norm = v => String(v ?? '').trim().toLowerCase();
const valid = v => (v === 'aprobado' || v === 'rechazado') ? v : 'sin-revisar';

const s1 = valid(norm(context.bound.p1));
const s2 = valid(norm(context.bound.p2));

return ['paper', `primera-${s1}`, `segunda-${s2}`];

```

```meta-bind-js-view
{primera-revisión} as p1
{segunda-revisión} as p2
save to {estado}
hidden
---
const norm = v => String(v ?? '').trim().toLowerCase();
const chosen = v => (v === 'aprobado' || v === 'rechazado');

const s1 = norm(context.bound.p1);
const s2 = norm(context.bound.p2);

let estado = 'obtenido-motor';

if (!chosen(s1) && !chosen(s2)) {
  estado = 'obtenido-motor';
} else if (s1 === 'rechazado') {
  estado = 'rechazado-final';
} else if (s1 === 'aprobado' && !chosen(s2)) {
  estado = 'en-segunda-revision';
} else if (s1 === 'aprobado' && chosen(s2)) {
  estado = (s2 === 'aprobado') ? 'aprobado-final' : 'rechazado-final';
} else if (chosen(s1) && !chosen(s2)) {
  estado = 'en-primera-revision';
}

return estado;
```

```meta-bind-js-view
{primera-revisión} as p1
{segunda-revisión} as p2
hidden
---
const norm = v => String(v ?? '').trim().toLowerCase();
const isApproved = norm(context.bound.p1) === 'aprobado';
const secondChosen = ['aprobado','rechazado'].includes(norm(context.bound.p2));

function findCallout(type){
  return document.querySelector('.markdown-preview-view .callout[data-callout="'+type+'"]')
      || document.querySelector('.cm-s-obsidian .callout[data-callout="'+type+'"]')
      || document.querySelector('.callout[data-callout="'+type+'"]');
}

function apply(){
  const first  = findCallout('primera-wrap');
  const second = findCallout('segunda-wrap');

  if (!first || !second) {
    requestAnimationFrame(apply);
    return;
  }

  second.style.display = isApproved ? '' : 'none';
  first.style.display = (isApproved && secondChosen) ? 'none' : '';

  const input2 = second.querySelector('select, input, textarea, .mb-input');
  if (input2) input2.disabled = !isApproved;

  const input1 = first.querySelector('select, input, textarea, .mb-input');
  if (input1) input1.disabled = (isApproved && secondChosen);
}

apply();
return '';
```