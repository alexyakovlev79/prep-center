"""Read-only browser audit of every route at desktop and two mobile widths.
No live email submissions: any Cloud Function request is blocked.
"""
import asyncio,json,os,re,sys
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=Path(os.getenv('CTA_REPORT_DIR','/tmp/cta-qa'));OUT.mkdir(parents=True,exist_ok=True)
BASE=os.getenv('CTA_BASE_URL','http://127.0.0.1:8765').rstrip('/')
FILES=sorted(p for p in ROOT.rglob('index.html') if not {'restoration','tools','components','serverless','.git','node_modules'} & set(p.relative_to(ROOT).parts))
JS=r'''() => {
 const errors=[],counts={form:0,telegram:0,nav:0,calc:0};
 for(const e of document.querySelectorAll('.pc-action')){
  const r=e.getBoundingClientRect();if(!r.width||!r.height||e.closest('details:not([open])'))continue;
  const c=getComputedStyle(e),n=e.textContent.trim().replace(/\s+/g,' ');
  let expected=null;
  for(const k of Object.keys(counts))if(e.classList.contains('pc-action--'+k))counts[k]++;
  if(e.classList.contains('pc-action--form')||e.classList.contains('pc-action--calc'))expected='rgb(255, 153, 0)';
  if(e.classList.contains('pc-action--telegram'))expected=e.dataset.ctaTone==='dark'?'rgb(255, 255, 255)':'rgb(34, 158, 217)';
  if(e.classList.contains('pc-action--nav'))expected='rgb(250, 250, 250)';
  if(expected&&c.backgroundColor!==expected)errors.push('color:'+n+':'+c.backgroundColor);
  if(c.borderTopLeftRadius!=='14px')errors.push('radius:'+n+':'+c.borderTopLeftRadius);
  if(c.cursor!=='pointer')errors.push('cursor:'+n);
  if(r.x<-.5||r.right>innerWidth+.5)errors.push('overflow:'+n);
  if(r.height<40)errors.push('touch-height:'+n);
 }
 return {errors,counts,overflow:document.documentElement.scrollWidth-innerWidth};
}'''
async def main():
 results=[]
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True)
  sem=asyncio.Semaphore(4)
  async def visit(f,w):
   async with sem:
    page=await browser.new_page(viewport={'width':w,'height':900});page.set_default_timeout(10000)
    path='/' if f.parent==ROOT else '/'+f.parent.relative_to(ROOT).as_posix()+'/'
    async def route(r):
     if r.request.url.startswith(BASE) or r.request.url.startswith('data:'):await r.continue_()
     else:await r.abort()
    await page.route('**/*',route)
    info={'path':path,'width':w,'errors':[],'modal_tests':0}
    try:
     await page.goto(BASE+path,wait_until='domcontentloaded',timeout=30000)
     await page.wait_for_function("!!window.PrepCenterLeadForm")
     await page.evaluate('document.fonts.ready');await page.add_style_tag(content='html{scroll-behavior:auto!important}')
     info.update(await page.evaluate(JS))
     for a in await page.locator('a.pc-action--form').all():
      if not await a.is_visible():continue
      expected=await a.get_attribute('data-prep-request') or ''
      await a.evaluate('(e)=>e.click()')
      dialog=page.locator('.prep-lead-overlay')
      if await dialog.count()!=1:info['errors'].append('modal-count');continue
      actual=await dialog.locator('[name=comment]').input_value()
      if actual!=expected:info['errors'].append('wrong-context:'+actual)
      if w>600:
       left=await dialog.locator('[name=full_name]').bounding_box();right=await dialog.locator('.prep-lead-phone').bounding_box()
       if abs(left['y']-right['y'])>1:info['errors'].append('field-alignment')
      info['modal_tests']+=1;await page.keyboard.press('Escape')
     if w in (1440,390):
      target=page.locator('main .pc-actions').first
      if await target.count():await target.evaluate('(e)=>e.scrollIntoView({block:"center",behavior:"instant"})')
      await page.screenshot(path=str(OUT/(path.strip('/').replace('/','__')+'-'+str(w)+'.png')))
    except Exception as e:info['errors'].append(type(e).__name__+':'+str(e)[:250])
    results.append(info);print(json.dumps(info,ensure_ascii=False),flush=True);await page.close()
  await asyncio.gather(*(visit(f,w) for f in FILES for w in (1440,390,360)))
  await browser.close()
 issues=[r for r in results if r['errors'] or r.get('overflow',0)>1]
 report={'base':BASE,'pages':len(FILES),'page_views':len(results),'modal_tests':sum(r['modal_tests'] for r in results),'issues':issues,'results':results}
 (OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print('SUMMARY',json.dumps({k:v for k,v in report.items() if k not in ['results','issues']}),'ISSUES',len(issues))
 if issues:sys.exit(1)
if __name__=='__main__':asyncio.run(main())
