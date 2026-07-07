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
