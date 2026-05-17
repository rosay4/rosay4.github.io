from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "posts"
CONTENT_DIR = ROOT / "content"
ARCHIVE_DIR = ROOT / "archive"


@dataclass
class Heading:
    level: int
    text: str
    slug: str


@dataclass
class Post:
    slug: str
    title: str
    date: str
    author: str
    description: str
    summary: str
    body_html: str
    headings: list[Heading]


@dataclass
class Page:
    path: str
    title: str
    description: str
    intro_title: str
    intro_text: str
    rail_one_label: str
    rail_one_text: str
    rail_two_label: str
    rail_two_text: str
    body_html: str


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    metadata: dict[str, str] = {}
    end_index = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_index = i
            break
        if ":" in lines[i]:
            key, value = lines[i].split(":", 1)
            metadata[key.strip()] = value.strip()

    if end_index is None:
        return {}, text

    return metadata, "\n".join(lines[end_index + 1 :]).strip()


GITHUB_SVG = '<svg class="icon" viewBox="0 0 16 16" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8a8 8 0 0 0 5.47 7.59c.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.63 7.63 0 0 1 4 0c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg>'
EMAIL_SVG = '<svg class="icon" viewBox="0 0 16 16" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M1.75 2h12.5c.966 0 1.75.784 1.75 1.75v8.5A1.75 1.75 0 0 1 14.25 14H1.75A1.75 1.75 0 0 1 0 12.25v-8.5C0 2.784.784 2 1.75 2ZM1.5 12.251c0 .138.112.25.25.25h12.5a.25.25 0 0 0 .25-.25V5.809L8.38 9.397a.75.75 0 0 1-.76 0L1.5 5.809v6.442Zm13-8.181v-.32a.25.25 0 0 0-.25-.25H1.75a.25.25 0 0 0-.25.25v.32L8 7.88Z"/></svg>'


def render_inline(text: str) -> str:
    escaped = escape(text)
    escaped = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        lambda m: f'<img src="{escape(m.group(2), quote=True)}" alt="{escape(m.group(1), quote=True)}">',
        escaped,
    )
    escaped = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: (
            f'<a href="{escape(m.group(2), quote=True)}" aria-label="{escape(m.group(1), quote=True)}">{GITHUB_SVG}</a>'
            if m.group(2).startswith("https://github.com/")
            else f'<a href="{escape(m.group(2), quote=True)}">{m.group(1)}</a>'
        ),
        escaped,
    )
    escaped = re.sub(
        r"([\w.+-]+@[\w-]+\.[\w.-]+)",
        lambda m: f'<a href="mailto:{m.group(1)}" aria-label="Email">{EMAIL_SVG}</a>',
        escaped,
    )
    escaped = re.sub(r"`([^`]+)`", lambda m: f"<code>{m.group(1)}</code>", escaped)
    return escaped


