# Troubleshooting

## `git2text: command not found`
- Ensure package install completed.
- Re-open shell so updated PATH is loaded.
- The wrapper script auto-falls back to `python -m src.git2text` (or `python3 -m src.git2text`) when `git2text` is not on PATH.
- Use `--dry-run` first to validate command composition without executing.

## Clipboard option fails on Linux
- Install one of:
  - `xclip`
  - `xsel`

## Output file is unexpectedly large
- Narrow scope with `-inc`.
- Add excludes via `-ig`.
- Use `-se` to skip empty files.

## Output validation failed (`--require-output`)
- Confirm you passed `-o <same-path>` in git2text options.
- Ensure destination directory exists and is writable.
- Re-run with `--dry-run` to verify argument order.

## Unexpected files missing
- Check `.gitignore` influence.
- Re-run with `-igi` to bypass `.gitignore` and `.globalignore` handling.

## Slow run on very large repositories
- Use include-first strategy (`-inc`) with only needed extensions.
- Exclude generated directories (`-ig "dist/" "build/" "node_modules/"`).
