// Builds a standalone file:// application from the original captured distribution.
import {build} from 'esbuild';
import {readFile,writeFile,mkdir,access} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url));
const assets=path.join(root,'captured/assets');
const read=name=>readFile(path.join(assets,name));
const data=async(name,type)=>`data:${type};base64,${(await read(name)).toString('base64')}`;
const physics=await data('qg_rust_bg-lyin4zVQ.wasm','application/wasm');
const synth=await data('qg_synth_bg-BD248i3-.wasm','application/wasm');
const sounds=await data('qg-sounds-Dw4vlPW3.mp3','audio/mpeg');
const worklet=(await read('music-worklet.4595755e.js')).toString();
const replaceOnce=(text,from,to)=>{
 if(!text.includes(from))throw new Error('Capture changed: missing patch '+from.slice(0,80));
 return text.replace(from,to);
};
const result=await build({
 entryPoints:[path.join(assets,'index-CvfDeoRD.js')],bundle:true,format:'iife',platform:'browser',target:'es2020',minify:true,write:false,
 legalComments:'inline',logLevel:'warning',
 plugins:[{name:'captured-offline-runtime',setup(b){
  b.onResolve({filter:/\.\/[^/]+\.js$/},async args=>{
   const p=path.resolve(args.resolveDir,args.path);
   try {await access(p);return;}catch{}
   // Only missing route modules use the explicitly documented local replacement.
   if(!/Page-|Demo-/.test(args.path))throw new Error('Missing required dependency: '+p);
   return {path:path.join(root,'offline-pages.js')};
  });
  b.onLoad({filter:/captured\/assets\/.*\.js$/},async args=>{
   let s=await readFile(args.path,'utf8'); const name=path.basename(args.path);
   if(name==='wasm-bindings-BNEWrK-F.js'){
    s=replaceOnce(s,'new URL("/assets/qg_rust_bg-lyin4zVQ.wasm",""+import.meta.url)',`window.__offlineBytes(${JSON.stringify(physics.split(',')[1])})`);
    s=replaceOnce(s,'"/assets/qg_synth_bg-BD248i3-.wasm"',JSON.stringify(synth));
   }
   if(name==='router-D-w4bM7T.js')s=replaceOnce(s,'history:Tn("/")','history:Tn("#")');
   if(name==='util-DiGQEveS.js'){
    const start=s.indexOf('n=new Promise((c,l)=>{const d=document.createElement("script")');
    const end=s.indexOf(';n.catch(',start);
    if(start<0||end<0)throw new Error('Google loader not found');
    s=s.slice(0,start)+'n=Promise.reject(new Error("Google sign-in requires the online service; use JSON download/upload to save offline"))'+s.slice(end);
   }
   if(name==='qg-sounds-CBR7WtIV.js')s='export default '+JSON.stringify(sounds)+';';
   if(name==='music-worklet-BbXJm0_d.js')s=`export default async context=>{if(!('audioWorklet' in context))return;const url=URL.createObjectURL(new Blob([${JSON.stringify(worklet)}],{type:'text/javascript'}));try{await context.audioWorklet.addModule(url);}finally{URL.revokeObjectURL(url);}};`;
   // Everything is bundled. Original Vite preloading would request nonexistent /assets URLs.
   s=s.replaceAll('if(e&&e.length>0)','if(false)').replaceAll('import.meta.resolve','undefined').replaceAll('import.meta.url','window.location.href');
   return {contents:s,loader:'js'};
  });
 }}]
});
let css=(await read('style-Ct0PjUft.css')).toString();
let fonts=await readFile(path.join(root,'captured/fonts/montserrat.css'),'utf8');
const faces=fonts.match(/@font-face\s*\{[^}]+\}/g)||[];
fonts='';
for(let face of faces){
 const m=face.match(/url\((https:[^)]+)\)/);if(!m)continue;
 try{
  const bytes=await readFile(path.join(root,'captured/fonts',path.basename(new URL(m[1]).pathname)));
  fonts+=face.replace(m[1],`data:font/woff2;base64,${bytes.toString('base64')}`)+'\n';
 }catch {/* Font subsets not used by the captured page were not present in the HAR. */}
}
const icon=(await readFile(path.join(root,'captured/favicon.ico'))).toString('base64');
const bridge=await readFile(path.join(root,'offline-runtime.js'),'utf8');
// Escape closing tags in JS strings so the HTML parser cannot terminate the script early.
const script=(bridge+'\n'+result.outputFiles[0].text).replace(/<\/script/gi,'<\\/script');
const html=`<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,minimum-scale=1">
<title>Virtual Lab by Quantum Flytrap</title>
<meta name="description" content="Offline copy of Virtual Lab by Quantum Flytrap, using the captured original simulation and interface.">
<meta http-equiv="Content-Security-Policy" content="default-src 'self' data: blob:; script-src 'unsafe-inline' 'unsafe-eval' blob:; style-src 'unsafe-inline'; img-src data: blob:; font-src data:; media-src data: blob:; connect-src data: blob:; worker-src blob:; object-src 'none'; base-uri 'none'">
<link rel="icon" href="data:image/x-icon;base64,${icon}"><style>${fonts}\n${css}</style></head>
<body><noscript>Please enable JavaScript to run the quantum simulation.</noscript><div id="app"></div><script>${script}</script></body></html>`;
await mkdir(path.join(root,'dist'),{recursive:true});
await writeFile(path.join(root,'dist/index.html'),html);
console.log(`Built standalone dist/index.html (${(Buffer.byteLength(html)/1024/1024).toFixed(2)} MiB). No server or network required.`);
