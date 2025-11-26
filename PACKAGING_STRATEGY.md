# Tokligence Gateway - Packaging Strategy for Different Scenarios

## Overview

This document outlines the packaging strategy for different use case scenarios: personal gateway, agent development, team deployment, and enterprise usage.

## Recommended Approach: Hybrid Strategy

**Single Package + Optional Extras + Config Profiles**

This combines the best of both worlds:
1. Single PyPI package for easy discovery and maintenance
2. Optional dependency groups for different scenarios
3. Built-in configuration profiles for quick setup

## Package Structure

### pyproject.toml Configuration

```toml
[project]
name = "tokligence"
version = "0.3.4"
dependencies = [
    "click>=8.0",
    "pyyaml>=5.4",
    "requests>=2.25",
    "rich>=10.0",
]

[project.optional-dependencies]
# AI Configuration Assistant
chat = [
    "openai>=1.0.0",
    "anthropic>=0.18.0",
    "google-generativeai>=0.4.0",
    "httpx>=0.24.0",
]

# Agent Development
agent = [
    "langchain>=0.1.0",      # LangChain integration
    "autogen>=0.2.0",        # AutoGen support
    "litellm>=1.0.0",        # Multi-provider SDK
    "python-dotenv>=1.0.0",  # Environment management
]

# Team Deployment
team = [
    "redis>=4.0.0",          # Distributed caching
    "celery>=5.3.0",         # Task queue
    "psycopg2-binary>=2.9",  # PostgreSQL support
    "python-multipart>=0.0.6", # File uploads
]

# Enterprise Features
enterprise = [
    "prometheus-client>=0.19.0",  # Metrics
    "kubernetes>=28.0.0",         # K8s deployment
    "hvac>=1.2.0",                # Vault integration
    "opentelemetry-api>=1.20.0",  # Observability
    "jwt>=1.3.0",                 # SSO/OIDC
]

# Development & Testing
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]

# Install everything
all = [
    "tokligence[chat,agent,team,enterprise,dev]"
]
```

### Configuration Profiles

```
tokligence/
  profiles/
    __init__.py
    personal.yaml      # Lightweight, SQLite, single-user
    agent.yaml         # Optimized for agent frameworks
    team.yaml          # Multi-user, PostgreSQL, Redis
    enterprise.yaml    # Full features, K8s ready
```

## Installation Scenarios

### 1. Personal Gateway (Default)

**Use Case:** Individual developer, local development, testing

**Installation:**
```bash
pip install tokligence
```

**Includes:**
- Core gateway functionality
- SQLite database
- Basic CLI tools
- Local configuration

**Init:**
```bash
tokligence init --profile personal
# or
tokligence init  # personal is default
```

**Config Highlights:**
```yaml
gateway:
  port: 8081
  auth:
    enabled: false  # No auth for local use
  work_mode: auto

database:
  type: sqlite
  path: ~/.config/tokligence/gateway.db

providers:
  openai:
    enabled: true
  anthropic:
    enabled: true
```

---

### 2. Agent Development

**Use Case:** Building AI agents with LangChain, AutoGen, etc.

**Installation:**
```bash
pip install "tokligence[agent,chat]"
```

**Includes:**
- Core gateway
- LangChain integration helpers
- AutoGen compatibility layer
- AI configuration assistant
- Multi-provider SDK

**Init:**
```bash
tokligence init --profile agent
```

**Config Highlights:**
```yaml
gateway:
  port: 8081
  work_mode: auto
  # Optimized for agent workloads
  max_concurrent_requests: 50
  request_timeout: 300  # Longer timeout for agents

database:
  type: sqlite  # or postgresql for production agents

providers:
  openai:
    enabled: true
    models:
      - gpt-4-turbo
      - gpt-3.5-turbo
  anthropic:
    enabled: true
    models:
      - claude-3-opus-20240229
      - claude-3-sonnet-20240229
  google:
    enabled: true

# Agent-specific settings
agent:
  enable_caching: true
  cache_ttl: 3600
  tool_calling:
    max_iterations: 10
    duplicate_detection: true
```

