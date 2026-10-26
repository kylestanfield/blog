import { mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const title = process.argv.slice(2).join(' ').trim();
const slug = title.normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
  .toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const reserved = new Set(['index', '404', 'rss', 'ryu', 'drafts', 'japanese-news-dark-mode']);

if (!title || !slug || reserved.has(slug)) {
  console.error('Usage: npm run new -- "My Post Title" (choose a title with a unique, non-reserved URL)');
  process.exit(1);
}

const directory = new URL('../src/content/blog/drafts/', import.meta.url);
const file = new URL(`${slug}.md`, directory);
await mkdir(directory, { recursive: true });
const content = `---
title: ${JSON.stringify(title)}
pubDate: ${JSON.stringify(new Date().toISOString())}
description: ""
draft: true
---

Write your post here.
`;

try {
  await writeFile(file, content, { flag: 'wx' });
  console.log(`Created ${fileURLToPath(file)}`);
} catch (error) {
  if (error.code !== 'EEXIST') throw error;
  console.log(`Draft already exists: ${fileURLToPath(file)} (left unchanged)`);
}
console.log(`Edit this file in Vim or your preferred editor, then run npm run dev.
Preview: http://localhost:4321/drafts/${slug}/
Publish: set draft: false and move the file to src/content/blog/${slug}.md`);
