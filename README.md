# Playfile

**Build complete features with AI teams that actually work together.**

Define your development workflow once in YAML. Get specialized AI agents that collaborate like a real team—passing context, validating work, and delivering complete implementations.

## Why Playfile?

AI coding assistants are powerful, but they work alone. One agent tries to be architect, coder, tester, and reviewer all at once. Context gets lost. Requirements get missed. You spend hours prompting for the pieces that were forgotten.

**Playfile orchestrates specialized AI agents into workflows.** Each agent has one job. Each agent gets exactly the context it needs. Together, they deliver what a single agent can't: complete, tested, production-ready features.

```bash
pip install playfile
pf init
pf run feature --prompt "Add user authentication"
```

Watch your AI team spec, test, implement, and review a complete feature—without the back-and-forth.

## How It Works

**1. Define specialized agents**
```yaml
agents:
  - id: architect
    role: "Software Architect"
    model: "claude-sonnet-4"
    instructions: ".play/agents/architect.md"

  - id: coder
    role: "Senior Developer"
    model: "claude-sonnet-4"
```

**2. Build multi-agent workflows**
```yaml
tasks:
  - id: feature
    description: "Full feature development with TDD"
    steps:
      - id: spec
        agent: { use: architect }

      - id: tests
        agent:
          use: tester
          context_from: [spec]  # Tester sees the spec

      - id: implementation
        agent:
          use: coder
          context_from: [spec, tests]  # Coder sees both
        validate:
          command: "pytest"  # Must pass before continuing
```

**3. Run and watch them collaborate**
```bash
pf run feature --prompt "Add rate limiting to the API"
```

The architect designs the complete solution. The tester writes comprehensive tests. The coder implements against both spec and tests. The reviewer validates the work. Each agent has clear context and a single responsibility.

## What You Get

**Complete implementations, not fragments**
Stop getting half-finished code. Multi-agent workflows ensure every part of the feature gets built—frontend, backend, tests, docs.

**Reproducible workflows**
Define your process once. Run it anytime. Same workflow, same quality, every time.

**Smart context control**
Each agent sees exactly what it needs. Specs flow to testers. Tests flow to coders. No information overload, no missing requirements.

**Built-in validation**
Tests must pass. Files must exist. Builds must succeed. Catch issues before they compound.

**Works with your stack**
Language-agnostic. Python, TypeScript, Go, Rust—use any stack. Playfile orchestrates the workflow, not the code.

**Pre-built workflows**
TDD, bug fixes, quick iterations, code review pipelines. Start with smart defaults or build your own.

## Quick Start

```bash
# Install
pip install playfile

# Initialize your project
pf init

# Run a workflow
pf run feature --prompt "Add user authentication"
```

## Example: Building a REST API

**The prompt:**
```bash
pf run feature --prompt "Add REST API with auth, rate limiting, and OpenAPI docs"
```

**What happens:**
1. **Architect** designs the complete system (endpoints, auth flow, rate limit strategy, OpenAPI spec)
2. **Tester** writes tests for auth, rate limiting, all endpoints, and error cases
3. **Coder** implements everything against the spec and tests
4. **Refactorer** cleans up code quality and structure
5. **Reviewer** validates completeness and best practices

**The result:**
Complete API with authentication, rate limiting, comprehensive tests, and OpenAPI documentation. Not just the happy path—error handling, edge cases, the whole system.

One prompt. One run. Complete feature.

## See It In Action

Check out `examples/calc3d`—a Flask calculator app with 3D rendering, built entirely by Playfile's TDD workflow.

```bash
cd examples/calc3d
pf run feature --prompt "Add calculation history with undo"
```

Watch how the architect, tester, coder, refactorer, and reviewer collaborate to build a complete, tested feature.

## Built-In Workflows

Run `pf init` and get production-ready workflows:

**Full TDD cycle**
`pf run feature` → Architect → Tester → Coder → Refactorer → Reviewer

**Quick iterations**
`pf run quick` → Coder → Tester → Reviewer

**Bug fixes**
`pf run fix` → Debugger → Fix → Validate → Review

Plus specialized agents and tool configurations. Use as-is or customize to match your process.

## Use Cases

**Feature development**: Build complete features with tests, docs, and review
**Bug fixes**: Debug, fix, validate, and review with specialized agents
**Code refactoring**: Improve code quality with dedicated refactoring workflows
**API design**: Architect, implement, test, and document APIs end-to-end
**Security audits**: Run security-focused agents on your codebase
**Custom pipelines**: Build any workflow your team needs

## Why Teams Choose Playfile

**No more incomplete features**: Every workflow ensures completeness
**Consistent quality**: Same process, same standards, every time
**Clear accountability**: Know exactly which agent did what
**Faster iterations**: No back-and-forth prompting for missing pieces
**Easy onboarding**: New team members run the same proven workflows

## Get Started Now

```bash
pip install playfile
pf init
```

Stop wrestling with single AI agents. Start building with AI teams.

---

**Questions? Issues?** [GitHub Issues](https://github.com/sofianedjerbi/playfile/issues)
**Documentation:** Coming soon
**License:** MIT
