# Git Lines Counter

A simple Python script to analyze Git repository statistics with support for author filtering and date ranges.

## Features

- Count lines added, removed, and changed in a Git repository
- Filter by author name
- Specify date range

## Installation

1. Have git installed
2. Clone / download the main script
3. Run the script in your desired repo locally
4. Thats it.

## Usage

Basic usage:
```bash
python main.py
```

With filters:
```bash
python main.py --start-date 2024-01-01 --end-date 2025-01-01 --author "John Doe"
```

### Arguments
- `--start-date`: Start date (YYYY-MM-DD)
- `--end-date`: End date (YYYY-MM-DD) 
- `--author`: Filter by author name

### Example Output
```
═══════════════════════════════════════
Git Repository Analysis
Period: 2024-01-01 to 2024-01-31
Author: John Doe

───────────────────────────────────────
Commits:        42
Lines added:    +1,234
Lines removed:  -567
Lines changed:   1,801
Net change:     +667
═══════════════════════════════════════
```
