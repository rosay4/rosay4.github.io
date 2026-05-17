# rosay4.github.io

Roselyn Chen 的个人网站，托管在 GitHub Pages。

## 结构

```text
.
├── index.html              # 主页（由 build 脚本生成）
├── styles.css              # 全局样式
├── content/
│   ├── home.md             # 主页内容源文件
│   └── about.md            # About 页面内容源文件
├── posts/
│   └── hello-world.md      # 博客文章（Markdown + frontmatter）
├── archive/
│   ├── index.html          # 归档总览（由 build 脚本生成）
│   └── <slug>/
│       └── index.html      # 单篇文章页（由 build 脚本生成）
├── about/
│   └── index.html          # About 页面（由 build 脚本生成）
├── scripts/
│   └── build_archive.py    # 静态站点生成脚本
└── .github/
    └── workflows/
        └── deploy-pages.yml  # GitHub Pages 自动部署
```

## 工作流

所有页面内容以 Markdown 编写，通过 `scripts/build_archive.py` 生成 HTML。

```bash
python scripts/build_archive.py
```

脚本会读取 `content/` 和 `posts/` 下的 `.md` 文件，生成对应的 HTML 页面。

提交时 pre-commit hook 会在 `.md` 文件有改动时自动重建 HTML 并加入暂存区。

## 页面

- **Home** — 个人概览、当前方向、联系方式
- **About** — 教育背景、项目经历、实习经验、技能
- **Archive** — 博客归档，从 `posts/*.md` 生成

## 设计方向

以 Thinking Machines 文章页风格为参考：白底、克制排版、细分隔线、接近研究出版物的气质。
