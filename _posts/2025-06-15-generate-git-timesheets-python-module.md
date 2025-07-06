---
title: "Generate Git Timesheet from Commit Logs"
layout: post
published: false
---

# Analyzing Developer Productivity with Generate Git Timesheet

In software development environments, accurately tracking time spent on various projects is essential for project management, client billing, and productivity analysis. While numerous time-tracking solutions exist, many require manual input, which can be error-prone and disruptive to developer workflow. This article introduces a Python-based solution that leverages existing git commit history to generate comprehensive timesheets automatically.

<!-- excerpt-end -->

## Introduction to Generate Git Timesheet

The [Generate Git Timesheet](https://github.com/mcgarrah/git_timesheet_python) is a Python package I developed to automate the creation of detailed timesheets from git commit logs. This tool analyzes commit patterns across multiple repositories, estimates time spent on development tasks, and produces formatted reports suitable for various use cases.

I built this tool to solve a specific problem: tracking my time across a multi-month project that spanned several different repositories with work done in irregular spurts. When it came time to report my hours, I needed an accurate way to reconstruct my work patterns without relying on memory or incomplete manual tracking.

## Quick Start: Using the GGTS CLI

The Git Timesheet Generator provides a simple command-line interface that makes it easy to generate timesheets from your git repositories. Here are some practical examples to get you started:

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

## Technical Architecture

The package is structured as a modular Python application with several key components:

1. **Repository Discovery**: Recursively identifies git repositories within a specified directory structure
2. **Commit Analysis**: Extracts commit metadata including timestamps, authors, and messages
3. **Time Estimation Algorithm**: Applies heuristics to estimate development time based on commit patterns
4. **Timezone Management**: Handles timezone conversions for distributed teams
5. **Output Formatting**: Generates reports in multiple formats (text, CSV, markdown)

## Core Functionality

### Repository Detection

The system employs a recursive directory traversal algorithm to identify git repositories:

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

### Commit History Extraction

The tool interfaces with git through subprocess calls to extract commit history with precise formatting:

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

### Time Estimation Algorithm

The core of the system is a sophisticated algorithm that estimates time spent on development tasks:

1. **Base Time Allocation**: Each commit receives a baseline of 15 minutes
2. **Semantic Analysis**: Additional time is allocated based on commit message keywords:
   - Bug fixes/issues: +15 minutes
   - New features/implementations: +30 minutes
   - Refactoring/improvements: +15 minutes
3. **Work Session Detection**: Commits within a configurable time window (default: 60 minutes) are considered part of the same work session, with time adjustments to prevent double-counting

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

### Timezone Management

For distributed teams working across multiple time zones, the system provides robust timezone handling:

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

## Configuration Management

The system implements a hierarchical configuration system that searches for configuration files in multiple locations:

1. `.ggtsrc` in the current directory
2. `ggts.ini` in the current directory
3. `.ggtsrc` in the user's home directory
4. `ggts.ini` in the user's `.config` directory

This approach follows the XDG Base Directory Specification while maintaining compatibility with traditional dotfile configurations.

## Output Formats

The tool generates timesheets in three formats:

1. **Text**: Plain text output organized by weeks and days, showing detailed commit information
2. **CSV**: Comma-separated values format suitable for importing into spreadsheet applications
3. **Markdown**: Formatted tables organized by week, suitable for documentation and reporting

## Command-Line Interface

The package provides a comprehensive CLI built with Click:

```
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

## Technical Implementation Considerations

### Performance Optimization

For large repositories or extensive date ranges, the tool implements several optimizations:

1. **Efficient Repository Discovery**: Early termination when base directory is a git repository
2. **Subprocess Optimization**: Single git command execution per repository
3. **Memory-Efficient Processing**: Stream processing of commit logs

### Error Handling

The system implements robust error handling for common failure scenarios:

1. **Repository Access Errors**: Graceful handling of permission issues
2. **Git Command Failures**: Proper subprocess error capture
3. **Timezone Conversion Errors**: Fallback to UTC when specified timezone is invalid

## Use Cases

The Generate Git Timesheet is particularly valuable for:

1. **Freelance Developers**: Accurate client billing based on actual development activity
2. **Project Managers**: Analyzing team productivity and resource allocation
3. **Open Source Contributors**: Tracking time spent on volunteer projects
4. **Development Teams**: Generating activity reports for stakeholders

## Future Enhancements

Planned improvements to the system include:

1. **Machine Learning Integration**: More sophisticated time estimation based on historical patterns
2. **Web Interface**: Browser-based timesheet generation and visualization
3. **Integration with Issue Trackers**: Correlating commits with issue tracking systems
4. **Team Analytics**: Aggregated reports for development teams

## Conclusion

The Generate Git Timesheet demonstrates how existing development artifacts can be leveraged to create valuable insights without disrupting developer workflow. By analyzing git commit patterns, the tool provides a non-intrusive approach to time tracking that integrates seamlessly with established development practices.

For developers and teams seeking to understand their time allocation without the overhead of manual time tracking, this Python package offers an elegant, data-driven solution that transforms git commit history into actionable productivity insights.

[GitHub Repository](https://github.com/mcgarrah/git_timesheet_python)
