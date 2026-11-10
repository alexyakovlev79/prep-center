"""One-time, idempotent compatibility patch for contextual CTA requests."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'assets/prep-lead-form.js';s=p.read_text()
old="const calculatorRequest=typeof prefill==='string' && prefill.length>0;"
new="const calculatorRequest=!!(opener&&opener.id==='calc-send-form'&&typeof prefill==='string'&&prefill.length);\n const contextualRequest=(opener&&opener.dataset&&opener.dataset.prepRequest)||'';"
if old in s:s=s.replace(old,new)
elif new not in s:raise SystemExit('Unexpected modal API: inspect before patching')
old="const form=createForm('modal',calculatorRequest?prefill:excursion?'Хочу записаться на экскурсию на склад.':'',calculatorRequest?'calculator':'general');"
new="const form=createForm('modal',calculatorRequest?prefill:contextualRequest||(excursion?'Хочу записаться на экскурсию на склад.':''),calculatorRequest?'calculator':'general');"
if old in s:s=s.replace(old,new)
elif new not in s:raise SystemExit('Unexpected modal form builder')
s=s.replace("container.appendChild(createForm('inline',''));", "container.appendChild(createForm('inline',container.dataset.prepRequest||''));")
p.write_text(s)
p=ROOT/'assets/shared-components.js';s=p.read_text();s=re.sub(r"/assets/prep-lead-form.js\?[^']+",'/assets/prep-lead-form.js?v=20261110-cta-v1',s);p.write_text(s)
p=ROOT/'scripts/build_components.py';s=p.read_text()
if ' # Route every contact/conversion CTA' in s:
 st=s.index(' # Route every contact/conversion CTA');en=s.index(' # Refresh the changed photo',st);s=s[:st]+s[en:]
if ' from polish_cta import normalize' not in s:s=s.replace(' if old!=s:'," from polish_cta import normalize\n s=normalize(s,route.strip('/'))\n if old!=s:")
p.write_text(s)
