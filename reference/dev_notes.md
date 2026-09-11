# Dev Notes

High-level, append-only notes on notable changes. Newest entries at the bottom.

## 2026-07-07 — Improve `datetime_from_string` robustness and coverage

Branch: `improve-datetime-parsing`

Reworked `morpc.utils.datetime_from_string` to catch a wider range of date/datetime
string and numeric representations and to fix correctness bugs:

- Numeric inputs (int **and** float) now dispatch by digit count
  (19=ns, 13=ms, 10=s, 8=YYYYMMDD, 6=YYYYMM). Fixes the float bug where any float
  was treated as Unix seconds (e.g. `20210310.0` -> 1970). `int`, `float`, and
  all-digit `str` now resolve identically.
- Removed the hand-rolled ISO regex; pandas validates/parses ISO 8601 directly.
- Ambiguous dates (e.g. `10/2/2020`) are parsed month-first (US) via `dateutil`.
- Added `dateparser` as an optional final fallback for natural-language, relative,
  and localized strings; skipped gracefully if not installed.
- Output normalized to tz-naive (wall-clock preserved) so results never mix
  aware and naive datetimes. **Behavior change:** ISO-with-offset inputs previously
  returned tz-aware; they now return naive.
- Added `dateparser` to `pyproject.toml` dependencies.

Not execution-tested in the dev container (pandas/dateparser not installed there);
pure-Python digit/regex logic verified, file byte-compiles. Run `pytest` in a full
env to confirm.

## 2026-09-11 — Pass release notes to `gh` in a file

Branch: `fix/release-notes-file`

`morpc.frictionless.create_release` passed the generated release notes inline as
`gh release create --notes <text>`. For a release with many resources the notes plus
the asset paths exceed the maximum Windows command line length, so `CreateProcess`
fails before `gh` runs with `FileNotFoundError: [WinError 206] The filename or
extension is too long`.

- Notes are now written to a file in a `tempfile.mkdtemp()` directory and passed as
  `--notes-file`. The directory is removed in a `finally` so it is cleaned up whether
  or not `gh` succeeds. A dry run writes nothing.
- Added an `overrideNotes` parameter that replaces the generated notes verbatim.
  `notes` keeps its meaning as intro text above the generated `## Resources` section
  and is ignored (with a warning) when `overrideNotes` is given.

Note this does not shorten the asset path list, which is still passed positionally and
contributes to the same command line length limit.

## 2026-09-11 — Upload release assets in batches

Branch: `fix/release-asset-batching`

Follow-up to the `--notes-file` change. Asset paths were still passed positionally to
`gh release create`, so a release with many resources could exceed the maximum Windows
command line length on the paths alone and fail the same way (WinError 206).

- Added `_batch_assets(assets, baseLength, limit=30000)`, which groups paths so each
  projected command line stays under the limit. 30000 leaves headroom below Windows'
  32767-character cap for quoting and the environment block.
- `create_release` now creates the release with no assets and uploads them with
  `gh release upload` in batches, logging progress per batch.
- If the create or any upload fails, the release and its tag are deleted
  (`gh release delete --yes --cleanup-tag`) and the original exception re-raised. The
  cleanup does not raise on failure so that it cannot mask the error that explains the
  failure; it logs instead and tells the user to delete the release manually.

**Behavior change:** releases are no longer atomic. There is a window in which the
release exists with only some assets. The rollback narrows that window but cannot close
it: if the delete also fails, a partial release and its tag are left behind and must be
removed by hand before retrying.