**Code Example:**
```python
from tokligence.agent import LangChainGateway, AutoGenGateway

# LangChain integration
llm = LangChainGateway(
    model="claude-3-sonnet-20240229",
    temperature=0.7
)

# AutoGen integration
config_list = AutoGenGateway.get_config_list()
```

---

### 3. Team Deployment

**Use Case:** Shared gateway for development team, multi-user, PostgreSQL

**Installation:**
```bash
pip install "tokligence[team,chat]"
```

**Includes:**
- Core gateway
- Redis for distributed caching
- PostgreSQL support
- Celery for async tasks
- AI configuration assistant

**Init:**
```bash
tokligence init --profile team
```

**Config Highlights:**
```yaml
gateway:
  port: 8081
  auth:
    enabled: true
    type: api_key
  work_mode: auto

database:
  type: postgresql
  host: localhost
  port: 5432
  database: tokligence
  username: tokligence
  pool_size: 20
  max_overflow: 10

cache:
  enabled: true
  type: redis
  host: localhost
  port: 6379
  ttl: 3600

# Rate limiting
rate_limit:
  enabled: true
  per_user: 1000  # requests per hour
  per_ip: 5000

# Metrics
metrics:
  enabled: true
  prometheus_port: 9090
```

**Setup Script:**
```python
from tokligence import Gateway, Daemon
from tokligence.team import create_team, add_member

# Initialize team gateway
gateway = Gateway.from_profile('team')
gateway.init()

# Create team
team = create_team("Engineering")

# Add members
for email in ["alice@team.com", "bob@team.com"]:
    member = add_member(team.id, email)
    print(f"Added {member.email} with API key: {member.api_key}")

# Start daemon
daemon = Daemon(port=8081)
daemon.start(background=True)
```

---

### 4. Enterprise Deployment

**Use Case:** Production, Kubernetes, full observability, SSO

**Installation:**
```bash
pip install "tokligence[enterprise,all]"
```

**Includes:**
- All features from personal, agent, team
- Kubernetes deployment configs
- Prometheus metrics
- OpenTelemetry tracing
- Vault integration
- SSO/OIDC support

**Init:**
```bash
tokligence init --profile enterprise
```

**Config Highlights:**
```yaml
gateway:
  port: 8081
  auth:
    enabled: true
    type: oidc
    oidc_provider: https://auth.company.com
    oidc_client_id: ${OIDC_CLIENT_ID}
  work_mode: auto
  high_availability: true

database:
  type: postgresql
  host: postgres.svc.cluster.local
  port: 5432
  database: tokligence
  pool_size: 50
  max_overflow: 20
  ssl_mode: require

cache:
  enabled: true
  type: redis
  host: redis.svc.cluster.local
  port: 6379
  cluster_mode: true

# Observability
metrics:
  enabled: true
  prometheus_port: 9090

tracing:
  enabled: true
  exporter: otlp
  endpoint: http://jaeger-collector:4318

# Secrets management
secrets:
  provider: vault
  vault_addr: https://vault.company.com
  vault_role: tokligence-gateway

# Kubernetes
kubernetes:
  namespace: tokligence
  replicas: 3
  resources:
    requests:
      cpu: "1"
      memory: "2Gi"
    limits:
      cpu: "2"
      memory: "4Gi"
```

**Deployment:**
```bash
# Using Helm chart
helm install tokligence ./charts/tokligence-gateway \
  --set profile=enterprise \
  --set replicas=3 \
  --set database.host=postgres.svc.cluster.local

# Or using kubectl
kubectl apply -f deployments/enterprise/
```

---

## Comparison Matrix

| Feature | Personal | Agent | Team | Enterprise |
|---------|----------|-------|------|------------|
| **Installation** | `pip install tokligence` | `pip install "tokligence[agent]"` | `pip install "tokligence[team]"` | `pip install "tokligence[enterprise]"` |
| **Database** | SQLite | SQLite/PostgreSQL | PostgreSQL | PostgreSQL (HA) |
| **Authentication** | None | Optional | API Keys | SSO/OIDC |
| **Caching** | None | Optional | Redis | Redis Cluster |
| **Metrics** | None | Basic | Prometheus | Full Observability |
| **Deployment** | Local | Local/Server | Server/Docker | Kubernetes |
| **Multi-User** | No | No | Yes | Yes |
| **Rate Limiting** | No | No | Yes | Yes |
| **SSO/OIDC** | No | No | No | Yes |
| **High Availability** | No | No | Optional | Yes |
| **Agent Integrations** | No | Yes | Yes | Yes |
| **Cost** | Free | Free | Free | Free (OSS) |

