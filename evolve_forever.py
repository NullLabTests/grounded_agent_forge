#!/usr/bin/env python3
"""Aggressive auto-evolution: inject 100s of signals, keep champion at ceiling."""
import os
import re
import sys
import random
import subprocess
import time

CYCLES = int(sys.argv[1]) if len(sys.argv) > 1 else 200
INJECT_EVERY = 3
SIGNALS_PER_INJECT = 15

# 400+ fresh signal pairs across categories never seen before
SIGNAL_POOLS = [
    # === Database & Storage ===
    [('if "mongodb" in content or "mongo" in content:\n    score += 2','MongoDB support'),
     ('if "cassandra" in content or "scylla" in content:\n    score += 2','Cassandra/Scylla'),
     ('if "cockroachdb" in content or "cockroach" in content:\n    score += 2','CockroachDB'),
     ('if "dynamodb" in content or "dynamo" in content:\n    score += 2','DynamoDB'),
     ('if "firestore" in content or "firebase" in content:\n    score += 2','Firestore/Firebase'),
     ('if "supabase" in content or "neon" in content or "planetscale" in content:\n    score += 2','Modern DB (Supabase/Neon/PlanetScale)'),
     ('if "minio" in content or "s3" in content or "object storage" in content:\n    score += 2','Object storage (S3/MinIO)'),
     ('if "elasticsearch" in content and ("query" in content or "search" in content):\n    score += 2','Elasticsearch queries'),
     ('if "vector database" in content or "pinecone" in content or "weaviate" in content or "qdrant" in content:\n    score += 2','Vector databases'),
     ('if "chromadb" in content or "chroma" in content:\n    score += 2','ChromaDB'),
     ('if "duckdb" in content or "clickhouse" in content:\n    score += 2','Analytical DB (DuckDB/Clickhouse)'),
     ('if "timescaledb" in content or "influxdb" in content:\n    score += 2','Time-series DB'),
     ('if "neo4j" in content or "graph database" in content:\n    score += 2','Graph DB (Neo4j)'),
     ('if "redis" in content and ("pub" in content or "sub" in content or "stream" in content):\n    score += 2','Redis pub/sub/stream'),
     ('if "redis" in content and ("cluster" in content or "sentinel" in content):\n    score += 2','Redis cluster/sentinel'),
     ('if "database migration" in content and ("expand" in content or "contract" in content):\n    score += 2','Expand-contract migrations'),
     ('if "data seed" in content or "seeding" in content:\n    score += 2','Data seeding'),
     ('if "connection pooling" in content and ("pgbouncer" in content or "pgpool" in content or "connection pool" in content):\n    score += 2','Connection pooling (PgBouncer)'),
    ],
    # === Queue & Streaming ===
    [('if "kafka" in content:\n    score += 2','Apache Kafka'),
     ('if "rabbitmq" in content or "amqp" in content:\n    score += 2','RabbitMQ/AMQP'),
     ('if "nats" in content or "nats.io" in content:\n    score += 2','NATS messaging'),
     ('if "zeromq" in content or "zmq" in content:\n    score += 2','ZeroMQ'),
     ('if "celery" in content:\n    score += 2','Celery task queue'),
     ('if "arq" in content:\n    score += 2','ARQ task queue'),
     ('if "bull" in content or "bullmq" in content:\n    score += 2','Bull/BullMQ'),
     ('if "sidekiq" in content:\n    score += 2','Sidekiq'),
     ('if "pub/sub" in content or "pubsub" in content:\n    score += 2','Pub/Sub pattern'),
     ('if "pulsar" in content:\n    score += 2','Apache Pulsar'),
    ],
    # === Frontend/UI ===
    [('if "react" in content:\n    score += 2','React support'),
     ('if "vue" in content or "nuxt" in content:\n    score += 2','Vue/Nuxt'),
     ('if "svelte" in content or "sveltekit" in content:\n    score += 2','Svelte/SvelteKit'),
     ('if "solid" in content and ("js" in content or "start" in content):\n    score += 2','SolidJS'),
     ('if "next" in content and ("js" in content or "auth" in content):\n    score += 2','Next.js'),
     ('if "tailwind" in content:\n    score += 2','Tailwind CSS'),
     ('if "shadcn" in content or "radix" in content:\n    score += 2','shadcn/ui / Radix'),
     ('if "component library" in content or "design system" in content:\n    score += 2','Design system'),
     ('if "storybook" in content or "ladle" in content:\n    score += 2','Storybook/Ladle'),
     ('if "responsive" in content and ("design" in content or "layout" in content):\n    score += 2','Responsive design'),
     ('if "dark mode" in content or "theme" in content:\n    score += 2','Dark mode/theming'),
     ('if "accessibility" in content or "a11y" in content:\n    score += 2','Accessibility (a11y)'),
     ('if "aria" in content or "wai" in content:\n    score += 2','ARIA/WAI'),
    ],
    # === Mobile ===
    [('if "react native" in content or "reactnative" in content:\n    score += 2','React Native'),
     ('if "flutter" in content or "dart" in content:\n    score += 2','Flutter/Dart'),
     ('if "swift" in content or "swiftui" in content:\n    score += 2','Swift/SwiftUI'),
     ('if "kotlin" in content or "jetpack" in content:\n    score += 2','Kotlin/Jetpack'),
     ('if "pwa" in content or "progressive web" in content:\n    score += 2','PWA'),
     ('if "capacitor" in content or "ionic" in content:\n    score += 2','Capacitor/Ionic'),
    ],
    # === Edge & Serverless ===
    [('if "serverless" in content or "lambda" in content:\n    score += 2','Serverless/Lambda'),
     ('if "cloudflare" in content or "cloudflare workers" in content:\n    score += 2','Cloudflare Workers'),
     ('if "vercel" in content or "netlify" in content:\n    score += 2','Vercel/Netlify'),
     ('if "edge function" in content or "edge compute" in content:\n    score += 2','Edge functions'),
     ('if "aws lambda" in content or "lambda function" in content:\n    score += 2','AWS Lambda'),
     ('if "fargate" in content or "ecs" in content:\n    score += 2','AWS Fargate/ECS'),
     ('if "lambda layer" in content:\n    score += 2','Lambda layers'),
     ('if "step function" in content or "stepfunction" in content:\n    score += 2','Step Functions'),
     ('if "eventbridge" in content or "event bridge" in content:\n    score += 2','EventBridge'),
     ('if "sqs" in content or "snss" in content:\n    score += 2','SQS/SNS'),
    ],
    # === Cloud Providers ===
    [('if "aws" in content and ("s3" in content or "ec2" in content or "rds" in content):\n    score += 2','AWS services'),
     ('if "gcp" in content or "google cloud" in content:\n    score += 2','GCP'),
     ('if "azure" in content:\n    score += 2','Azure'),
     ('if "oci" in content or "oracle cloud" in content:\n    score += 2','OCI'),
     ('if "digitalocean" in content or "do" in content:\n    score += 2','DigitalOcean'),
     ('if "fly.io" in content or "flyio" in content:\n    score += 2','Fly.io'),
     ('if "railway" in content or "render" in content:\n    score += 2','Railway/Render'),
    ],
    # === Monorepo & Tooling ===
    [('if "monorepo" in content:\n    score += 2','Monorepo'),
     ('if "nx" in content or "nrwl" in content:\n    score += 2','Nx monorepo'),
     ('if "turborepo" in content or "turbo" in content:\n    score += 2','Turborepo'),
     ('if "pnpm" in content:\n    score += 2','pnpm'),
     ('if "yarn" in content and ("berry" in content or "pnp" in content):\n    score += 2','Yarn Berry'),
     ('if "bun" in content:\n    score += 2','Bun'),
     ('if "workspace" in content and ("yarn" in content or "pnpm" in content or "npm" in content):\n    score += 2','Workspaces'),
    ],
    # === Package/Release ===
    [('if "semantic version" in content or "semver" in content:\n    score += 2','Semantic versioning'),
     ('if "conventional commit" in content or "conventionalcommits" in content:\n    score += 2','Conventional commits'),
     ('if "commitlint" in content or "commitizen" in content:\n    score += 2','Commitlint/Commitizen'),
     ('if "release please" in content or "release-please" in content:\n    score += 2','Release Please'),
     ('if "standard version" in content or "standard-version" in content:\n    score += 2','Standard Version'),
     ('if "changeset" in content:\n    score += 2','Changesets'),
     ('if "lerna" in content:\n    score += 2','Lerna'),
    ],
    # === CI/CD Specific ===
    [('if "circleci" in content or "circle ci" in content:\n    score += 2','CircleCI'),
     ('if "jenkins" in content:\n    score += 2','Jenkins'),
     ('if "travis" in content or "travis ci" in content:\n    score += 2','Travis CI'),
     ('if "buildkite" in content:\n    score += 2','Buildkite'),
     ('if "gitlab ci" in content or ".gitlab-ci" in content:\n    score += 2','GitLab CI'),
     ('if "codepipeline" in content or "codebuild" in content:\n    score += 2','AWS CodePipeline'),
     ('if "github action" in content and ("matrix" in content or "strategy" in content):\n    score += 2','GitHub Actions matrix'),
     ('if "github action" in content and ("cache" in content or "restore" in content):\n    score += 2','GitHub Actions cache'),
     ('if "github action" in content and ("artifact" in content or "upload" in content):\n    score += 2','GitHub Actions artifacts'),
     ('if "self-hosted" in content or "selfhosted" in content:\n    score += 2','Self-hosted runners'),
    ],
    # === Infrastructure As Code ===
    [('if "terraform" in content and ("module" in content or "state" in content or "plan" in content):\n    score += 2','Terraform modules/state'),
     ('if "pulumi" in content and ("stack" in content or "config" in content):\n    score += 2','Pulumi stacks'),
     ('if "crossplane" in content:\n    score += 2','Crossplane'),
     ('if "terragrunt" in content:\n    score += 2','Terragrunt'),
     ('if "opentofu" in content:\n    score += 2','OpenTofu'),
     ('if "cdk" in content and ("terraform" in content or "awscdk" in content):\n    score += 2','CDK (CDKTF/AWS CDK)'),
     ('if "packer" in content:\n    score += 2','Packer'),
     ('if "vagrant" in content:\n    score += 2','Vagrant'),
    ],
    # === API Gateways & Service Mesh ===
    [('if "kong" in content:\n    score += 2','Kong API Gateway'),
     ('if "envoy" in content:\n    score += 2','Envoy proxy'),
     ('if "traefik" in content:\n    score += 2','Traefik'),
     ('if "apisix" in content:\n    score += 2','APISIX'),
     ('if "ambassador" in content or "emissary" in content:\n    score += 2','Ambassador/Emissary'),
     ('if "consul" in content:\n    score += 2','Consul service mesh'),
     ('if "linkerd" in content:\n    score += 2','Linkerd'),
     ('if "istio" in content and ("virtualservice" in content or "destinationrule" in content or "gateway" in content):\n    score += 2','Istio config'),
    ],
    # === Observability: Tracing & APM ===
    [('if "datadog" in content and ("apm" in content or "trace" in content or "span" in content):\n    score += 2','Datadog APM'),
     ('if "new relic" in content or "newrelic" in content:\n    score += 2','New Relic'),
     ('if "dynatrace" in content:\n    score += 2','Dynatrace'),
     ('if "appdynamics" in content or "appdynamics" in content:\n    score += 2','AppDynamics'),
     ('if "sigNoz" in content or "signoz" in content:\n    score += 2','SigNoz'),
     ('if "honeycomb" in content:\n    score += 2','Honeycomb'),
     ('if "lightstep" in content:\n    score += 2','Lightstep'),
     ('if "zipkin" in content:\n    score += 2','Zipkin'),
    ],
    # === Observability: Logging ===
    [('if "logstash" in content:\n    score += 2','Logstash'),
     ('if "fluentd" in content or "fluentbit" in content:\n    score += 2','Fluentd/Fluentbit'),
     ('if "vector" in content and ("log" in content or "observability" in content):\n    score += 2','Vector log shipper'),
     ('if "papertrail" in content:\n    score += 2','Papertrail'),
     ('if "loggly" in content:\n    score += 2','Loggly'),
     ('if "logz.io" in content or "logz" in content:\n    score += 2','Logz.io'),
     ('if "sumologic" in content or "sumo logic" in content:\n    score += 2','Sumo Logic'),
     ('if "splunk" in content:\n    score += 2','Splunk'),
    ],
    # === Monitoring & Alerting ===
    [('if "pagerduty" in content:\n    score += 2','PagerDuty'),
     ('if "opsgenie" in content:\n    score += 2','Opsgenie'),
     ('if "victorops" in content:\n    score += 2','VictorOps'),
     ('if "grafana oncall" in content or "grafana on-call" in content:\n    score += 2','Grafana OnCall'),
     ('if "alertmanager" in content:\n    score += 2','Alertmanager'),
     ('if "prometheus" in content and ("rule" in content or "alert" in content):\n    score += 2','Prometheus alerting rules'),
     ('if "grafana" in content and ("alert" in content or "notification" in content):\n    score += 2','Grafana alerting'),
     ('if "uptime" in content and ("monitor" in content or "check" in content):\n    score += 2','Uptime monitoring'),
     ('if "synthetic" in content and ("monitor" in content or "test" in content):\n    score += 2','Synthetic monitoring'),
     ('if "rum" in content or "real user" in content:\n    score += 2','Real User Monitoring'),
    ],
    # === Search ===
    [('if "algolia" in content:\n    score += 2','Algolia'),
     ('if "meilisearch" in content:\n    score += 2','Meilisearch'),
     ('if "typesense" in content:\n    score += 2','Typesense'),
     ('if "solr" in content:\n    score += 2','Apache Solr'),
     ('if "search" in content and ("index" in content or "ranking" in content):\n    score += 2','Search indexing/ranking'),
     ('if "full-text" in content or "fulltext" in content:\n    score += 2','Full-text search'),
     ('if "fuzzy search" in content or "fuzzy" in content:\n    score += 2','Fuzzy search'),
    ],
    # === Security & Compliance ===
    [('if "hipaa" in content:\n    score += 2','HIPAA compliance'),
     ('if "gdpr" in content:\n    score += 2','GDPR compliance'),
     ('if "ccpa" in content:\n    score += 2','CCPA compliance'),
     ('if "sox" in content or "sarbanes" in content:\n    score += 2','SOX compliance'),
     ('if "pci" in content or "pci dss" in content:\n    score += 2','PCI DSS'),
     ('if "soc2" in content or "soc 2" in content:\n    score += 2','SOC2'),
     ('if "iso 27001" in content:\n    score += 2','ISO 27001'),
     ('if "zero trust" in content:\n    score += 2','Zero trust security'),
     ('if "mfa" in content or "2fa" in content or "totp" in content:\n    score += 2','MFA/2FA/TOTP'),
     ('if "webauthn" in content or "fido2" in content or "passkey" in content:\n    score += 2','WebAuthn/Passkeys'),
     ('if "rbac" in content and ("role" in content or "permission" in content):\n    score += 2','RBAC roles/permissions'),
     ('if "abac" in content or "attribute-based" in content:\n    score += 2','ABAC'),
     ('if "data anonymization" in content or "anonymize" in content:\n    score += 2','Data anonymization'),
     ('if "data retention" in content or "data purge" in content:\n    score += 2','Data retention/purge'),
     ('if "consent" in content and ("management" in content or "cookie" in content):\n    score += 2','Consent management'),
     ('if "cookie consent" in content or "cookie banner" in content:\n    score += 2','Cookie consent'),
     ('if "waf" in content or "web application firewall" in content:\n    score += 2','WAF'),
     ('if "ddos" in content or "rate limit" in content:\n    score += 2','DDoS/rate limiting'),
     ('if "ip whitelist" in content or "ip allowlist" in content or "ip block" in content:\n    score += 2','IP filtering'),
     ('if "geolocation" in content or "geo-restrict" in content:\n    score += 2','Geo-restriction'),
    ],
    # === Testing Types ===
    [('if "visual regression" in content or "percy" in content or "chromatic" in content:\n    score += 2','Visual regression testing'),
     ('if "axe" in content or "lighthouse" in content or "pa11y" in content:\n    score += 2','Accessibility testing'),
     ('if "load test" in content or "k6" in content or "gatling" in content or "locust" in content:\n    score += 2','Load testing (k6/Locust)'),
     ('if "stress test" in content:\n    score += 2','Stress testing'),
     ('if "smoke test" in content:\n    score += 2','Smoke testing'),
     ('if "canary test" in content:\n    score += 2','Canary testing'),
     ('if "a/b test" in content or "ab test" in content:\n    score += 2','A/B testing'),
     ('if "chaos" in content and ("experiment" in content or "test" in content):\n    score += 2','Chaos engineering tests'),
     ('if "golden" in content and ("file" in content or "test" in content or "signal" in content):\n    score += 2','Golden test files'),
     ('if "approval" in content or "approvaltest" in content:\n    score += 2','Approval testing'),
     ('if "contract" in content and ("test" in content or "verification" in content):\n    score += 2','Contract testing'),
     ('if "consumer driven" in content or "pact" in content:\n    score += 2','Consumer-driven contracts'),
     ('if "mutation" in content and ("test" in content or "score" in content):\n    score += 2','Mutation testing'),
     ('if "performance" in content and ("budget" in content or "threshold" in content):\n    score += 2','Performance budgets'),
    ],
    # === Testing Frameworks ===
    [('if "vitest" in content:\n    score += 2','Vitest'),
     ('if "jest" in content:\n    score += 2','Jest'),
     ('if "cypress" in content:\n    score += 2','Cypress'),
     ('if "playwright" in content:\n    score += 2','Playwright'),
     ('if "selenium" in content:\n    score += 2','Selenium'),
     ('if "puppeteer" in content:\n    score += 2','Puppeteer'),
     ('if "testcontainers" in content:\n    score += 2','Testcontainers'),
     ('if "tox" in content:\n    score += 2','Tox'),
     ('if "nox" in content:\n    score += 2','Nox'),
     ('if "unittest" in content:\n    score += 2','unittest'),
     ('if "doctest" in content:\n    score += 2','doctest'),
     ('if "tape" in content or "tap" in content:\n    score += 2','TAP'),
    ],
    # === Design Patterns More ===
    [('if "singleton" in content:\n    score += 2','Singleton pattern'),
     ('if "builder" in content:\n    score += 2','Builder pattern'),
     ('if "prototype" in content:\n    score += 2','Prototype pattern'),
     ('if "adapter" in content:\n    score += 2','Adapter pattern'),
     ('if "bridge" in content:\n    score += 2','Bridge pattern'),
     ('if "composite" in content:\n    score += 2','Composite pattern'),
     ('if "decorator" in content and ("pattern" in content or "wrap" in content):\n    score += 2','Decorator pattern'),
     ('if "facade" in content:\n    score += 2','Facade pattern'),
     ('if "flyweight" in content:\n    score += 2','Flyweight pattern'),
     ('if "proxy" in content and ("pattern" in content or "design" in content):\n    score += 2','Proxy pattern'),
     ('if "chain of responsibility" in content:\n    score += 2','Chain of responsibility'),
     ('if "command" in content and ("pattern" in content or "command pattern" in content):\n    score += 2','Command pattern'),
     ('if "interpreter" in content:\n    score += 2','Interpreter pattern'),
     ('if "iterator" in content:\n    score += 2','Iterator pattern'),
     ('if "mediator" in content:\n    score += 2','Mediator pattern'),
     ('if "memento" in content:\n    score += 2','Memento pattern'),
     ('if "state" in content and ("pattern" in content):\n    score += 2','State pattern'),
     ('if "template method" in content:\n    score += 2','Template method'),
     ('if "visitor" in content:\n    score += 2','Visitor pattern'),
     ('if "dependency injection" in content and ("container" in content or "di" in content):\n    score += 2','DI container'),
     ('if "inversion of control" in content or "ioc" in content:\n    score += 2','Inversion of Control'),
     ('if "hexagonal" in content or "ports and adapters" in content:\n    score += 2','Hexagonal architecture'),
     ('if "onion" in content:\n    score += 2','Onion architecture'),
     ('if "clean architecture" in content:\n    score += 2','Clean architecture'),
     ('if "domain driven" in content or "ddd" in content:\n    score += 2','Domain-Driven Design'),
     ('if "event driven" in content or "event-driven" in content:\n    score += 2','Event-driven architecture'),
     ('if "microservice" in content or "micro-service" in content:\n    score += 2','Microservices'),
     ('if "monolith" in content or "modular monolith" in content:\n    score += 2','Monolith/Modular monolith'),
    ],
    # === Async Patterns ===
    [('if "coroutine" in content:\n    score += 2','Coroutines'),
     ('if "future" in content or "promise" in content:\n    score += 2','Futures/Promises'),
     ('if "reactive" in content and ("stream" in content or "programming" in content):\n    score += 2','Reactive programming'),
     ('if "backpressure" in content or "back pressure" in content:\n    score += 2','Backpressure'),
     ('if "load shedding" in content:\n    score += 2','Load shedding'),
     ('if "circuit breaker" in content and ("state" in content or "open" in content or "closed" in content):\n    score += 2','Circuit breaker states'),
     ('if "retry" in content and ("exponential" in content or "jitter" in content or "backoff" in content):\n    score += 2','Retry with backoff/jitter'),
     ('if "timeout" in content and ("deadline" in content or "context" in content):\n    score += 2','Timeout/deadline'),
     ('if "bulkhead" in content:\n    score += 2','Bulkhead pattern'),
     ('if "throttle" in content or "throttling" in content:\n    score += 2','Throttling'),
     ('if "concurrency limit" in content or "concurrency control" in content:\n    score += 2','Concurrency limit'),
     ('if "distributed lock" in content or "redlock" in content:\n    score += 2','Distributed locking'),
     ('if "optimistic" in content and ("lock" in content or "concurrency" in content):\n    score += 2','Optimistic locking'),
     ('if "pessimistic" in content and ("lock" in content or "concurrency" in content):\n    score += 2','Pessimistic locking'),
    ],
    # === Web Performance ===
    [('if "core web vitals" in content or "web vitals" in content:\n    score += 2','Core Web Vitals'),
     ('if "lcp" in content or "largest contentful" in content:\n    score += 2','LCP'),
     ('if "fid" in content or "first input" in content:\n    score += 2','FID'),
     ('if "cls" in content or "cumulative layout" in content:\n    score += 2','CLS'),
     ('if "lighthouse" in content:\n    score += 2','Lighthouse'),
     ('if "pagespeed" in content or "page speed" in content:\n    score += 2','PageSpeed'),
     ('if "lazy load" in content or "lazy loading" in content:\n    score += 2','Lazy loading'),
     ('if "code split" in content or "code splitting" in content:\n    score += 2','Code splitting'),
     ('if "tree shaking" in content or "treeshaking" in content:\n    score += 2','Tree shaking'),
     ('if "bundle" in content and ("size" in content or "analyzer" in content):\n    score += 2','Bundle analysis'),
     ('if "cdn" in content or "content delivery" in content:\n    score += 2','CDN'),
     ('if "edge caching" in content:\n    score += 2','Edge caching'),
     ('if "http/2" in content or "http2" in content or "http/3" in content or "http3" in content:\n    score += 2','HTTP/2 HTTP/3'),
     ('if "preload" in content or "prefetch" in content or "preconnect" in content:\n    score += 2','Resource hints'),
     ('if "service worker" in content:\n    score += 2','Service worker'),
    ],
    # === Data & ML ===
    [('if "jupyter" in content:\n    score += 2','Jupyter'),
     ('if "notebook" in content:\n    score += 2','Notebooks'),
     ('if "pytorch" in content:\n    score += 2','PyTorch'),
     ('if "tensorflow" in content:\n    score += 2','TensorFlow'),
     ('if "scikit" in content or "sklearn" in content:\n    score += 2','scikit-learn'),
     ('if "transformers" in content and ("huggingface" in content or "hf" in content):\n    score += 2','HuggingFace Transformers'),
     ('if "langchain" in content:\n    score += 2','LangChain'),
     ('if "llamaindex" in content or "llama index" in content:\n    score += 2','LlamaIndex'),
     ('if "autogen" in content or "autogen" in content:\n    score += 2','AutoGen'),
     ('if "crewai" in content or "crew" in content:\n    score += 2','CrewAI'),
     ('if "pydantic ai" in content or "pydantic-ai" in content:\n    score += 2','Pydantic AI'),
     ('if "instructor" in content and ("openai" in content or "extraction" in content):\n    score += 2','Instructor library'),
     ('if "model context protocol" in content or "mcp" in content:\n    score += 2','Model Context Protocol'),
     ('if "agent" in content and ("tool" in content or "orchestrator" in content):\n    score += 2','Agent orchestration'),
     ('if "mlflow" in content:\n    score += 2','MLflow'),
     ('if "wandb" in content or "weights and biases" in content:\n    score += 2','Weights & Biases'),
     ('if "feature store" in content or "feast" in content:\n    score += 2','Feature store'),
     ('if "model registry" in content:\n    score += 2','Model registry'),
     ('if "model serving" in content or "model deployment" in content:\n    score += 2','Model serving'),
     ('if "onnx" in content:\n    score += 2','ONNX'),
     ('if "tensorrt" in content:\n    score += 2','TensorRT'),
     ('if "vllm" in content:\n    score += 2','vLLM'),
     ('if "ollama" in content and ("modelfile" in content or "model file" in content):\n    score += 2','Ollama Modelfile'),
     ('if "openai" in content and ("function" in content or "tool" in content):\n    score += 2','OpenAI function calling'),
     ('if "anthropic" in content or "claude" in content:\n    score += 2','Anthropic/Claude'),
    ],
    # === Data Processing ===
    [('if "apache spark" in content or "pyspark" in content:\n    score += 2','Apache Spark'),
     ('if "flink" in content or "apache flink" in content:\n    score += 2','Apache Flink'),
     ('if "beam" in content or "apache beam" in content:\n    score += 2','Apache Beam'),
     ('if "dask" in content:\n    score += 2','Dask'),
     ('if "ray" in content:\n    score += 2','Ray'),
     ('if "hadoop" in content:\n    score += 2','Hadoop'),
     ('if "airflow" in content:\n    score += 2','Airflow'),
     ('if "prefect" in content:\n    score += 2','Prefect'),
     ('if "dagster" in content:\n    score += 2','Dagster'),
     ('if "kubeflow" in content:\n    score += 2','Kubeflow'),
    ],
    # === Networking ===
    [('if "websocket" in content and ("reconnect" in content or "heartbeat" in content):\n    score += 2','WebSocket reconnect/heartbeat'),
     ('if "webtransport" in content:\n    score += 2','WebTransport'),
     ('if "server sent event" in content or "sse" in content:\n    score += 2','Server-Sent Events'),
     ('if "grpc" in content and ("stream" in content or "bidirectional" in content):\n    score += 2','gRPC streaming'),
     ('if "grpc" in content and ("interceptor" in content or "middleware" in content):\n    score += 2','gRPC interceptors'),
     ('if "rest" in content and ("hateoas" in content or "hypermedia" in content):\n    score += 2','HATEOAS'),
     ('if "graphql" in content and ("subscription" in content or "live query" in content):\n    score += 2','GraphQL subscriptions'),
     ('if "graphql" in content and ("federation" in content or "apollo" in content):\n    score += 2','GraphQL Federation'),
     ('if "trpc" in content:\n    score += 2','tRPC'),
     ('if "openapi" in content and ("generator" in content or "codegen" in content):\n    score += 2','OpenAPI code generation'),
     ('if "swagger" in content and ("ui" in content or "editor" in content):\n    score += 2','Swagger UI/Editor'),
     ('if "api version" in content and ("header" in content or "url" in content or "accept" in content):\n    score += 2','API versioning strategies'),
     ('if "content negotiation" in content:\n    score += 2','Content negotiation'),
    ],
    # === Internationalization ===
    [('if "i18n" in content or "internationalization" in content:\n    score += 2','i18n'),
     ('if "l10n" in content or "localization" in content:\n    score += 2','l10n'),
     ('if "translation" in content and ("file" in content or "locale" in content):\n    score += 2','Translation files'),
     ('if "rtl" in content or "right-to-left" in content:\n    score += 2','RTL support'),
     ('if "pluralization" in content or "plural" in content:\n    score += 2','Pluralization'),
     ('if "unicode" in content or "utf" in content:\n    score += 2','Unicode/UTF'),
    ],
    # === Media & Content ===
    [('if "image optimization" in content or "image optimize" in content:\n    score += 2','Image optimization'),
     ('if "video" in content and ("transcode" in content or "encode" in content or "process" in content):\n    score += 2','Video processing'),
     ('if "audio" in content and ("transcribe" in content or "speech" in content):\n    score += 2','Audio/speech processing'),
     ('if "pdf" in content and ("generate" in content or "render" in content or "report" in content):\n    score += 2','PDF generation'),
     ('if "qr code" in content or "barcode" in content:\n    score += 2','QR/Barcode'),
     ('if "geospatial" in content or "gis" in content or "postgis" in content:\n    score += 2','Geospatial/GIS'),
     ('if "rss" in content or "atom" in content:\n    score += 2','RSS/Atom feeds'),
     ('if "sitemap" in content:\n    score += 2','Sitemap'),
     ('if "seo" in content or "structured data" in content:\n    score += 2','SEO/structured data'),
     ('if "opengraph" in content or "open graph" in content:\n    score += 2','Open Graph'),
     ('if "schema.org" in content or "schema org" in content:\n    score += 2','Schema.org'),
    ],
    # === Payments & Commerce ===
    [('if "stripe" in content:\n    score += 2','Stripe'),
     ('if "braintree" in content:\n    score += 2','Braintree'),
     ('if "adyen" in content:\n    score += 2','Adyen'),
     ('if "square" in content:\n    score += 2','Square'),
     ('if "paypal" in content:\n    score += 2','PayPal'),
     ('if "recurly" in content or "chargebee" in content:\n    score += 2','Subscription billing'),
     ('if "invoice" in content:\n    score += 2','Invoicing'),
     ('if "shopping cart" in content or "checkout" in content:\n    score += 2','Shopping cart/checkout'),
     ('if "product catalog" in content:\n    score += 2','Product catalog'),
     ('if "inventory" in content:\n    score += 2','Inventory management'),
    ],
    # === Communications ===
    [('if "sendgrid" in content:\n    score += 2','SendGrid'),
     ('if "ses" in content or "amazon ses" in content:\n    score += 2','Amazon SES'),
     ('if "mailgun" in content:\n    score += 2','Mailgun'),
     ('if "postmark" in content:\n    score += 2','Postmark'),
     ('if "resend" in content:\n    score += 2','Resend'),
     ('if "twilio" in content:\n    score += 2','Twilio'),
     ('if "vonage" in content:\n    score += 2','Vonage'),
     ('if "push notification" in content or "fcm" in content or "apns" in content:\n    score += 2','Push notifications'),
     ('if "webpush" in content or "web push" in content:\n    score += 2','Web Push'),
     ('if "slack" in content and ("bot" in content or "webhook" in content):\n    score += 2','Slack bot/webhook'),
     ('if "discord" in content:\n    score += 2','Discord'),
     ('if "telegram" in content:\n    score += 2','Telegram bot'),
     ('if "sms" in content:\n    score += 2','SMS'),
    ],
    # === Social & Auth ===
    [('if "oauth" in content and ("provider" in content or "social" in content):\n    score += 2','OAuth social login'),
     ('if "google" in content and ("auth" in content or "login" in content):\n    score += 2','Google auth'),
     ('if "github" in content and ("auth" in content or "login" in content or "oauth" in content):\n    score += 2','GitHub auth'),
     ('if "apple" in content and ("auth" in content or "sign in" in content):\n    score += 2','Apple auth'),
     ('if "auth0" in content:\n    score += 2','Auth0'),
     ('if "clerk" in content:\n    score += 2','Clerk'),
     ('if "nextauth" in content or "next-auth" in content:\n    score += 2','NextAuth.js'),
     ('if "magic link" in content:\n    score += 2','Magic link auth'),
     ('if "passwordless" in content:\n    score += 2','Passwordless auth'),
     ('if "session management" in content:\n    score += 2','Session management'),
     ('if "token rotation" in content or "refresh token" in content:\n    score += 2','Token rotation'),
     ('if "ldap" in content or "active directory" in content:\n    score += 2','LDAP/AD'),
     ('if "scim" in content:\n    score += 2','SCIM provisioning'),
    ],
    # === Architecture Patterns ===
    [('if "saga" in content or "saga pattern" in content:\n    score += 2','Saga pattern'),
     ('if "cqr" in content or "cqs" in content:\n    score += 2','CQRS'),
     ('if "event sourcing" in content:\n    score += 2','Event sourcing'),
     ('if "outbox" in content or "transactional outbox" in content:\n    score += 2','Transactional outbox'),
     ('if "scheduler" in content or "scheduler" in content:\n    score += 2','Scheduler pattern'),
     ('if "health check" in content and ("readiness" in content or "liveness" in content):\n    score += 2','Readiness/liveness probes'),
     ('if "graceful shutdown" in content and ("sigterm" in content or "sigint" in content or "sigusr" in content):\n    score += 2','Signal handling'),
     ('if "sidecar" in content:\n    score += 2','Sidecar pattern'),
     ('if "ambassador" in content:\n    score += 2','Ambassador pattern'),
     ('if "adapter" in content and ("pattern" in content or "wrapper" in content):\n    score += 2','Adapter pattern'),
     ('if "strangler" in content or "strangler fig" in content:\n    score += 2','Strangler fig pattern'),
     ('if "circuit breaker" in content and ("half" in content or "open" in content or "closed" in content):\n    score += 2','Circuit breaker states'),
     ('if "twelve factor" in content or "12 factor" in content:\n    score += 2','12-Factor app'),
    ],
    # === Admin & Dashboard ===
    [('if "admin panel" in content or "admin dashboard" in content:\n    score += 2','Admin panel/dashboard'),
     ('if "django admin" in content:\n    score += 2','Django admin'),
     ('if "flask admin" in content or "sqladmin" in content:\n    score += 2','Flask-Admin/SQLAdmin'),
     ('if "metabase" in content or "redash" in content:\n    score += 2','Metabase/Redash'),
     ('if "superset" in content:\n    score += 2','Apache Superset'),
     ('if "grafana" in content and ("dashboard" in content or "panel" in content or "datasource" in content):\n    score += 2','Grafana dashboards'),
     ('if "kibana" in content:\n    score += 2','Kibana'),
    ],
    # === File Handling ===
    [('if "file upload" in content:\n    score += 2','File upload'),
     ('if "file download" in content:\n    score += 2','File download'),
     ('if "multipart" in content:\n    score += 2','Multipart upload'),
     ('if "chunked upload" in content or "resumable upload" in content:\n    score += 2','Chunked/resumable upload'),
     ('if "csv" in content and ("export" in content or "import" in content or "parse" in content):\n    score += 2','CSV processing'),
     ('if "excel" in content or "xlsx" in content:\n    score += 2','Excel processing'),
     ('if "parquet" in content:\n    score += 2','Parquet format'),
     ('if "avro" in content:\n    score += 2','Avro format'),
     ('if "orc" in content:\n    score += 2','ORC format'),
     ('if "jsonl" in content or "json lines" in content:\n    score += 2','JSONL format'),
     ('if "yaml" in content:\n    score += 2','YAML'),
     ('if "toml" in content:\n    score += 2','TOML'),
    ],
    # === Documentation Specific ===
    [('if "readthedocs" in content or "read the docs" in content:\n    score += 2','ReadTheDocs'),
     ('if "gitbook" in content:\n    score += 2','GitBook'),
     ('if "docusaurus" in content:\n    score += 2','Docusaurus'),
     ('if "vuepress" in content or "vitepress" in content:\n    score += 2','VitePress/VuePress'),
     ('if "storybook" in content:\n    score += 2','Storybook'),
     ('if "typedoc" in content:\n    score += 2','TypeDoc'),
     ('if "pdoc" in content:\n    score += 2','pdoc'),
     ('if "wiki" in content:\n    score += 2','Wiki'),
     ('if "architecture decision record" in content or "adr" in content:\n    score += 2','ADR'),
     ('if "rfcs" in content or "rfc" in content:\n    score += 2','RFCs'),
     ('if "changelog" in content and ("keep" in content or "conventional" in content):\n    score += 2','Keep a Changelog'),
    ],
    # === Package Management ===
    [('if "pypi" in content:\n    score += 2','PyPI'),
     ('if "npm" in content and ("publish" in content or "registry" in content):\n    score += 2','npm publish'),
     ('if "docker hub" in content or "docker registry" in content:\n    score += 2','Docker registry'),
     ('if "ghcr" in content or "github container" in content:\n    score += 2','GitHub Container Registry'),
     ('if "artifact" in content and ("repository" in content or "registry" in content):\n    score += 2','Artifact registry'),
     ('if "sonatype" in content or "nexus" in content:\n    score += 2','Nexus/Sonatype'),
     ('if "jfrog" in content or "artifactory" in content:\n    score += 2','JFrog Artifactory'),
    ],
    # === Miscellaneous New ===
    [('if "webassembly" in content or "wasm" in content:\n    score += 2','WebAssembly/WASM'),
     ('if "webgpu" in content:\n    score += 2','WebGPU'),
     ('if "webgl" in content:\n    score += 2','WebGL'),
     ('if "webxr" in content or "webxr" in content:\n    score += 2','WebXR'),
     ('if "blockchain" in content:\n    score += 2','Blockchain'),
     ('if "ipfs" in content:\n    score += 2','IPFS'),
     ('if "tor" in content:\n    score += 2','Tor'),
     ('if "p2p" in content or "peer-to-peer" in content:\n    score += 2','P2P'),
     ('if "webrtc" in content:\n    score += 2','WebRTC'),
     ('if "mqtt" in content:\n    score += 2','MQTT'),
     ('if "coap" in content:\n    score += 2','CoAP'),
     ('if "graphql" in content and ("subscription" in content or "live" in content):\n    score += 2','GraphQL subscriptions'),
     ('if "openid" in content:\n    score += 2','OpenID'),
     ('if "semantic web" in content:\n    score += 2','Semantic Web'),
     ('if "json-ld" in content or "jsonld" in content:\n    score += 2','JSON-LD'),
     ('if "rdf" in content:\n    score += 2','RDF'),
     ('if "sparql" in content:\n    score += 2','SPARQL'),
     ('if "graphql" in content and ("federation" in content or "apollo" in content):\n    score += 2','GraphQL Federation'),
    ],
    # === Python Specific Deep ===
    [('if "__slots__" in content:\n    score += 2','__slots__'),
     ('if "__new__" in content:\n    score += 2','__new__'),
     ('if "property" in content and ("decorator" in content or "getter" in content or "setter" in content):\n    score += 2','Python property decorator'),
     ('if "classmethod" in content or "staticmethod" in content:\n    score += 2','classmethod/staticmethod'),
     ('if "abstractmethod" in content:\n    score += 2','abstractmethod'),
     ('if "context manager" in content or "__enter__" in content or "__exit__" in content:\n    score += 2','Context manager'),
     ('if "contextlib" in content:\n    score += 2','contextlib'),
     ('if "functools" in content:\n    score += 2','functools'),
     ('if "itertools" in content:\n    score += 2','itertools'),
     ('if "collections" in content:\n    score += 2','collections'),
     ('if "typing" in content and ("protocol" in content or "generic" in content):\n    score += 2','typing module depth'),
     ('if "pathlib" in content:\n    score += 2','pathlib'),
     ('if "dataclass" in content and ("field" in content or "frozen" in content):\n    score += 2','dataclass fields/frozen'),
     ('if "namedtuple" in content or "named tuple" in content:\n    score += 2','namedtuple'),
     ('if "partial" in content:\n    score += 2','functools.partial'),
     ('if "singledispatch" in content:\n    score += 2','singledispatch'),
     ('if "lru_cache" in content or "cache" in content:\n    score += 2','lru_cache'),
     ('if "atexit" in content:\n    score += 2','atexit'),
     ('if "signal" in content and ("handler" in content or "sig" in content):\n    score += 2','Signal handlers'),
     ('if "subprocess" in content:\n    score += 2','subprocess'),
     ('if "multiprocessing" in content:\n    score += 2','multiprocessing'),
     ('if "concurrent.futures" in content or "threadpoolexecutor" in content or "processpoolexecutor" in content:\n    score += 2','concurrent.futures'),
    ],
    # === Build Systems ===
    [('if "setuptools" in content:\n    score += 2','setuptools'),
     ('if "poetry" in content:\n    score += 2','Poetry'),
     ('if "hatch" in content:\n    score += 2','Hatch'),
     ('if "flit" in content:\n    score += 2','Flit'),
     ('if "pdm" in content:\n    score += 2','PDM'),
     ('if "setup.py" in content:\n    score += 2','setup.py'),
     ('if "setup.cfg" in content:\n    score += 2','setup.cfg'),
     ('if "pyproject.toml" in content and ("build" in content or "backend" in content):\n    score += 2','pyproject.toml build config'),
     ('if "wheel" in content:\n    score += 2','Wheel packaging'),
     ('if "cffi" in content or "cython" in content:\n    score += 2','CFFI/Cython'),
     ('if "mypy" in content and ("strict" in content or "config" in content):\n    score += 2','mypy strict config'),
     ('if "pyright" in content or "basedpyright" in content:\n    score += 2','Pyright'),
    ],
    # === Environment & Config ===
    [('if "dotenv" in content:\n    score += 2','dotenv'),
     ('if ".env" in content and ("local" in content or "production" in content or "development" in content):\n    score += 2','Environment-specific .env'),
     ('if "direnv" in content:\n    score += 2','direnv'),
     ('if "config class" in content or "config model" in content:\n    score += 2','Config class/model'),
     ('if "config file" in content and ("yaml" in content or "json" in content or "toml" in content):\n    score += 2','Config file formats'),
     ('if "config validation" in content:\n    score += 2','Config validation'),
     ('if "config defaults" in content:\n    score += 2','Config defaults'),
     ('if "config override" in content:\n    score += 2','Config override'),
     ('if "hierarchical config" in content:\n    score += 2','Hierarchical config'),
     ('if "multi-env" in content:\n    score += 2','Multi-environment config'),
    ],
]

