# Common Agent Guidelines

## Shell Environment

Your shell is NON-INTERACTIVE. Commands that prompt for input will hang.
- For interactive tools (npm, git, etc), use non-interactive flags or set CI=true
- For background processes, use disown or nohup to prevent hanging
- Examples: `CI=true npm install`, `npm install --yes`, `nohup server &`
