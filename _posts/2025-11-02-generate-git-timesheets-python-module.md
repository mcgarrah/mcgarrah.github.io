---
title: "Generate Git Timesheet from Commit Logs"
layout: post
categories: [technical, development]
tags: [python, git, timetracking, automation, cli, development]
published: true
---

I hate time tracking. Seriously. Most time tracking tools require you to remember to start timers, categorize work, and generally interrupt your flow to feed some system that's probably going to be wrong anyway. But when you're freelancing or need to report hours on projects, you're stuck with it.

So I built a Python tool that generates timesheets from git commit history - because your commits are already there, they're timestamped, and they actually reflect when you were working on stuff.

<!-- excerpt-end -->

## The Problem I Had

I was working on a multi-month project spread across several repositories - API backend, client dashboard, admin portal, the usual mess. Work happened in irregular spurts, sometimes late nights, sometimes weekend debugging sessions. When it came time to report my hours, I had no idea how much time I'd actually spent.

Manual time tracking? I'd forget to start the timer half the time. Guessing from memory? That's how you end up either shortchanging yourself or looking like you're padding hours.

But I had git commits. Lots of them. With timestamps. That's when I realized I could reverse-engineer my work patterns from commit history.

## How to Use It

The tool has a simple command-line interface. Here's how I typically use it:

### Basic Usage

Generate a timesheet for the last two weeks:

```bash
# Install the package
pip install git-timesheet

# Generate timesheet for the last 2 weeks
ggts --since="2 weeks ago"
```

### Filtering by Repository

If you're working across multiple repositories like I was, you can specify which ones to include:

```bash
# Generate timesheet for specific repositories
ggts --repos project-api client-dashboard admin-portal --since="1 month ago"
```

### Different Output Formats

Need to share your timesheet with others? Export it in different formats:

```bash
# Generate CSV for spreadsheet import
ggts --since="1 month ago" --output=csv --output-file=timesheet.csv

# Generate markdown for documentation
ggts --since="1 month ago" --output=markdown --output-file=timesheet.md
```

### Sample Output (Markdown Format)

Here's what the output might look like in markdown format:

```markdown
# Git Activity Timesheet

## Week of 2025-06-01

| Day | Date | Time | TZ | Repository | Hours | Description |
|-----|------|------|-------|------------|-------|-------------|
| Monday | 2025-06-02 | 09:15 | EDT | client-dashboard | 1.25 | Implement user profile page... (3 commits) |
| | | 11:30 | EDT | project-api | 0.75 | Fix authentication bug... (2 commits) |
| | | 14:45 | EDT | admin-portal | 2.00 | Add reporting features... (4 commits) |
| **Total** | | | | | **4.00** | |
| | | | | | | |
```

# Git Activity Timesheet

## Week of 2025-06-01

| Day | Date | Time | TZ | Repository | Hours | Description |
|-----|------|------|-------|------------|-------|-------------|
| Monday | 2025-06-02 | 09:15 | EDT | client-dashboard | 1.25 | Implement user profile page... (3 commits) |
| | | 11:30 | EDT | project-api | 0.75 | Fix authentication bug... (2 commits) |
| | | 14:45 | EDT | admin-portal | 2.00 | Add reporting features... (4 commits) |
| **Total** | | | | | **4.00** | |
| | | | | | | |

## How It Works Under the Hood

The tool does a few things that turned out to be trickier than I initially thought:

1. **Finds your repos**: Recursively hunts down git repositories in your project directories
2. **Extracts commit data**: Pulls timestamps, authors, and commit messages from git logs
3. **Estimates time spent**: This is the interesting part - uses heuristics to guess how long you worked
4. **Handles timezones**: Because I work across time zones and git commits can be confusing
5. **Formats output**: Generates reports in text, CSV, or markdown

## Core Functionality

### Finding Your Repositories

First challenge: finding all the git repos in your project structure. This turned out to be straightforward:

```python
def get_git_repos(base_dir):
    """Find git repositories in the specified directory."""
    repos = []
    
    # First check if the base_dir itself is a git repository
    if os.path.exists(os.path.join(base_dir, '.git')):
        repos.append(base_dir)
        return repos
    
    # If not, look for git repositories in subdirectories
    for item in os.listdir(base_dir):
        full_path = os.path.join(base_dir, item)
        if os.path.isdir(full_path) and os.path.exists(os.path.join(full_path, '.git')):
            repos.append(full_path)
    return repos
```

### Getting Commit Data

Next, I needed to extract commit information in a consistent format. Git's pretty-format option is your friend here:

```python
def get_git_log(repo_path, since=None, until=None, author=None):
    """Get git log for a repository with author date and commit message."""
    cmd = ['git', 'log', '--pretty=format:%ad|%an|%ae|%s|%h', '--date=iso']
    
    if since:
        cmd.append(f'--since={since}')
    if until:
        cmd.append(f'--until={until}')
    if author:
        cmd.append(f'--author={author}')
    
    # Execute git command and process output
    result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    return []
```

### The Time Estimation Magic

