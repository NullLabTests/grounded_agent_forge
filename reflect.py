#!/usr/bin/env python3
import os
import re
from datetime import datetime


def get_current_scores() -> list:
    scores = []
    for f in sorted(os.listdir("population")):
        if f.endswith(".txt"):
            path = os.path.join("population", f)
            raw = open(path).read()
            content = raw.lower()
            s = 30.0

            # Tech stack
            if "ollama" in content: s += 6
            if "local" in content: s += 3
            if "langgraph" in content: s += 5
            if "react" in content or "react loop" in content: s += 3
            if "pydantic" in content: s += 3
            if "httpx" in content: s += 2
            if "rich" in content: s += 2
            if "structlog" in content: s += 2
            if "tenacity" in content: s += 2
            if "tiktoken" in content: s += 1
            if "pytest" in content: s += 2
            if "ruff" in content: s += 1
            if "mypy" in content: s += 1
            if "pre-commit" in content or "precommit" in content: s += 2

            # Quality
            if "pyproject.toml" in content: s += 4
            if "requirements.txt" in content: s += 1
            if "type hint" in content or "type hints" in content: s += 3
            if "error handling" in content: s += 2
            if "logging" in content: s += 2
            if "test" in content or "tests" in content: s += 2
            if "async" in content: s += 2
            if "streaming" in content or "stream" in content: s += 2
            if "retry" in content: s += 2
            if "context window" in content or "context management" in content: s += 2
            if "token tracking" in content or "token count" in content: s += 2
            if "fallback" in content: s += 2
            if "main()" in content or "entrypoint" in content or "__main__" in content: s += 2
            if "asyncio" in content: s += 1
            if "async generator" in content: s += 1
            if "custom exception" in content: s += 1
            if "dataclass" in content: s += 1
            if "enum" in content: s += 1
            if "env" in content and ("example" in content or ".env" in content): s += 2
            if "docker-compose" in content: s += 2
            if "makefile" in content or "taskfile" in content: s += 2
            if ".gitignore" in content or "gitignore" in content: s += 2
            if "docstring" in content: s += 2
            if "parallel" in content or "concurrent" in content: s += 2
            if "rate limit" in content or "ratelimit" in content: s += 2
            if "caching" in content or "cache" in content: s += 2
            if "pydantic" in content and ("setting" in content or "basesetting" in content): s += 2
            if "ci" in content or "github action" in content: s += 2
            if "src/" in content: s += 2
            if "__init__.py" in content: s += 2
            if "dockerfile" in content: s += 2
            if "memory" in content or "persistence" in content: s += 2
            if "session" in content or "conversation" in content: s += 2
            if "tool calling" in content or "function calling" in content: s += 2
            if "coverage" in content or "--cov" in content: s += 2
            if "healthcheck" in content or "health check" in content: s += 2
            if "development" in content and "depend" in content: s += 2
            if "openai" in content and "compatible" in content: s += 2
            if "cli" in content or "command line" in content: s += 2
            if "timeout" in content or "deadline" in content: s += 2
            if "middleware" in content or "interceptor" in content: s += 2
            if "observability" in content or "monitoring" in content or "tracing" in content: s += 2
            if "metrics" in content or "prometheus" in content: s += 2
            if "websocket" in content or "sse" in content or "server-sent" in content: s += 2
            if "safety" in content or "guardrail" in content: s += 2
            if "event" in content and "driven" in content: s += 2
            if "serialization" in content or "serialize" in content: s += 2
            if "state" in content and ("management" in content or "machine" in content): s += 2
            if "multi-turn" in content or "multi-step" in content: s += 2
            if "embedding" in content or "vector" in content: s += 2
            if "rag" in content or "retrieval" in content: s += 2
            if "tokenizer" in content or "tokenize" in content: s += 2
            if "thread" in content and ("safe" in content or "safety" in content): s += 2
            if "validation" in content and ("config" in content or "schema" in content): s += 2
            if "dependency injection" in content or "di" in content: s += 2
            if "callback" in content or "webhook" in content: s += 2
            if "feedback" in content or "self-critique" in content: s += 2
            if "ablation" in content: s += 2
            if "semantic" in content and ("cache" in content or "search" in content): s += 2
            # Security
            if "auth" in content or "authentication" in content: s += 2
            if "api key" in content or "secret" in content: s += 2
            if "sanitization" in content or "sanitize" in content: s += 2
            if "encrypt" in content: s += 2
            # Performance
            if "connection pool" in content or "pooling" in content: s += 2
            if "lazy" in content and ("load" in content or "init" in content): s += 2
            if "background" in content and ("task" in content or "worker" in content): s += 2
            if "batch" in content: s += 2
            if "circuit breaker" in content: s += 2
            # Storage
            if "database" in content or "sqlite" in content or "postgres" in content: s += 2
            if "migration" in content and ("alembic" in content or "db" in content): s += 2
            if "redis" in content: s += 2
            if "file" in content and ("storage" in content or "system" in content): s += 2
            # Testing depth
            if "integration" in content and ("test" in content or "testing" in content): s += 2
            if "e2e" in content or "end-to-end" in content: s += 2
            if "snapshot" in content: s += 2
            if "property" in content and ("test" in content or "based" in content): s += 2
            if "mock" in content or "fixture" in content: s += 2
            # Documentation
            if "sphinx" in content or "mkdocs" in content: s += 2
            if "openapi" in content or "swagger" in content: s += 2
            if "changelog" in content: s += 2
            # Deployment
            if "kubernetes" in content or "k8s" in content: s += 2
            if "systemd" in content or "supervisor" in content: s += 2
            if "health" in content and ("endpoint" in content or "probe" in content): s += 2
            if "graceful" in content and ("shutdown" in content or "signal" in content): s += 2
            # Design patterns
            if "factory" in content: s += 2
            if "strategy" in content: s += 2
            if "observer" in content: s += 2
            if "repository" in content: s += 2
            if "pipeline" in content: s += 2
            # Code quality
            if "cyclomatic" in content: s += 2
            if "coverage" in content and ("threshold" in content or "percent" in content): s += 2
            if "format" in content or "formatter" in content: s += 2
            # Ollama specific
            if "keep_alive" in content or "num_ctx" in content: s += 2
            if "vision" in content or "multimodal" in content: s += 2
            if "mirostat" in content or "top_p" in content or "top_k" in content: s += 2
            # Project files
            if "dockerignore" in content or ".dockerignore" in content: s += 2
            if "editorconfig" in content or ".editorconfig" in content: s += 2
            if "makefile" in content and ("target" in content or "phony" in content): s += 2
            # Streaming
            if "chunk" in content or "delta" in content: s += 2
            # Config
            if "env" in content and ("file" in content or "loader" in content): s += 2
            if "config" in content and ("hierarchical" in content or "multi-env" in content): s += 2
            # LLM/Agent
            if "system prompt" in content or "system message" in content: s += 2
            if "temperature" in content: s += 2
            if "max token" in content: s += 2
            if "stop sequence" in content: s += 2
            if "few shot" in content or "few-shot" in content: s += 2
            if "chain of thought" in content or "cot" in content: s += 2
            if "structured output" in content: s += 2
            if "json mode" in content or "json format" in content: s += 2
            # Observability
            if "opentelemetry" in content or "otel" in content: s += 2
            if "grafana" in content or "datadog" in content: s += 2
            if "alert" in content: s += 2
            if "dashboard" in content: s += 2
            if "log level" in content or "log_level" in content: s += 2
            # Advanced Python
            if "descriptor" in content: s += 2
            if "metaclass" in content: s += 2
            if "abstract" in content and ("class" in content or "base" in content): s += 2
            if "protocol" in content: s += 2
            if "generic" in content or "typevar" in content: s += 2
            if "decorator" in content: s += 2
            if "contextvar" in content: s += 2
            if "weakref" in content: s += 2
            # Networking
            if "rest" in content or "restful" in content: s += 2
            if "graphql" in content: s += 2
            if "grpc" in content: s += 2
            if "oauth" in content: s += 2
            if "jwt" in content: s += 2
            if "cors" in content: s += 2
            # Data
            if "pandas" in content: s += 2
            if "numpy" in content: s += 2
            if "parquet" in content or "feather" in content: s += 2
            if "dataframe" in content: s += 2
            # Testing advanced
            if "benchmark" in content: s += 2
            if "load test" in content or "stress test" in content: s += 2
            if "fuzz" in content: s += 2
            if "regression" in content: s += 2

            # Output
            if "```" in content: s += 3
            if "readme" in content or "README" in raw: s += 2
            if "installable" in content or "pip install" in content: s += 2
            if "runnable" in content or "python -m" in content: s += 2

            # Word count
            words = len(content.split())
            if words > 150: s += 2
            if words > 250: s += 2
            if words > 350: s += 2
            if words > 450: s += 2
            if words > 600: s += 2
            if words > 800: s += 2

            # Pins
            if "==" in content or ">=" in content: s += 2
            if ">=" in content and "0" in content: s += 1
            if re.search(r'>=\s*\d+\.\d+\.\d+', content): s += 2

            scores.append((f, round(min(1000, s), 1)))
    return scores


