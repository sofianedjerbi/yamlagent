# Playfile

**Your AI development team, orchestrated in YAML.**

Stop wrestling with single AI agents that forget context or miss requirements. Playfile lets you build workflows where specialized AI agents work together, each one focused on what it does best.

## The Problem

You ask an AI to build a feature. It writes backend code. Tests pass. Ship it!

Then you realize: the frontend is just a placeholder. The AI focused on passing the tests and called it done.

Sound familiar?

## The Solution

Playfile gives you **workflows, not just agents**. An architect designs the complete system. A tester writes comprehensive tests. A coder implements everything from the spec. A reviewer checks the work.

Each agent gets exactly the context it needs. Each one has a clear job. Together, they deliver complete features.

```yaml
tasks:
  - id: feature
    description: "Full feature development with TDD"
    steps:
      - id: spec
        name: "Create technical specification"
        agent:
          use: architect

      - id: tests
        name: "Write tests first"
        agent:
          use: tester
          context_from:
            - spec

      - id: implementation
        name: "Implement complete feature"
        agent:
          use: coder
          context_from:
            - spec
            - tests
        validate:
          command: "pytest"
```

The coder gets both the architect's vision AND the test requirements. It implements the complete spec, not just what makes tests green.

## How It Works

**1. Define your agents**

Agents are AI assistants with specific expertise. A security auditor. A performance optimizer. An API designer. Whatever your team needs.

```yaml
agents:
  - id: architect
    role: "Software Architect"
    model: "claude-sonnet-4"
    instructions: ".play/agents/architect.md"
```

**2. Build workflows**

Chain agents together. Pass context between steps. Add validation checkpoints. Create reproducible development processes.

The original user request flows through every step, so priorities never get lost.

**3. Let them work**

Run your workflow. Watch specialized agents collaborate. Get complete implementations that match your vision.

```bash
pf run feature --prompt "Build a 3D calculator with sound effects"
```

The architect specs out the complete system (backend, frontend, 3D rendering, audio). The tester writes comprehensive tests. The coder implements everything. The reviewer validates quality.

No missing pieces. No surprises.

## Built For Real Development

**TDD workflows out of the box**
Red, green, refactor. With AI agents that understand the full cycle.

**Smart context passing**
Control exactly what context each agent sees. No information overload. No missing requirements.

**Validation at every step**
Run tests after implementation. Check for file existence. Verify builds. Catch issues early.

**Works with your stack**
Python? Node? Rust? Go? Mix them all. Playfile doesn't care about your tech choices.

**Project aware**
Agents explore your codebase first. They learn your patterns, your structure, your conventions.

## Get Started

```bash
# Install
pip install playfile

# Initialize your project
pf init

# Run a workflow
pf run feature --prompt "Add user authentication"
```

Three commands. Complete features.

## What You Can Build

**Development workflows**
Spec → Test → Implement → Refactor → Review

**Bug fixes**
Debug → Root cause → Fix → Validate → Review

**Quick iterations**
Implement → Test → Ship

**Custom pipelines**
Security audits. Performance optimization. Documentation generation. API design. Whatever your process needs.

## Why Playfile

**Reproducible**
Same workflow, same results. Every time.

**Transparent**
See what each agent does. Understand every decision.

**Controllable**
You define the process. Agents follow it.

**Complete**
No more "I forgot the frontend" moments.

**Flexible**
One agent or ten. Simple tasks or complex pipelines. Your choice.

## Real Example

You need a REST API with authentication, rate limiting, and documentation.

**Without Playfile:**
Ask an AI. Get code. Realize it's missing rate limiting. Ask again. Get different code. Lose the auth implementation. Start over.

**With Playfile:**
1. Architect specs the complete system
2. Tester writes tests for auth, rate limits, endpoints
3. Coder implements everything from spec
4. Refactorer cleans up the code
5. Reviewer validates quality

One run. Complete implementation. Nothing missing.

## Smart Defaults

Initialize a project and get:
- TDD workflow (architect → test → implement → refactor → review)
- Quick coding workflow (implement → test → review)
- Bug fix workflow (debug → fix → validate → review)
- Specialized agents (coder, tester, architect, debugger, reviewer)
- Tool configurations (git, language tools, file utilities)

Customize everything or use as is. Your project, your rules.

## See It In Action

Check out `examples/calc3d` for a complete Flask calculator app built with Playfile's TDD workflow.

The example shows:
- Five agent collaboration (architect, tester, coder, refactorer, reviewer)
- Context passing between workflow steps
- Automatic test validation
- Clean architecture implementation
- Complete frontend and backend

Run it yourself:
```bash
cd examples/calc3d
uv sync
python run.py
```

Or build a new feature:
```bash
pf run feature --prompt "Add calculation history"
```

Watch how agents work together to deliver a complete, tested implementation.

## Beyond Single Agents

Single AI agents are powerful. Teams of specialized agents working together? That's transformative.

Stop asking one agent to do everything. Build workflows where each agent excels at their specific role.

Welcome to development orchestration.

```bash
pf init
```

Let's build something complete.