def markdown_to_html(markdown: str) -> tuple[str, list[Heading]]:
    lines = markdown.splitlines()
    html_parts: list[str] = []
    headings: list[Heading] = []
    paragraph_buffer: list[str] = []
    list_items: list[str] = []
    ordered_list_items: list[str] = []
    quote_lines: list[str] = []
    code_lines: list[str] = []
    code_lang = ""
    in_code_block = False

    def flush_paragraph() -> None:
        nonlocal paragraph_buffer
        if not paragraph_buffer:
            return
        content = " ".join(line.strip() for line in paragraph_buffer).strip()
        if content:
            html_parts.append(f"<p>{render_inline(content)}</p>")
        paragraph_buffer = []

    def flush_list() -> None:
        nonlocal list_items
        if not list_items:
            return
        items = "".join(f"<li>{render_inline(item)}</li>" for item in list_items)
        html_parts.append(f"<ul>{items}</ul>")
        list_items = []

    def flush_ordered_list() -> None:
        nonlocal ordered_list_items
        if not ordered_list_items:
            return
        items = "".join(f"<li>{render_inline(item)}</li>" for item in ordered_list_items)
        html_parts.append(f"<ol>{items}</ol>")
        ordered_list_items = []

    def flush_quote() -> None:
        nonlocal quote_lines
        if not quote_lines:
            return
        content = " ".join(line.strip() for line in quote_lines).strip()
        html_parts.append(f"<blockquote><p>{render_inline(content)}</p></blockquote>")
        quote_lines = []

    def flush_code() -> None:
        nonlocal code_lines, code_lang
        if not code_lines and not code_lang:
            return
        class_attr = f' class="language-{escape(code_lang, quote=True)}"' if code_lang else ""
        content = "\n".join(code_lines)
        html_parts.append(f"<pre><code{class_attr}>{escape(content)}</code></pre>")
        code_lines = []
        code_lang = ""

    for line in lines:
        stripped = line.rstrip()

        if stripped.strip().startswith("```"):
            flush_paragraph()
            flush_list()
            flush_ordered_list()
            flush_quote()
            if in_code_block:
                flush_code()
                in_code_block = False
            else:
                in_code_block = True
                code_lang = stripped.strip()[3:].strip()
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        clean = stripped.strip()
        if not clean:
            flush_paragraph()
            flush_list()
            flush_ordered_list()
            flush_quote()
            continue

        if clean.startswith("> "):
            flush_paragraph()
            flush_list()
            flush_ordered_list()
            quote_lines.append(clean[2:])
            continue

        unordered = re.match(r"^[-*]\s+(.+)$", clean)
        if unordered:
            flush_paragraph()
            flush_ordered_list()
            flush_quote()
            list_items.append(unordered.group(1))
            continue

        ordered = re.match(r"^\d+\.\s+(.+)$", clean)
        if ordered:
            flush_paragraph()
            flush_list()
            flush_quote()
            ordered_list_items.append(ordered.group(1))
            continue

        if clean.startswith("### "):
            flush_paragraph()
            flush_list()
            flush_ordered_list()
            flush_quote()
            text = clean[4:].strip()
            slug = slugify(text)
            headings.append(Heading(3, text, slug))
            html_parts.append(f'<h3 id="{slug}">{render_inline(text)}</h3>')
            continue

        if clean.startswith("## "):
            flush_paragraph()
            flush_list()
            flush_ordered_list()
            flush_quote()
            text = clean[3:].strip()
            slug = slugify(text)
            headings.append(Heading(2, text, slug))
            html_parts.append(f'<h2 id="{slug}">{render_inline(text)}</h2>')
            continue

        if clean.startswith("# "):
            flush_paragraph()
            flush_list()
            flush_ordered_list()
            flush_quote()
            text = clean[2:].strip()
            slug = slugify(text)
            headings.append(Heading(1, text, slug))
            html_parts.append(f'<h1 id="{slug}">{render_inline(text)}</h1>')
            continue

        paragraph_buffer.append(clean)

    flush_paragraph()
    flush_list()
    flush_ordered_list()
    flush_quote()
    if in_code_block:
        flush_code()

    return "\n          ".join(html_parts), headings


def load_posts() -> list[Post]:
    posts: list[Post] = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        metadata, markdown = parse_frontmatter(path.read_text(encoding="utf-8"))
        body_html, headings = markdown_to_html(markdown)
        posts.append(
            Post(
                slug=path.stem,
                title=metadata.get("title", path.stem.replace("-", " ").title()),
                date=metadata.get("date", ""),
                author=metadata.get("author", "Roselyn Chen"),
                description=metadata.get("description", ""),
                summary=metadata.get("summary", ""),
                body_html=body_html,
                headings=headings,
            )
        )
    return posts


def load_page(name: str) -> Page:
    metadata, markdown = parse_frontmatter((CONTENT_DIR / f"{name}.md").read_text(encoding="utf-8"))
    body_html, _ = markdown_to_html(markdown)
    return Page(
        path=metadata.get("path", "./"),
        title=metadata.get("title", "Roselyn Chen"),
        description=metadata.get("description", ""),
        intro_title=metadata.get("intro_title", ""),
        intro_text=metadata.get("intro_text", ""),
        rail_one_label=metadata.get("rail_one_label", ""),
        rail_one_text=metadata.get("rail_one_text", ""),
        rail_two_label=metadata.get("rail_two_label", ""),
        rail_two_text=metadata.get("rail_two_text", ""),
        body_html=body_html,
    )


def render_toc(post: Post) -> str:
    lines = []
    for heading in post.headings:
        klass = ' class="tm-toc-child"' if heading.level == 3 else ""
        lines.append(f'        <a{klass} href="#{heading.slug}">{escape(heading.text)}</a>')
    return "\n".join(lines)


def render_post(post: Post) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Roselyn Chen | Article</title>
  <meta
    name="description"
    content="{escape(post.description)}"
  >
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link
    href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap"
    rel="stylesheet"
  >
  <link rel="stylesheet" href="../../styles.css">
</head>
<body>
  <div class="page page-article-ref">
    <header class="tm-header">
      <div class="tm-header-left">
        <a class="tm-wordmark" href="../../">Roselyn Chen</a>
      </div>
      <nav class="tm-top-nav" aria-label="Primary">
        <a href="../../">Home</a>
        <a href="../../about/">About</a>
        <a href="../" aria-current="page">Archive</a>
      </nav>
    </header>

    <main class="tm-main">
      <aside class="tm-toc" aria-label="On this page">
{render_toc(post)}
      </aside>

      <article class="tm-content">
        <header class="tm-hero tm-hero-centered">
          <p class="tm-kicker">Archive</p>
          <h1 class="tm-title-highlight">{escape(post.title)}</h1>
          <div class="tm-publish-metadata">
            <span>{escape(post.author)}</span>
            <span>{escape(post.date)}</span>
          </div>
        </header>

        <section class="tm-article-body">
          {post.body_html}
        </section>
      </article>
    </main>
  </div>
