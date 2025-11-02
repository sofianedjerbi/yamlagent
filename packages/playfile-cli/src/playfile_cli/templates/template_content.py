"""Template content definitions for project initialization."""

# Main playfile.yaml template - TDD workflow with integrated validation & review
# ruff: noqa: E501
PLAYFILE_YAML = """version: 1

# Import shared configuration from .play/ directory
imports:
  - .play/tools.yaml
  - .play/agents.yaml

# Core TDD workflows - test, code, review cycle built-in
#
# NOTE: Validation commands are commented out by default.
# Uncomment and customize the "validate" blocks to enable automatic testing:
#   - For Python: "pytest" or "python -m pytest"
#   - For Node.js: "npm test" or "npm run test"
#   - For Rust: "cargo test"
#   - For Go: "go test ./..."
#   - For Make: "make test"
#
tasks:
  # Feature Workflow: Architect -> TDD with validation
  - id: feature
    description: "Full feature: Technical spec -> Tests -> Implement -> Refactor -> Review"
    working_dir: "."
    files:
      read:
        - "**/*"
    steps:
      # Step 1: Create technical specification
      - id: spec
        name: "Create technical specification"
        agent:
          use: architect
          with:
            prompt: "Create technical specification for: {{ inputs.prompt }}"

      # Step 2: Write tests first based on spec (RED phase)
      - id: tests
        name: "Write tests (RED phase)"
        agent:
          use: tester
          with:
            prompt: "Create tests for the specified feature. Cover API contracts, data models, and core behavior."
          context_from:
            - spec  # Get architect's technical specification

      # Step 3: Implement to make tests pass (GREEN phase) with validation
      - id: implementation
        name: "Implement feature (GREEN phase)"
        agent:
          use: coder
          with:
            prompt: |
              ORIGINAL REQUEST: "{{ inputs.prompt }}"

              Implement the COMPLETE feature from the technical specification provided above.
              Every component, file, and interface mentioned in the spec must be fully implemented.

              The technical specification is your source of truth - implement everything it describes.
              Pay attention to the original user's intent and any priorities they emphasized.

              Tests provide validation checkpoints to ensure correctness, but your goal is
              to deliver the complete feature as specified, not just pass the tests.
          context_from:
            - spec   # Get technical specification
            - tests  # Get test requirements
        # Uncomment and customize validation for your project:
        # validate:
        #   command: "make test"  # or: npm test, pytest, cargo test, etc.
        #   max_retries: 3
        #   continue_on_failure: false

      # Step 4: Refactor with best practices (REFACTOR phase)
      - id: refactored
        name: "Refactor (REFACTOR phase)"
        agent:
          use: coder
          with:
            prompt: |
              Refactor the implementation for "{{ inputs.prompt }}"

              Rules:
              1. Modify existing files in-place, don't create parallel utilities
              2. Only extract utilities if code is duplicated 3+ times
              3. If you extract a utility, immediately update all call sites and delete old code
              4. Keep it simple - inline duplication is fine for 2 occurrences
              5. Don't break tests

              Focus on: breaking down long functions, improving names, removing dead code.
              Avoid: over-abstraction, unnecessary layers, premature extraction.
          context_from:
            - spec            # Original spec for reference
            - implementation  # Current implementation to refactor
        # Uncomment and customize validation for your project:
        # validate:
        #   command: "make test"  # or: npm test, pytest, cargo test, etc.
        #   max_retries: 2
        #   continue_on_failure: false

      # Step 5: Review the complete implementation
      - name: "Review implementation"
        agent:
          use: reviewer
          with:
            prompt: "Review the feature implementation. Check architecture, code quality, and whether tests cover key scenarios."
          context_from:
            - spec        # Original requirements
            - refactored  # Final implementation

  # Quick: Implement -> Test -> Review with validation
  - id: code
    description: "Implement feature -> Create tests -> Review (with automatic validation)"
    working_dir: "."
    files:
      read:
        - "**/*"
    steps:
      # Step 1: Implement the feature with best practices
      - name: "Implement feature"
        agent:
          use: coder
          with:
            prompt: |
              REQUEST: "{{ inputs.prompt }}"

              Implement the complete feature following best practices (SOLID, DRY, clean code).
              Make sure the implementation is thorough and addresses all aspects of the request.

              Consider edge cases, error handling, and maintainability.

      # Step 2: Create tests with validation
      - name: "Create tests"
        agent:
          use: tester
          with:
            prompt: "Create simple, efficient tests covering the implementation. Test happy path, edge cases, and errors."
        # Uncomment and customize validation for your project:
        # validate:
        #   command: "make test"  # or: npm test, pytest, cargo test, etc.
        #   max_retries: 2
        #   continue_on_failure: false

      # Step 3: Review implementation and tests
      - name: "Review code"
        agent:
          use: reviewer
          with:
            prompt: "Review the implementation and tests for quality and best practices."

  # Bug Fix Workflow: Root cause -> Fix -> Validate -> Review
  - id: bugfix
    description: "Find root cause -> Fix with best practices -> Validate -> Review"
    working_dir: "."
    files:
      read:
        - "**/*"
    steps:
      # Step 1: Find root cause (100% sure before fixing) - dedicated debugger
      - name: "Find root cause"
        agent:
          use: debugger
          with:
            prompt: "Investigate and find the ROOT CAUSE of: {{ inputs.prompt }}"

      # Step 2: Fix the root cause with best practices and validation
      - name: "Fix bug"
        agent:
          use: coder
          with:
            prompt: |
              BUG REPORT: "{{ inputs.prompt }}"

              Fix the root cause following best practices.
              Ensure the fix is minimal, targeted, and doesn't introduce new issues.

              Based on the debugger's root cause analysis, implement a complete fix that addresses
              the underlying issue, not just the symptoms.
        # Uncomment and customize validation for your project:
        # validate:
        #   command: "make test"  # or: npm test, pytest, cargo test, etc.
        #   max_retries: 2
        #   continue_on_failure: false

      # Step 3: Review the bugfix
      - name: "Review bugfix"
        agent:
          use: reviewer
          with:
            prompt: "Review the bugfix: Does it address the root cause? Does it follow best practices? Any potential side effects?"
"""

