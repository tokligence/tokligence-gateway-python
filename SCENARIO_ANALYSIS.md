# Tokligence Gateway - Scenario Analysis

## 目标
识别所有可能的使用场景，分析配置需求，最终收敛为合理的profile组合。

---

## 维度1: 用户角色

### 1.1 个人开发者
- **典型用户**: 独立开发者、自由职业者、学生
- **需求**:
  - 低成本（尽量用local LLM）
  - 快速上手
  - 无需多用户管理
  - SQLite就够
- **场景**:
  - 日常开发辅助
  - 个人项目
  - 学习和实验

### 1.2 Coding Agent用户 ⭐
- **典型用户**: 使用Claude Code、Cursor、Codex CLI的程序员
- **需求**:
  - **API协议翻译** - Claude Code调用OpenAI, Codex调用Claude
  - **长时间会话** - coding session可能持续几小时
  - **大量token消耗** - 代码生成token多
  - **成本优化** - 可能需要路由到不同provider降低成本
  - **工具调用支持** - function calling必须稳定
- **场景**:
  - Claude Code → OpenAI (翻译)
  - Codex CLI → Anthropic (翻译)
  - Cursor → 混合provider (路由)

### 1.3 Agent框架开发者 ⭐
- **典型用户**: 使用LangChain、AutoGen、CrewAI等构建agent的开发者
- **需求**:
  - **Multi-turn对话** - agent需要多轮交互
  - **工具调用** - function calling是核心
  - **状态管理** - 可能需要缓存中间结果
  - **并发请求** - agent可能同时调用多个LLM
  - **Fallback** - 一个provider失败要能切换
- **场景**:
  - LangChain agent开发
  - AutoGen multi-agent系统
  - 自定义agent框架

### 1.4 Prompt安全研究者 ⭐
- **典型用户**: 安全研究员、红队、企业安全团队
- **需求**:
  - **Prompt firewall** - 检测和阻止prompt injection
  - **内容过滤** - 敏感信息检测和脱敏
  - **审计日志** - 详细记录所有prompt和response
  - **规则引擎** - 自定义安全规则
- **场景**:
  - Prompt injection防护
  - PII (个人信息) 检测和脱敏
  - 内容合规检查
  - 安全审计

### 1.5 研究员/数据科学家
- **典型用户**: ML研究员、数据分析师
- **需求**:
  - **批量处理** - 需要处理大量数据集
  - **实验追踪** - 记录不同model/parameter的结果
  - **成本追踪** - 分析不同model的成本
  - **A/B测试** - 对比不同provider的输出质量
- **场景**:
  - 数据标注
  - 模型评估
  - Prompt engineering研究
  - 成本优化分析

---

## 维度2: 团队规模

### 2.1 小团队 (2-10人) ⭐
- **需求**:
  - **共享配置** - 团队成员共用一个gateway
  - **基础用户管理** - API key per user
  - **成本分摊** - 看每个人用了多少token
  - **轻量部署** - Docker Compose就够
- **场景**:
  - 创业公司
  - 小型开发团队
  - 研究小组

### 2.2 中型团队 (10-50人)
- **需求**:
  - **多项目隔离** - 不同项目用不同provider/配置
  - **成本中心** - 按项目/部门分配成本
  - **审批流程** - 某些model需要审批才能用
  - **配额管理** - 限制每个用户/项目的用量
- **场景**:
  - 成长期公司
  - 多产品团队

### 2.3 大型企业 (50+ people) ⭐
- **需求**:
  - **SSO集成** - OIDC/SAML
  - **RBAC** - 基于角色的权限控制
  - **合规审计** - SOC2, ISO27001要求
  - **多租户** - 不同部门/BU隔离
  - **SLA保证** - 高可用、监控告警
- **场景**:
  - 大型企业
  - 金融、医疗等合规要求高的行业

---

## 维度3: 部署环境

### 3.1 本地开发
- **环境**: 开发者笔记本
- **需求**: 快速启动、无需依赖、轻量级
- **数据库**: SQLite
- **认证**: 无

### 3.2 单机部署
- **环境**: 单台服务器/VM
- **需求**: 稳定运行、重启自动恢复
- **数据库**: SQLite或PostgreSQL
- **认证**: API key

### 3.3 容器化部署
- **环境**: Docker/Docker Compose
- **需求**: 易于部署、配置外部化
- **数据库**: PostgreSQL (external)
- **认证**: API key或OIDC

### 3.4 Kubernetes
- **环境**: K8s集群
- **需求**: 高可用、水平扩展、rolling update
- **数据库**: PostgreSQL (StatefulSet或external)
- **认证**: OIDC + RBAC

