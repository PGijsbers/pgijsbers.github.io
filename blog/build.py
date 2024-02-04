import argparse
import logging
import re
from pathlib import Path
import argparse
from typing import NamedTuple
from string import Template
import markdown

logger = logging.getLogger(__file__)

class Post(NamedTuple):
    title: str
    tags: list[str]
    content: str

    @property
    def url(self):
        # TODO: Sanitize title for safe url
        return f"/{self.title}.html"

# - generated html for blogposts
# - generated index page
# - generated next/previous
# - tagging
# - published / last edit
# - interpost-links

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="posts",
        type=Path,
        help="Path to a file or directory. If a directory is provided, all markdown files in the directory are converted."
    )
    parser.add_argument(
        "--output",
        default="generated",
        type=Path,
        help="Directory to write the generated files to.",
    )
    parser.add_argument(
        "--template-directory",
        default="templates",
        type=Path,
        help="Path to directory with templates for `index.html` and `post.html`",
    )

    return parser.parse_args()


def generate_index_html(template: str, posts: list[Post]) -> str:
    index = [f"<li><a href=\"{post.url}\">{post.title}</a></li>" for post in posts]
    return Template(template).substitute(
        POSTS='\n'.join(index)
    )


def generate_post_html(template: str, post: Post, prev: Post | None = None, next_: Post | None = None) -> str:
    content_html = markdown.markdown(post.content)
    prev_link = f"<a href=\"{prev.url}\">prev</a>" if prev else ""
    next_link = f"<a href=\"{next_.url}\">next</a>" if next_ else ""
    return Template(template).substitute(
        TITLE=post.title,
        TAGS=", ".join(post.tags),
        POST=content_html,
        NAV=prev_link+next_link,
    )


def parse_post(post: str) -> Post:
    header, content = post.split("---\n")

    if match := re.search(r"title: ([^\n]*)\n", header):
        (title,) = match.groups()
    else:
        title = "Unknown Title"

    logger.debug(f"Found title '{title}'.")

    if match := re.search(r"tags: ([^\n]*)\n", header):
        (tags,) = match.groups()
        tags = tags.split(", ")
    else:
        tags = []

    logger.debug(f"Found tags: '{tags}'")

    return Post(title, tags, content)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    args = parse_args()
    posts = [parse_post(post.read_text()) for post in Path(args.input).rglob("*.md")]
    index_template = (args.template_directory / "index.html").read_text()
    index_html = generate_index_html(index_template, posts)
    (args.output / "index.html").write_text(index_html)

    post_template = (args.template_directory / "post.html").read_text()
    for prev_post, post, next_post in zip([None] + posts, posts, posts[1:] + [None]):
        post_html = generate_post_html(
            post_template,
            post,
            prev_post,
            next_post,
        )
        (args.output / post.url[1:]).write_text(post_html)