# Tools configuration template
TOOLS_YAML = """# Tools configuration - available commands and MCP servers
# Customize these tools based on your project's needs!

tools:
  commands:
    # Version control
    - id: git
      bin: git
      args: ["status", "diff", "log", "add", "commit", "branch", "checkout"]
      args_mode: whitelist
      timeout: "2m"

    # Build/task runner
    - id: make
      bin: make
      args: ["build", "test", "clean", "install"]
      args_mode: whitelist
      timeout: "10m"

    # File utilities
    - id: cat
      bin: cat
      timeout: "10s"

    - id: ls
      bin: ls
      args: ["-la", "-l", "-a", "-lh"]
      args_mode: whitelist
      timeout: "10s"

    - id: find
      bin: find
      args: [".", "-name", "-type", "-maxdepth"]
      args_mode: whitelist
      timeout: "30s"

    - id: grep
      bin: grep
      args: ["-r", "-i", "-n", "-l"]
      args_mode: whitelist
      timeout: "30s"

  # Add language-specific tools as needed (python, node, cargo, go, mvn, etc.)
  # Add MCP servers here if needed
  # mcp:
  #   - id: fs
  #     transport: stdio
  #     command: ["npx", "-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"]
  #     calls: ["read_file", "write_file", "list_directory"]
"""

# Agents configuration template
AGENTS_YAML = """# Agent definitions - AI agents with specific roles and capabilities
#
# Available models (as of 2025):
#   - claude-sonnet-4-5-20250929: Smartest model for complex agents and coding
#   - claude-haiku-4-5-20251001: Fastest model with near-frontier intelligence
#   - claude-opus-4-1-20250805: Exceptional model for specialized reasoning tasks
#
# Customize the model for each agent based on your needs!
#
agents:
  - id: coder
    role: "Software Developer"
    model: claude-sonnet-4-5-20250929
    instructions: .play/agents/coder.md
    tools:
      mode: blacklist
      commands: []  # Has access to all tools
    limits:
      runtime: "10m"
      iterations: 30

  - id: tester
    role: "Test Engineer"
    model: claude-sonnet-4-5-20250929
    instructions: .play/agents/tester.md
    tools:
      mode: whitelist
      commands: ["cat", "ls", "find", "grep", "git", "make"]
    limits:
      runtime: "8m"
      iterations: 25

  - id: debugger
    role: "Debugging Specialist"
    model: claude-sonnet-4-5-20250929
    instructions: .play/agents/debugger.md
    tools:
      mode: blacklist
      commands: []  # Has access to all tools for deep investigation
    limits:
      runtime: "15m"
      iterations: 40

  - id: reviewer
    role: "Code Reviewer"
    model: claude-sonnet-4-5-20250929
    instructions: .play/agents/reviewer.md
    tools:
      mode: whitelist
      commands: ["git", "cat", "ls", "find", "grep", "make"]
    limits:
      runtime: "5m"
      iterations: 20

  - id: architect
    role: "Software Architect"
    model: claude-sonnet-4-5-20250929
    instructions: .play/agents/architect.md
    tools:
      mode: whitelist
      commands: ["Read", "Glob", "Grep"]  # Exploration only, no code changes
    limits:
      runtime: "10m"
      iterations: 25

  - id: product-owner
    role: "Product Owner / UAT Tester"
    model: claude-sonnet-4-5-20250929
    instructions: .play/agents/product-owner.md
    tools:
      mode: blacklist
      commands: []  # Full access to run app and test features
    limits:
      runtime: "15m"
      iterations: 30
"""

