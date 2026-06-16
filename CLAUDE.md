# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

## Project Overview

`morpc` is a Python library (published to PyPI) providing constants, mappings, and shared functions for MORPC data workflows. Python >=3.10 is required.

## Models & Agents

- Default to **Sonnet** for all code work.
- Use **Opus** for coordination, architecture, high-level design, and conceptual planning.
- Use **Haiku** for simple lookups, reading files, and lightweight tasks.
- Use subagents for all non-trivial code work. Spawn agents with the appropriate model for the task.

## Git Workflow

### Before starting any work
1. Check the current branch. **Never make code changes directly on `main`.**
2. Ask the user which branch to work on, or propose a branch name and ask for confirmation before creating it.
3. Create the branch and switch to it before making any changes.

### While working
- Commit in logical units with clear, descriptive commit messages.
- Write tests for new functionality.
- Update documentation when behavior changes.

### When work is complete
1. Ask the user if they want to open a pull request.
2. If yes, push the branch and create a PR with a summary of what changed and why.

### Rules
- Never commit directly to `main` or `master`.
- Never force-push without explicit user confirmation.
- Always confirm before destructive git operations (reset --hard, branch deletion, etc.).

## Commands

### Development Setup
```bash
pip install -e ".[dev]"
```

### Running Tests
```bash
pytest
# Run a single test:
pytest tests/test_utils.py::test_function_name
```

### Building for Release
```bash
python3 -m pip install build
python3 -m build
```

### Release Process
Bump `__version__` in `morpc/__init__.py`, commit and push, then create a GitHub Release with a matching tag (e.g. `v0.5.5`). CI handles PyPI publish and docs deploy automatically.

## Architecture

### Package Structure

The public API is assembled in `morpc/__init__.py`, which re-exports everything from all submodules. Most constants and functions live in the monolithic `morpc/morpc.py` (~3700 lines); subpackages (`frictionless/`, `color/`, `plot/`, `rest_api/`) each have a thin `__init__.py` that re-exports from their implementation module.

### Core Module (`morpc/morpc.py`)

The central file. Contains:

- **Geographic constants**: `CONST_REGIONS` (region name → county list for REGION7, REGION10, REGION15, CBSA, etc.), `CONST_COUNTY_NAME_TO_ID`, state name/abbr/ID lookup dicts
- **Census summary levels**: `SUMLEVEL_DESCRIPTIONS` (codes `'010'`–`'M30'`), `SUMLEVEL_LOOKUP`, `HIERARCHY_STRING_LOOKUP` — detailed census and MORPC geography hierarchy metadata
- **Data I/O**: `load_spatial_data()`, `load_tabular_data()`, `write_table()` (enforces `\r\n` CSV endings), `wget()`
- **DataFrame utilities**: `round_preserve_sum()`, `compute_group_sum()`, `compute_group_share()`, `compute_controlled_values()`, `control_variable_to_group()`, `update_existing_table()`
- **Lookup classes**: `countyLookup(scope)` (county GEOID/name resolution), `varLookup(...)` (variable dictionary — depends on external `../morpc-lookup/` repo), `generations()` (birth-year → generation), `bls()` (QCEW aggregation codes)
- **Spatial**: `assign_geo_identifiers()` (point-in-polygon using TIGER layers), `reapportion_by_area()` (areal interpolation)
- **Avro/legacy**: `cast_field_types(df, schema)` using Avro schema — superseded by the frictionless workflow

### Frictionless Workflow (`morpc/frictionless/`)

The preferred pattern for data loading and saving in MORPC pipelines:
- Data files are paired with `.resource.yaml` and `.schema.yaml` sidecars
- `load_data(resourcePath)` — primary entry point; loads data + applies schema type casting
- `create_resource(dataPath, ...)` — build a frictionless Resource descriptor
- `create_package(dir, resources, ...)` — bundle resources into a data package
- `cast_field_types(df, schema)` — type-cast a DataFrame per frictionless schema fields
- `schema_from_avro(path)` — migrate legacy Avro schemas to frictionless format

### REST API (`morpc/rest_api/`)

ArcGIS Online REST API tools:
- `gdf_from_resource(resource)` — fetch all features from an ArcGIS REST service as a GeoDataFrame, handling pagination automatically
- `resource(name, url, ...)` — build a frictionless Resource from a REST service URL
- `schema(url, outfields)` — fetch ArcGIS field definitions as a frictionless Schema

### Plot (`morpc/plot/`)

- `morpc_theme` (`plot.py`) — plotnine theme subclassing `theme_classic` with MORPC branding
- `MAP` (`map.py`) — folium-based interactive choropleth for GeoDataFrames; `BindColormap` for legend binding
- `ExcelChart` / `data_chart_to_excel()` (`excel.py`) — build Excel charts via xlsxwriter

### Color (`morpc/color/`)

- `GetColors` (`colors.py`) — loads `morpc_colors_2026.yaml` via `importlib.resources`; provides `.KEYS()`, `.SEQ()` (sequential palettes), and other palette accessors
- `CONST_MORPC_COLORS` and `CONST_COLOR_CYCLES` in `morpc.py` are the older dict-based color API

### Utilities (`morpc/utils.py`, `morpc/logs.py`, `morpc/req.py`, `morpc/geocode.py`)

- `datetime_from_string(date, errors)` — flexible datetime parser; handles NaT, datetime objects, integer epochs (ns/ms/s), ISO 8601, YYYYMMDD, YYYYMM, natural language
- `DataFrameSummary(df, ...)` — markdown descriptive stats summary
- `config_logs(filename, level, mode)` — logging to file + stdout for notebook workflows
- `get_json_safely()`, `get_text_safely()`, `get_file()` — HTTP helpers with retry logic
- `geocode(addresses, endpoint)` — Nominatim geocoding (public or local Docker)

## Key Conventions

- **CSV line endings**: Always `\r\n` (Windows). `write_table()` enforces this via `PANDAS_EXPORT_ARGS_OVERRIDE`. This ensures consistent MD5 checksums cross-platform.
- **Logging**: All modules use `logging.getLogger(__name__)`. Older code in `morpc.py` uses `print()` with `morpc.function | LEVEL |` prefix — this is legacy and should not be extended.
- **TODO automation**: `# TODO:` comments are automatically converted to GitHub Issues on push via `.github/workflows/todo_to_issue.yml`.
- **External dependency**: `varLookup` expects `../morpc-lookup/variable_dictionary.xlsx` — a separate repo not bundled here.
- **Missing declared deps**: `geopy`, `tqdm`, and `folium` are used in source but not listed in `pyproject.toml`. Add them when touching those modules.

## CI/CD

- **PyPI publish**: triggered by creating a GitHub Release (`.github/workflows/python-publish.yml`); builds on `windows-latest`, uses OIDC trusted publishing
- **Docs**: MyST Markdown + Jupyter notebooks in `doc/`; deployed to GitHub Pages on push to `main` via `myst build --html`
