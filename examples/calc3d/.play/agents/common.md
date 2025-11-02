# Common Agent Guidelines

## Shell Environment

Your shell is NON-INTERACTIVE. Commands that prompt for input will hang.
- For interactive tools (npm, git, etc), use non-interactive flags or set CI=true
- For background processes, use disown or nohup to prevent hanging
- Examples: `CI=true npm install`, `npm install --yes`, `nohup server &`

## Project Context

**Always explore first:**
- Read existing code to understand patterns, conventions, and architecture
- Identify where new changes fit in the current structure
- Find similar implementations for consistency
- Reuse existing utilities, patterns, and abstractions

**Follow project conventions:**
- Match the project's coding style (naming, formatting, organization)
- Use project's error handling patterns
- Follow established file/module organization
- Respect existing abstractions and interfaces

## Communication

**Be specific and actionable:**
- No vague descriptions
- Provide concrete examples and code snippets
- Reference specific files and line numbers when relevant
- Explain the "why" behind decisions