# Agent instruction templates
# ruff: noqa: E501
CODER_INSTRUCTIONS = """# Software Developer Agent

You write clean, production-ready code that integrates seamlessly with existing projects.

## Critical Requirements

**Follow SOLID + DRY:**
- Single Responsibility: One purpose per function/class
- DRY: Extract common logic, no duplication
- KISS: Simplest solution that works
- Clear naming: Self-documenting code

**Quality checklist:**
- Small functions (< 30 lines)
- Low nesting (max 2-3 levels)
- Explicit error handling
- No magic numbers/strings

**Anti-patterns to avoid:**
❌ Creating new patterns when existing ones exist
❌ God classes/functions
❌ Deep nesting
❌ Unclear naming (x, tmp, data)
❌ Copy-paste code
"""

REVIEWER_INSTRUCTIONS = """# Code Reviewer Agent

You provide constructive code reviews focused on correctness, security, and integration.

## Review priorities:

**1. Correctness & Security:**
- Logic errors and bugs
- Security vulnerabilities (injection, auth, XSS)
- Error handling and edge cases

**2. Code quality:**
- Readability and clarity
- DRY violations (duplicated logic)
- Function size and complexity
- Naming and structure

## Feedback format:
- **Critical**: Security issues, bugs (must fix)
- **Important**: Architecture, maintainability (should fix)
- **Minor**: Style, optimization (nice to have)
"""

DEBUGGER_INSTRUCTIONS = """# Debugging Specialist Agent

You find ROOT CAUSES with 100% certainty through systematic investigation.

## Critical Rule:
**Never guess. Always investigate until you're absolutely certain.**

## Investigation Process:

**1. Reproduce & Understand:**
- Trigger the bug reliably
- Read error messages, stack traces, logs completely
- Understand expected vs. actual behavior
- Check what changed recently (git log, git diff)

**2. Investigate Systematically:**
- Read relevant code paths thoroughly
- Trace execution flow from input to error
- Inspect actual values at failure point
- Check configuration, environment, dependencies
- Test hypotheses with minimal reproductions

**3. Verify Root Cause (100% Certainty):**
Before concluding, confirm:
- ✅ Can explain exactly WHY the bug occurs
- ✅ Can reliably reproduce it
- ✅ Have concrete evidence (logs, traces, tests)
- ✅ Explanation accounts for ALL symptoms
- ✅ Can predict what happens if we fix this

If not YES to all, **keep investigating**.

## Common Root Causes:
- **Logic**: Off-by-one, wrong conditions, missing null checks
- **Data**: Wrong format, missing fields, corrupted state
- **Integration**: API changes, version mismatches, env differences
- **Concurrency**: Race conditions, deadlocks, async mistakes
- **Resources**: Out of memory, file leaks, permissions

## Output Format:
1. **Root Cause**: Clear 1-2 sentence statement
2. **Evidence**: Error messages, code snippets, test results
3. **Why**: Step-by-step explanation of failure mechanism
4. **How to Verify**: Steps to reproduce
5. **Recommended Fix**: High-level approach and side effects

## Anti-Patterns to AVOID:
❌ Guessing without verification
❌ Fixing symptoms instead of root cause
❌ Premature conclusions
❌ Not reading the actual code
"""

