---
name: generate-image
description: "Generate images from a text prompt using OpenAI's gpt-image-2 (default) or Google Gemini (Nano Banana) and open them in the system image viewer. Use whenever the user asks to create, generate, draw, make, or produce an image/picture/illustration/poster/icon/logo/infographic/thumbnail/wallpaper from a description — even if they don't mention OpenAI, Gemini, gpt-image-2, or DALL·E explicitly. Triggers include phrases like 'generate an image of', 'draw me a', 'create a picture', 'make a visual of'. Also use when the user names a backend ('draw it with gemini', 'make it with gpt') or wants to compare/race both models on the same prompt ('race gpt vs gemini'), and for iterating on a prompt (regenerating with variations or a refined description). Requires OPENAI_API_KEY (and GEMINI_API_KEY for the gemini provider or --race)."
metadata:
  argument-hint: "<prompt> [--provider openai|gemini] [--race] [--tier low|medium|high] [--aspect 1:1|3:2|2:3|4:3|3:4|16:9|9:16] [--resolution 1K|2K|4K] [--size <WxH>] [-n 1-10] [--thinking low|medium|high] [--out-dir <path>] [--no-display]"
---

# Generate Image

Generate raster images from a text prompt, save them as PNGs, and open them in the system image viewer. Two backends:

- **openai** (default) — `gpt-image-2`, reads `OPENAI_API_KEY`.
- **gemini** — Gemini native image generation (Nano Banana), reads `GEMINI_API_KEY`.
- **--race** — run both on the same prompt for a side-by-side comparison.

The bundled script handles the API call, file save, and terminal render in one shot — don't re-implement it inline.

## Usage

```bash
python {{SKILL_DIR}}/generate_image.py "<prompt>" [options]
```

`{{SKILL_DIR}}` is the directory containing this SKILL.md. Resolve it relative to this file's location.

The script prints each saved PNG path to stdout (one per line) and opens each in the system image viewer (`open` on macOS). On other platforms it just prints the path; pass `--no-display` to skip opening the viewer entirely.

Files default to `~/Pictures/ai-generated/<timestamp>.png`. In `--race` (or any multi-provider run) filenames are tagged with the provider, e.g. `<timestamp>-openai.png` / `<timestamp>-gemini.png`, so generations don't collide and stay easy to tell apart.

### Options

| Flag | Purpose |
|------|---------|
| `--provider openai\|gemini` | Backend. Default `openai`. |
| `--race` | Generate from BOTH providers on the same prompt and preview both. Needs both API keys. |
| `--tier low\|medium\|high` | Quality/model tier, applied per provider (default `high`). See mapping below. |
| `--aspect 1:1` | Cross-provider aspect ratio: `1:1`, `3:2`, `2:3`, `4:3`, `3:4`, `16:9`, `9:16`. Default `1:1`. |
| `--resolution 1K\|2K\|4K` | Output detail. Default `1K` (moderate). Raise only when the user asks for higher resolution. See note below. |
| `--size 1536x1024` | OpenAI-only pixel override (skips `--aspect` mapping for openai). Supported: `1024x1024`, `1536x1024`, `1024x1536`, `2000x1000`, `1000x2000`, `2000x667`, `667x2000`. |
| `-n 4` | Images per provider, 1–10. OpenAI batches in one call; Gemini loops the call. |
| `--thinking medium` | OpenAI-only reasoning mode (`low`/`medium`/`high`). Use for rendered text, charts, multi-panel layouts, or precise composition — costs extra reasoning tokens but fixes garbled text. |
| `--out-dir <path>` | Override output directory. |
| `--no-display` | Skip opening the system viewer (batch / non-interactive runs). |

### Tier mapping

`--tier` picks an equivalent-caliber model on each provider so `--race` stays apples-to-apples. The user shouldn't have to memorize raw model IDs — just ask for low/medium/high.

| Tier | OpenAI (`gpt-image-2`) | Gemini |
|------|------------------------|--------|
| `high` (default) | `quality=high` | `gemini-3-pro-image` (Nano Banana Pro) |
| `medium` | `quality=medium` | `gemini-3.1-flash-image` (Nano Banana 2) |
| `low` | `quality=low` | `gemini-2.5-flash-image` (Nano Banana) |

Tier is model/quality only — resolution is a separate axis (`--resolution`).

### Resolution

