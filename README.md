# Everyday Agent Skills

Practical Skills for the tasks people actually give an Agent. **Start with PetLife: real pets, real receipts, less scattered care information.**

[中文](README.zh-CN.md) · [PetLife Skill](skills/pet-life/SKILL.md) · [Worked example](examples/pet-life/agent-example.md)

## PetLife · Let your Agent handle the pet paperwork

> “Here are food labels, receipts and our routine. How long will the food last for both cats? What did I spend this month? Prepare a three-day sitter handoff.”

The Agent reads the supplied material, matches pets and products, reconciles records, calls a small arithmetic helper, and writes a useful answer. The Skill supplies the workflow, record format, unit rules and local helper. **You use it inside your existing Agent.** Image reading depends on the host Agent; the helper does not bundle OCR.

```sh
npx skills add l422145205-source/showcase-skills --skill pet-life
```

Then ask:

> Use `$pet-life` to organize these real-pet records, check our food supply, and prepare a sitter card. Keep unclear receipt values unknown.

| You bring | Your Agent can deliver |
| --- | --- |
| Food labels + actual paid prices | Consistent price/unit and label-calorie comparisons |
| A stock count + recorded use + the existing routine | Shared household stock coverage, with per-pet quantities |
| Receipts, including repeated uploads | Deduplicated spending and a pet-life monthly brief |
| Feeding times, quirks and travel dates | A sitter handoff and packing quantities, with missing essentials visible |

### A tiny example, with actual calculation outputs

Two fictional cats, one shared bag, a duplicated receipt, an unclear purchase and a future record:

- **CNY 209** recorded spending in the example period; the repeated receipt counts once.
- **25.7 days** of dry-food coverage and **7 days** of wet-food coverage, based on the supplied book stock and daily routine.
- **CNY 13.22/day** projected from the latest receipt prices, kept separate from actual cash spending.
- A **three-day handoff draft** with separate pet quantities; missing emergency arrangements are not invented.

[Read the synthetic source packet and worked conversation →](examples/pet-life/agent-example.md)  
[Open the generated brief](examples/pet-life/brief.md) · [Sitter card](examples/pet-life/care-card.md)

### Lightweight by design

Python 3.10+; the PetLife helper uses **only the standard library**. No additional model service, database or web app. The host Agent supplies reasoning and any image understanding.

```sh
python skills/pet-life/scripts/petlife.py build --input skills/pet-life/assets/household.example.json --as-of 2026-10-03 --trip-days 3 --out work/pet-life-demo
```

Records stay in the selected workspace. The helper makes no network calls and never edits the input file or sends a sitter card. Ambiguous units, conflicting receipt IDs and mixed currencies are surfaced rather than guessed. It uses the owner's current quantities for bookkeeping; it does not prescribe diets or medication. [Format and calculation rules](skills/pet-life/references/record-format.md) · [Label sources](skills/pet-life/references/labels-and-care.md)

Want it to handle a particular real-life pet chore? Open an Issue with a **redacted or synthetic** example. If it saves you some paperwork, a Star helps the next pet owner find it.

## Also kept in this repository

The earlier RepoPet README mascot Skill and its demo remain available below. PetLife is the practical real-pet Skill described above.

<details>
<summary>RepoPet — animated repository mascot (earlier project)</summary>

<p align="center">
  <img src="examples/repopet-hero.gif" alt="RepoPet: an animated pixel dragon reacts to passing, failing, running, skipped and unknown test signals" width="100%">
</p>

# RepoPet · Your repo has feelings.

**Give your README a tiny dragon. Let your test results decide its mood.**

