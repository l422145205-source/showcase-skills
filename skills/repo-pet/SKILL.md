---
name: repo-pet
description: Create an animated pixel pet for a repository README from real local JUnit or GitHub workflow evidence. Use for README pets, CI mascots, playful repo badges, mood galleries, or previewing a repo pet before publishing.
---

# RepoPet

Give the repository an original pixel dragon named Patch, with GIF/PNG assets and a small evidence snapshot. Match the requested look and keep setup lightweight. The renderer is `scripts/repopet.py`, relative to this skill directory.

## Make the pet

1. Use an available Python 3.10+ environment with Pillow 10.1+. If missing, install Pillow in a project-local virtual environment; do not modify a system environment. No model, account, network API or GPU is needed for rendering.
2. Read an existing JUnit file or workflow-result JSON when provided. With no explicit file, the renderer checks only `junit.xml`, `test-results.xml`, and `reports/junit.xml` in the target repository. It does not run tests or traverse the user's other folders.
3. Render and visually inspect the result. Default name: Patch; palettes: mint/lilac/peach. Default stage is auto: egg for 0–2 reachable commits, baby for 3–24, dragon for 25+. When Git is unavailable the look defaults to baby, and the commit count stays unknown. Choosing a stage manually changes the look, not the evidence.

```bash
python <skill-dir>/scripts/repopet.py render --repo <repo> --junit <report.xml> --out <repo>/assets/repopet
```

To put the image in the README when that is part of the user's request, add `--readme <repo>/README.md`. The script replaces only the `repopet:start` / `repopet:end` block, or appends a new block. Ambiguous existing markers stop the README edit.

For a look preview, use:

```bash
python <skill-dir>/scripts/repopet.py demo --out <preview-directory>
```

Demo assets are labeled **DEMO DATA** and are not measurements of the user's repository. For a different look, add `--theme lilac` or `--stage dragon` to `render`.

## Keep the mood honest

Read [references/evidence.md](references/evidence.md) for unusual inputs or CI adapters. Missing, malformed or empty test evidence produces unknown; an all-skipped suite produces skipped. Workflow success says CI success, not a made-up number of tests. The card keeps that distinction visible.

Use the bundled renderer for its pixel geometry and animations. Do not download arbitrary character art or add unrelated build tools. The helper collects only aggregate Git/test facts, not author names, emails, remotes, source code or local report paths in the output snapshot.

## Deliver

Show the actual GIF/PNG and its output location, describe where the status came from, and provide the README embed if requested. Check that the image remains readable at README size. Keep generated files inside the chosen output folder.

Git commits/pushes, GitHub Actions write permissions, repository settings and public uploads are separate actions: perform them only when the user has authorized that scope. A request for a local pet preview does not authorize publishing it.
