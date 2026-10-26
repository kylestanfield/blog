import assert from 'node:assert/strict';
import { readFile, readdir, stat } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../dist/', import.meta.url));
async function filesIn(directory) {
  const result = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const file = path.join(directory, entry.name);
    result.push(...(entry.isDirectory() ? await filesIn(file) : [file]));
  }
  return result;
}

const files = await filesIn(root);
const htmlFiles = files.filter((file) => file.endsWith('.html'));
const site = new URL('https://kylestanfield.com');
for (const page of [
  'index.html', '1/index.html', '2/index.html', 'ryu/privacy-policy/index.html',
  'japanese-news-dark-mode/support/index.html', 'japanese-news-dark-mode/privacy/index.html',
]) {
  assert(files.includes(path.join(root, page)), `Missing historical page: ${page}`);
}

for (const file of htmlFiles) {
  const html = await readFile(file, 'utf8');
  assert(!/\{[%{]/.test(html), `Unconverted template syntax in ${file}`);
  assert(!/Draft \(local preview only\)|noindex, nofollow|\/drafts\//.test(html), `Draft leaked into ${file}`);
  const pageUrl = new URL(path.relative(root, file).replace(/index\.html$/, ''), site);
  for (const [, attribute] of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
    const url = new URL(attribute.replaceAll('&amp;', '&'), pageUrl);
    if (url.origin !== site.origin) continue;
    const pathname = decodeURIComponent(url.pathname);
    const target = path.join(root, pathname.endsWith('/') ? `${pathname}index.html` : pathname);
    assert(await stat(target).then((info) => info.isFile()).catch(() => false),
      `Broken local link in ${path.relative(root, file)}: ${attribute}`);
  }
}

assert(!files.some((file) => /\.(sqlite|py|md)$/.test(file)), 'Private source files leaked into output');
assert(!files.some((file) => path.relative(root, file).split(path.sep).includes('drafts')), 'Draft directory leaked into output');
const first = await readFile(path.join(root, '1/index.html'), 'utf8');
const contest = await readFile(path.join(root, '2/index.html'), 'utf8');
assert(first.includes('/static/images/gecko.jpg'), 'Historical post image is missing');
assert(first.includes('June 09, 2025') && contest.includes('July 11, 2025'), 'Publication dates changed');
assert(contest.includes('<details>') && contest.includes('<summary>Python Code</summary>'), 'Expandable code section is missing');
const codeBlocks = [...contest.matchAll(/<details>[\s\S]*?<\/details>/g)];
assert.equal(codeBlocks.length, 4, 'Expected four expandable solutions');
for (const [block] of codeBlocks) {
  assert(/<pre[^>]*class="[^"]*astro-code/.test(block), 'A solution is missing highlighted code');
  assert(!block.includes('```'), 'A solution still contains unrendered Markdown fences');
}
for (const number of [1, 2, 3, 4]) {
  assert(new RegExp(`<h3[^>]*>Question ${number}:`).test(contest), `Question ${number} is not a heading`);
}
const feed = await readFile(path.join(root, 'rss.xml'), 'utf8');
assert(feed.includes('https://kylestanfield.com/1/') && feed.includes('https://kylestanfield.com/2/'), 'RSS omits historical posts');
assert(!feed.includes('/drafts/'), 'Draft leaked into RSS');
console.log(`Verified ${htmlFiles.length} HTML pages, all local links/assets, historical content, RSS, and draft exclusion.`);