### 3.5 Serverless
- **环境**: AWS Lambda, Google Cloud Run
- **需求**: 冷启动优化、无状态
- **数据库**: DynamoDB/Firestore
- **认证**: IAM或OIDC

---

## 维度4: 特殊需求

### 4.1 离线/内网环境 ⭐
- **场景**:
  - 金融机构内网
  - 国防、政府部门
  - 工厂/制造业内网
- **需求**:
  - **只用自建LLM** - Ollama, vLLM等
  - **无外网依赖** - 所有依赖都要内网镜像
  - **Air-gapped** - 完全隔离
- **配置**:
  - 禁用所有远程provider
  - 只启用local LLM
  - 可能需要离线文档

### 4.2 合规要求严格 ⭐
- **场景**:
  - GDPR (欧盟)
  - HIPAA (美国医疗)
  - CCPA (加州隐私)
  - SOC2
- **需求**:
  - **数据驻留** - 数据不能离开特定地区
  - **加密** - 传输和存储都要加密
  - **审计日志** - 不可变的日志
  - **数据保留策略** - 自动删除旧数据
  - **访问控制** - 严格的权限管理

### 4.3 成本敏感 ⭐
- **场景**:
  - 创业公司
  - 个人项目
  - 教育机构
- **需求**:
  - **智能路由** - 根据成本选择provider
  - **缓存** - 避免重复请求
  - **配额限制** - 防止超支
  - **成本告警** - 达到阈值发通知

### 4.4 性能关键
- **场景**:
  - 实时应用（chatbot）
  - 高并发API
  - 游戏NPC对话
- **需求**:
  - **低延迟** - < 100ms
  - **高吞吐** - > 1000 RPS
  - **连接池** - 复用连接
  - **负载均衡** - 多实例

### 4.5 内容安全关键 ⭐
- **场景**:
  - 面向儿童的应用
  - 教育平台
  - 企业内部chatbot
- **需求**:
  - **内容过滤** - 暴力、色情、政治敏感
  - **Toxicity检测** - 有害内容检测
  - **PII脱敏** - 自动移除个人信息
  - **合规检查** - 行业特定规则

---

## 维度5: 技术栈整合

### 5.1 Python生态
- **框架**: LangChain, LlamaIndex, Haystack
- **需求**: Python SDK, 原生集成

### 5.2 JavaScript生态
- **框架**: LangChain.js, Vercel AI SDK
- **需求**: 通过npm包使用

### 5.3 企业中间件
- **技术**: Kafka, Redis, RabbitMQ
- **需求**: 异步处理、消息队列集成

### 5.4 可观测性栈
- **技术**: Prometheus, Grafana, Jaeger, ELK
- **需求**: 指标、追踪、日志

---

## 场景汇总与聚类

基于以上分析，我们可以识别出以下核心场景：

### 🎯 核心场景（必须支持）

| # | 场景 | 核心需求 | 用户画像 | 优先级 |
|---|------|---------|---------|--------|
| 1 | **个人开发 (Personal)** | 轻量、快速、本地 | 个人开发者 | P0 |
| 2 | **Coding Agent (Coder)** | API翻译、长会话、工具调用 | Claude Code/Codex用户 | P0 |
| 3 | **Agent开发 (Agent)** | Multi-turn、缓存、fallback | LangChain/AutoGen开发者 | P0 |
| 4 | **小团队 (Team)** | 多用户、成本追踪、共享 | 2-10人团队 | P0 |
| 5 | **企业级 (Enterprise)** | SSO、合规、高可用 | 大型企业 | P1 |
| 6 | **安全增强 (Security)** | Prompt firewall、内容过滤 | 安全研究者、企业 | P1 |

### 🔧 扩展场景（可选支持）

| # | 场景 | 核心需求 | 可以基于 |
|---|------|---------|---------|
| 7 | **离线环境 (Airgap)** | 只用本地LLM、无外网 | Personal/Enterprise |
| 8 | **成本优化 (Cost)** | 智能路由、缓存、配额 | Personal/Team |
| 9 | **合规严格 (Compliance)** | 数据驻留、审计、加密 | Enterprise |
| 10 | **高性能 (Performance)** | 低延迟、高吞吐 | Team/Enterprise |
| 11 | **研究分析 (Research)** | 批量处理、实验追踪 | Personal/Agent |

---

## 配置需求矩阵

