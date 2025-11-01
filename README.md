<div align="center">

# Playfile

### Build complete features with AI teams that actually work together

**Define your development workflow once in YAML. Get specialized AI agents that collaborate like a real team.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

```bash
pip install playfile && pf init
```

[Quick Start](#quick-start) • [Examples](#see-it-in-action) • [Documentation](#get-started-now) • [GitHub](https://github.com/sofianedjerbi/playfile)

</div>

---

## 🎯 Why Playfile?

### The Problem

AI assistants are great at coding but **terrible at following process**.

Tools like Claude Code have subagents that *can* delegate to specialists. But they only do it when the main agent *wants to*.

- ❌ The architect might skip writing tests
- ❌ The coder might ignore the spec
- ❌ The reviewer might never run

### The Solution

**Playfile enforces your workflow with rigor.**

- ✅ Every step runs
- ✅ Every agent executes
- ✅ Every validation passes

No shortcuts. No skipped steps. No "forgot to test the edge cases."

**Built for CI/CD and automation** from day one.

## 🚀 How It Works

### 1️⃣ Define specialized agents

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

### 2️⃣ Build multi-agent workflows

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

### 3️⃣ Run and watch them collaborate

```bash
pf run feature --prompt "Add rate limiting to the API"
```

> **The architect** designs the complete solution → **The tester** writes comprehensive tests → **The coder** implements against both spec and tests → **The reviewer** validates the work
>
> Each agent has clear context and a single responsibility.

## ✨ What You Get

### 🎨 Complete implementations
Stop getting half-finished code. Multi-agent workflows ensure every part of the feature gets built: frontend, backend, tests, docs.

### 🔄 Reproducible workflows
Define your process once. Run it anytime. Same workflow, same quality, every time.

### 🎯 Smart context control
Each agent sees exactly what it needs. Specs flow to testers. Tests flow to coders. No information overload, no missing requirements.

### ✅ Built-in validation
Tests must pass. Files must exist. Builds must succeed. Catch issues before they compound.

### 🛠️ Works with your stack
Language-agnostic. Python, TypeScript, Go, Rust, or anything else. Playfile orchestrates the workflow, not the code.

### 📦 Pre-built workflows
TDD, bug fixes, quick iterations, code review pipelines. Start with smart defaults or build your own.

## 📦 Quick Start

```bash
# Install
pip install playfile

# Initialize your project
pf init

# Run a workflow
pf run feature --prompt "Add user authentication"
```

---

## 💡 Example: Building a REST API

**The Prompt:**

```bash
pf run feature --prompt "Add REST API with auth, rate limiting, and OpenAPI docs"
```

**What Happens:**

1. **Architect** → designs the complete system
2. **Tester** → writes comprehensive tests
3. **Coder** → implements everything
4. **Refactorer** → cleans up code quality
5. **Reviewer** → validates best practices

**The result:** Complete API with authentication, rate limiting, comprehensive tests, and OpenAPI documentation. Not just the happy path. Error handling, edge cases, the whole system.

> 💪 One prompt. One run. Complete feature.

## 🎬 See It In Action

Check out **`examples/calc3d`**: a Flask calculator app with 3D rendering, built entirely by Playfile's TDD workflow.

```bash
cd examples/calc3d
pf run feature --prompt "Add calculation history with undo"
```

> Watch how the architect, tester, coder, refactorer, and reviewer collaborate to build a complete, tested feature.

---

## 🤖 Run in CI/CD

Playfile is designed for automation. Here's a GitHub Actions example:

```yaml
name: AI Feature Development
on:
  workflow_dispatch:
    inputs:
      feature_request:
        description: 'Feature to build'
        required: true

jobs:
  build-feature:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install playfile
      - run: pf run feature --prompt "${{ github.event.inputs.feature_request }}"
      - uses: peter-evans/create-pull-request@v5
        with:
          title: "AI: ${{ github.event.inputs.feature_request }}"
```

> 🔥 The workflow runs completely autonomously. **Spec → Test → Implement → Review → PR.** No human intervention.

## 🎯 Built-In Workflows

Run `pf init` and get production-ready workflows:

| Workflow | Command | Pipeline |
|----------|---------|----------|
| **Full TDD cycle** | `pf run feature` | Architect → Tester → Coder → Refactorer → Reviewer |
| **Quick iterations** | `pf run quick` | Coder → Tester → Reviewer |
| **Bug fixes** | `pf run fix` | Debugger → Fix → Validate → Review |

> Plus specialized agents and tool configurations. Use as-is or customize to match your process.

## 🎨 Use Cases

| Use Case | Description |
|----------|-------------|
| 🤖 **Automated feature development** | Run complete TDD cycles in CI (spec, test, implement, review) with no human in the loop |
| 🌙 **Nightly code improvements** | Schedule refactoring, security audits, or performance optimization workflows |
| 🔍 **Pull request validation** | Enforce review workflows on every PR (architecture check, test coverage, code quality) |
| 🔄 **Bulk migrations** | Update APIs, refactor patterns, or migrate dependencies across your entire codebase |
| ⚡ **Development acceleration** | Local workflows that enforce your team's best practices automatically |
| 🛠️ **Custom CI pipelines** | Build any automated development workflow your team needs |

## ⚖️ Playfile vs. Discretionary Subagents

### Other tools (Claude Code, Cursor, etc.)

- ❓ Main agent *can* call specialists
- ❓ Delegation happens *if* agent decides to
- ❌ Steps might get skipped
- ❌ No guarantees about process
- ✅ Great for interactive coding

### Playfile

- ✅ **Enforced workflows**: Every step runs, guaranteed
- ✅ **Mandatory validation**: Tests must pass, builds must succeed
- ✅ **CI-first design**: Run unattended in automation pipelines
- ✅ **Reproducible**: Same input → same process → same output
- ✅ **Auditable**: Track exactly which agent did what, when

> 💡 If you need **rigor, reproducibility, and automation**, Playfile is your tool.

## 🏆 Why Teams Choose Playfile

### 💯 Guaranteed Completeness
Workflows enforce every step (spec, test, implement, review)

### 🔄 CI/CD Native
Designed to run in GitHub Actions, GitLab CI, Jenkins, or any pipeline

### 📊 Reproducible Results
Same workflow definition → identical execution every time

### 🤖 No Human Oversight
Set it and forget it. Workflows run autonomously.

### 📝 Clear Audit Trail
Know exactly which agent did what at each step

### ⚡ Fast & Efficient
Parallel agent execution for maximum speed

---

<div align="center">

## 🚀 Get Started Now

```bash
pip install playfile && pf init
```

**Stop wrestling with single AI agents. Start building with AI teams.**

[![GitHub](https://img.shields.io/badge/GitHub-sofianedjerbi%2Fplayfile-blue?logo=github)](https://github.com/sofianedjerbi/playfile)
[![Issues](https://img.shields.io/badge/Issues-Report%20Bug-red?logo=github)](https://github.com/sofianedjerbi/playfile/issues)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**Documentation:** Coming soon

</div>
