import { defineConfig } from 'astro/config';
import { satteri } from '@astrojs/markdown-satteri';

export default defineConfig({
  site: 'https://kylestanfield.com',
  output: 'static',
  trailingSlash: 'always',
  build: { format: 'directory' },
  markdown: {
    processor: satteri({ features: { smartPunctuation: false } }),
    shikiConfig: { theme: 'github-light' },
  },
});