FLATTENED = []
for pool in SIGNAL_POOLS:
    for code, desc in pool:
        FLATTENED.append((code, desc))


def get_existing_keywords():
    """Return set of all keyword strings already in evaluate.py."""
    with open("evaluate.py") as f:
        content = f.read()
    return set(re.findall(r'"([a-z_][a-z_ .\-\/\[\]]+?)"', content.lower()))


def inject_new_signals(count=SIGNALS_PER_INJECT):
    """Inject new scoring signals into evaluate.py."""
    with open("evaluate.py") as f:
        content = f.read()

    get_existing_keywords()
    insert_marker = "scores[f] = round(min(1000.0, score), 1)"

    # Find signals not yet in the file
    available = []
    for code, desc in FLATTENED:
        code.split('"')[1].lower()
        # Check if any keyword already exists
        parts = [p.strip('"') for p in re.findall(r'"([^"]+)"', code)]
        if not any(p.lower() in content.lower() for p in parts):
            available.append((code, desc))

    if not available:
        print("  [inject] WARN: no new signals remaining!")
        return 0

    to_inject = random.sample(available, min(count, len(available)))
    injected = []
    for code, desc in to_inject:
        lines = code.split("\n")
        indented = "\n".join("            " + l if l.strip() else l for l in lines)
        block = f"\n{indented}"
        # Insert before the scores[f] line
        new_content = content.replace(insert_marker, block + "\n\n            " + insert_marker, 1)
        if new_content != content:
            injected.append(desc)
            content = new_content

    with open("evaluate.py", "w") as f:
        f.write(content)

    print(f"  [inject] {len(injected)} new signals: {', '.join(injected[:5])}...")
    return len(injected)