This is where it gets interesting. How do you estimate time from commits? I tried a few approaches:

1. **Base time**: Every commit gets 15 minutes minimum (because even small commits take time)
2. **Keyword analysis**: Certain commit messages suggest more work:
   - Bug fixes: +15 minutes (debugging is time-consuming)
   - New features: +30 minutes (implementation takes longer)
   - Refactoring: +15 minutes (thinking time)
3. **Session detection**: Commits close together (within 60 minutes) are probably the same work session

The algorithm isn't perfect, but it's surprisingly accurate for my work patterns:

```python
# Adjust based on commit message
if re.search(r'fix|bug|issue', message, re.I):
    time_spent += 15
if re.search(r'feature|implement|add', message, re.I):
    time_spent += 30
if re.search(r'refactor|clean|improve', message, re.I):
    time_spent += 15

# Check time gap to next commit
if i < len(parsed_commits) - 1:
    next_date = parsed_commits[i+1][0]
    time_gap = (next_date - date).total_seconds() / 60
    
    # If commits are close together, they're likely part of the same work session
    if time_gap < session_timeout_minutes:
        time_spent = min(time_spent, time_gap)
```

### Timezone Headaches

Git commits can have weird timezone info, especially if you work across different machines or travel. I added timezone conversion because I got tired of trying to figure out when I actually worked:

```python
def convert_to_timezone(date, timezone_str='UTC'):
    """Convert datetime to specified timezone."""
    if date.tzinfo is None:
        date = date.replace(tzinfo=pytz.UTC)
    
    # Handle common timezone aliases
    timezone_aliases = {
        'US/Eastern': 'America/New_York',
        'US/Central': 'America/Chicago',
        # Additional mappings...
    }
    
    # Use the alias if available
    tz_name = timezone_aliases.get(timezone_str, timezone_str)
    
    try:
        target_tz = pytz.timezone(tz_name)
    except pytz.exceptions.UnknownTimeZoneError:
        target_tz = pytz.UTC
        
    return date.astimezone(target_tz)
```

## Configuration

The tool looks for config files in the usual places - current directory, home directory, `.config` folder. I tried to follow standard conventions so it doesn't surprise anyone:

1. `.ggtsrc` in your current directory
2. `ggts.ini` in your current directory  
3. `.ggtsrc` in your home directory
4. `ggts.ini` in your `.config` directory

Basically, it checks local first, then falls back to global settings.

## Output Options

I needed different formats depending on who was asking for the timesheet:

1. **Text**: For quick terminal viewing
2. **CSV**: For importing into Excel or Google Sheets (because managers love spreadsheets)
3. **Markdown**: For documentation or GitHub issues

## Command-Line Interface

The package provides a comprehensive CLI built with Click:

```shell
ggts [options]
```

Key options include:
- `--base-dir PATH`: Base directory containing git repositories
- `--since DATE`: Show commits more recent than a specific date
- `--until DATE`: Show commits older than a specific date
- `--repos REPO [REPO ...]`: Specific repository names to include
- `--output FORMAT`: Output format (text, csv, markdown)
- `--author PATTERN`: Filter commits by author
- `--timezone TIMEZONE`: Timezone for dates
- `--session-timeout MINUTES`: Minutes between commits to consider them part of the same work session

## The Technical Stuff

### Performance

I learned the hard way that scanning large repositories can be slow. A few optimizations that helped:

1. **Smart repo discovery**: If the base directory is already a git repo, don't scan subdirectories
2. **Single git calls**: One command per repo instead of multiple queries
3. **Stream processing**: Don't load everything into memory at once

### Error Handling

Because things always go wrong:

1. **Permission issues**: Some repos you can't read (gracefully skip them)
2. **Git command failures**: Subprocess calls can fail (capture and continue)
3. **Timezone weirdness**: When timezone conversion fails, fall back to UTC

## Who This Helps

I built this for myself, but it turns out other people have similar problems:

1. **Freelancers**: Need accurate billing without the overhead of manual tracking
2. **Project managers**: Want to understand where time actually goes
3. **Open source contributors**: Curious about time investment in volunteer projects
4. **Teams**: Need activity reports for stakeholders who don't understand git

## What's Next

I've got a few ideas for improvements, though I'm not sure when I'll get to them:

1. **Smarter time estimation**: Maybe use machine learning on historical patterns
2. **Web interface**: Command line is fine for me, but others might want a GUI
3. **Issue tracker integration**: Connect commits to Jira tickets or GitHub issues
4. **Team reports**: Aggregate data across multiple developers

## Wrapping Up

This tool solved my specific problem: reconstructing work hours from git history without disrupting my workflow. The time estimates aren't perfect, but they're close enough for billing and project planning.

If you're tired of manual time tracking but need to report hours, give it a try. The worst case is you get a different perspective on your work patterns. Best case, you save yourself the hassle of remembering to start and stop timers.

It's not revolutionary, but it's useful. Sometimes that's enough.

[GitHub Repository](https://github.com/mcgarrah/git_timesheet_python) is available and it is a `pip` installable tool.