Default `1K` keeps generations moderate (cheaper, faster). Bump to `2K`/`4K` only when the user explicitly wants higher resolution. Where a provider exposes a real resolution parameter the script uses it; where it doesn't, the request is passed through as a prompt instruction instead:

- **Gemini** → sets the native `imageSize` param (`1K`/`2K`/`4K`).
- **OpenAI** → `gpt-image-2` has no resolution param (pixel count is fixed by `--size`), so an above-default `--resolution` is appended to the prompt as a detail hint. For an exact OpenAI pixel size, use `--size`.

### Aspect quick guide

- Square / icon / avatar → `1:1`
- Landscape scene, wallpaper, slide → `3:2` (or `4:3`)
- Portrait poster, story, mobile wallpaper → `2:3` (or `3:4`)
- Ultra-wide banner, header → `16:9`
- Tall column, infographic → `9:16`

`--aspect` maps to fixed pixel sizes on OpenAI and to ratio strings on Gemini. For an exact OpenAI pixel size, pass `--size` instead.

### When to raise `--thinking`

OpenAI-only, default off (fastest, cheapest). Escalate to `medium` or `high` when the prompt includes any of:

- Rendered text inside the image (labels, captions, signage, UI mockups, posters with words)
- Multi-panel / grid layouts (comics, infographics, before-after)
- Charts, diagrams, maps, or anything with spatial precision
- Non-Latin scripts (Korean, Japanese, Chinese, etc.) — reasoning helps with layout

If a first pass comes out with garbled text or messy layout on openai, suggest retrying with `--thinking medium` rather than just regenerating. (Gemini's Pro/Flash models reason internally, so there's no equivalent flag for the gemini provider.)

## Examples

User: "draw me a watercolor of a cat sleeping on a windowsill"

```bash
python {{SKILL_DIR}}/generate_image.py "A cat sleeping on a sunlit windowsill, soft watercolor, warm pastel tones"
```

User: "draw this with gemini"

```bash
python {{SKILL_DIR}}/generate_image.py "<prompt>" --provider gemini
```

User: "generate it with both gpt and gemini and compare"

```bash
python {{SKILL_DIR}}/generate_image.py "<prompt>" --race --aspect 3:2
```

(Saves `<stamp>-openai.png` and `<stamp>-gemini.png`, previews both with a labeled header.)

User: "make this big, in 4K high resolution"

```bash
python {{SKILL_DIR}}/generate_image.py "<prompt>" --provider gemini --resolution 4K
```

(Default stays moderate `1K`; only raise resolution when the user asks.)

User: "a 4-panel infographic explaining the OAuth 2.1 flow, with Korean labels"

```bash
python {{SKILL_DIR}}/generate_image.py \
  "4-panel infographic explaining the OAuth 2.1 authorization code flow, Korean labels, clean flat design, numbered steps" \
  --aspect 3:2 --thinking medium
```

User: "generate 4 with the same concept"

```bash
python {{SKILL_DIR}}/generate_image.py "<same prompt>" -n 4
```

(Single OpenAI call, not four separate ones — stylistically consistent and cheaper.)

User: "redo the previous image a little differently"

Don't just rerun the same prompt — ask what to change, refine the prompt, then call again. Saving the user from paying for near-duplicates is part of the job.

## First-run dependencies

- `OPENAI_API_KEY` must be exported for the openai provider; `GEMINI_API_KEY` for the gemini provider. `--race` needs both. The script errors out early if the required key is missing — ask the user to export it rather than hunting through dotfiles.
- Python 3 only (stdlib — no `pip install` needed). Uses `curl` for the HTTP call to dodge Python SSL cert issues. Preview just shells out to macOS `open`; no extra tooling required.

## Scope

In scope: text → image generation on either provider, head-to-head `--race`, batch (`-n`), aspect + resolution control, tier selection, OpenAI reasoning mode, system-viewer preview.

Out of scope (don't try to shoehorn in):

- **Editing an existing image** (inpaint, mask, variation) — different endpoints on both providers. Tell the user and stop.
- **Imagen** — the gemini provider uses Gemini native image generation only; Imagen's separate `:predict` endpoint isn't wired up. Mention it if the user specifically wants Imagen's photorealism.
- **Vector / SVG output or code-rendered diagrams** — use the appropriate tool; these models produce raster only.
- **Video, animation, 3D** — out of model scope.
```
