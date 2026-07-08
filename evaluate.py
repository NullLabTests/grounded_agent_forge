#!/usr/bin/env python3
import os
import re
import subprocess
from pathlib import Path

def evaluate_generated_project(project_path: str) -> float:
    """Try to actually run the generated project and score it."""
    score = 40.0
    project_path = Path(project_path)
    
    if not project_path.exists():
        return 30.0
    
    # Check for basic structure
    if (project_path / "pyproject.toml").exists() or (project_path / "requirements.txt").exists():
        score += 15
    
    if any((project_path).rglob("*.py")):
        score += 10
    
    # Try to run it (very carefully)
    try:
        # Simple test: can we at least parse the main Python files?
        py_files = list(project_path.rglob("*.py"))[:3]
        for py in py_files:
            result = subprocess.run(
                ["python", "-m", "py_compile", str(py)],
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0:
                score += 8
    except Exception:
        pass
    
    # Bonus for modern tooling
    if (project_path / "pyproject.toml").exists():
        score += 7
    
    return min(100.0, round(score, 1))


def evaluate_population():
    scores = {}
    for f in sorted(os.listdir("population")):
        if f.endswith(".txt"):
            path = os.path.join("population", f)
            with open(path) as file:
                raw = file.read()
            content = raw.lower()
            
            score = 30.0
            
            # --- Tech stack signals ---
            if "ollama" in content:
                score += 6
            if "local" in content:
                score += 3
            if "langgraph" in content:
                score += 5
            if "react" in content or "react loop" in content:
                score += 3
            if "pydantic" in content:
                score += 3
            if "httpx" in content:
                score += 2
            if "rich" in content:
                score += 2
            if "structlog" in content:
                score += 2
            if "tenacity" in content:
                score += 2
            if "tiktoken" in content:
                score += 1
            if "pytest" in content:
                score += 2
            if "ruff" in content:
                score += 1
            if "mypy" in content:
                score += 1
            if "pre-commit" in content or "precommit" in content:
                score += 2
            
            # --- Quality signals ---
            if "pyproject.toml" in content:
                score += 4
            if "requirements.txt" in content:
                score += 1
            if "type hint" in content or "type hints" in content:
                score += 3
            if "error handling" in content:
                score += 2
            if "logging" in content:
                score += 2
            if "test" in content or "tests" in content:
                score += 2
            if "async" in content:
                score += 2
            if "streaming" in content or "stream" in content:
                score += 2
            if "retry" in content:
                score += 2
            if "context window" in content or "context management" in content:
                score += 2
            if "token tracking" in content or "token count" in content:
                score += 2
            if "fallback" in content:
                score += 2
            if "main()" in content or "entrypoint" in content or "__main__" in content:
                score += 2
            if "asyncio" in content:
                score += 1
            if "async generator" in content:
                score += 1
            if "custom exception" in content:
                score += 1
            if "dataclass" in content:
                score += 1
            if "enum" in content:
                score += 1
            if "env" in content and ("example" in content or ".env" in content):
                score += 2
            if "docker-compose" in content:
                score += 2
            if "makefile" in content or "taskfile" in content:
                score += 2
            if ".gitignore" in content or "gitignore" in content:
                score += 2
            if "docstring" in content:
                score += 2
            if "parallel" in content or "concurrent" in content:
                score += 2
            if "rate limit" in content or "ratelimit" in content:
                score += 2
            if "caching" in content or "cache" in content:
                score += 2
            if "pydantic" in content and ("setting" in content or "basesetting" in content):
                score += 2
            if "ci" in content or "github action" in content or "gitlab ci" in content:
                score += 2
            if "src/" in content:
                score += 2
            if "__init__.py" in content:
                score += 2
            if "dockerfile" in content:
                score += 2
            if "memory" in content or "persistence" in content:
                score += 2
            if "session" in content or "conversation" in content:
                score += 2
            if "tool calling" in content or "function calling" in content:
                score += 2
            if "coverage" in content or "--cov" in content:
                score += 2
            if "healthcheck" in content or "health check" in content:
                score += 2
            if "development" in content and "depend" in content:
                score += 2
            if "openai" in content and "compatible" in content:
                score += 2
            if "cli" in content or "command line" in content:
                score += 2
            if "timeout" in content or "deadline" in content:
                score += 2
            if "middleware" in content or "interceptor" in content:
                score += 2
            if "observability" in content or "monitoring" in content or "tracing" in content:
                score += 2
            if "metrics" in content or "prometheus" in content:
                score += 2
            if "websocket" in content or "sse" in content or "server-sent" in content:
                score += 2
            if "safety" in content or "guardrail" in content:
                score += 2
            if "event" in content and "driven" in content:
                score += 2
            if "serialization" in content or "serialize" in content:
                score += 2
            if "state" in content and ("management" in content or "machine" in content):
                score += 2
            if "multi-turn" in content or "multi-step" in content:
                score += 2
            if "embedding" in content or "vector" in content:
                score += 2
            if "rag" in content or "retrieval" in content:
                score += 2
            if "tokenizer" in content or "tokenize" in content:
                score += 2
            if "thread" in content and ("safe" in content or "safety" in content):
                score += 2
            if "validation" in content and ("config" in content or "schema" in content):
                score += 2
            if "dependency injection" in content or "di" in content:
                score += 2
            if "callback" in content or "webhook" in content:
                score += 2
            if "feedback" in content or "self-critique" in content:
                score += 2
            if "ablation" in content:
                score += 2
            if "semantic" in content and ("cache" in content or "search" in content):
                score += 2
            
            # --- Security & Auth ---
            if "auth" in content or "authentication" in content:
                score += 2
            if "api key" in content or "secret" in content:
                score += 2
            if "sanitization" in content or "sanitize" in content:
                score += 2
            if "encrypt" in content:
                score += 2
            
            # --- Performance ---
            if "connection pool" in content or "pooling" in content:
                score += 2
            if "lazy" in content and ("load" in content or "init" in content):
                score += 2
            if "background" in content and ("task" in content or "worker" in content):
                score += 2
            if "batch" in content:
                score += 2
            if "circuit breaker" in content:
                score += 2
            
            # --- Storage ---
            if "database" in content or "sqlite" in content or "postgres" in content:
                score += 2
            if "migration" in content and ("alembic" in content or "db" in content):
                score += 2
            if "redis" in content:
                score += 2
            if "file" in content and ("storage" in content or "system" in content):
                score += 2
            
            # --- Testing depth ---
            if "integration" in content and ("test" in content or "testing" in content):
                score += 2
            if "e2e" in content or "end-to-end" in content:
                score += 2
            if "snapshot" in content:
                score += 2
            if "property" in content and ("test" in content or "based" in content):
                score += 2
            if "mock" in content or "fixture" in content:
                score += 2
            
            # --- Documentation ---
            if "sphinx" in content or "mkdocs" in content:
                score += 2
            if "openapi" in content or "swagger" in content:
                score += 2
            if "changelog" in content:
                score += 2
            
            # --- Deployment & Ops ---
            if "kubernetes" in content or "k8s" in content:
                score += 2
            if "systemd" in content or "supervisor" in content:
                score += 2
            if "health" in content and ("endpoint" in content or "probe" in content):
                score += 2
            if "graceful" in content and ("shutdown" in content or "signal" in content):
                score += 2
            if "dependabot" in content or "renovate" in content:
                score += 2
            
            # --- Design Patterns ---
            if "factory" in content:
                score += 2
            if "strategy" in content:
                score += 2
            if "observer" in content:
                score += 2
            if "repository" in content:
                score += 2
            if "pipeline" in content:
                score += 2
            
            # --- Advanced Code Quality ---
            if "cyclomatic" in content:
                score += 2
            if "coverage" in content and ("threshold" in content or "percent" in content):
                score += 2
            if "format" in content or "formatter" in content:
                score += 2
            
            # --- Ollama/Model Specific ---
            if "keep_alive" in content or "num_ctx" in content:
                score += 2
            if "vision" in content or "multimodal" in content:
                score += 2
            if "mirostat" in content or "top_p" in content or "top_k" in content:
                score += 2
            
            # --- Project files ---
            if "dockerignore" in content or ".dockerignore" in content:
                score += 2
            if "editorconfig" in content or ".editorconfig" in content:
                score += 2
            if "dependabot" in content or "renovate" in content:
                score += 2
            if "makefile" in content and ("target" in content or "phony" in content):
                score += 2
            
            # --- Streaming / Real-time ---
            if "chunk" in content or "delta" in content:
                score += 2
            
            # --- Configuration ---
            if "env" in content and ("file" in content or "loader" in content):
                score += 2
            if "config" in content and ("hierarchical" in content or "multi-env" in content):
                score += 2
            
            # --- LLM/Agent Specific ---
            if "system prompt" in content or "system message" in content:
                score += 2
            if "temperature" in content:
                score += 2
            if "max token" in content:
                score += 2
            if "stop sequence" in content:
                score += 2
            if "few shot" in content or "few-shot" in content:
                score += 2
            if "chain of thought" in content or "cot" in content:
                score += 2
            if "structured output" in content:
                score += 2
            if "json mode" in content or "json format" in content:
                score += 2
            
            # --- Observability depth ---
            if "opentelemetry" in content or "otel" in content:
                score += 2
            if "grafana" in content or "datadog" in content:
                score += 2
            if "alert" in content:
                score += 2
            if "dashboard" in content:
                score += 2
            if "log level" in content or "log_level" in content:
                score += 2
            
            # --- Advanced Python ---
            if "descriptor" in content:
                score += 2
            if "metaclass" in content:
                score += 2
            if "abstract" in content and ("class" in content or "base" in content):
                score += 2
            if "protocol" in content:
                score += 2
            if "generic" in content or "typevar" in content:
                score += 2
            if "decorator" in content:
                score += 2
            if "contextvar" in content:
                score += 2
            if "weakref" in content:
                score += 2
            
            # --- Networking/API ---
            if "rest" in content or "restful" in content:
                score += 2
            if "graphql" in content:
                score += 2
            if "grpc" in content:
                score += 2
            if "oauth" in content:
                score += 2
            if "jwt" in content:
                score += 2
            if "cors" in content:
                score += 2
            
            # --- Data Processing ---
            if "pandas" in content:
                score += 2
            if "numpy" in content:
                score += 2
            if "parquet" in content or "feather" in content:
                score += 2
            if "dataframe" in content:
                score += 2
            
            # --- Advanced Testing ---
            if "benchmark" in content:
                score += 2
            if "load test" in content or "stress test" in content:
                score += 2
            if "fuzz" in content:
                score += 2
            if "regression" in content:
                score += 2
            
            # --- Output structure ---
            if "```" in content:
                score += 3
            if "." in raw and ("readme" in content or "README" in raw):
                score += 2
            if "installable" in content or "pip install" in content:
                score += 2
            if "runnable" in content or "python -m" in content:
                score += 2
            
            # --- Comprehensiveness ---
            words = len(content.split())
            if words > 150:
                score += 2
            if words > 250:
                score += 2
            if words > 350:
                score += 2
            if words > 450:
                score += 2
            if words > 600:
                score += 2
            if words > 800:
                score += 2
            if words > 1000:
                score += 2

            # --- Advanced Architecture ---
            if "plugin" in content or "extension" in content:
                score += 2
            if "multiprocessing" in content or "distributed" in content:
                score += 2
            if "cqrs" in content or "event sourcing" in content:
                score += 2
            if "api version" in content or "versioning" in content:
                score += 2
            if "service mesh" in content or "istio" in content or "linkerd" in content:
                score += 2
            if "feature flag" in content or "toggle" in content:
                score += 2
            if "canary" in content or "blue-green" in content or "rolling update" in content:
                score += 2

            # --- ML/AI Depth ---
            if "fine-tune" in content or "finetune" in content:
                score += 2
            if "lora" in content or "qlora" in content or "peft" in content:
                score += 2
            if "prompt template" in content or "jinja" in content or "mustache" in content:
                score += 2
            if "beam search" in content or "sampling" in content:
                score += 2
            if "classifier" in content or "classification" in content:
                score += 2
            if "sentiment" in content or "ner" in content or "entity extraction" in content:
                score += 2
            if "summarization" in content or "summarize" in content:
                score += 2
            if "translation" in content or "translate" in content:
                score += 2
            if "question answering" in content or "qa" in content:
                score += 2

            # --- Monitoring & Error Tracking ---
            if "sentry" in content or "rollbar" in content or "error tracking" in content:
                score += 2
            if "datadog" in content and ("apm" in content or "trace" in content):
                score += 2
            if "elk" in content or "elasticsearch" in content or "kibana" in content:
                score += 2
            if "loki" in content or "promtail" in content:
                score += 2
            if "jaeger" in content or "tempo" in content:
                score += 2
            if "pagerduty" in content or "opsgenie" in content or "incident" in content:
                score += 2
            if "slo" in content or "sli" in content or "sla" in content:
                score += 2

            # --- Testing Specific ---
            if "pytest-cov" in content or "pytest-cov" in content:
                score += 2
            if "pytest-asyncio" in content or "pytest-asyncio" in content:
                score += 2
            if "tox" in content or "nox" in content:
                score += 2
            if "mutation testing" in content or "mutmut" in content or "pytest-mutagen" in content:
                score += 2
            if "contract test" in content or "pact" in content:
                score += 2

            # --- Security Depth ---
            if "rbac" in content or "role-based" in content:
                score += 2
            if "mfa" in content or "2fa" in content or "multi-factor" in content:
                score += 2
            if "sso" in content or "saml" in content or "oidc" in content:
                score += 2
            if "csrf" in content or "xss" in content or "injection" in content:
                score += 2
            if "csp" in content or "content security" in content or "helmet" in content:
                score += 2
            if "certificate" in content or "tls" in content or "ssl" in content:
                score += 2
            if "hsm" in content or "vault" in content or "key management" in content:
                score += 2

            # --- DevOps & Infrastructure ---
            if "terraform" in content or "pulumi" in content or "iac" in content:
                score += 2
            if "ansible" in content or "chef" in content or "puppet" in content:
                score += 2
            if "helm" in content or "chart" in content:
                score += 2
            if "argo" in content or "flux" in content or "gitops" in content:
                score += 2
            if "hpa" in content or "horizontal pod autoscale" in content or "pod disruption" in content:
                score += 2
            if "service account" in content or "serviceaccount" in content:
                score += 2
            if "ingress" in content or "load balancer" in content:
                score += 2
            if "configmap" in content or "config map" in content or "secret" in content:
                score += 2

            # --- API & Integration Depth ---
            if "rest api" in content or "rest endpoint" in content or "restful api" in content:
                score += 2
            if "webhook" in content and ("signature" in content or "verify" in content):
                score += 2
            if "asyncapi" in content or "async api" in content:
                score += 2
            if "grpc" in content and ("proto" in content or "protobuf" in content):
                score += 2
            if "graphql" in content and ("schema" in content or "resolver" in content or "query" in content):
                score += 2

            # --- Observability Depth ---
            if "distributed tracing" in content or "trace id" in content:
                score += 2
            if "span" in content and ("trace" in content or "parent" in content):
                score += 2
            if "metrics" in content and ("histogram" in content or "counter" in content or "gauge" in content or "summary" in content):
                score += 2
            if "grafana" in content and ("dashboard" in content or "datasource" in content or "panel" in content):
                score += 2
            if "structured logging" in content or "json logging" in content:
                score += 2

            # --- Data Pipeline ---
            if "etl" in content or "elt" in content:
                score += 2
            if "data pipeline" in content or "data processing" in content:
                score += 2
            if "stream" in content and ("process" in content or "analytics" in content):
                score += 2
            if "olap" in content or "oltp" in content:
                score += 2
            if "data warehouse" in content or "data lake" in content or "data mart" in content:
                score += 2
            if "redshift" in content or "bigquery" in content or "snowflake" in content or "clickhouse" in content:
                score += 2

            # --- Performance & Reliability ---
            if "load balanc" in content:
                score += 2
            if "auto-scaling" in content or "autoscale" in content or "autoscaling" in content:
                score += 2
            if "chaos" in content or "chaos engineering" in content:
                score += 2
            if "disaster recovery" in content or "dr" in content:
                score += 2
            if "backup" in content and ("restore" in content or "recovery" in content):
                score += 2

            # --- Specificity: mentions concrete versions/pins ---
            if "==" in content or ">=" in content:
                score += 2
            if ">=" in content and "0" in content:
                score += 1
            if re.search(r'>=\s*\d+\.\d+\.\d+', content):
                score += 2

            # --- Document structure depth ---
            paragraphs = content.count("\n\n")
            if paragraphs > 30: score += 2
            if paragraphs > 60: score += 2
            if paragraphs > 100: score += 2
            if paragraphs > 150: score += 2

            # --- Code block coverage ---
            code_blocks = len(re.findall(r"```(\w+)", raw))
            if code_blocks > 10: score += 2
            if code_blocks > 20: score += 2
            if code_blocks > 40: score += 2

            # --- Technology diversity ---
            tech_mentions = sum(1 for t in ["ollama", "langgraph", "pydantic", "httpx", "rich",
                "structlog", "tenacity", "tiktoken", "pytest", "ruff", "mypy",
                "pre-commit", "sqlalchemy", "alembic", "redis", "docker",
                "kubernetes", "k8s", "fastapi", "uvicorn", "opentelemetry",
                "grafana", "prometheus", "cryptography", "pandas", "numpy",
                "sphinx", "mkdocs", "github actions", "hypothesis",
                "datadog", "sentry", "elasticsearch", "kibana", "helm",
                "terraform", "ansible", "argocd", "jaeger"] if t in content)
            if tech_mentions > 20: score += 3
            if tech_mentions > 30: score += 3

            
            if "sequence diagram" in content or "plantuml" in content or "mermaid" in content:
                score += 2
            
            if "keepalive" in content or "keep alive" in content:
                score += 2
            
            if "pprof" in content:
                score += 2
            
            if "index" in content and ("database" in content or "sql" in content or "query" in content):
                score += 2
            
            if "idle" in content and ("timeout" in content or "connection" in content):
                score += 2
            
            if "healthz" in content or "readyz" in content or "livez" in content:
                score += 2
            
            if "asyncio.lock" in content or "asyncio.Lock" in content:
                score += 2
            
            if "code of conduct" in content or "conduct.md" in content:
                score += 2
            
            if "connection string" in content or "dsn" in content:
                score += 2
            
            if "conventional commit" in content:
                score += 2
            
            if "parametrize" in content or "parameterize" in content:
                score += 2
            
            if "debug" in content and ("endpoint" in content or "mode" in content or "profile" in content):
                score += 2
            
            if "extras" in content and ("require" in content or "depend" in content):
                score += 2
            
            if "compression" in content or "gzip" in content or "deflate" in content:
                score += 2
            
            if "adr" in content or "architecture decision" in content:
                score += 2
            
            if "audit" in content and ("log" in content or "trail" in content):
                score += 2
            
            if "read replica" in content or "replica" in content:
                score += 2
            
            if "bulkhead" in content or "bulk head" in content:
                score += 2
            
            if "build matrix" in content or "matrix" in content:
                score += 2
            
            if "refresh token" in content or "token refresh" in content:
                score += 2
            
            if "hsts" in content or "strict-transport" in content:
                score += 2
            
            if "contributing" in content or "contributing.md" in content:
                score += 2
            
            if "approval" in content or "approvaltest" in content:
                score += 2
            
            if "semantic release" in content or "semantic-release" in content:
                score += 2
            
            if "brotli" in content or "zstd" in content:
                score += 2
            
            if "seccomp" in content or "apparmor" in content:
                score += 2
            
            if "correlation" in content and ("id" in content or "header" in content):
                score += 2
            
            if "proxy" in content and ("http" in content or "https" in content):
                score += 2
            
            if "asyncio.queue" in content or "asyncio.Queue" in content:
                score += 2
            
            if "dns" in content and ("resolve" in content or "lookup" in content):
                score += 2
            
            if "content-type" in content or "content type" in content:
                score += 2
            
            if "pagination" in content:
                score += 2
            
            if "conftest" in content:
                score += 2
            
            if "non-root" in content or "nonroot" in content:
                score += 2
            
            if "artifact" in content and ("upload" in content or "download" in content):
                score += 2
            
            if "asyncio.semaphore" in content or "asyncio.Semaphore" in content:
                score += 2
            
            if "entry_point" in content or "console_script" in content:
                score += 2
            
            if "c4" in content and ("model" in content or "diagram" in content):
                score += 2
            
            if "sharding" in content or "shard" in content:
                score += 2
            
            if "pod security" in content or "psp" in content or "psa" in content:
                score += 2
            
            if "readonly" in content and ("rootfs" in content or "filesystem" in content):
                score += 2
            
            if "golden" in content and ("file" in content or "test" in content):
                score += 2
            
            if "securitycontext" in content or "security context" in content:
                score += 2
            
            if "langchain" in content:
                score += 2

            
            if "a/b test" in content or "ab test" in content:
                score += 2

            
            if "clerk" in content:
                score += 2

            
            if "edge caching" in content:
                score += 2

            
            if "webgpu" in content:
                score += 2

            
            if "appdynamics" in content or "appdynamics" in content:
                score += 2

            
            if "pci" in content or "pci dss" in content:
                score += 2

            
            if "cloudflare" in content or "cloudflare workers" in content:
                score += 2

            
            if "supabase" in content or "neon" in content or "planetscale" in content:
                score += 2

            
            if "consul" in content:
                score += 2

            
            if "itertools" in content:
                score += 2

            
            if "content negotiation" in content:
                score += 2

            
            if "yarn" in content and ("berry" in content or "pnp" in content):
                score += 2

            
            if "twilio" in content:
                score += 2

            
            if "webpush" in content or "web push" in content:
                score += 2

            
            if "webxr" in content or "webxr" in content:
                score += 2

            
            if "classmethod" in content or "staticmethod" in content:
                score += 2

            
            if "abstractmethod" in content:
                score += 2

            
            if "bundle" in content and ("size" in content or "analyzer" in content):
                score += 2

            
            if "packer" in content:
                score += 2

            
            if "apisix" in content:
                score += 2

            
            if "kafka" in content:
                score += 2

            
            if "buildkite" in content:
                score += 2

            
            if "mediator" in content:
                score += 2

            
            if "distributed lock" in content or "redlock" in content:
                score += 2

            
            if "template method" in content:
                score += 2

            
            if "ambassador" in content or "emissary" in content:
                score += 2

            
            if "ip whitelist" in content or "ip allowlist" in content or "ip block" in content:
                score += 2

            
            if "pwa" in content or "progressive web" in content:
                score += 2

            
            if "preload" in content or "prefetch" in content or "preconnect" in content:
                score += 2

            
            if "unicode" in content or "utf" in content:
                score += 2

            
            if "new relic" in content or "newrelic" in content:
                score += 2

            
            if "resend" in content:
                score += 2

            
            if "bridge" in content:
                score += 2

            
            if "svelte" in content or "sveltekit" in content:
                score += 2

            
            if "onion" in content:
                score += 2

            
            if "webtransport" in content:
                score += 2

            
            if "openid" in content:
                score += 2

            
            if "scim" in content:
                score += 2

            
            if "json-ld" in content or "jsonld" in content:
                score += 2

            
            if "turborepo" in content or "turbo" in content:
                score += 2

            
            if "pluralization" in content or "plural" in content:
                score += 2

            
            if "atexit" in content:
                score += 2

            
            if "vitest" in content:
                score += 2

            
            if "geolocation" in content or "geo-restrict" in content:
                score += 2

            
            if "hexagonal" in content or "ports and adapters" in content:
                score += 2

            
            if "config override" in content:
                score += 2

            
            if "step function" in content or "stepfunction" in content:
                score += 2

            
            if "vector database" in content or "pinecone" in content or "weaviate" in content or "qdrant" in content:
                score += 2

            
            if "image optimization" in content or "image optimize" in content:
                score += 2

            
            if "schema.org" in content or "schema org" in content:
                score += 2

            
            if "selenium" in content:
                score += 2

            
            if "flyweight" in content:
                score += 2

            
            if "tree shaking" in content or "treeshaking" in content:
                score += 2

            
            if "rss" in content or "atom" in content:
                score += 2

            
            if "lcp" in content or "largest contentful" in content:
                score += 2

            
            if "hierarchical config" in content:
                score += 2

            
            if "concurrency limit" in content or "concurrency control" in content:
                score += 2

            
            if "shadcn" in content or "radix" in content:
                score += 2

            
            if "__slots__" in content:
                score += 2

            
            if "webassembly" in content or "wasm" in content:
                score += 2

            
            if "metabase" in content or "redash" in content:
                score += 2

            
            if "edge function" in content or "edge compute" in content:
                score += 2

            
            if "setuptools" in content:
                score += 2

            
            if "webgl" in content:
                score += 2

            
            if "rum" in content or "real user" in content:
                score += 2

            
            if "dynatrace" in content:
                score += 2

            
            if "cassandra" in content or "scylla" in content:
                score += 2

            
            if "config defaults" in content:
                score += 2

            
            if "gdpr" in content:
                score += 2

            
            if "docusaurus" in content:
                score += 2

            
            if "airflow" in content:
                score += 2

            
            if "sigNoz" in content or "signoz" in content:
                score += 2

            
            if "nats" in content or "nats.io" in content:
                score += 2

            
            if "sitemap" in content:
                score += 2

            
            if "flask admin" in content or "sqladmin" in content:
                score += 2

            
            if "file upload" in content:
                score += 2

            
            if "admin panel" in content or "admin dashboard" in content:
                score += 2

            
            if "pulsar" in content:
                score += 2

            
            if "storybook" in content:
                score += 2

            
            if "sparql" in content:
                score += 2

            
            if "fluentd" in content or "fluentbit" in content:
                score += 2

            
            if "mqtt" in content:
                score += 2

            
            if "direnv" in content:
                score += 2

            
            if "setup.py" in content:
                score += 2

            
            if "zeromq" in content or "zmq" in content:
                score += 2

            
            if "waf" in content or "web application firewall" in content:
                score += 2

            
            if "saga" in content or "saga pattern" in content:
                score += 2

            
            if "setup.cfg" in content:
                score += 2

            
            if "changeset" in content:
                score += 2

            
            if "pytorch" in content:
                score += 2

            
            if "accessibility" in content or "a11y" in content:
                score += 2

            
            if "config validation" in content:
                score += 2

            
            if "pub/sub" in content or "pubsub" in content:
                score += 2

            
            if "sonatype" in content or "nexus" in content:
                score += 2

            
            if "data retention" in content or "data purge" in content:
                score += 2

            
            if "zipkin" in content:
                score += 2

            
            if "mailgun" in content:
                score += 2

            
            if "throttle" in content or "throttling" in content:
                score += 2

            
            if "adyen" in content:
                score += 2

            
            if "timescaledb" in content or "influxdb" in content:
                score += 2

            
            if "mlflow" in content:
                score += 2

            
            if "chromadb" in content or "chroma" in content:
                score += 2

            
            if "magic link" in content:
                score += 2

            
            if "fargate" in content or "ecs" in content:
                score += 2

            
            if "load shedding" in content:
                score += 2

            
            if "playwright" in content:
                score += 2

            
            if "nextauth" in content or "next-auth" in content:
                score += 2

            
            if "iterator" in content:
                score += 2

            
            if "readthedocs" in content or "read the docs" in content:
                score += 2

            
            if "__new__" in content:
                score += 2

            
            if "hipaa" in content:
                score += 2

            
            if "passwordless" in content:
                score += 2

            
            if "celery" in content:
                score += 2

            
            if "outbox" in content or "transactional outbox" in content:
                score += 2

            
            if "twelve factor" in content or "12 factor" in content:
                score += 2

            
            if "autogen" in content or "autogen" in content:
                score += 2

            
            if "superset" in content:
                score += 2

            
            if "composite" in content:
                score += 2

            
            if "zero trust" in content:
                score += 2

            
            if "tensorflow" in content:
                score += 2

            
            if "apache spark" in content or "pyspark" in content:
                score += 2

            
            if "rtl" in content or "right-to-left" in content:
                score += 2

            
            if "square" in content:
                score += 2

            
            if "typedoc" in content:
                score += 2

            
            if "telegram" in content:
                score += 2

            
            if "invoice" in content:
                score += 2

            
            if "jest" in content:
                score += 2

            
            if "memento" in content:
                score += 2

            
            if "ldap" in content or "active directory" in content:
                score += 2

            
            if "pyright" in content or "basedpyright" in content:
                score += 2

            
            if "neo4j" in content or "graph database" in content:
                score += 2

            
            if "wheel" in content:
                score += 2

            
            if "chain of responsibility" in content:
                score += 2

            
            if "terragrunt" in content:
                score += 2

            
            if "semantic web" in content:
                score += 2

            
            if "data seed" in content or "seeding" in content:
                score += 2

            
            if "alertmanager" in content:
                score += 2

            
            if "inversion of control" in content or "ioc" in content:
                score += 2

            
            if "notebook" in content:
                score += 2

            
            if "trpc" in content:
                score += 2

            
            if "minio" in content or "s3" in content or "object storage" in content:
                score += 2

            
            if "sendgrid" in content:
                score += 2

            
            if "discord" in content:
                score += 2

            
            if "hadoop" in content:
                score += 2

            
            if "flit" in content:
                score += 2

            
            if "jfrog" in content or "artifactory" in content:
                score += 2

            
            if "vonage" in content:
                score += 2

            
            if "pnpm" in content:
                score += 2

            
            if "firestore" in content or "firebase" in content:
                score += 2

            
            if "dynamodb" in content or "dynamo" in content:
                score += 2

            
            if "lerna" in content:
                score += 2

            
            if "data anonymization" in content or "anonymize" in content:
                score += 2

            
            if "ccpa" in content:
                score += 2

            
            if "monolith" in content or "modular monolith" in content:
                score += 2

            
            if "kong" in content:
                score += 2

            
            if "splunk" in content:
                score += 2

            
            if "aria" in content or "wai" in content:
                score += 2

            
            if "jupyter" in content:
                score += 2

            
            if "transformers" in content and ("huggingface" in content or "hf" in content):
                score += 2

            
            if "facade" in content:
                score += 2

            
            if "wandb" in content or "weights and biases" in content:
                score += 2

            
            if "namedtuple" in content or "named tuple" in content:
                score += 2

            
            if "backpressure" in content or "back pressure" in content:
                score += 2

            
            if "concurrent.futures" in content or "threadpoolexecutor" in content or "processpoolexecutor" in content:
                score += 2

            
            if "jenkins" in content:
                score += 2

            
            if "soc2" in content or "soc 2" in content:
                score += 2

            
            if "cffi" in content or "cython" in content:
                score += 2

            
            if "avro" in content:
                score += 2

            
            if "paypal" in content:
                score += 2

            
            if "dagster" in content:
                score += 2

            
            if "railway" in content or "render" in content:
                score += 2

            
            if "model serving" in content or "model deployment" in content:
                score += 2

            
            if "anthropic" in content or "claude" in content:
                score += 2

            
            if "sox" in content or "sarbanes" in content:
                score += 2

            
            if "vllm" in content:
                score += 2

            
            if "domain driven" in content or "ddd" in content:
                score += 2

            
            if "service worker" in content:
                score += 2

            
            if "semantic version" in content or "semver" in content:
                score += 2

            
            if "circleci" in content or "circle ci" in content:
                score += 2

            
            if "contextlib" in content:
                score += 2

            
            if "event driven" in content or "event-driven" in content:
                score += 2

            
            if "pdoc" in content:
                score += 2

            
            if "sqs" in content or "snss" in content:
                score += 2

            
            if "kotlin" in content or "jetpack" in content:
                score += 2

            
            if "model context protocol" in content or "mcp" in content:
                score += 2

            
            if "sidecar" in content:
                score += 2

            
            if "blockchain" in content:
                score += 2

            
            if "yaml" in content:
                score += 2

            
            if "smoke test" in content:
                score += 2

            
            if "aws lambda" in content or "lambda function" in content:
                score += 2

            
            if "react native" in content or "reactnative" in content:
                score += 2

            
            if "webrtc" in content:
                score += 2

            
            if "crewai" in content or "crew" in content:
                score += 2

            
            if "azure" in content:
                score += 2

            
            if "functools" in content:
                score += 2

            
            if "axe" in content or "lighthouse" in content or "pa11y" in content:
                score += 2

            
            if "partial" in content:
                score += 2

            
            if "rfcs" in content or "rfc" in content:
                score += 2

            
            if "lambda layer" in content:
                score += 2

            
            if "gitbook" in content:
                score += 2

            
            if "audio" in content and ("transcribe" in content or "speech" in content):
                score += 2

            
            if "cls" in content or "cumulative layout" in content:
                score += 2

            
            if "geospatial" in content or "gis" in content or "postgis" in content:
                score += 2

            
            if "push notification" in content or "fcm" in content or "apns" in content:
                score += 2

            
            if "prototype" in content:
                score += 2

            
            if "clean architecture" in content:
                score += 2

            
            if "visual regression" in content or "percy" in content or "chromatic" in content:
                score += 2

            
            if "core web vitals" in content or "web vitals" in content:
                score += 2

            
            if "cypress" in content:
                score += 2

            
            if "crossplane" in content:
                score += 2

            
            if "victorops" in content:
                score += 2

            
            if "pagespeed" in content or "page speed" in content:
                score += 2

            
            if "interpreter" in content:
                score += 2

            
            if "strangler" in content or "strangler fig" in content:
                score += 2

            
            if "cookie consent" in content or "cookie banner" in content:
                score += 2

            
            if "tensorrt" in content:
                score += 2

            
            if "vue" in content or "nuxt" in content:
                score += 2

            
            if "mongodb" in content or "mongo" in content:
                score += 2

            
            if "singleton" in content:
                score += 2

            
            if "flutter" in content or "dart" in content:
                score += 2

            
            if "ipfs" in content:
                score += 2

            
            if "tailwind" in content:
                score += 2

            
            if "canary test" in content:
                score += 2

            
            if "builder" in content:
                score += 2

            
            if "fly.io" in content or "flyio" in content:
                score += 2

            
            if "visitor" in content:
                score += 2

            
            if "postmark" in content:
                score += 2

            
            if "feature store" in content or "feast" in content:
                score += 2

            
            if "i18n" in content or "internationalization" in content:
                score += 2

            
            if "sms" in content:
                score += 2

            
            if "poetry" in content:
                score += 2

            
            if "scikit" in content or "sklearn" in content:
                score += 2

            
            if "inventory" in content:
                score += 2

            
            if "microservice" in content or "micro-service" in content:
                score += 2

            
            if "testcontainers" in content:
                score += 2

            
            if "typesense" in content:
                score += 2

            
            if "abac" in content or "attribute-based" in content:
                score += 2

            
            if "django admin" in content:
                score += 2

            
            if "model registry" in content:
                score += 2

            
            if "qr code" in content or "barcode" in content:
                score += 2

            
            if "chunked upload" in content or "resumable upload" in content:
                score += 2

            
            if "algolia" in content:
                score += 2

            
            if "kubeflow" in content:
                score += 2

            
            if "auth0" in content:
                score += 2

            
            if "coap" in content:
                score += 2

            
            if "graceful shutdown" in content and ("sigterm" in content or "sigint" in content or "sigusr" in content):
                score += 2

            
            if "commitlint" in content or "commitizen" in content:
                score += 2

            
            if "opentofu" in content:
                score += 2

            
            if "seo" in content or "structured data" in content:
                score += 2

            
            if "prefect" in content:
                score += 2

            
            if "dark mode" in content or "theme" in content:
                score += 2

            
            if "rabbitmq" in content or "amqp" in content:
                score += 2

            
            if "loggly" in content:
                score += 2

            
            if "vercel" in content or "netlify" in content:
                score += 2

            
            if "iso 27001" in content:
                score += 2

            
            if "vagrant" in content:
                score += 2

            
            if "fuzzy search" in content or "fuzzy" in content:
                score += 2

            
            if "file download" in content:
                score += 2

            
            if "self-hosted" in content or "selfhosted" in content:
                score += 2

            
            if "travis" in content or "travis ci" in content:
                score += 2

            
            if "lazy load" in content or "lazy loading" in content:
                score += 2

            
            if "onnx" in content:
                score += 2

            
            if "full-text" in content or "fulltext" in content:
                score += 2

            
            if "papertrail" in content:
                score += 2

            
            if "braintree" in content:
                score += 2

            
            if "puppeteer" in content:
                score += 2

            
            if "code split" in content or "code splitting" in content:
                score += 2

            
            if "codepipeline" in content or "codebuild" in content:
                score += 2

            
            if "http/2" in content or "http2" in content or "http/3" in content or "http3" in content:
                score += 2

            
            if "component library" in content or "design system" in content:
                score += 2

            
            if "grafana oncall" in content or "grafana on-call" in content:
                score += 2

            
            if "cockroachdb" in content or "cockroach" in content:
                score += 2

            
            if "eventbridge" in content or "event bridge" in content:
                score += 2

            
            if "solr" in content:
                score += 2

            
            if "llamaindex" in content or "llama index" in content:
                score += 2

            
            if "pdm" in content:
                score += 2

            
            if "sidekiq" in content:
                score += 2

            
            if "context manager" in content or "__enter__" in content or "__exit__" in content:
                score += 2

            
            if "excel" in content or "xlsx" in content:
                score += 2

            
            if "swift" in content or "swiftui" in content:
                score += 2

            
            if "sumologic" in content or "sumo logic" in content:
                score += 2

            
            if "l10n" in content or "localization" in content:
                score += 2

            
            if "stripe" in content:
                score += 2

            
            if "multipart" in content:
                score += 2

            
            if "logz.io" in content or "logz" in content:
                score += 2

            
            if "singledispatch" in content:
                score += 2

            
            if "opengraph" in content or "open graph" in content:
                score += 2

            
            if "product catalog" in content:
                score += 2

            
            if "dotenv" in content:
                score += 2

            
            if "flink" in content or "apache flink" in content:
                score += 2

            
            if "webauthn" in content or "fido2" in content or "passkey" in content:
                score += 2

            
            if "pypi" in content:
                score += 2

            
            if "honeycomb" in content:
                score += 2

            
            if "collections" in content:
                score += 2

            
            if "monorepo" in content:
                score += 2

            
            if "session management" in content:
                score += 2

            
            if "gcp" in content or "google cloud" in content:
                score += 2

            
            if "fid" in content or "first input" in content:
                score += 2

            
            if "config class" in content or "config model" in content:
                score += 2

            
            if "shopping cart" in content or "checkout" in content:
                score += 2

            
            if "bull" in content or "bullmq" in content:
                score += 2

            
            if "recurly" in content or "chargebee" in content:
                score += 2

            
            if "logstash" in content:
                score += 2

            
            if "ray" in content:
                score += 2

            
            if "envoy" in content:
                score += 2

            
            if "dask" in content:
                score += 2

            
            if "wiki" in content:
                score += 2

            
            if "scheduler" in content or "scheduler" in content:
                score += 2

            
            if "unittest" in content:
                score += 2

            
            if "traefik" in content:
                score += 2

            
            if "pydantic ai" in content or "pydantic-ai" in content:
                score += 2

            
            if "hatch" in content:
                score += 2

            
            if "release please" in content or "release-please" in content:
                score += 2

            
            if "coroutine" in content:
                score += 2

            
            if "ghcr" in content or "github container" in content:
                score += 2

            
            if "standard version" in content or "standard-version" in content:
                score += 2

            
            if "p2p" in content or "peer-to-peer" in content:
                score += 2

            
            if "docker hub" in content or "docker registry" in content:
                score += 2

            
            if "capacitor" in content or "ionic" in content:
                score += 2

            
            if "meilisearch" in content:
                score += 2

            
            if "lightstep" in content:
                score += 2

            
            if "oci" in content or "oracle cloud" in content:
                score += 2

            
            if "vuepress" in content or "vitepress" in content:
                score += 2

            
            if "doctest" in content:
                score += 2

            
            if "cdn" in content or "content delivery" in content:
                score += 2

            
            if "rdf" in content:
                score += 2

            scores[f] = round(min(1000.0, score), 1)
            print(f"{f}: {scores[f]}")
    
    if scores:
        best = max(scores, key=scores.get)
        print(f"\nBest prompt this round: {best} ({scores[best]})")

    # Write results.log for mutate.py to read
    with open("results.log", "w") as f:
        for name, sc in sorted(scores.items(), key=lambda x: -x[1]):
            f.write(f"{name}: {sc}\n")

    return scores


if __name__ == "__main__":
    evaluate_population()