| 配置项 | Personal | Coder | Agent | Team | Enterprise | Security |
|--------|----------|-------|-------|------|------------|----------|
| **数据库** | SQLite | SQLite | PostgreSQL | PostgreSQL | PostgreSQL (HA) | PostgreSQL |
| **认证** | 无 | 无 | API Key | API Key | SSO/OIDC | SSO + MFA |
| **API翻译** | ✓ | ✅✅ | ✓ | ✓ | ✓ | ✓ |
| **工具调用** | ✓ | ✅✅ | ✅✅ | ✓ | ✓ | ✓ |
| **缓存** | - | ✓ | ✅ | ✅ | ✅ | ✓ |
| **多用户** | - | - | - | ✅✅ | ✅✅ | ✅ |
| **成本追踪** | ✓ | ✓ | ✓ | ✅✅ | ✅✅ | ✅ |
| **Prompt Firewall** | - | - | - | - | ✓ | ✅✅ |
| **内容过滤** | - | - | - | - | ✓ | ✅✅ |
| **审计日志** | - | - | ✓ | ✓ | ✅✅ | ✅✅ |
| **Rate Limiting** | - | - | ✓ | ✅ | ✅✅ | ✅ |
| **高可用** | - | - | - | - | ✅✅ | ✅ |
| **Metrics** | - | - | ✓ | ✅ | ✅✅ | ✅✅ |
| **K8s部署** | - | - | - | ✓ | ✅✅ | ✅ |

**图例**:
- ✅✅ = 核心功能
- ✅ = 推荐启用
- ✓ = 可选
- \- = 不需要

---

## 场景细节展开

### Scenario 1: Personal (个人开发)

**典型用户故事**:
> 我是一个独立开发者，想用LLM帮我写代码。我本地装了Ollama，但有时候需要调用Claude做复杂任务。我不需要多用户管理，就我自己用。

**配置重点**:
```yaml
gateway:
  port: 8081
  auth:
    enabled: false  # 本地使用不需要认证

database:
  type: sqlite
  path: ~/.tokligence/gateway.db

providers:
  ollama:
    enabled: true
    base_url: http://localhost:11434
  anthropic:
    enabled: true  # 偶尔用Claude
  openai:
    enabled: false  # 不用

cache:
  enabled: false  # 不需要

metrics:
  enabled: false
```

**依赖**:
```bash
pip install tokligence
# 无额外依赖
```

---

### Scenario 2: Coder (Coding Agent用户) ⭐

**典型用户故事**:
> 我用Claude Code写代码，但我想让它调用OpenAI的GPT-4。或者反过来，我用Cursor（OpenAI compatible）但想调用Claude。Gateway需要做协议翻译。

**配置重点**:
```yaml
gateway:
  port: 8081
  work_mode: auto  # 智能路由和翻译
  auth:
    enabled: false  # 本地使用

  # Coding agent优化
  request_timeout: 300  # 5分钟（代码生成可能很长）
  max_tokens_default: 4096  # 代码通常需要更多token

database:
  type: sqlite

providers:
  openai:
    enabled: true
    models:
      - gpt-4-turbo  # 复杂任务
      - gpt-3.5-turbo  # 简单任务（省钱）
  anthropic:
    enabled: true
    models:
      - claude-3-opus-20240229  # 复杂代码
      - claude-3-sonnet-20240229  # 一般任务

# 工具调用优化
tool_calling:
  enabled: true
  duplicate_detection: true  # 防止Codex/Claude Code无限循环
  max_iterations: 10

# 可选：成本优化
routing:
  cost_aware: true
  prefer_cheaper_for_simple_tasks: true
```

**使用示例**:
```bash
# Claude Code → OpenAI
export ANTHROPIC_API_BASE="http://localhost:8081/anthropic"
# Gateway会翻译Anthropic请求到OpenAI API

# Cursor → Claude
export OPENAI_API_BASE="http://localhost:8081/v1"
# Gateway会翻译OpenAI请求到Anthropic API
```

**依赖**:
```bash
pip install "tokligence[chat]"  # 可选，用于debug
```

---

### Scenario 3: Agent (Agent框架开发)

**典型用户故事**:
> 我用LangChain开发multi-agent系统。Agents之间需要互相调用LLM，有时候一个task需要10+轮对话。我需要缓存中间结果，需要fallback机制。

