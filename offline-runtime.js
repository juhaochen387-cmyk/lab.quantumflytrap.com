/* Local-file compatibility only; the original app and physics run unchanged. */
(function () {
  window.__offlineBytes = encoded => Uint8Array.from(atob(encoded), char => char.charCodeAt(0));
  // Hash navigation works in file:// without rewriting the local file's pathname.
  if (!location.hash.startsWith('#/')) {
    const parameters = new URLSearchParams(location.search);
    if (!parameters.has('mode')) parameters.set('mode', 'waves');
    history.replaceState(null, '', location.pathname + location.search + '#/lab?' + parameters);
  }
  const nativeFetch = window.fetch.bind(window);
  window.fetch = async (input, options) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;
    if (url === '/graphql' || /\/graphql(?:\?|$)/.test(url)) {
      let request = {};
      try {request = JSON.parse(options?.body || '{}');} catch {}
      let result;
      if (request.operationName === 'AppConfig') {
        result = {data:{appConfig:{__typename:'AppConfigPayload',googleClientId:''}}};
      } else if (request.operationName === 'MySequences') {
        // Anonymous state matches the supplied capture. Never fabricate a cloud account.
        result = {data:null,errors:[{message:'Forbidden',path:['mySequences']}]};
      } else {
        result = {data:null,errors:[{message:'This feature requires the online service. Download/upload JSON to save and load offline.'}]};
      }
      return new Response(JSON.stringify(result), {status:200, headers:{'Content-Type':'application/json'}});
    }
    if (/^(data:|blob:)/.test(url)) return nativeFetch(input, options);
    throw new Error('Network access is disabled in this offline copy: ' + url);
  };
})();
