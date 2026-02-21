# Contributing

This is a personal collection of tools I've built for my own Claude Code workflow. You're welcome to:

- Fork and adapt for your needs
- Submit bug reports via Issues
- Suggest improvements via Pull Requests

## Adding New Tools

Each tool lives in `tools/<tool-name>/` with:
- `README.md` — Documentation
- Source files in appropriate subdirectories
- Install/uninstall logic added to `install.sh`

## Code Style

- Bash scripts: POSIX-compatible where possible
- Python: Standard library only (no pip dependencies)
- All scripts must be idempotent (safe to re-run)
- Clear error messages for non-technical users

## License

All contributions are under MIT License.
