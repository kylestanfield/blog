#!/usr/bin/env python3
"""
new_post.py - Write a new blog post from the command line.

Usage:
  python new_post.py "My Post Title"   # create or resume a draft by title
  python new_post.py                   # list saved drafts and pick one

A local Flask server starts automatically so you get a live preview in your
browser using your blog's actual template. Save in vim (:w) then refresh the
browser tab to see changes. Quit vim (:q) when done.

Quitting vim does NOT publish — you'll be asked "Publish? [y/N]" first.
If you say no (or just hit Enter), the draft is saved in drafts/ for later.

After publishing, commit blog.sqlite and push to master to go live:
  git add blog.sqlite
  git commit -m "Add post: My Post Title"
  git push
"""

import os
import re
import subprocess
import sys
import time
import webbrowser

BLOG_DIR = os.path.dirname(os.path.abspath(__file__))
DRAFTS_DIR = os.path.join(BLOG_DIR, "drafts")
PREVIEW_PORT = 5001

DRAFT_HEADER = """\
# Instructions (delete before publishing)
# To embed an image: place it in static/images/ and write:
#   ![alt text](/static/images/your-image.jpg)
# Lines starting with # are comments — they will NOT appear in your post.
# When you're happy, quit vim (:q) and choose 'y' to publish.
# -----------------------------------------------------------------------

"""


def slugify(title):
    slug = title.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    return re.sub(r"-+", "-", slug).strip("-")


def list_drafts():
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    return sorted(f[:-3] for f in os.listdir(DRAFTS_DIR) if f.endswith(".md"))


def pick_title_and_slug():
    drafts = list_drafts()
    if not drafts:
        return input("Post title: ").strip(), None

    print("Saved drafts:")
    for i, slug in enumerate(drafts, 1):
        print(f"  {i}. {slug}")
    print("  n. New post")
    choice = input("Pick a number or 'n': ").strip().lower()

    if choice == "n" or choice == "":
        return input("Post title: ").strip(), None

    if choice.isdigit() and 1 <= int(choice) <= len(drafts):
        slug = drafts[int(choice) - 1]
        default_title = slug.replace("-", " ").title()
        title = input(f"Title [{default_title}]: ").strip() or default_title
        return title, slug

    print("Invalid choice.")
    sys.exit(1)


def strip_comments(text):
    lines = [l for l in text.splitlines() if not l.startswith("#")]
    return "\n".join(lines).strip()


def main():
    os.makedirs(DRAFTS_DIR, exist_ok=True)

    resume_slug = None
    if len(sys.argv) > 1:
        title = " ".join(sys.argv[1:])
    else:
        title, resume_slug = pick_title_and_slug()

    if not title:
        print("Error: title is required.")
        sys.exit(1)

    slug = resume_slug or slugify(title)
    draft_path = os.path.join(DRAFTS_DIR, f"{slug}.md")

    if not os.path.exists(draft_path):
        with open(draft_path, "w") as f:
            f.write(DRAFT_HEADER)

    # Start Flask dev server for live preview
    flask_env = {**os.environ, "FLASK_APP": "src", "FLASK_ENV": "development"}
    flask_proc = subprocess.Popen(
        [sys.executable, "-m", "flask", "run", "--port", str(PREVIEW_PORT), "--no-debugger", "--no-reload"],
        cwd=BLOG_DIR,
        env=flask_env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1.5)
    preview_url = f"http://localhost:{PREVIEW_PORT}/preview/{slug}"
    print(f"Preview: {preview_url}")
    webbrowser.open(preview_url)

    editor = os.environ.get("EDITOR", "vim")
    try:
        subprocess.run([editor, draft_path])
    finally:
        flask_proc.terminate()
        flask_proc.wait()

    with open(draft_path) as f:
        body = strip_comments(f.read())

    if not body:
        print(f"Draft is empty — saved to drafts/{slug}.md")
        sys.exit(0)

    answer = input(f"\nPublish '{title}'? [y/N] ").strip().lower()
    if answer != "y":
        print(f"Draft saved to drafts/{slug}.md")
        sys.exit(0)

    sys.path.insert(0, BLOG_DIR)
    import src
    from src.models import Post, User

    app = src.create_app()
    with app.app_context():
        db = app.extensions["db_manager"].get_database_session()
        user = db.query(User).first()
        if not user:
            print("Error: no users found in database.")
            sys.exit(1)
        post = Post(author_id=user.id, title=title, body=body)
        db.add(post)
        db.commit()
        print(f"Published: '{title}' (id={post.id})")

    os.unlink(draft_path)

    print(f"\nTo go live:")
    print(f"  git add blog.sqlite")
    print(f"  git commit -m 'Add post: {title}'")
    print(f"  git push")


if __name__ == "__main__":
    main()