[Try the playground](https://l422145205-source.github.io/showcase-skills/) · [中文介绍](README.zh-CN.md) · [The Skill](skills/repo-pet/SKILL.md) · [Evidence & CI recipe](skills/repo-pet/references/evidence.md)

Patch celebrates green checks, throws a tiny tantrum when tests break, and takes a nap when everything is skipped. Original animated pixel art, rendered locally with Python. **No model, API key, or account required to render.**

## Adopt Patch

Install with the [Skills CLI](https://www.skills.sh/docs/cli):

```sh
npx skills add l422145205-source/showcase-skills --skill repo-pet
```

Then ask your agent:

> Use `$repo-pet` to give this repository a mint dragon named Patch. Use my existing JUnit report and add the GIF to README.md.

The agent locates this Skill's helper, checks Pillow, renders the GIF and updates only a marked README block. The renderer also works on its own:

```sh
git clone https://github.com/l422145205-source/showcase-skills.git
cd showcase-skills
python -m venv .venv
# Activate .venv with the command for your shell, then:
python -m pip install -r requirements.txt
python skills/repo-pet/scripts/repopet.py demo --out repopet-demo
```

Open `repopet-demo/passing/pet.gif`. Already have a report? Render a pet for your own project:

```sh
python skills/repo-pet/scripts/repopet.py render \
  --repo ../your-project --junit ../your-project/junit.xml \
  --out ../your-project/assets/repopet --readme ../your-project/README.md
```

The standalone commands require **Python 3.10+ and Pillow 10.1+**. `render` does not call an AI model. `npx skills add` needs Node.js; it is optional for the standalone renderer. Shell continuation syntax above is for bash; use one line in PowerShell.

## Five moods. One small dragon.

| All green. Snack time. | Build broken. Still cute. | Hold on. Dragon at work. |
| :---: | :---: | :---: |
| ![Passing preview](examples/gallery/passing/pet.gif) | ![Failing preview](examples/gallery/failing/pet.gif) | ![Running preview](examples/gallery/running/pet.gif) |

These are **labeled synthetic previews**, not this repository's CI. [Play with all five moods →](https://l422145205-source.github.io/showcase-skills/)

| Input signal | Patch's reaction |
| --- | --- |
| JUnit records executed passes with no failures/errors | Happy dance |
| Any recorded failure/error, or failed workflow | Tiny tantrum |
| Workflow queued or in progress | Busy dragon |
| All test cases skipped, or workflow explicitly skipped | Nap time |
| Missing/invalid report, cancelled/neutral workflow, no individual cases | Just vibes; status unknown |

A successful workflow is labeled **CI evidence**, not a fabricated test count. A missing report never becomes a passing badge. Images are snapshots; rerun the command to refresh them. [Full input rules and CI integration →](skills/repo-pet/references/evidence.md)

## Grow your dragon

![Egg, baby and dragon evolution stages](examples/evolution.png)

Reachable local commits unlock **egg (0–2) → baby (3–24) → dragon (25+)**. This is cosmetic, not a contribution score. Shallow clones count only available history; use full history if that matters. No Git repository? Patch starts as a baby.

```sh
python skills/repo-pet/scripts/repopet.py render --repo . --theme lilac --name Pixel --stage dragon
```

Choose **mint, lilac or peach**; select a stage manually when you just want the look. Demo previews use a baby. Git history and CI status are independent: an older dragon can still have a broken build.

## Small footprint, clear boundaries

- Reads a supplied JUnit XML/workflow JSON, plus a local aggregate commit count. No remote calls in the renderer.
- Exports `pet.gif`, `pet.png` and `status.json`. No author names, emails, commit messages, remote URLs or source paths enter these artifacts.
- Never runs tests, installs system packages, pushes commits or creates write-enabled workflows by itself.
- README editing is opt-in and confined to `<!-- repopet:start -->` / `<!-- repopet:end -->`.

You choose the pet name; use a public alias if you plan to publish its image. Skill installers have their own network/telemetry behavior; RepoPet does not change those settings.

## Make another little dragon

Requests for new expressions, palettes and original creature designs are welcome in [Issues](https://github.com/l422145205-source/showcase-skills/issues). If Patch makes your README more fun, a Star helps other people discover it.

Run the behavior checks with `python -m unittest discover -s tests -v`. Rebuild the gallery with `python scripts/build_showcase.py`.

MIT licensed. All dragon sprites in this repository are original code-drawn artwork.

</details>
