# Project Guidelines

## Code Organization
- playfile.yaml: Main workflow definitions
- .play/: Shared configuration (tools.yaml, agents.yaml)

## Key Patterns
- TDD workflow: RED (tests) -> GREEN (implement) -> REFACTOR
- Multi-agent orchestration: architect -> tester -> coder -> reviewer
- Validation gates with configurable retry logic

## Conventions
- Naming: Task IDs use lowercase (feature, code, bugfix)
- Testing: Post-command validation (commented by default)
- Commands: Customize validate.post_command per project type
