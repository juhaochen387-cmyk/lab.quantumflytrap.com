// Local navigation for pages whose original lazy-loaded code was not captured.
// The simulator and all listed experiment/game data are the original captured code.
import { _t as h, Xt as ref, Ot as onUnmounted, St as initializeRuntime } from './captured/assets/graphql-CRgiIBgc.js';
import { U as examples, O as campaign } from './captured/assets/util-DiGQEveS.js';
initializeRuntime();

const style = {
  page: { minHeight: '100vh', boxSizing: 'border-box', background: '#26005b', color: '#fff', fontFamily: 'Montserrat, sans-serif', padding: '30px clamp(18px, 5vw, 75px)', overflowY: 'auto', height: '100vh' },
  nav: { display: 'flex', gap: '24px', flexWrap: 'wrap', marginBottom: '38px', alignItems: 'center' },
  link: { color: '#edeaf4', textDecoration: 'none', lineHeight: '1.6' },
  title: { fontSize: '30px', fontWeight: '700', margin: '16px 0' },
  note: { fontSize: '14px', color: '#c3cbd3', maxWidth: '850px', lineHeight: '1.8' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(235px, 1fr))', gap: '14px', margin: '26px 0', maxWidth: '1200px' },
  card: { padding: '19px', background: '#330076', border: '1px solid #46505b', borderRadius: '5px', color: '#fff', display: 'block', textDecoration: 'none', lineHeight: '1.6' },
  sub: { display: 'block', color: '#c4aadf', fontSize: '12px', marginTop: '7px' }
};
const link = (text, href) => h('a', { href, style: style.link }, text);
const paragraph = text => h('p', { style: style.note }, text);
const title = text => h('h1', { style: style.title }, text);
const cards = (items, kind) => h('div', { style: style.grid }, items.map((item, index) =>
  h('a', { href: kind === 'game' ? `#/game/level/${item.slug}` : `#/lab/${item.slug}?mode=waves`, style: style.card }, [
    h('strong', null, `${kind === 'game' ? `${index + 1}. ` : ''}${item.name || item.slug}`),
    h('span', { style: style.sub }, kind === 'game' ? 'Play the original embedded level →' : 'Open the original experiment in the lab →')
  ])
));

export default {
  name: 'OfflineCapturedPages',
  inheritAttrs: false,
  setup() {
    const route = ref(location.hash.slice(1) || '/experiments');
    const updateRoute = () => { route.value = location.hash.slice(1) || '/experiments'; };
    window.addEventListener('hashchange', updateRoute);
    onUnmounted(() => window.removeEventListener('hashchange', updateRoute));
    return () => {
      const path = route.value.split('?')[0];
      let content;
      if (path === '/experiments') {
        content = [title('Experimental setups'), paragraph('Open any original built-in experiment below. The browser page has been recreated for this offline copy; the experiment data and simulator are the original captured website.'), cards(examples, 'lab')];
      } else if (path === '/game') {
        content = [title('Quantum Game — level map'), paragraph('All embedded campaign levels are available offline. This local level browser opens each level in the original game engine.'), cards(campaign(), 'game')];
      } else if (path === '/about') {
        content = [title('About this offline copy'), paragraph('Quantum Flytrap Virtual Lab is an interactive quantum optics laboratory. This package preserves the captured lab interface, optical components, simulator, sounds, examples, and campaign levels.'), paragraph('The original code for this particular page was not included in the supplied download. This page is a local substitute. The live service’s account system, cloud storage, public user experiments, and external linked articles are not available offline.'), paragraph('Use the lab’s download and upload buttons to save experiments as JSON files and reopen them on this computer. Browser autosave is local and is not a substitute for exported files.')];
      } else if (path === '/options') {
        content = [title('Offline settings'), paragraph('The original options page was not included in the capture. Use the original lab controls to change simulation mode, speed, view, audio volume, board size, and component properties.'), paragraph('Your lab preferences and unsaved board changes are stored by the original application in this browser. Export important experiments with the lab’s download button.')];
      } else if (path.startsWith('/game/rocks/')) {
        content = [title('Rock conversations'), paragraph('The original conversation page was not included in the capture. All embedded campaign levels remain playable.'), link('Browse game levels →', '#/game')];
      } else if (path === '/login' || path === '/register' || path === '/myaccount' || path.startsWith('/u')) {
        content = [title('Online account features'), paragraph('Sign-in, account creation, cloud experiment storage, sequences, and the public user gallery require the live Quantum Flytrap service. They cannot work in an offline HTML file, and no account is required to use this local lab.'), paragraph('Save your own experiments with the lab’s download button, and reopen them using upload. Built-in examples and game levels are available here without an account.'), link('Browse built-in experiments →', '#/experiments')];
      } else {
        content = [title('Page unavailable in this capture'), paragraph('The supplied archive did not include this page. The offline laboratory, built-in experiments, and embedded game levels remain available.')];
      }
      return h('main', { style: style.page }, [
        h('nav', { style: style.nav }, [
          link('← Virtual Lab', '#/lab?mode=waves'),
          link('Experimental setups', '#/experiments'),
          link('Quantum Game', '#/game'),
          link('About', '#/about')
        ]),
        ...content,
        h('p', { style: { ...style.note, borderTop: '1px solid #46505b', marginTop: '40px', paddingTop: '18px' } }, 'Offline navigation page · Original captured simulator and experiment data')
      ]);
    };
  }
};
