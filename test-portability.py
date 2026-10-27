"""Prove that the distributed HTML needs no server-side routing or extra assets.
The managed Chromium forbids file://. Fulfil just the document at a nested path
with spaces, with network offline and no server listening; reject everything else.
"""
from playwright.sync_api import sync_playwright
from pathlib import Path
import json
root=Path(__file__).resolve().parent
html=(root/'dist/index.html').read_text()
requests=[];errors=[];console_errors=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 c=b.new_context(offline=True)
 url='http://127.0.0.1:8471/My%20Offline%20Lab/index.html'
 def route(r):
  requests.append(r.request.url)
  if r.request.url==url:r.fulfill(status=200,content_type='text/html; charset=utf-8',body=html)
  else:r.abort()
 c.route('**/*',route)
 page=c.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('console',lambda m:console_errors.append(m.text) if m.type=='error' else None)
 page.goto(url);page.wait_for_timeout(1000)
 assert page.locator('.Board').count()==1
 page.locator('.close-button').first.click()
 page.locator('button.i-stepForward').click();page.wait_for_timeout(100)
 assert '|3 3→H⟩' in page.locator('body').inner_text()
 page.evaluate("location.hash='/lab/mach-zehnder?mode=waves'")
 page.wait_for_timeout(300)
 assert page.locator('.Board').count()==1
 assert 'Mach-Zehnder' in page.locator('h1.title').inner_text()
 assert requests==[url],requests
 assert not errors,errors
 assert not console_errors,console_errors
 b.close()
result={'passed':True,'network':'Browser offline; no HTTP server; document supplied from disk to browser routing harness','path':'Nested directory with spaces','document_requests':len(requests),'extra_asset_requests':0,'page_errors':errors,'console_errors':console_errors,'file_protocol_test':'Blocked by managed browser administrator policy; not executed'}
(root/'test-results/portability.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
