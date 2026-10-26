# Kyle's Blog

A static Astro blog deployed to S3 and CloudFront at https://kylestanfield.com.

## Develop

Use Node 24 LTS (`nvm use` if you use nvm).

```sh
npm ci
npm run dev
```

Open http://localhost:4321. Saving Markdown or a template refreshes the preview.

## Write a post

```sh
npm run new -- "My Post Title"
```

This creates a private Markdown draft in `src/content/blog/drafts/` and prints
its file path and preview URL. Open the file in Vim or your preferred editor.
Drafts appear in development only. They are ignored by Git, excluded from the
production content store, and omitted from RSS.

When ready to publish:

1. Set `draft: false`, fill in `description`, and set `pubDate` to the intended
   publication date. Dates are displayed in UTC.
2. Move the file from `src/content/blog/drafts/` to `src/content/blog/`.
3. Run `npm run check` and `npm test`, then commit the Markdown and new images.
4. Push to `master` to run the existing S3/CloudFront deployment.

The filename determines the URL: `my-post.md` becomes `/my-post/`. Imported posts
retain `1.md` and `2.md`, preserving `/1/` and `/2/`. Keep filenames unique and use
lowercase letters, numbers, and hyphens. Avoid `index`, `404`, `rss`, `ryu`,
`drafts`, and `japanese-news-dark-mode`.

To keep an unpublished draft in Git, place it directly in `src/content/blog/`
with `draft: true`; it will still be excluded from production pages and RSS.
Markdown headings, fenced code blocks, and inline HTML are supported. Put images
in `public/static/images/` and embed them using the existing URL format:

```md
![Description of the image](/static/images/your-image.jpg)
```

## Build and preview production

```sh
npm run check
npm test
npm run preview
```

Output is `dist/`, with directory index files matching the previous S3 object
paths. Tests check historical URLs, local links/assets, code rendering, RSS,
and draft exclusion. Google Analytics runs in production builds only.

GitHub Actions builds with Node 24, checks the output, syncs `dist/` to the
existing S3 bucket, and invalidates the existing CloudFront distribution.
Hosting and AWS secret names are unchanged. Deployment happens when pushed.

## Migration backup

`legacy/flask/` preserves the Python app, templates, assets, and writing script,
including local edits present at migration time. The original `blog.sqlite` and
ignored root `drafts/` remain untouched for recovery. Neither is read by Astro
or uploaded to S3. The existing local draft has also been copied into Astro's
private draft directory for previewing.

The two published Markdown bodies were exported from SQLite without rewriting
their prose or code. Line endings and blank lines around HTML details blocks
were normalized so all four solutions render correctly. Support and privacy pages keep
their original text and URLs. New posts no longer use SQLite or require Python.