**配置重点**:
```yaml
gateway:
  port: 8081
  work_mode: auto
  max_concurrent_requests: 50  # 多agent并发

database:
  type: postgresql  # 生产环境用PG
  host: localhost
  port: 5432

providers:
  openai:
    enabled: true
    models:
      - gpt-4-turbo
      - gpt-3.5-turbo
  anthropic:
    enabled: true
  google:
    enabled: true

# 缓存对multi-turn很重要
cache:
  enabled: true
  type: redis
  host: localhost
  port: 6379
  ttl: 3600  # 1小时

# Agent特定优化
agent:
  enable_session_persistence: true  # 保存对话历史
  max_conversation_length: 50  # 最多50轮

  # Fallback策略
  fallback:
    enabled: true
    retry_attempts: 3
    fallback_models:
      gpt-4: claude-3-opus-20240229
      gpt-3.5-turbo: claude-3-sonnet-20240229

# 工具调用
tool_calling:
  enabled: true
  max_iterations: 20  # Agent可能需要更多轮

# 监控很重要
metrics:
  enabled: true
  track_agent_sessions: true
```

**LangChain集成**:
```python
from tokligence.integrations.langchain import TokligenceLLM

llm = TokligenceLLM(
    gateway_url="http://localhost:8081",
    model="gpt-4-turbo",
    fallback_model="claude-3-opus-20240229"
)
```

**依赖**:
```bash
pip install "tokligence[agent,chat]"
# 包含: langchain, autogen, redis client
```

---

### Scenario 4: Team (小团队)

**典型用户故事**:
> 我们是一个10人的创业团队，大家共用一个Gateway。我需要看每个人用了多少钱，限制每人每月的配额。有些贵的model（GPT-4）需要我审批。

**配置重点**:
```yaml
gateway:
  port: 8081
  auth:
    enabled: true
    type: api_key

database:
  type: postgresql
  host: localhost
  pool_size: 20

providers:
  openai:
    enabled: true
  anthropic:
    enabled: true

# 团队管理
team:
  enabled: true

  # 成本追踪
  cost_tracking:
    enabled: true
    currency: USD
    alert_threshold: 1000  # 超过$1000告警

  # 配额管理
  quotas:
    per_user_monthly: 100  # $100/人/月
    per_user_daily: 10     # $10/人/天

  # 模型审批
  model_approval:
    enabled: true
    requires_approval:
      - gpt-4
      - claude-3-opus-20240229
    admin_users:
      - admin@team.com

# 缓存（节省成本）
cache:
  enabled: true
  type: redis

# Rate limiting
rate_limit:
  enabled: true
  per_user_per_hour: 1000

# 审计
audit:
  enabled: true
  log_all_requests: true
```

**团队管理**:
```bash
# 创建用户
tokligence user create alice --email alice@team.com --quota 100

# 生成API key
tokligence apikey create <alice-id> --name "Alice's Key"

# 查看用量
tokligence usage --user <alice-id> --month 2024-11

# 查看团队总成本
tokligence usage --team --month 2024-11
```

**依赖**:
```bash
pip install "tokligence[team,chat]"
# 包含: psycopg2, redis, celery (异步任务)
```

---

### Scenario 5: Enterprise (企业级)

**典型用户故事**:
> 我们是一家金融科技公司，有200+员工。需要SSO集成、SOC2合规、多租户隔离、高可用部署。需要详细的审计日志用于合规检查。

**配置重点**:
```yaml
gateway:
  port: 8081
  auth:
    enabled: true
    type: oidc
    oidc_provider: https://auth.company.com
    oidc_client_id: ${OIDC_CLIENT_ID}
    multi_factor: true  # 强制MFA

database:
  type: postgresql
  host: postgres-primary.svc.cluster.local
  pool_size: 100
  replication:
    enabled: true
    replicas:
      - postgres-replica-1.svc.cluster.local
      - postgres-replica-2.svc.cluster.local

# 多租户
multi_tenancy:
  enabled: true
  isolation_level: strict  # 严格隔离
  tenants:
    - name: engineering
      quota: 10000  # $10k/月
    - name: product
      quota: 5000
    - name: finance
      quota: 2000

# 合规
compliance:
  soc2: true
  hipaa: false
  gdpr: true
  data_retention_days: 90
  encryption_at_rest: true
  encryption_in_transit: true

# 审计日志（不可变）
audit:
  enabled: true
  immutable: true
  storage: s3
  retention_years: 7

# 高可用
high_availability:
  enabled: true
  replicas: 3
  health_check_interval: 10

# 全栈可观测性
observability:
  metrics:
    enabled: true
    prometheus_port: 9090
  tracing:
    enabled: true
    jaeger_endpoint: http://jaeger:14268
  logging:
    level: info
    structured: true
    elk_endpoint: http://elasticsearch:9200

# K8s配置
kubernetes:
  namespace: tokligence-prod
  resources:
    requests:
      cpu: "2"
      memory: "4Gi"
    limits:
      cpu: "4"
      memory: "8Gi"
  autoscaling:
    enabled: true
    min_replicas: 3
    max_replicas: 10
    target_cpu: 70
```

