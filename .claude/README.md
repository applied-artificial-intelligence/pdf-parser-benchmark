# Claude Code Configuration - pdf-bench

This project is configured with Claude Code support for Python development.

## Enabled Plugins

- **system@local** - System utilities (audit, cleanup, setup, status)
- **workflow@local** - Task workflow (explore, plan, next, ship)
- **memory@local** - Memory management, knowledge persistence, handoff
- **development@local** - Development tools (analyze, review, test, fix, run, git operations)

## Available Commands

Run `/help` to see all available commands. Key commands:

- `/explore` - Analyze requirements and create work breakdown
- `/plan` - Create implementation plan
- `/next` - Execute next available task
- `/test` - Run tests or create TDD workflow
- `/review` - Code review and quality analysis

## MCP Servers

- **chrome-devtools** - Browser automation and testing (26 tools)
- **serena** - Semantic code understanding (70-90% token reduction on code tasks)
- **context7** - Up-to-date library documentation access
- **sequential-thinking** - Complex multi-step reasoning

## Permissions

Standard Python permissions configured:
- Allowed: pytest, ruff, mypy, git, python commands
- File operations: Read all common files, write/edit in src/ and tests/
- Denied: Destructive operations (rm -rf, sudo)

## Next Steps

1. Restart Claude Code session to load MCP servers
2. Initialize your project structure (src/, tests/, etc.)
3. Use `/explore` to break down your first task
