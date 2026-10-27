# Quantum Flytrap — offline laboratory

Open **index.html** in a current desktop browser (Chrome or Edge recommended). It is a single, self-contained HTML file. You can move or rename it; no installation, web server, account, or internet connection is required by the packaged application. If you downloaded the release ZIP, extract it first and open **index.html**.

The file starts at the original waves lab. JavaScript and WebAssembly must be enabled. Click once before expecting audio; browsers prevent automatic sound playback.

## Downloading from GitHub

Use **Code → Download ZIP** on this repository, extract it, and open the root **index.html**. Alternatively, open **quantum-flytrap-offline.zip** in GitHub and use its download button to get the packaged release.

## Using the lab

- Use Play/Pause, Step, Step Back, and Stop, or the original keyboard shortcuts shown in their tooltips.
- Drag optical components from Elements to the board. Right-click a board component to change its properties. Rotation menus also support the arrow keys and Enter.
- The speed/mode slider switches between waves, detections, and beam.
- Experimental Setups opens all 20 original built-in examples. The local game browser opens the embedded campaign levels.
- **Download** exports your experiment to a JSON file; **Upload** reopens it. Use these for durable saves and moving experiments between computers. The floppy-disk Save control is the original cloud-only control and remains unavailable without an online account.
- The original application also autosaves modified boards and settings in this browser. File-based storage behavior can vary between browsers, private sessions, and file locations. Export important work rather than relying on browser storage.

## What matches, and what is unavailable

The lab uses the supplied site's original production JavaScript, CSS, component graphics, quantum-physics WebAssembly, captured Montserrat font subsets, sound effects, and synthesized music. The editor, simulation controls, visualizations, built-in experiment data, and game engine run locally. This is the real captured application, not a screenshot or a new approximate simulator.

**The supplied files are not a complete capture of the entire website.** Missing lazy-loaded pages (the original experiment gallery, game map, About, account pages, and others) have clearly labeled local navigation/replacement pages. Those replacement pages are not pixel-identical to the originals. The original embedded lab examples and game scenes themselves remain available.

Google sign-in, account creation, cloud saves, cloud sequences, the public user-experiment database, and online sharing require the original remote service and are unavailable offline. Educational links still point to their original external articles/videos. The offline app does not fetch those resources. No fake account or fabricated public experiment data is supplied.

The captured campaign data has 33 entries but two share the same `ghz` slug. Its original router exposes 32 distinct campaign routes. The captured data and routing behavior are preserved.

Consequently, this package is an offline copy of the captured lab with documented substitutions, not a claim that the missing pages or remote services have been reproduced completely.

## Validation

Automated Chromium checks covered:

- Original waves-lab startup, play/pause, step/step-back, stop, and state evolution.
- Component-parameter editing and waves/detections/beam selection.
- JSON download/upload round trips and modified-board autosave after reload.
- All 20 built-in example scenes and 32 distinct campaign scenes.
- Desktop, tablet, and mobile viewport rendering; component property editing.
- Physics and audio-engine initialization, with no external network requests or JavaScript errors during the checked workflows.
- A standalone-document test with the browser offline, no HTTP server, and a nested path containing spaces. Only the HTML document was provided; no additional asset requests were needed.

This cloud machine's managed browser blocks `file://` navigation, so **direct double-click/file-protocol execution could not be tested here**. The file is deliberately packaged for that use: no module imports, absolute asset paths, external fonts, or remote WASM loads; navigation uses URL hashes. Browser checks used loopback HTTP or supplied the document directly through the browser test harness. No browser security settings need to be disabled to use this package.

Detailed machine-generated results are in `test-results/` in the development source package. Audible output and every possible combination of optical elements have not been manually tested. No live-site pixel comparison was possible because this environment denied access to the live domain.

## Rebuilding (optional; not needed to run the HTML)

Requires Node.js 20+ and npm. From this directory:

```sh
npm ci
npm run build
```

The generated file is `dist/index.html`. `captured/` contains the original files recovered from the supplied ZIP and the response bodies of the supplied HAR. The original ZIP JavaScript is retained unchanged there. The HAR itself, request headers, and cookies are not included in the release.

`build.mjs` bundles the application and embeds its binary assets. `offline-runtime.js` supplies local-file navigation and handles the two anonymous startup API requests locally. `offline-pages.js` provides the explicitly labeled replacement pages for missing chunks. There is no service worker or external cache dependency.

For the recorded browser checks, install Python Playwright and a Chromium browser, then run a temporary local server in `dist` on port 8765 before running `test-offline.py` and `test-presets.py`. The test scripts currently use `/usr/bin/chromium`. `test-portability.py` needs no server.

## Attribution

Original application: Virtual Lab by Quantum Flytrap, https://lab.quantumflytrap.com/ (captured build `2026-10-09 d8ef3c6`). The captured page credits Piotr Migdał, Klem Jankiewicz, Paweł Grabarz, et al. Original authorship and notices in the captured code are retained. Offline compatibility and packaging changes are separate from the original application. No additional rights to the original artwork, code, or fonts are claimed by this package.
