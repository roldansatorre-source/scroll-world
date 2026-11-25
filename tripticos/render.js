// node render.js name  -> name.pdf + name-exterior.png + name-interior.png
const { chromium } = require('playwright');
(async () => {
  const name = process.argv[2], b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1145, height: 816 }, deviceScaleFactor: 2 });
  await p.goto('file://' + process.cwd() + '/' + name + '.html', { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: name + '.pdf', width: '303mm', height: '216mm', printBackground: true, preferCSSPageSize: true });
  const sheets = await p.$$('.sheet');
  await sheets[0].screenshot({ path: name + '-exterior.png' });
  await sheets[1].screenshot({ path: name + '-interior.png' });
  console.log(await p.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight).join(', ')));
  await b.close();
})();
