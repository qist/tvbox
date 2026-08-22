export default {
  async fetch(request) {
    const u = new URL(request.url);
    let t = u.searchParams.get('q') || u.pathname.slice(1);
    if (!t) return new Response('', { status: 404 });
    if (!t.startsWith('http')) t = 'https://' + t;
    try {
      const target = new URL(t);
      const r = await fetch(t, {
        method: 'GET',
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
          'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
          'Accept-Encoding': 'gzip, deflate, br',
          'Referer': target.origin + '/',
          'Origin': target.origin,
          'Connection': 'keep-alive',
          'Upgrade-Insecure-Requests': '1',
          'Sec-Fetch-Dest': 'document',
          'Sec-Fetch-Mode': 'navigate',
          'Sec-Fetch-Site': 'same-origin',
          'Sec-Fetch-User': '?1',
        },
        redirect: 'follow',
      });
      const h = new Headers(r.headers);
      h.set('Access-Control-Allow-Origin', '*');
      h.delete('set-cookie');
      return new Response(r.body, { status: r.status, headers: h });
    } catch {
      return new Response('', { status: 502 });
    }
  },
};