</body>
</html>
"""


def render_archive(posts: list[Post]) -> str:
    items = []
    for post in posts:
        items.append(
            f"""          <article class="tm-list-item">
            <h3><a href="./{post.slug}/">{escape(post.title)}</a></h3>
            <p>{escape(post.summary or post.description)}</p>
          </article>"""
        )

    list_html = "\n\n".join(items)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Roselyn Chen | Archive</title>
  <meta
    name="description"
    content="Archive for future writing, project notes, and technical posts generated from markdown."
  >
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link
    href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap"
    rel="stylesheet"
  >
  <link rel="stylesheet" href="../styles.css">
</head>
<body>
  <div class="page page-article-ref">
    <header class="tm-header">
      <div class="tm-header-left">
        <a class="tm-wordmark" href="../">Roselyn Chen</a>
      </div>
      <nav class="tm-top-nav" aria-label="Primary">
        <a href="../">Home</a>
        <a href="../about/">About</a>
        <a href="./" aria-current="page">Archive</a>
      </nav>
    </header>

    <main class="tm-main">
      <aside class="tm-toc" aria-label="On this page">
        <a href="#archive-top">Introduction</a>
        <a href="#selected-posts">Selected posts</a>
      </aside>

      <div class="tm-content">
        <section id="archive-top" class="tm-hero">
          <p class="tm-kicker">Archive</p>
          <h1>Writing archive for future technical posts and project notes.</h1>
          <div class="tm-meta">
            <span>Roselyn Chen</span>
            <span>May 2026</span>
          </div>
          <p class="tm-intro">
            This page is generated from markdown source files. Future writing on robotics, reinforcement learning, simulation, testing workflows, and project retrospectives will appear here.
          </p>
        </section>

        <section id="selected-posts" class="tm-article-body tm-archive-list">
          <h2>Selected posts</h2>
{list_html}
        </section>
      </div>
    </main>
  </div>
</body>
</html>
"""


def render_page(page: Page, nav_key: str) -> str:
    home_current = ' aria-current="page"' if nav_key == "home" else ""
    about_current = ' aria-current="page"' if nav_key == "about" else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(page.title)}</title>
  <meta
    name="description"
    content="{escape(page.description)}"
  >
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link
    href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap"
    rel="stylesheet"
  >
  <link rel="stylesheet" href="{page.path}styles.css">
</head>
<body>
  <div class="page">
    <header class="site-header">
      <a class="brand" href="{page.path}">Roselyn Chen</a>
      <nav class="site-nav" aria-label="Primary">
        <a href="{page.path}"{home_current}>Home</a>
        <a href="{page.path}about/"{about_current}>About</a>
        <a href="{page.path}archive/">Archive</a>
      </nav>
    </header>

    <main class="layout home-layout">
      <aside class="side-rail">
        <section class="rail-block">
          <p class="rail-label">{escape(page.rail_one_label)}</p>
          <p class="rail-copy">{render_inline(page.rail_one_text)}</p>
        </section>

        <section class="rail-block">
          <p class="rail-label">{escape(page.rail_two_label)}</p>
          <p class="rail-copy">{render_inline(page.rail_two_text)}</p>
        </section>
      </aside>

      <div class="content">
        <section class="home-intro">
          <p class="eyebrow">{'Home' if nav_key == 'home' else 'About'}</p>
          <h1>{escape(page.intro_title)}</h1>
          <p class="intro-lead">{render_inline(page.intro_text)}</p>
        </section>

        <section class="tm-article-body page-markdown-body">
          {page.body_html}
        </section>
      </div>
    </main>
  </div>
</body>
</html>
"""


def main() -> None:
    posts = load_posts()
    ARCHIVE_DIR.mkdir(exist_ok=True)
    (ARCHIVE_DIR / "index.html").write_text(render_archive(posts), encoding="utf-8")

    for post in posts:
        post_dir = ARCHIVE_DIR / post.slug
        post_dir.mkdir(parents=True, exist_ok=True)
        (post_dir / "index.html").write_text(render_post(post), encoding="utf-8")

    home_page = load_page("home")
    about_page = load_page("about")
    ROOT.joinpath("index.html").write_text(render_page(home_page, "home"), encoding="utf-8")
    ROOT.joinpath("about", "index.html").write_text(render_page(about_page, "about"), encoding="utf-8")


if __name__ == "__main__":
    main()
