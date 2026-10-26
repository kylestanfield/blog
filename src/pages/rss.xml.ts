import rss from '@astrojs/rss';
import type { APIContext } from 'astro';
import { getPosts, isDraft, postUrl } from '../lib/posts';

export async function GET(context: APIContext) {
  const posts = (await getPosts()).filter((post) => !isDraft(post));
  return rss({
    title: "Kyle's Blog",
    description: 'Thoughts on networking, tech, and movies.',
    site: context.site!,
    items: posts.map((post) => ({
      title: post.data.title,
      pubDate: post.data.pubDate,
      description: post.data.description,
      link: postUrl(post),
    })),
  });
}
