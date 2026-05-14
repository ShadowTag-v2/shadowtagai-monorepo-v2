# Task Breakdown

- [x] Find the sovereign_ingestor daemon script modified recently.
- [x] Hard lock the script's execution to `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3` via shebang or subprocess calls.
- [x] Run a quick test to ensure the daemon doesn't crash on startup.
- [x] Fix basedpyright Jupyter notebook parsing error (`TypeError: Cannot read properties of undefined (reading 'filter')`)
- [ ] Add `pyrightconfig.json` to exclude subdirectories and fix enumeration timeout.
- [ ] Run a quick test to ensure the daemon doesn't crash on startup.
