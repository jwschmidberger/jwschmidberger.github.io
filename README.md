# Personal Site

Jekyll 4 site for showcasing data-science projects, writing, and CV. The repo is GitHub Pages–ready thanks to a lightweight Gemfile and the official Cayman remote theme.

## Prerequisites
- Ruby 3.x (via rbenv, rvm, or your system Ruby)
- Bundler 2.x — `gem install bundler`

## Setup
```bash
bundle config set --local path vendor/bundle # optional
bundle install
```

## Local development
```bash
bundle exec jekyll serve --livereload
```
The site will be served at http://localhost:4000. Changes to Markdown and Sass under `_sass/custom.scss` hot-reload automatically.

## Structure
- `index.md` – landing page content.
- `_posts/` – Markdown posts rendered in chronological order and surfaced on `/blog`.
- `_projects/` – custom collection powering `/projects` (each file becomes a standalone case study).
- `blog/`, `projects/`, `cv.md` – navigation pages rendered with the remote theme’s default layout.
- `pdfs/`, `images/` – static assets linked from the content.

## Deployment
Push to `main` (or whichever branch GitHub Pages monitors). GitHub will run the Pages build using this Gemfile. For pull request previews or custom build steps, add the official [pages-build-deployment GitHub Action](https://github.com/actions/starter-workflows/blob/main/pages/jekyll.yml).
