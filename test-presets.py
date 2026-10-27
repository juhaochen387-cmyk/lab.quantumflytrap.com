"""Exercise bundled presets and responsive lab UI with all remote networking blocked."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import json,re,time,sys

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'test-results'/'presets'
OUT.mkdir(parents=True,exist_ok=True)
URL='http://127.0.0.1:8765/index.html'
source=(ROOT/'captured/assets/util-DiGQEveS.js').read_text()
raw=source.split('JSON.parse(`',1)[1].split('`)',1)[0]
original_examples=json.loads(raw.replace('\\\\','\\').replace('\\`','`'))
original_examples={item['slug']:item for item in original_examples}
results={'method':'Chromium on loopback HTTP; all non-loopback network blocked. No file:// execution (administrator policy).','examples':[],'campaign':[],'responsive':[],'interactions':[],'blocked_network':[]}
INTERACTIONS_ONLY='--interactions-only' in sys.argv
if INTERACTIONS_ONLY:
    results=json.loads((OUT/'results.json').read_text())
    results['interactions']=[]
    results['blocked_network']=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1440,'height':1000})
    def allow_only_local(route):
        if route.request.url.startswith(('http://127.0.0.1:8765/','data:','blob:')): route.continue_()
        else:
            results['blocked_network'].append(route.request.url)
            route.abort()
    context.route('**/*',allow_only_local)
    page=context.new_page()
    errors=[]
    page.on('pageerror',lambda error: errors.append(str(error)))
    page.set_default_timeout(5000)
    def go(path):
        page.goto(URL+'#'+path)
        page.wait_for_timeout(350)
        if page.locator('.close-button').is_visible():
            page.locator('.close-button').click()
        page.wait_for_timeout(100)
    def board_state():
        return page.locator('.Board').evaluate('''e=>({
            cells:e.querySelectorAll('.AppCell').length,
            paths:e.querySelectorAll('path').length,
            viewbox:e.querySelector('svg')?.getAttribute('viewBox'),
            width:e.getBoundingClientRect().width,
            height:e.getBoundingClientRect().height,
            nonFinitePaths:[...e.querySelectorAll('path[d]')].filter(p=>/NaN|Infinity/.test(p.getAttribute('d'))).length
        })''')
    if not INTERACTIONS_ONLY:
        go('/lab?mode=waves')
        page.locator('button.text-button').click()
        examples=page.locator('a[href^="#/lab/"]').evaluate_all('(es)=>es.map(e=>({name:e.innerText,href:e.getAttribute("href")}))')
        assert len(examples)==20
        for item in examples:
            start=len(errors)
            go(item['href'][1:]+'?mode=waves')
            state=board_state()
            title_present=item['name'] in page.locator('body').inner_text()
            expected=original_examples[item['href'].rsplit('/',1)[-1]]
            entry={**item,**state,'expected_cells':len(expected['grid']['pieces']),'expected_viewbox':f"0 0 {expected['grid']['width']*64} {expected['grid']['height']*64}",'title_present':title_present,'errors':errors[start:]}
            entry['passed']=state['cells']==entry['expected_cells'] and state['viewbox']==entry['expected_viewbox'] and title_present and state['cells']>0 and state['nonFinitePaths']==0 and not entry['errors']
            results['examples'].append(entry)
        go('/game')
        campaign=page.locator('a[href^="#/game/level/"]').evaluate_all('(es)=>es.map(e=>({name:e.querySelector("strong")?.innerText,href:e.getAttribute("href")}))')
        results['campaign_cards']=len(campaign)
        results['campaign_unique_routes']=len({i['href'] for i in campaign})
        seen=set()
        for item in campaign:
            if item['href'] in seen:continue
            seen.add(item['href'])
            start=len(errors)
            go(item['href'][1:])
            state=board_state()
            expected=re.sub(r'^\d+\.\s*','',item['name'])
            title_present=expected in page.locator('body').inner_text()
            entry={**item,**state,'title_present':title_present,'errors':errors[start:]}
            entry['passed']=title_present and state['cells']>0 and state['nonFinitePaths']==0 and not entry['errors']
            results['campaign'].append(entry)
        for width,height in [(1440,1000),(1024,768),(768,1024),(390,844)]:
            page.set_viewport_size({'width':width,'height':height})
            start=len(errors)
            go('/lab/mach-zehnder?mode=waves')
            page.wait_for_timeout(250)
            state=board_state()
            path=OUT/f'viewport-{width}x{height}.png'
            page.screenshot(path=str(path),full_page=True)
            entry={'viewport':{'width':width,'height':height},**state,'screenshot':str(path.relative_to(ROOT)),'errors':errors[start:]}
            entry['passed']=state['width']>0 and state['height']>0 and state['cells']>0 and state['nonFinitePaths']==0 and not entry['errors']
            results['responsive'].append(entry)
    page.set_viewport_size({'width':1440,'height':1000})
    go('/lab/mach-zehnder?mode=waves')
    page.wait_for_timeout(700)
    # Real mouse events hit the interaction canvas at the rendered mirror center.
    cell=page.locator('.Board .AppCell').nth(1)
    bounds=cell.bounding_box()
    page.mouse.click(bounds['x']+bounds['width']/2,bounds['y']+bounds['height']/2,button='right')
    page.wait_for_timeout(200)
    text=page.locator('body').inner_text()
    results['interactions'].append({'operation':'Right-click original scene mirror opens component properties','passed':all(t in text for t in ['Mirror','Element description','Draggable','Rotatable'])})
    if not all(t in text for t in ['Mirror','Element description','Draggable','Rotatable']):
        page.screenshot(path=str(OUT/'interaction-failure.png'))
        (OUT/'interaction-failure.txt').write_text(text)
    rotation=page.locator('.ListSelect.kind-default')
    before=rotation.locator('.option.active').inner_text()
    before_transform=cell.get_attribute('style')
    rotation.click()
    rotation.press('ArrowUp')
    rotation.press('Enter')
    page.wait_for_timeout(500)
    after=rotation.locator('.option.active').inner_text()
    after_transform=cell.get_attribute('style')
    results['interactions'].append({'operation':'Edit mirror rotation with supported keyboard control','before':before,'after':after,'before_transform':before_transform,'after_transform':after_transform,'passed':before!=after and before_transform!=after_transform})
    page.keyboard.press('Escape')
    for slug,particle_count in [('hong-ou-mandel',2),('ghz-state',3)]:
        start=len(errors)
        go('/lab/'+slug+'?mode=waves')
        before=page.locator('body').inner_text().split('QUANTUM STATE',1)[-1]
        page.get_by_title('Step forward [→]',exact=True).click()
        page.wait_for_timeout(250)
        after=page.locator('body').inner_text().split('QUANTUM STATE',1)[-1]
        state=board_state()
        results['interactions'].append({'operation':f'Step original {particle_count}-photon {slug} simulation','before_quantum_state':before,'after_quantum_state':after,'errors':errors[start:],'passed':before!=after and state['nonFinitePaths']==0 and not errors[start:]})
    results['all_page_errors']=errors
    browser.close()
results['passed']=all(item['passed'] for section in ['examples','campaign','responsive','interactions'] for item in results[section]) and not results['blocked_network']
(OUT/'results.json').write_text(json.dumps(results,indent=2))
print(json.dumps({'passed':results['passed'],'examples':len(results['examples']),'campaign_unique_routes':len(results['campaign']),'responsive':len(results['responsive']),'errors':results['all_page_errors'],'blocked_network':results['blocked_network'],'failures':[item for section in ['examples','campaign','responsive','interactions'] for item in results[section] if not item['passed']]},indent=2))
raise SystemExit(0 if results['passed'] else 1)
