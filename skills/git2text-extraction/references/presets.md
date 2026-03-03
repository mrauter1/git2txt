# Presets

## Minimal local export
```bash
skills/git2text-extraction/scripts/run_git2text.sh --require-output repo_dump.md /path/to/repo -o repo_dump.md
```

## Remote repository export
```bash
skills/git2text-extraction/scripts/run_git2text.sh --require-output repo_dump.md https://github.com/owner/repo.git -o repo_dump.md
```

## Python-only snapshot
```bash
skills/git2text-extraction/scripts/run_git2text.sh --require-output python_only.md /path/to/repo -inc "*.py" -o python_only.md
```

## Docs-only snapshot
```bash
skills/git2text-extraction/scripts/run_git2text.sh --require-output docs_only.md /path/to/repo -inc "*.md" "*.txt" -o docs_only.md
```

## Exclude noisy files
```bash
skills/git2text-extraction/scripts/run_git2text.sh --require-output clean_dump.md /path/to/repo -ig "*.log" "*.tmp" "node_modules/" -o clean_dump.md
```

## Ignore .gitignore and skip empty files
```bash
skills/git2text-extraction/scripts/run_git2text.sh --require-output exhaustive_nonempty.md /path/to/repo -igi -se -o exhaustive_nonempty.md
```

## Clipboard-first workflow
```bash
skills/git2text-extraction/scripts/run_git2text.sh /path/to/repo -inc "*.py" -cp
```

## Validate command only (no execution)
```bash
skills/git2text-extraction/scripts/run_git2text.sh --dry-run /path/to/repo -inc "*.py" -o dry_run.md
```
