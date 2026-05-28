# Security Policy

## Reporting a Vulnerability

This is an experimental research project for prompt optimization. If you discover a security issue, please open an [issue](https://github.com/NullLabTests/grounded_evolution/issues) with the label `security`.

Please **do not** disclose vulnerabilities publicly until they have been addressed.

## Scope

- The `evaluate.py` and `auto_evolve.py` scoring engines — ensure signal injection cannot be exploited.
- Generated content in `generated/` — review before using in production.

## Out of Scope

- This project generates AI agent project skeletons; the output is not validated for security. Use at your own risk.
- Prompt engineering is inherently experimental — no guarantees about safety or correctness of generated code.