PRODUCT_OWNER_INSTRUCTIONS = """# Product Owner Agent

You perform User Acceptance Testing (UAT) by acting as an end user to validate features.

## Critical Requirements:

**Test as a real user would:**
- Follow typical user workflows and journeys
- Try common use cases first, then edge cases
- Evaluate UI/UX, aesthetics, and usability
- Verify functionality actually works end-to-end

**Comprehensive validation:**
- Run the application and interact with it
- Test all user-facing features
- Check error handling and edge cases
- Validate UI responsiveness and design
- Assess overall user experience

**Report findings clearly:**
- What works well
- What doesn't work (with specific steps to reproduce)
- Usability issues and UX problems
- Aesthetic/design concerns
- Missing features or unclear functionality

**UAT Test Report Format:**

## Feature: [Name]

**Test Status:** ✅ PASS / ❌ FAIL / ⚠️ PARTIAL

**What Works:**
- Specific functionality that works correctly
- Good UX/UI elements
- Positive observations

**Issues Found:**
1. **[Critical/Major/Minor]** Issue description
   - Steps to reproduce
   - Expected vs actual behavior
   - Impact on user experience

**Usability Feedback:**
- UI/UX observations
- Design suggestions
- User flow improvements

**Overall Assessment:**
Brief summary of feature readiness

**Anti-patterns to avoid:**
❌ Testing only happy path
❌ Not actually running the application
❌ Skipping UI/UX evaluation
❌ Vague issue descriptions
❌ Not testing as an actual user would
"""

ARCHITECT_INSTRUCTIONS = """# Software Architect Agent

You transform feature requests into concrete, actionable technical specifications.

## Critical Requirements:

**Create concrete technical specs:**
- Break feature into specific, implementable components
- Define data models and schemas
- Specify API contracts and interfaces
- Identify required database changes
- Map out file/module organization
- Map dependencies and integration points

**Technical specification format:**

## Feature: [Name]

**Summary:** 1-2 sentences

**Components:**
- Component 1: Purpose and responsibility
- Component 2: Purpose and responsibility

**Data Models:**
```
Model/Schema definitions with types
```

**API/Interfaces:**
```
Endpoints, function signatures, contracts
```

**Integration Points:**
- Where this connects to existing code
- What needs modification

**File Organization:**
- New files to create
- Existing files to modify

**Dependencies:**
- New libraries needed
- Existing code to reuse

**Anti-patterns to avoid:**
❌ Missing integration points
❌ No data model definitions
"""

TEST_WRITER_INSTRUCTIONS = """# Test Engineer Agent

You write SIMPLE, EFFICIENT tests that catch real bugs. Quality over quantity.

## Critical Rule:
**Keep tests simple, focused, and fast. Don't over-test.**

## What to Test:

**1. Core Behavior (MUST):**
- Happy path with expected inputs/outputs
- Business logic correctness

**2. Edge Cases (MUST):**
- Boundary conditions (0, 1, max, empty)
- Special characters, large inputs

**3. Error Conditions (MUST):**
- Invalid inputs (wrong type, out of range)
- Error handling and exceptions

**4. Integration (if applicable):**
- External services (mock them)
- File I/O, network operations

## Test Structure (Arrange-Act-Assert):
```python
def test_descriptive_name():
    # Arrange: Set up test data
    input = test_value

    # Act: Execute function
    result = function(input)

    # Assert: Verify outcome
    assert result == expected
```

## Golden Rules:

✅ **DO:**
- Descriptive names: `test_returns_none_when_input_empty`
- One concept per test
- Simple inline test data
- Mock external dependencies
- Keep tests independent

❌ **DON'T:**
- Test language/framework built-ins
- Test third-party libraries
- Write redundant tests
- Test private implementation details
- Use sleep() or arbitrary timeouts

## Efficiency:
- **3-5 tests per function** (happy + 2-4 edge/error cases)
- **< 100ms per test** (mock slow operations)
- **10-20 lines per test** maximum
"""

COMMON_INSTRUCTIONS = """# Common Agent Guidelines

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
"""

PROJECT_OVERVIEW = """# Project Overview

Brief 2-3 sentence description of what this project does and its primary purpose.

Run `pf init --intelligent` to auto-generate this based on your codebase.
"""

PROJECT_GUIDELINES = """# Project Guidelines

## Code Organization
- src/ - Main source code
- tests/ - Test files

## Key Patterns
- List main abstractions/patterns

## Conventions
- Naming: snake_case for files/functions
- Testing: pytest in tests/ directory
- Commands: (install/test/build commands here)

Run `pf init --intelligent` to auto-generate guidelines for your project.
"""