def reflect():
    scores = get_current_scores()
    scores.sort(key=lambda x: -x[1])

    with open("reflection.md", "a") as f:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        f.write(f"\n## Generation @ {now}\n")
        f.write(f"Population size: {len(scores)}\n\n")

        if scores:
            best_file, best_score = scores[0]
            f.write(f"**Best:** {best_file} ({best_score})\n\n")

            f.write("### Rankings\n")
            for name, s in scores:
                f.write(f"- {name}: {s}\n")

            avg = sum(s for _, s in scores) / len(scores)
            f.write(f"\n**Average:** {avg:.1f}  |  **Max:** {best_score}  |  **Min:** {min(s for _, s in scores)}\n")

            if len(scores) > 1:
                delta = scores[0][1] - scores[1][1]
                f.write(f"**Spread (1st-2nd):** {delta:+.1f}\n")

            f.write("\n### Observations\n")
            top3 = [n for n, _ in scores[:3]]
            top3_content = ""
            for name in top3:
                p = os.path.join("population", name)
                if os.path.exists(p):
                    top3_content += open(p).read()
            top3_lower = top3_content.lower()

            if "auth" in top3_lower or "authentication" in top3_lower:
                f.write("- Auth/security is differentiating top prompts\n")
            if "database" in top3_lower or "postgres" in top3_lower:
                f.write("- Database/storage persistence separates elite prompts\n")
            if "integration" in top3_lower and "test" in top3_lower:
                f.write("- Integration testing depth is a new frontier\n")
            if "kubernetes" in top3_lower or "k8s" in top3_lower:
                f.write("- Kubernetes/container orchestration adds ops readiness\n")
            if "factory" in top3_lower or "strategy" in top3_lower:
                f.write("- Design patterns (factory, strategy) improve architecture\n")
            if "circuit breaker" in top3_lower:
                f.write("- Circuit breaker pattern adds resilience\n")
            if "background" in top3_lower:
                f.write("- Background task/worker support for async operations\n")
            if "openapi" in top3_lower or "swagger" in top3_lower:
                f.write("- OpenAPI/Swagger documentation is emerging\n")
            if "vision" in top3_lower or "multimodal" in top3_lower:
                f.write("- Vision/multimodal model support is forward-looking\n")
            if best_score > 250:
                f.write("- New scoring frontier: breaking past 250\n")

        f.write("\n")


if __name__ == "__main__":
    reflect()
