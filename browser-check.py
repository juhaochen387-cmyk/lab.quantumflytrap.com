from playwright.sync_api import sync_playwright
import pathlib,json
root=pathlib.Path(__file__).resolve().parent
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
 page=context.new_page()
 errors=[];requests=[];messages=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('console',lambda m:messages.append(m.type+': '+m.text))
 page.on('request',lambda r:requests.append(r.url))
 page.goto('http://127.0.0.1:8765/index.html')
 page.wait_for_timeout(4000)
 (root/'test-results').mkdir(exist_ok=True)
 page.screenshot(path=str(root/'test-results/initial.png'),full_page=True)
 print('URL',page.url)
 print('ERRORS',json.dumps(errors))
 print('CONSOLE',json.dumps(messages)[-5000:])
 print('REQUESTS',json.dumps(requests))
 print('TEXT',page.locator('body').inner_text()[:12000])
 print('BUTTONS',json.dumps(page.locator('button').evaluate_all('(es)=>es.map(e=>({text:e.innerText,title:e.title,aria:e.getAttribute("aria-label"),class:e.className}))')))
 print('INPUTS',json.dumps(page.locator('input').evaluate_all('(es)=>es.map(e=>({type:e.type,value:e.value,placeholder:e.placeholder}))')))
 browser.close()
