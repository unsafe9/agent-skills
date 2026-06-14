# generate-image

Generate raster images from a text prompt with OpenAI's `gpt-image-2` (default)
or Google Gemini (Nano Banana), save them as PNGs, and open them in the system
image viewer. Supports `--race` to run both providers on the same prompt for a
side-by-side comparison.

## Prerequisites

- **Programs**: Python 3 (standard library only — no `pip install`), and `curl`
  (used for the HTTP call to sidestep Python SSL cert issues). Inline preview /
  auto-open uses the macOS `open` command; on other platforms the script just
  prints the saved path, or pass `--no-display` to skip opening entirely.
- **Environment variables**:
  - `OPENAI_API_KEY` — required for the `openai` provider (the default).
  - `GEMINI_API_KEY` — required for the `gemini` provider.
  - `--race` needs **both** keys.
- **Services / auth**: an OpenAI API account (for `gpt-image-2`) and/or a Google
  Gemini API key (for Gemini native image generation).

## Usage

```bash
python generate_image.py "<prompt>" [options]
```

See `SKILL.md` for the full option list, tier/resolution/aspect mappings, and
examples.
