---
fecha-creación: {{ fecha_actual.strftime("%d/%m/%Y") }}
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

`BUTTON[regresar-4to3, regresar-3to2, regresar-2to1]`

> [!primera-wrap]+ ① **Primera revisión** 
> `INPUT[inlineSelect(option(aprobado, '🟢 aprobado'), option(rechazado, '🔴 rechazado')):primera-revisión]`

> [!segunda-wrap]+ ② **Segunda revisión** 
> `INPUT[inlineSelect(option(aprobado, '🟢 aprobado'), option(rechazado, '🔴 rechazado')):segunda-revisión]`

> [!extraccion-wrap]+ ③ **Extracción de datos**
> `BUTTON[start-extraccion]`

```meta-bind-button
id: regresar-4to3
label: "Regresar"
style: plain
icon: arrow-left
class: btn-regresar step-4to3
hidden: true
tooltip: "Fase 4 → 3 (extracción → aprobado-final)"
action:
  type: updateMetadata
  bindTarget: estado
  evaluate: false
  value: "aprobado-final"
```

```meta-bind-button
id: regresar-3to2
label: "Regresar"
style: plain
icon: arrow-left
class: btn-regresar step-3to2
hidden: true
tooltip: "Fase 3 → 2 (quitar segunda-revisión)"
action:
  type: updateMetadata
  bindTarget: segunda-revisión
  evaluate: false
  value: ""
```

```meta-bind-button
id: regresar-2to1
label: "Regresar"
style: plain
icon: arrow-left
class: btn-regresar step-2to1
hidden: true
tooltip: "Fase 2 → 1 (quitar primera-revisión)"
action:
  type: updateMetadata
  bindTarget: primera-revisión
  evaluate: false
  value: ""
```

```meta-bind-js-view
{estado} as est
{primera-revisión} as p1
{segunda-revisión} as p2
hidden
---
const norm   = v => String(v ?? '').trim().toLowerCase();
const chosen = v => v === 'aprobado' || v === 'rechazado';

const E  = norm(context.bound.est);
const S1 = norm(context.bound.p1);
const S2 = norm(context.bound.p2);

let showClass = null;


if (E === 'en-extracción') showClass = 'step-4to3';
else if ((E === 'aprobado-final' || E === 'rechazado-final') && chosen(S2)) showClass = 'step-3to2';
else if ((S1 === 'aprobado' || S1 === 'rechazado') && !chosen(S2)) showClass = 'step-2to1';


const css = `

.step-4to3, .step-3to2, .step-2to1 { display: none !important; }

${showClass ? `.${showClass} { display: inline-flex !important; }` : ''}
`;


let style = document.getElementById('mb-regresar-style');
if (!style) {
  style = document.createElement('style');
  style.id = 'mb-regresar-style';
  document.head.appendChild(style);
}
style.textContent = css;

return '';

```

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
const n = v => String(v ?? '').trim().toLowerCase();
const c = v => v==='aprobado' || v==='rechazado';
const s1 = n(context.bound.p1);
const s2 = n(context.bound.p2);

if (!c(s1) && !c(s2)) return 'obtenido-motor';
if (s1 === 'rechazado') return 'rechazado-final';
if (s1 === 'aprobado' && !c(s2)) return 'en-segunda-revision';
if (s1 === 'aprobado' && c(s2)) return (s2==='aprobado') ? 'aprobado-final' : 'rechazado-final';
return 'obtenido-motor';

```

```meta-bind-js-view
{primera-revisión} as p1
{segunda-revisión} as p2
{estado} as est
hidden
---
const norm = v => String(v ?? '').trim().toLowerCase();
const isApproved   = norm(context.bound.p1) === 'aprobado';
const secondChosen = ['aprobado','rechazado'].includes(norm(context.bound.p2));
const enEx         = norm(context.bound.est) === 'en-extracción';

function findCallout(type){
  return document.querySelector('.markdown-preview-view .callout[data-callout="'+type+'"]')
      || document.querySelector('.cm-s-obsidian .callout[data-callout="'+type+'"]')
      || document.querySelector('.callout[data-callout="'+type+'"]');
}

function apply(){
  const first  = findCallout('primera-wrap');
  const second = findCallout('segunda-wrap');
  if (!first || !second) { requestAnimationFrame(apply); return; }

  second.style.display = (isApproved && !enEx) ? '' : 'none';
  first.style.display = (isApproved && secondChosen) ? 'none' : '';

  const input2 = second.querySelector('select, input, textarea, .mb-input');
  if (input2) input2.disabled = (!isApproved || enEx);

  const input1 = first.querySelector('select, input, textarea, .mb-input');
  if (input1) input1.disabled = (isApproved && secondChosen) || enEx;
}

apply();
return '';

```

```meta-bind-button
label: "Empezar extracción"
style: primary
icon: play
id: start-extraccion
hidden: true
tooltip: "Marcar paper como en-extracción"
actions:
  - type: updateMetadata
    bindTarget: estado
    evaluate: false
    value: "en-extracción"


```

```meta-bind-js-view
{estado} as est
hidden
---
const norm = v => String(v ?? '').trim().toLowerCase();
const allowed = norm(context.bound.est) === 'aprobado-final';

function findCallout(type){
  return document.querySelector('.markdown-preview-view .callout[data-callout="'+type+'"]')
      || document.querySelector('.cm-s-obsidian .callout[data-callout="'+type+'"]')
      || document.querySelector('.callout[data-callout="'+type+'"]');
}

function toggle(){
  const ex = findCallout('extraccion-wrap');
  if (!ex) { requestAnimationFrame(toggle); return; }

  // Mostrar/ocultar el callout completo
  ex.style.display = allowed ? '' : 'none';

  // Mostrar/ocultar el botón (y quitarle el "hidden" duro si existe)
  const btn = document.querySelector('[data-mb-id="start-extraccion"]') 
           || document.getElementById('start-extraccion');
  if (btn) {
    if (allowed) {
      btn.removeAttribute('hidden');
      btn.style.display = '';
    } else {
      btn.setAttribute('hidden','true');
      btn.style.display = 'none';
    }
  }
}
toggle();
return '';


```