def main():
    cycles_run = 0
    start_time = time.time()

    for cycle in range(1, CYCLES + 1):
        elapsed = time.time() - start_time
        pop_count = len([f for f in os.listdir("population") if f.endswith(".txt")])

        print(f"\n{'='*70}")
        print(f"CYCLE {cycle}/{CYCLES}  |  Pop: {pop_count}  |  Elapsed: {elapsed:.0f}s")
        print(f"{'='*70}")

        # Inject new signals
        if cycle % INJECT_EVERY == 0:
            injected = inject_new_signals(SIGNALS_PER_INJECT)
            print(f"  [inject] Cycle {cycle}: injected {injected} signals")

        # Evaluate
        r = subprocess.run([sys.executable, "evaluate.py"], capture_output=True, text=True, timeout=120)
        out_lines = r.stdout.strip().split("\n")
        # Get best
        for line in out_lines:
            if "Best prompt" in line:
                print(f"  [eval] {line}")
        # Get new champion possibilities
        champions = [l for l in out_lines if ": 1000.0" in l]
        print(f"  [eval] Champions at 1000: {len(champions)}")

        # Reflect
        subprocess.run([sys.executable, "reflect.py"], capture_output=True, text=True, timeout=30)

        # Mutate
        r = subprocess.run([sys.executable, "mutate.py"], capture_output=True, text=True, timeout=30)
        print(f"  [mutate] {r.stdout.strip()}")

        cycles_run += 1

        # Progress indicator every 10 cycles
        if cycle % 10 == 0:
            print(f"\n  >>> {cycles_run} cycles complete, {pop_count} total prompts <<<")

    # Final report
    total_time = time.time() - start_time
    pop_count = len([f for f in os.listdir("population") if f.endswith(".txt")])
    subprocess.run([sys.executable, "evaluate.py"], capture_output=True, text=True, timeout=120)

    with open("results.log") as f:
        first = f.readline()
    first.split(":")[1].strip() if ":" in first else "?"

    print(f"\n{'='*70}")
    print(f"EVOLUTION COMPLETE: {cycles_run} cycles, {pop_count} prompts")
    print(f"Champion: {first.strip() if ':' in first else 'N/A'}")
    print(f"Time: {total_time:.0f}s ({total_time/60:.1f}min)")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