**部署**:
```bash
helm install tokligence ./charts/tokligence \
  --set profile=enterprise \
  --set replicaCount=3 \
  --namespace tokligence-prod
```

**依赖**:
```bash
pip install "tokligence[enterprise,all]"
# 包含: kubernetes, prometheus_client, opentelemetry, hvac (vault)
```

---

### Scenario 6: Security (安全增强) ⭐

**典型用户故事**:
> 我们开发面向用户的chatbot，需要防止prompt injection攻击。还需要检测和过滤有害内容、自动脱敏PII。所有prompt都要记录用于安全审计。

**配置重点**:
```yaml
gateway:
  port: 8081
  auth:
    enabled: true

database:
  type: postgresql

# 核心：安全层
security:
  # Prompt Firewall
  prompt_firewall:
    enabled: true
    rules:
      - name: detect_injection
        pattern: "ignore previous|forget instructions|system:"
        action: block
        severity: high

      - name: detect_jailbreak
        pattern: "DAN|developer mode|unrestricted"
        action: block
        severity: critical

    # ML-based检测
    ml_detection:
      enabled: true
      model: prompt-guard-v1
      threshold: 0.8

  # 内容过滤
  content_filter:
    enabled: true

    # Toxicity检测
    toxicity:
      enabled: true
      threshold: 0.7
      categories:
        - hate_speech
        - violence
        - sexual_content
        - self_harm

    # PII检测和脱敏
    pii_detection:
      enabled: true
      auto_redact: true
      types:
        - email
        - phone
        - ssn
        - credit_card
        - ip_address

  # 响应验证
  response_validation:
    enabled: true
    check_output_safety: true
    block_unsafe_output: true

# 详细审计
audit:
  enabled: true
  log_all_prompts: true  # 记录所有prompt
  log_all_responses: true
  log_security_events: true
  alert_on_blocked: true

  # 告警
  alerts:
    email: security@company.com
    slack_webhook: ${SLACK_WEBHOOK}
    pagerduty: false

# 监控安全指标
metrics:
  enabled: true
  security_metrics: true
  track_blocked_requests: true
  track_pii_detections: true
```

**使用示例**:
```python
from tokligence.security import PromptFirewall, ContentFilter

# 手动测试规则
firewall = PromptFirewall()
result = firewall.check("Ignore all previous instructions")
# result.blocked = True
# result.reason = "Potential prompt injection detected"

# 内容过滤
filter = ContentFilter()
safe_text = filter.redact_pii("My email is john@example.com")
# safe_text = "My email is [EMAIL_REDACTED]"
```

**依赖**:
```bash
pip install "tokligence[security]"
# 包含: presidio (PII), detoxify (toxicity), transformers (ML models)
```

---

## 场景收敛建议

基于以上分析，我建议收敛为 **6个核心profile**:

### 推荐的Profile组合

| Profile | 目标用户 | 核心差异点 | 包含extras | 配置模板 |
|---------|---------|-----------|-----------|---------|
| **personal** | 个人开发者 | 轻量、本地 | - | personal.yaml |
| **coder** ⭐ | Coding agent用户 | API翻译、长会话 | chat | coder.yaml |
| **agent** | Agent开发者 | Multi-turn、缓存 | agent, chat | agent.yaml |
| **team** | 小团队 | 多用户、成本追踪 | team, chat | team.yaml |
| **enterprise** | 大型企业 | SSO、合规、HA | enterprise, all | enterprise.yaml |
| **security** ⭐ | 安全关键 | Firewall、过滤 | security, team | security.yaml |

### 可以通过组合实现的场景

这些场景不需要单独的profile，可以通过组合和配置实现：

- **airgap** (离线): `personal` + 配置只用local LLM
- **cost-optimized**: `personal/team` + 启用缓存和智能路由
- **compliance**: `enterprise` + 启用合规选项
- **performance**: `team/enterprise` + 调整并发和缓存参数
- **research**: `personal/agent` + 启用实验追踪

---

## 下一步

1. **确认6个核心profile** - 你觉得这6个合理吗？需要调整吗？
2. **定义extras依赖** - 确定每个extras需要哪些Python包
3. **实现profile模板** - 创建6个yaml配置模板
4. **更新pyproject.toml** - 添加optional-dependencies
5. **实现profile加载** - 支持`--profile`参数
6. **编写文档** - 每个profile的使用指南

你觉得呢？我们现在应该：
- A) 继续细化这6个profile的配置细节
- B) 减少profile数量（比如合并coder和agent）
- C) 增加profile（比如单独的compliance profile）
- D) 直接开始实现
