import { getCollection, type CollectionEntry } from 'astro:content';

export type Post = CollectionEntry<'blog'>;
export const isDraft = (post: Post) => post.data.draft || post.id.startsWith('drafts/');
export const postUrl = (post: Post) => `/${post.id}/`;

export async function getPosts() {
  const posts = await getCollection('blog', (post) => import.meta.env.DEV || !isDraft(post));
  return posts.sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());
}

export function formatDate(date: Date, short = false) {
  return date.toLocaleDateString('en-US', {
    month: short ? 'short' : 'long', day: '2-digit', year: 'numeric', timeZone: 'UTC',
  });
}
