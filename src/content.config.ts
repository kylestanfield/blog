import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
  // Private drafts are never even loaded into the production content store.
  loader: glob({
    base: './src/content/blog',
    pattern: import.meta.env.DEV ? '**/*.md' : ['**/*.md', '!drafts/**'],
  }),
  schema: z.object({
    title: z.string(),
    pubDate: z.coerce.date(),
    author: z.string().default('Kyle Stanfield'),
    description: z.string().default(''),
    draft: z.boolean().default(false),
  }),
});

export const collections = { blog };
