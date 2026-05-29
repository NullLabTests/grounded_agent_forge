# Security Policy

## Reporting a Vulnerability

This is an experimental research project for evolving AI agent architectures. If you discover a security issue, please open an [issue](https://github.com/NullLabTests/grounded_agent_forge/issues) with the label `security`.

Please **do not** disclose vulnerabilities publicly until they have been addressed.

## Scope

- The `agent_forge/` module — ensure generated agent specs cannot produce harmful behavior
- The Docker sandbox — validate that agent execution is properly isolated
- The dashboard — ensure it doesn't expose sensitive evolution data

## Out of Scope

- This project generates AI agent blueprints; the output is experimental and not validated for production use
- Agent blueprint evolution is inherently experimental — no guarantees about safety or correctness of generated agents
- Docker sandbox isolation depends on the host Docker configuration
