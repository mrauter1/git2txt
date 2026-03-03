---
name: git2text-extraction
description: Use this skill when a user wants to export a local codebase or remote git repository into a single markdown text artifact for LLM context, including include/ignore glob filtering, .gitignore control, and optional clipboard copy.
---

# Git2Text Extraction

## When to use
- User asks to export, flatten, snapshot, or package a repo/folder for LLM ingestion.
- User needs one markdown artifact containing a project tree and file contents.

## Inputs to collect
- Source path or git URL.
- Output file path (`-o`) if the user wants to save output to a file.
- Include globs (`-inc`) and/or ignore globs (`-ig`).
- Whether to ignore `.gitignore` (`-igi`).
- Whether to skip empty files (`-se`).
- Whether to copy output to clipboard (`-cp`).

## Core workflow
1. Confirm source type:
   - Local path exists, or
   - Remote URL ends with `.git` (or is a valid clone URL).
2. Build the command incrementally starting from:
   - `skills/git2text-extraction/scripts/run_git2text.sh <source>`
3. Append options only as requested.
4. Execute command.
5. Validate result:
   - Prefer `--require-output <path>` when `-o` is used.
   - Report the exact command and output path.

## Command templates
- Full export to file:
  - `skills/git2text-extraction/scripts/run_git2text.sh --require-output output.md <source> -o output.md`
- Include-only extraction:
  - `skills/git2text-extraction/scripts/run_git2text.sh --require-output output.md <source> -inc "*.py" -o output.md`
- Ignore patterns:
  - `skills/git2text-extraction/scripts/run_git2text.sh --require-output output.md <source> -ig "*.log" "__pycache__" -o output.md`
- Ignore `.gitignore` and skip empty files:
  - `skills/git2text-extraction/scripts/run_git2text.sh --require-output output.md <source> -igi -se -o output.md`
- Validate command plan only (no execution):
  - `skills/git2text-extraction/scripts/run_git2text.sh --dry-run <source> -inc "*.py" -o output.md`

## References
- Presets and copy-ready command recipes: `references/presets.md`
- Failure modes and fixes: `references/troubleshooting.md`

## Notes
- Prefer small include sets when users care about token budget.
- If user needs clipboard output on Linux, remind them `xclip` or `xsel` may be required.
