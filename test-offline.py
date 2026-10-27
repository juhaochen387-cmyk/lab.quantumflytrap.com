"""Functional browser checks. Uses loopback because managed browser blocks file://."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import json,re
root=Path(__file__).resolve().parent
results=[]; errors=[]; outside=[]; console_errors=[]
def check(name,condition,detail=None):
 results.append({'check':name,'passed':bool(condition),'detail':detail})
 assert condition,(name,detail)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
 def guard(route):
  url=route.request.url
  if url.startswith(('http://127.0.0.1:8765/','data:','blob:')):route.continue_()
  else:outside.append(url);route.abort()
 context.route('**/*',guard)
 page=context.new_page();page.set_default_timeout(7000)
 page.on('pageerror',lambda e: errors.append(str(e)))
 page.on('console',lambda m:console_errors.append(m.text) if m.type=='error' else None)
 page.goto('http://127.0.0.1:8765/index.html');page.wait_for_timeout(1000)
 if page.locator('.close-button').count():page.locator('.close-button').first.click()
 check('original waves lab rendered',page.locator('.Board').count()==1 and 'mode=waves' in page.url)
 # Edit the original beam-splitter property panel, then verify serialized physics input.
 parameter=page.locator('input[type=number]').first
 parameter.fill('37');parameter.press('Tab');page.wait_for_timeout(100)
 before=page.locator('body').inner_text()
 page.locator('button.i-stepForward').click();page.wait_for_timeout(150)
 after=page.locator('body').inner_text()
 check('single step evolves photon quantum state','|3 3→H⟩' in after and '|2 3→H⟩' in before)
 page.locator('button.i-stepBack').click();page.wait_for_timeout(150)
 check('step backward restores quantum state','|2 3→H⟩' in page.locator('body').inner_text())
 page.locator('button.i-playLab').click();page.wait_for_timeout(600)
 check('play advances simulation',page.locator('button.i-pauseLab').count()==1)
 page.locator('button.i-pauseLab').click()
 page.locator('button.i-stopLab').click();page.wait_for_timeout(100)
 check('stop resets quantum state','|2 3→H⟩' in page.locator('body').inner_text())
 # Original mode/speed slider switches between all three simulation presentations.
 track=page.locator('.ModeSelector .track');box=track.bounding_box()
 for fraction,mode in [(0.5,'detections'),(0.85,'beam'),(0.18,'waves')]:
  track.click(position={'x':box['width']*fraction,'y':box['height']/2})
  page.wait_for_timeout(100)
  check(mode+' mode selectable',page.locator('.ModeSelector .labels .active').inner_text()==mode)
 # Local JSON export and import are the offline persistence contract.
 with page.expect_download() as event:page.locator('button.i-download').click()
 download=event.value;dest=root/'test-results'/download.suggested_filename;download.save_as(dest)
 board=json.loads(dest.read_text());check('edited reflectance affects simulation board',any(abs(state.get('reflectance',-1)-0.37)<1e-6 for piece in board['grid']['pieces'] for state in piece['states']))
 check('JSON download contains original editable board',board['grid']['width']>0 and len(board['grid']['pieces'])>0,list(board))
 board['name']='Offline round-trip';payload=json.dumps(board).encode()
 page.locator('input[type=file]').set_input_files({'name':'offline-roundtrip.json','mimeType':'application/json','buffer':payload})
 page.wait_for_timeout(300)
 check('JSON upload restores experiment','Offline round-trip' in page.locator('body').inner_text())
 with page.expect_download() as event:page.locator('button.i-download').click()
 file2=root/'test-results/roundtrip.json';event.value.save_as(file2)
 check('round-trip preserves grid data',json.loads(file2.read_text())['grid']==board['grid'])
 # Original autosave saves modified experiments on navigation/unload.
 page.locator('button.i-editName').click()
 page.locator('input[data-consume-keyboard]').fill('Offline renamed')
 page.locator('button.i-confirm').click()
 page.reload();page.wait_for_timeout(500)
 check('experiment autosave survives reload','Offline renamed' in page.locator('body').inner_text())
 # Dropdown should expose original built-in experiments without missing asset requests.
 setup=page.locator('button.text-button').filter(has_text=re.compile('experimental setups',re.I))
 check('setups dropdown available',setup.count()==1)
 setup.click();page.wait_for_timeout(100)
 text=page.locator('body').inner_text();check('setups includes original Mach-Zehnder example','Mach-Zehnder' in text or 'Mach–Zehnder' in text,'Original built-in examples appear in dropdown')
 page.screenshot(path=str(root/'test-results/lab-working.png'))
 check('no external network requests',not outside,outside)
 check('no JavaScript errors',not errors,errors)
 check('no console errors',not console_errors,console_errors)
 browser.close()
(root/'test-results/functional.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
