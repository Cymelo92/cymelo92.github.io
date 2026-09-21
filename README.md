# Carlo Y. Meloni - personal academic website

This repository is a Quarto website intended for publication at:

https://cymelo92.github.io

The recommended workflow is to keep the repository private while developing the site locally, leave GitHub Pages disabled, and publish only when the site is ready.

## 1. Prerequisites

Install:

- Git
- Quarto
- a text editor or IDE (VS Code, Positron, RStudio, or another editor)

Check that the commands are available:

```bash
git --version
quarto --version
```

## 2. Create the GitHub repository

On GitHub, create a new repository under the `Cymelo92` account.

Repository name:

```text
cymelo92.github.io
```

Use lowercase letters in the repository name. Set the repository visibility to **Private** initially.

For the cleanest setup, create it without adding a README, `.gitignore`, or license, because this starter package already contains the relevant files.

Do not enable GitHub Pages yet.

## 3. Clone the empty private repository

Choose a directory on your computer and run:

```bash
git clone https://github.com/Cymelo92/cymelo92.github.io.git
cd cymelo92.github.io
```

If GitHub asks for authentication, use your normal GitHub credential method (for example GitHub CLI, a credential manager, or SSH).

## 4. Copy this starter into the repository

Copy all files from this starter package into the cloned `cymelo92.github.io` directory, including hidden files such as:

```text
.nojekyll
.gitignore
```

Do **not** copy a `.git/` directory from anywhere else.

The source tree should look approximately like this before the first render:

```text
cymelo92.github.io/
|-- .gitignore
|-- .nojekyll
|-- _quarto.yml
|-- 404.qmd
|-- README.md
|-- LAUNCH_CHECKLIST.md
|-- index.qmd
|-- research.qmd
|-- projects.qmd
|-- publications.qmd
|-- talks.qmd
|-- teaching.qmd
|-- cv.qmd
|-- references.bib
|-- styles.css
|-- files/
|   `-- Carlo_Meloni_CV.pdf
`-- images/
    `-- README.md
```

After rendering, Quarto will create a `docs/` directory containing the static site.

## 5. Preview the site locally

From the repository directory:

```bash
quarto preview
```

Quarto will render a local preview and show a local URL in the terminal. Keep that process running while editing the `.qmd` files; Quarto will normally refresh the preview when files change.

Stop the preview with `Ctrl+C`.

## 6. Edit the content

The main files are:

- `index.qmd`: homepage and contact information
- `research.qmd`: research profile and methods
- `projects.qmd`: current and past projects
- `publications.qmd`: publication list
- `talks.qmd`: invited talks and conference presentations
- `teaching.qmd`: teaching and academic service
- `cv.qmd`: short CV page and PDF download
- `styles.css`: visual styling
- `_quarto.yml`: site navigation and global settings
- `references.bib`: BibTeX metadata for future bibliography automation

The homepage currently uses the existing CALC Lab portrait as a remote image. See `images/README.md` if you prefer to store the photo in this repository.

## 7. Render the complete static site

Before committing a version you want to preserve, run:

```bash
quarto render
```

Because `_quarto.yml` contains:

```yaml
project:
  type: website
  output-dir: docs
```

Quarto will write the finished static website into `docs/`.

Confirm that this file exists:

```text
docs/index.html
```

The `docs/` directory should be committed to Git because GitHub Pages will later publish directly from it.

## 8. Commit the private draft

Check what Git sees:

```bash
git status
```

Then commit the source and rendered site:

```bash
git add .
git commit -m "Create personal academic website"
git push -u origin main
```

The repository can remain private throughout development.

At this stage, **do not enable GitHub Pages**. You can continue to preview the site locally with `quarto preview`.

## 9. Normal editing workflow while private

For each update:

```bash
quarto preview
```

Edit and inspect the site. When satisfied:

```bash
quarto render
git status
git add .
git commit -m "Update website"
git push
```

The private repository now acts as your remote backup and version history, but the website is not published.

## 10. Prepare for launch

Before changing the repository to public:

1. Review `LAUNCH_CHECKLIST.md`.
2. Run a full render:

```bash
quarto render
```

3. Verify that the PDF CV and all external links work.
4. Check `git status` for unexpected or sensitive files.
5. Commit and push the final draft.

Never commit passwords, API keys, private datasets, unpublished confidential material, or other secrets. Repository history can remain accessible after a file is deleted if it was previously committed.

## 11. Make the repository public

When ready to launch, open the repository on GitHub and go to:

```text
Settings > General > Danger Zone > Change repository visibility
```

Change the repository from **Private** to **Public** and follow GitHub's confirmation prompts.

For GitHub Free, GitHub Pages is available for public repositories. Paid plans can support Pages from private repositories, but a Pages site is generally public once published unless you are using an offering that specifically supports access-controlled Pages.

## 12. Enable GitHub Pages

After the repository is public, go to:

```text
Settings > Pages
```

Under **Build and deployment** choose:

```text
Source: Deploy from a branch
Branch: main
Folder: /docs
```

Save the setting.

GitHub will deploy the files from the `docs/` directory. After deployment, the site should be available at:

```text
https://cymelo92.github.io
```

The first deployment can take a short time. The Pages settings screen will show the deployment status and site URL.

## 13. Updating the live site

After launch, the routine is:

```bash
quarto preview
```

Make your changes, then:

```bash
quarto render
git add .
git commit -m "Update publications"
git push
```

Because GitHub Pages is configured to publish `main/docs`, each push containing updated files in `docs/` will update the live website.

## 14. Updating the CV

Replace:

```text
files/Carlo_Meloni_CV.pdf
```

with the new PDF, keeping the same filename. Then run:

```bash
quarto render
git add .
git commit -m "Update CV"
git push
```

Keeping the filename stable means the website's CV link does not need to change.

## 15. Optional improvements later

Once the basic site is stable, useful extensions include:

- automate publications from BibTeX
- add a news or blog section
- add project-specific code and data links
- add publication abstracts and BibTeX download buttons
- use a custom domain
- switch deployment from committed `docs/` output to a GitHub Actions workflow
- add privacy-respecting analytics if you actually need them

For the initial launch, the current `main` + `docs/` workflow is deliberately simple and easy to debug.