---

## Profile Switching

Users can easily switch between profiles:

### During Init
```bash
tokligence init --profile agent
tokligence init --profile team
tokligence init --profile enterprise
```

### Programmatically
```python
from tokligence import Gateway

# Load specific profile
gateway = Gateway.from_profile('agent')

# Or customize
gateway = Gateway(config_path='~/.config/tokligence/config.yaml')
gateway.load_profile('team')
gateway.override({
    'gateway.port': 8082,
    'database.type': 'postgresql'
})
gateway.save()
```

### Environment Override
```bash
export TOKLIGENCE_PROFILE=team
tokligence init  # Uses team profile

# Or in code
import os
os.environ['TOKLIGENCE_PROFILE'] = 'enterprise'
```

---

## Migration Path

### From Personal to Team

```bash
# 1. Export personal data
tokligence export --output personal_backup.json

# 2. Reinit with team profile
tokligence init --profile team

# 3. Setup PostgreSQL
# Create database and user

# 4. Import data
tokligence import --input personal_backup.json

# 5. Create team users
tokligence user create alice --email alice@team.com
tokligence apikey create <user-id> --name "Alice's Key"
```

### From Team to Enterprise

```bash
# 1. Backup
tokligence backup --output team_backup.tar.gz

# 2. Deploy enterprise
helm install tokligence ./charts/tokligence-gateway \
  --set profile=enterprise

# 3. Restore
kubectl exec -it tokligence-0 -- tokligence restore --input team_backup.tar.gz

# 4. Configure SSO
kubectl apply -f configs/oidc-config.yaml
```

---

## Custom Profiles

Users can create custom profiles:

```bash
# Create custom profile
tokligence profile create my-custom \
  --base team \
  --set gateway.port=9000 \
  --set database.pool_size=100

# Use custom profile
tokligence init --profile my-custom

# List available profiles
tokligence profile list
```

**Custom Profile Location:**
```
~/.config/tokligence/profiles/
  my-custom.yaml
```

---

## Implementation Tasks

- [ ] Create profile templates in `tokligence/profiles/`
- [ ] Add `--profile` flag to `tokligence init` command
- [ ] Implement `Gateway.from_profile()` method
- [ ] Add profile management commands (`profile create`, `profile list`)
- [ ] Update documentation with scenario-specific guides
- [ ] Create Helm chart for enterprise deployment
- [ ] Add agent integration helpers (`tokligence.agent`)
- [ ] Add team management helpers (`tokligence.team`)
- [ ] Write migration guides
- [ ] Add profile validation

---

## Future Enhancements

### Scenario-Specific Packages (Optional)

If demand grows, we can create convenience meta-packages:

```bash
pip install tokligence-personal    # = tokligence
pip install tokligence-agent        # = tokligence[agent,chat]
pip install tokligence-team         # = tokligence[team,chat]
pip install tokligence-enterprise   # = tokligence[enterprise,all]
```

These would just be meta-packages that install the main package with the right extras.

### Profile Marketplace

Allow community to share profiles:

```bash
# Install community profile
tokligence profile install langchain-optimized \
  --from github.com/user/tokligence-profiles

# Publish profile
tokligence profile publish my-profile \
  --to github.com/myuser/tokligence-profiles
```

---

## Conclusion

The hybrid approach (single package + optional extras + config profiles) provides:

1. **Simplicity** - One package name, one installation command
2. **Flexibility** - Users can mix and match extras
3. **Optimization** - Each scenario has optimized defaults
4. **Growth Path** - Easy migration from personal → team → enterprise
5. **Maintainability** - Single codebase, single version

This approach is proven by other popular packages:
- Django: `django[argon2,bcrypt]`
- FastAPI: `fastapi[all]`
- Airflow: `apache-airflow[postgres,celery,redis]`
