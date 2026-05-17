---
title: Designing a Personal Research Archive for Writing, Projects, and Technical Notes
date: May 17, 2026
author: Roselyn Chen
description: A publication-style article layout generated from markdown.
summary: Notes on using a publication-like archive for technical posts, project retrospectives, and future markdown-driven writing.
---

## Introduction

A personal archive should do more than store writing. It should create a stable reading environment for essays, project retrospectives, and technical notes, while remaining simple enough to maintain over time.

The goal of this layout is to provide that environment: a narrow reading column, restrained typography, centered title treatment, and a left-hand table of contents that follows the article structure automatically.

## Structure

The archive page and the article page serve different purposes. The archive should remain concise and scannable, while the article page should slow the reader down and give the text enough room to unfold without distraction.

That separation makes the site easier to extend. As new writing is added, the archive can stay readable at a glance, and each post can preserve a consistent article rhythm.

### Reading width

A narrow body column improves continuity in long-form technical writing. It reduces visual drift, keeps paragraphs legible, and makes section transitions feel more deliberate.

### Metadata

Author and date should be present, but quiet. They anchor the article without competing with the title or introducing the kind of noisy chrome more common in generic blog templates.

## Navigation

A useful article page should expose structure without requiring manual maintenance. The left sidebar in this layout is generated directly from the headings in the article, so the navigation always matches the content.

This also makes the page a better fit for a future markdown workflow, where headings written in source content can be converted into both article structure and in-page navigation automatically.

## Future workflow

If the site later adopts markdown as the primary writing format, the article content can still compile into this exact layout. A generator is helpful, but it is not necessary at this stage as long as the article structure remains predictable.

In practice, that means the writing flow can eventually become: write markdown, convert to HTML, inject it into this article shell, and regenerate the archive list from frontmatter metadata.
