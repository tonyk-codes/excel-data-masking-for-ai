# SheetVeil

**Local deterministic tokenization of before-and-after Excel workbook pairs for privacy-safe AI workflow inference.**

SheetVeil replaces every nonblank constant cell with a stable HMAC-SHA-256 token. The same original value receives the same token in both workbooks, even when it moves to another sheet or cell. An external AI can therefore study copying, movement, filtering, deletion, duplication, sorting, and layout changes without receiving the original cell contents.

## Important security model

- Processing is local. SheetVeil has no network code.
- It uses keyed HMAC-SHA-256, not plain SHA-256.
- The same secret key is used for the entire workbook pair.
- The key is not included in the shareable output.
- By default, a temporary key is generated in memory and not saved.
- Tokens intentionally reveal equality, repetition, and movement patterns.
- This is not encryption and there is no decrypt function.
- Formula preservation may expose formula literals, file paths, sheet names, or business logic.
- Complicated workbook features can contain data outside ordinary cell values. Review macros, queries, pivot caches, charts, images, external links, and embedded objects before sharing.

## Install

```bash
python -m venv .venv
```

Windows:

```cmd
.venv\Scripts\activate
python -m pip install -e .
```

macOS/Linux:

```bash
source .venv/bin/activate
python -m pip install -e .
```

## Commands

### English desktop UI

```cmd
sheetveil ui
```

### Run from CMD or terminal

```cmd
sheetveil run --before before.xlsx --after after.xlsx --output safe_pair
```

From a source checkout on Windows, `sheetveil.cmd` runs the same command and automatically uses `.venv` when it exists:

```cmd
sheetveil.cmd run --before before.xlsx --after after.xlsx --output safe_pair
```

Existing output files are protected by default. Use `--force` only when replacing a previous package is intentional.

The output directory contains:

- `masked_before.xlsx`
- `masked_after.xlsx`
- `movement_map.json`
- `masking_report.json`
- `AI_INSTRUCTIONS.md`

### Configuration

Create a default config:

```cmd
sheetveil config init --path sheetveil.json
```

Show the default or effective config:

```cmd
sheetveil config show
sheetveil config show --path sheetveil.json
```

Validate:

```cmd
sheetveil config validate --path sheetveil.json
```

Use it:

```cmd
sheetveil run --before before.xlsx --after after.xlsx --output safe_pair --config sheetveil.json
```

### Reusable project key

Only use this when future workbook pairs must produce tokens consistent with an earlier run.

```cmd
sheetveil keygen --output private_project.key
sheetveil run --before before.xlsx --after after.xlsx --output safe_pair --key-file private_project.key
```

Never upload the key to GitHub or send it to an AI provider.

## Configuration reference

```json
{
  "formula_mode": "preserve",
  "token_style": "typed",
  "token_hex_length": 32,
  "include_headers": true,
  "strip_comments": true,
  "strip_hyperlinks": true,
  "strip_metadata": true,
  "strip_defined_names": false,
  "include_hidden_sheets": true,
  "write_reports": true
}
```

- `formula_mode`: `preserve` or `hash`.
- `token_style`: `typed` produces `TEXT_...`, `INT_...`, and similar prefixes; `opaque` produces only `VAL_...`.
- `token_hex_length`: 16 to 64 hexadecimal characters. Default 32 gives a 128-bit displayed token.
- `strip_defined_names`: potentially disruptive, so disabled by default.

`include_headers`: when `true` (default), the first row is tokenized like all other data. When `false`, row 1 of every sheet is preserved for easier workflow interpretation. Only disable it when those headers are safe to disclose. If `include_hidden_sheets` is `false`, hidden sheets are removed rather than left unmasked.

## What SheetVeil can show an AI

It is well suited to exact-value lineage:

- Copy or move data
- Reorder rows or columns
- Filter records
- Remove records
- Duplicate values
- Split values among sheets
- Consolidate exact values
- Compare layout and formatting

It cannot, by token identity alone, prove transformations that create new values:

- Hardcoded arithmetic
- Text splitting or concatenation
- Date calculations
- Rounding
- Currency conversion
- Categorization

Preserved Excel formulas can still provide evidence of those operations.

## Development

```bash
python -m pip install -e ".[dev]"
pytest
ruff check src tests
```

Create demo files:

```bash
cd examples
python create_demo_pair.py
sheetveil run --before before_demo.xlsx --after after_demo.xlsx --output demo_output
```

## Threat model

SheetVeil protects original constant cell contents from direct disclosure while preserving equality patterns. It does not hide workbook shape, sheet count, cell positions, formatting, repeated-value frequency, or exact movement patterns. Preserved formulas and complex Excel objects may expose information.

## Key handling

A generated key is temporary unless `--save-key` is explicitly used. Reusable keys must be stored outside the repository and output package. Losing a reusable key prevents reproducing the same tokens; exposing it enables dictionary testing against guessed values.

## License

MIT. See `LICENSE`.