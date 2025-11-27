---
layout: post
title: "Ruby Gem Release Automation - Part 1: Infrastructure Implementation"
categories: [ruby, devops, automation, ci-cd]
tags: [ruby-gem, github-actions, readthedocs, rubygems, release-automation, devops]
excerpt: "Building a complete release automation pipeline for Ruby gems with GitHub Actions, Read the Docs integration, and RubyGems publishing - lessons learned from 10+ manual steps to single command deployment."
published: true
---

<!-- excerpt-end -->

While developing the [jekyll-pandoc-exports](https://github.com/mcgarrah/jekyll-pandoc-exports) plugin, I discovered that building the actual functionality was only half the battle. The real challenge was creating a professional release pipeline that could handle documentation, testing, and publishing automatically. This is Part 1 of a two-part series - here I'll cover the infrastructure and automation challenges. In [Part 2](/jekyll-pandoc-exports-plugin) I will cover implementing the core functionality of the plugin.

## The Manual Release Hell

Initially, my release process looked like this nightmare checklist:

1. Update version in `lib/jekyll-pandoc-exports/version.rb`
2. Update `CHANGELOG.md` with new version details
3. Run tests locally and fix any issues
4. Commit version changes to development branch
5. Create pull request from dev to main
6. Manually review and merge PR
7. Create and push git tag
8. Build gem locally with `gem build`
9. Test gem installation locally
10. Push to RubyGems with `gem push`
11. Update documentation and push to Read the Docs
12. Create GitHub release with changelog
13. Reset development branch for next iteration

This 13-step process was error-prone, time-consuming, and frankly demoralizing. I needed automation. This was something I already learned in my work writing a [Python Library](/oneworldsync-python-module) earlier this year.

## The Infrastructure Challenge

### Read the Docs Integration

Coming from Python development, I expected Read the Docs integration to be straightforward. It wasn't. Ruby gems have different documentation patterns than Python packages:

**MkDocs Configuration** (`.readthedocs.yaml`):

```yaml
version: 2

build:
  os: ubuntu-22.04
  tools:
    python: "3.11"

mkdocs:
  configuration: docs/mkdocs.yml

python:
  install:
    - requirements: docs/requirements.txt
```

**Documentation Structure**:
```
docs/
├── mkdocs.yml
├── requirements.txt
├── index.md
├── installation.md
├── quick-start.md
├── configuration.md
├── hooks.md
├── cli.md
└── testing.md
```

Unlike Python's Sphinx autodoc, Ruby documentation required manual organization and cross-referencing.

### RubyGems Publishing Automation

RubyGems publishing presented unique challenges compared to PyPI:

**Trusted Publishers Setup**:

```yaml
# .github/workflows/publish.yml
name: Publish to RubyGems
on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.2'
          bundler-cache: true
      - name: Publish to RubyGems
        uses: rubygems/release-gem@v1
```

The trusted publishers feature was newer and less documented than PyPI's equivalent.

## GitHub Actions Complexity

### Multi-Ruby Testing Matrix

Ruby version compatibility testing proved more complex than Python:

```yaml
strategy:
  matrix:
    ruby-version: ['3.0', '3.1', '3.2', '3.3']
    os: [ubuntu-latest, macos-latest]
```

**Bundler Cache Issues**:
The biggest headache was Bundler's frozen lockfile behavior in CI:

```yaml
- name: Install dependencies
  run: |
    bundle config set --local deployment false
    bundle config set --local frozen false
    bundle install
```

This took weeks to resolve properly across all Ruby versions.

### Release Workflow Orchestration

The release workflow needed to coordinate multiple moving parts:

```yaml
name: Release
on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to release'
        required: true
        type: string

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - name: Create PR
        run: |
          gh pr create --title "Release v${{ inputs.version }}" \
                      --body "$changelog_content" \
                      --base main --head dev
      
      - name: Auto-merge PR
        run: |
          gh pr merge --auto --squash
      
      - name: Create and push tag
        run: |
          git tag "v${{ inputs.version }}"
          git push origin "v${{ inputs.version }}"
      
      - name: Create GitHub release
        run: |
          gh release create "v${{ inputs.version }}" \
                           --title "Release v${{ inputs.version }}" \
                           --notes "$changelog_content"
```

## The bin/release Script

The breakthrough was creating a comprehensive Ruby release script with extensive error checking and validation:

```ruby
#!/usr/bin/env ruby

class ReleaseManager
  def initialize
    @changelog_path = 'CHANGELOG.md'
    @version_file = 'lib/jekyll-pandoc-exports/version.rb'
    @current_version = get_current_version
  end
  
  def run(new_version = nil, skip_tests = false)
    # Version validation
    unless valid_version?(new_version)
      puts "Invalid version format. Use semantic versioning (e.g., 1.0.0)"
      exit 1
    end
    
    if version_exists?(new_version)
      puts "Version #{new_version} already exists in CHANGELOG.md"
      exit 1
    end
    
    # Update version and changelog
    update_version_file(new_version)
    update_changelog(new_version)
    
    # Run tests with skip option
    unless skip_tests
      unless system('bundle exec rake test')
        puts "Tests failed! Use --skip-tests to bypass for patch releases."
        exit 1
      end
    end
    
    # Git operations with error handling
    system("git add #{@version_file} #{@changelog_path} Gemfile.lock")
    system("git commit -m 'Bump version to #{new_version}'")
    
    current_branch = `git branch --show-current`.strip
    
    if current_branch == 'main'
      # Direct release from main
      system("git tag v#{new_version}")
      system("git push origin main && git push origin v#{new_version}")
    else
      # PR workflow with auto-merge
      system("git push origin #{current_branch}")
      
      pr_title = "Release v#{new_version}: #{get_release_description(new_version)}"
      pr_body = generate_pr_body(new_version)
      
      # Create and merge PR
      unless system("gh pr create --base main --head #{current_branch} --title '#{pr_title}' --body '#{pr_body}'")
        puts "❌ Failed to create PR. Manual steps required."
        exit 1
      end
      
      unless system("gh pr merge --merge --delete-branch=false")
        puts "❌ Failed to merge PR automatically."
        exit 1
      end
      
      # Create release tag
      system("git checkout main && git pull origin main")
      system("git tag v#{new_version} && git push origin v#{new_version}")
    end
    
    puts "✅ Release v#{new_version} completed!"
    puts "🔗 Verify at: https://rubygems.org/gems/jekyll-pandoc-exports"
  end
  
  private
  
  def valid_version?(version)
    version&.match?(/^\d+\.\d+\.\d+$/)
  end
  
  def version_exists?(version)
    File.exist?(@changelog_path) && 
    File.read(@changelog_path).include?("## [#{version}]")
  end
  
  def update_version_file(new_version)
    content = File.read(@version_file)
    updated = content.gsub(/VERSION = ['"][^'"]+['"]/, "VERSION = '#{new_version}'")
    File.write(@version_file, updated)
  end
  
  def update_changelog(new_version)
    # Sophisticated changelog parsing and updating
    # Handles unreleased sections and proper formatting
  end
end

ReleaseManager.new.run(ARGV[0], ARGV.include?('--skip-tests'))
```

**Key Ruby Script Features:**

- **Semantic version validation** with regex patterns
- **Duplicate version detection** in changelog
- **Conditional test execution** with `--skip-tests` flag
- **Branch-aware workflow** (main vs development branches)
- **Comprehensive error handling** with meaningful messages
- **Automatic changelog generation** with proper formatting
- **PR body generation** with extracted changelog content

Usage Examples:

- `./bin/release 0.1.6` - Full release with testing
- `./bin/release 0.1.8 --skip-tests` - Quick patch release

The Ruby implementation is much more robust than a simple bash script that I started with initially, with proper error handling, validation, and structured code organization.

### The bin/reset-dev Companion Script

After releases, the development branch needs to be reset to match main. This enhanced Ruby script handles the cleanup with proper validation:

```ruby
#!/usr/bin/env ruby

class DevResetManager
  VERSION_FILE = 'lib/jekyll-pandoc-exports/version.rb'
  
  def run
    if ARGV.include?('--help') || ARGV.include?('-h')
      show_help
      exit 0
    end
    
    # Validate environment before proceeding
    validate_environment
    
    puts "🔄 Hard resetting dev branch to match main..."
    puts "⚠️  WARNING: This will discard ALL changes on dev branch!"
    
    # Execute the reset commands with status updates
    puts "📥 Pulling latest main..."
    system("git pull origin main")
    
    puts "🔄 Switching to dev branch..."
    system("git checkout dev")
    
    puts "💥 Hard resetting dev to main..."
    system("git reset --hard main")
    
    puts "📤 Force pushing dev branch..."
    system("git push origin dev --force")
    
    puts "✅ Dev branch hard reset complete!"
    puts "📊 Dev branch is now identical to main branch"
    puts "🚀 Ready for next development cycle!"
    
    suggest_next_version
  end
  
  private
  
  def validate_environment
    # Check if git command exists
    unless system('which git > /dev/null 2>&1')
      puts "❌ Error: Git command not found. Please install Git."
      exit 1
    end
    
    # Check if we're in a git repository
    unless system('git rev-parse --git-dir > /dev/null 2>&1')
      puts "❌ Error: Not in a Git repository. Please run from project root."
      exit 1
    end
    
    # Check if main and dev branches exist
    unless system('git show-ref --verify --quiet refs/heads/main')
      puts "❌ Error: 'main' branch does not exist."
      exit 1
    end
    
    unless system('git show-ref --verify --quiet refs/heads/dev')
      puts "❌ Error: 'dev' branch does not exist."
      exit 1
    end
    
    puts "✅ Environment validation passed"
  end
  
  def suggest_next_version
    current_version = get_current_version
    return unless current_version
    
    parts = current_version.split('.').map(&:to_i)
    patch_version = "#{parts[0]}.#{parts[1]}.#{parts[2] + 1}"
    minor_version = "#{parts[0]}.#{parts[1] + 1}.0"
    
    puts "💡 Next versions:"
    puts "   Patch: #{patch_version} (bug fixes)"
    puts "   Minor: #{minor_version} (new features)"
    puts "🏷️  When ready: bin/release <version>"
  end
end

DevResetManager.new.run
```

**Features:**

- **Hard reset** dev branch to match main exactly
- **Version suggestions** for next development cycle
- **Warning messages** about destructive operations
- **Simple workflow** for post-release cleanup
- **Environment validation** checks Git installation and repository state
- **Branch existence verification** ensures main and dev branches exist
- **Help system** with `--help` flag
- **Detailed status updates** during each operation
- **Error handling** with meaningful exit codes

Usage: `./bin/reset-dev` or `./bin/reset-dev --help`

I am much less proud of this script but it gets the job done. And I got my Ruby groove back doing these rather than just blast out a `bash` or `zsh` shell script. It has been several years since I did **Ruby for Rails** or **Groovy for Grails**. So the syntax needed a bit of time to saturate my brain and get the muscle memory back.

## Lessons Learned

### Ruby vs Python Ecosystem Differences

**Dependency Management**: Bundler's behavior differs significantly from pip/poetry. Frozen lockfiles in CI required careful configuration.

**Documentation**: Ruby lacks Python's autodoc ecosystem. Manual documentation organization was necessary.

**Testing**: Ruby's testing culture emphasizes different patterns than Python's pytest ecosystem.

### GitHub Actions Gotchas

**Permissions**: Token permissions for trusted publishing required specific scopes.

**Timing**: Automated workflows needed careful sequencing and wait conditions.

**Matrix Builds**: Ruby version compatibility testing had unique edge cases.

### Release Automation Benefits

The automated pipeline reduced release time from 2+ hours to 5 minutes:

- **Zero Manual Steps**: Single `bin/release` command
- **Consistent Process**: No forgotten steps or human errors
- **Immediate Feedback**: Automated verification and links
- **Documentation Sync**: Read the Docs builds automatically

## Infrastructure Components

### Final Architecture

```text
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Development   │──▶│  GitHub Actions  │───▶│   RubyGems.org  │
│     Branch      │    │   CI/CD Pipeline │    │   Publication   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  bin/release    │    │  Read the Docs   │    │  GitHub Release │
│     Script      │    │  Documentation   │    │    Creation     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Key Files

- **`.github/workflows/`**: CI/CD pipeline definitions
- **`docs/`**: MkDocs documentation source
- **`bin/release`**: Automated release orchestration
- **`bin/reset-dev`**: Post-release development setup
- **`.readthedocs.yaml`**: Documentation build configuration

## The Payoff

After weeks of infrastructure work, the release process became:

```bash
# Release with full testing:
./bin/release 1.2.0

# Quick patch release (skip tests):
./bin/release 1.2.1 --skip-tests

# Reset dev branch for next cycle:
./bin/reset-dev
```

Two commands handle the complete release cycle:

- PR creation and merging
- Git tagging and pushing
- GitHub release creation
- RubyGems publication
- Documentation updates
- Development branch reset

## Next Steps

In [Part 2](/jekyll-pandoc-exports-plugin-part-2/), I'll cover the actual plugin development - the Jekyll hooks system, Pandoc integration, and technical implementation details that make the automated document exports work.

The infrastructure investment was substantial, but it enabled rapid iteration on the plugin functionality itself. Professional release automation isn't just about convenience - it's about enabling sustainable open-source development.

---

**Resources:**

- [Release Workflow Documentation](https://jekyll-pandoc-exports.readthedocs.io/en/latest/release-process/)
- [GitHub Actions Workflows](https://github.com/mcgarrah/jekyll-pandoc-exports/tree/main/.github/workflows)
- [bin/release Script](https://github.com/mcgarrah/jekyll-pandoc-exports/blob/main/bin/release)
- [Read the Docs Configuration](https://github.com/mcgarrah/jekyll-pandoc-exports/blob/main/.readthedocs.yaml)