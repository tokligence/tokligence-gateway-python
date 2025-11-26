# Coder Profile - 功能规格说明

## 目标用户

使用 Coding Agent 工具的程序员：
- **Claude Code** 用户（Anthropic SDK）
- **GitHub Copilot / Codex CLI** 用户（OpenAI SDK）
- **Cursor** 用户（OpenAI-compatible）
- **Continue.dev** 用户
- **Aider** 用户
- 任何需要 IDE 级别 LLM 集成的开发者

## 核心痛点

### 痛点1: 协议不兼容 ⭐⭐⭐
**问题**:
- 我用 Claude Code，但想调用 OpenAI 的 GPT-4
- 我用 Cursor（OpenAI），但想调用 Anthropic 的 Claude
- 工具锁定在一个协议上，无法切换 provider

**解决方案**: **双向协议翻译**
- OpenAI API → Anthropic Messages API
- Anthropic API → OpenAI Chat Completions API
- 完全透明，零配置

### 痛点2: 工具调用无限循环 ⭐⭐⭐
**问题**:
- Codex CLI 调用 Claude 时，tool calling 重复触发
- Agent 陷入无限循环（同一个 tool 被反复调用）
- 浪费 token，浪费钱，浪费时间

**解决方案**: **智能去重检测**
- 检测重复的 tool call（相同 name + arguments）
- 自动打断无限循环
- 可配置去重策略

### 痛点3: 长时间会话超时 ⭐⭐
**问题**:
- Coding session 可能持续几小时
- 默认超时（30s-60s）太短
- 复杂代码生成需要更长时间

**解决方案**: **长超时配置**
- 默认 5 分钟超时
- 支持 streaming 保持连接
- 可配置超时策略

### 痛点4: 成本失控 ⭐⭐
**问题**:
- GPT-4 很贵，但有时候 GPT-3.5 就够了
- 不知道哪个 task 花了多少钱
- 月底账单爆炸

**解决方案**: **智能路由 + 成本追踪**
- 简单问题自动路由到便宜模型
- 实时显示当前会话成本
- 月度/周度成本报告

### 痛点5: 上下文窗口限制 ⭐
**问题**:
- 大型代码库超过模型上下文限制
- 需要精细控制发送给 LLM 的内容

**解决方案**: **上下文管理**
- 智能裁剪上下文
- 优先保留重要信息
- 可配置上下文策略

---

## 功能需求清单

### 1. 核心功能（Must Have）

#### 1.1 双向协议翻译 ⭐⭐⭐
```yaml
translation:
  enabled: true
  bidirectional: true

  # OpenAI → Anthropic
  openai_to_anthropic:
    enabled: true
    preserve_tool_calls: true
    preserve_streaming: true

  # Anthropic → OpenAI
  anthropic_to_openai:
    enabled: true
    preserve_tool_use: true
    preserve_streaming: true

  # 自动检测和选择
  auto_detect: true
```

**实现细节**:
```python
class ProtocolTranslator:
    def translate_openai_to_anthropic(self, request):
        """
        OpenAI Chat Completions → Anthropic Messages

        映射:
        - messages[] → messages[]
        - functions[] → tools[]
        - function_call → tool_choice
        - stream → stream
        """
        pass

    def translate_anthropic_to_openai(self, request):
        """
        Anthropic Messages → OpenAI Chat Completions

        映射:
        - messages[] → messages[]
        - tools[] → functions[]
        - tool_choice → function_call
        - stream → stream
        """
        pass
```

#### 1.2 工具调用去重 ⭐⭐⭐
```yaml
tool_calling:
  enabled: true

  # 去重配置
  deduplication:
    enabled: true
    strategy: exact_match  # exact_match | semantic_similarity

    # 检测窗口
    window_size: 10  # 检查最近10次调用

    # 相同调用定义
    exact_match:
      compare_name: true
      compare_arguments: true
      ignore_fields: [timestamp, id]

    # 语义相似度（可选）
    semantic_similarity:
      threshold: 0.95
      model: sentence-transformers

  # 无限循环检测
  loop_detection:
    enabled: true
    max_same_tool_calls: 3  # 同一工具最多调用3次
    action: warn_and_break  # warn_and_break | warn | break

  # 调试模式
  debug:
    log_all_tool_calls: true
    alert_on_duplicate: true
```

**实现细节**:
```python
class ToolCallDeduplicator:
    def __init__(self, window_size=10):
        self.recent_calls = []
        self.window_size = window_size

    def is_duplicate(self, tool_call):
        """检查是否重复"""
        for recent in self.recent_calls[-self.window_size:]:
            if self._is_same_call(tool_call, recent):
                return True
        return False

    def _is_same_call(self, call1, call2):
        """比较两个tool call是否相同"""
        return (
            call1['name'] == call2['name'] and
            call1['arguments'] == call2['arguments']
        )

    def detect_loop(self):
        """检测无限循环"""
        # 统计最近N次调用中，每个工具被调用的次数
        tool_counts = {}
        for call in self.recent_calls[-self.window_size:]:
            name = call['name']
            tool_counts[name] = tool_counts.get(name, 0) + 1

        # 如果某个工具被调用超过阈值，认为是循环
        for name, count in tool_counts.items():
            if count > self.max_same_tool_calls:
                return True, name
        return False, None
```

#### 1.3 长超时支持 ⭐⭐
```yaml
timeout:
  # Coding 场景需要更长超时
  request_timeout: 300  # 5分钟
  streaming_timeout: 600  # 10分钟（streaming可以更长）

  # 保活机制
  keepalive:
    enabled: true
    interval: 30  # 每30秒发送heartbeat
```

#### 1.4 成本追踪 ⭐⭐
```yaml
cost_tracking:
  enabled: true

  # 实时显示
  real_time:
    enabled: true
    show_per_request: true
    show_session_total: true

  # 成本报告
  reporting:
    daily_summary: true
    weekly_summary: true
    monthly_summary: true
    email_report: false

  # 预算告警
  budget_alerts:
    enabled: true
    daily_limit: 10  # $10/天
    monthly_limit: 300  # $300/月
    alert_at_percentage: 80  # 80%时告警
```

**实现细节**:
```python
class CostTracker:
    def calculate_cost(self, model, input_tokens, output_tokens):
        """计算单次请求成本"""
        pricing = {
            'gpt-4-turbo': {
                'input': 0.01 / 1000,   # $0.01 per 1K tokens
                'output': 0.03 / 1000,
            },
            'gpt-3.5-turbo': {
                'input': 0.0015 / 1000,
                'output': 0.002 / 1000,
            },
            'claude-3-opus': {
                'input': 0.015 / 1000,
                'output': 0.075 / 1000,
            },
            'claude-3-sonnet': {
                'input': 0.003 / 1000,
                'output': 0.015 / 1000,
            },
        }

        model_pricing = pricing.get(model, pricing['gpt-3.5-turbo'])
        cost = (
            input_tokens * model_pricing['input'] +
            output_tokens * model_pricing['output']
        )
        return cost

    def get_session_cost(self, session_id):
        """获取会话总成本"""
        pass

    def check_budget(self, user_id):
        """检查是否超预算"""
        daily_usage = self.get_daily_usage(user_id)
        if daily_usage > self.daily_limit:
            raise BudgetExceededError(f"Daily limit ${self.daily_limit} exceeded")
```

---

### 2. 高级功能（Should Have）

#### 2.1 智能路由 ⭐⭐
```yaml
intelligent_routing:
  enabled: true

  # 基于复杂度路由
  complexity_based:
    enabled: true

    # 简单任务（cheap model）
    simple_tasks:
      model: gpt-3.5-turbo
      triggers:
        - short_prompt  # < 100 tokens
        - simple_keywords: ["explain", "what is", "how to"]

    # 复杂任务（expensive model）
    complex_tasks:
      model: gpt-4-turbo
      triggers:
        - long_prompt  # > 500 tokens
        - complex_keywords: ["refactor", "optimize", "debug"]
        - has_code_blocks: true

  # 基于成本路由
  cost_based:
    enabled: true
    prefer_cheaper: true
    fallback_to_expensive: true  # 便宜模型失败时切换

  # 负载均衡
  load_balancing:
    enabled: true
    strategy: round_robin  # round_robin | least_latency | random
```

#### 2.2 上下文管理 ⭐
```yaml
context_management:
  enabled: true

  # 上下文窗口限制
  max_context_tokens: 8000

  # 裁剪策略
  truncation_strategy: smart  # smart | head | tail | middle

  # 智能裁剪
  smart_truncation:
    # 优先级
    priority:
      - system_message  # 系统消息（最高优先级）
      - recent_messages  # 最近的对话
      - code_blocks  # 代码块
      - tool_results  # 工具调用结果
      - older_messages  # 旧对话（最低优先级）

    # 保留策略
    preserve:
      min_recent_messages: 5  # 至少保留最近5条
      min_system_tokens: 200  # 系统消息至少200 tokens
```

#### 2.3 缓存优化 ⭐
```yaml
caching:
  enabled: true

  # 代码相关的查询很适合缓存
  cache_candidates:
    - documentation_queries  # "what is X?"
    - error_explanations     # "what does this error mean?"
    - simple_code_snippets   # "write a function to..."

  # 缓存配置
  ttl: 3600  # 1小时
  max_cache_size: 1000  # 最多1000条

  # 语义缓存（高级）
  semantic_cache:
    enabled: false  # 可选
    similarity_threshold: 0.95
```

#### 2.4 响应优化 ⭐
```yaml
response_optimization:
  # 流式响应优化
  streaming:
    enabled: true
    chunk_size: 50  # 每50个token发送一次

  # 代码格式化
  code_formatting:
    enabled: true
    auto_detect_language: true
    syntax_highlighting: false  # IDE 自己会做

  # Markdown 渲染
  markdown:
    enabled: true
    preserve_code_blocks: true
```

---

### 3. 调试和监控（Nice to Have）

#### 3.1 详细日志 ⭐⭐
```yaml
logging:
  level: info  # debug | info | warn | error

  # Coder 特定日志
  coder_logs:
    log_protocol_translation: true
    log_tool_calls: true
    log_cost_per_request: true
    log_latency: true

  # 文件输出
  file:
    enabled: true
    path: ~/.tokligence/coder.log
    rotate: daily
```

#### 3.2 性能监控
```yaml
monitoring:
  enabled: true

  # Coder 关心的指标
  metrics:
    - request_latency
    - tokens_per_request
    - cost_per_request
    - tool_call_count
    - duplicate_tool_calls
    - cache_hit_rate

  # Dashboard
  dashboard:
    enabled: false  # CLI 用户可能不需要
    port: 9090
```

#### 3.3 调试模式
```yaml
debug:
  enabled: false

  # 详细信息
  verbose:
    show_raw_requests: false
    show_raw_responses: false
    show_translations: true  # 显示协议翻译过程

  # Dry run
  dry_run:
    enabled: false
    skip_actual_api_calls: true
```

---

## 配置文件模板

### coder.yaml (完整配置)

```yaml
# Tokligence Gateway - Coder Profile
# 优化用于 Claude Code, Cursor, Codex CLI 等 coding agent

profile: coder
version: 0.3.4

gateway:
  port: 8081
  work_mode: auto  # 智能路由和翻译

  # 本地使用不需要认证
  auth:
    enabled: false

  # Coding 需要更长超时
  timeout:
    request: 300  # 5分钟
    streaming: 600  # 10分钟

  # 较高并发（IDE 可能同时发多个请求）
  max_concurrent_requests: 20

database:
  # 个人使用 SQLite 足够
  type: sqlite
  path: ~/.tokligence/coder.db

providers:
  # OpenAI
  openai:
    enabled: true
    api_key: ${OPENAI_API_KEY}
    models:
      - gpt-4-turbo          # 复杂任务
      - gpt-4                # 备选
      - gpt-3.5-turbo        # 简单任务（省钱）

  # Anthropic
  anthropic:
    enabled: true
    api_key: ${ANTHROPIC_API_KEY}
    models:
      - claude-3-opus-20240229      # 最强，复杂代码
      - claude-3-sonnet-20240229    # 平衡性价比
      - claude-3-haiku-20240307     # 快速简单任务

  # Google (可选)
  google:
    enabled: false
    api_key: ${GOOGLE_API_KEY}

  # Local LLM (可选)
  ollama:
    enabled: false
    base_url: http://localhost:11434

# 核心功能：协议翻译
translation:
  enabled: true
  bidirectional: true
  preserve_tool_calls: true
  preserve_streaming: true
  auto_detect: true

# 核心功能：工具调用去重
tool_calling:
  enabled: true

  deduplication:
    enabled: true
    strategy: exact_match
    window_size: 10

  loop_detection:
    enabled: true
    max_same_tool_calls: 3
    action: warn_and_break

  debug:
    log_all_tool_calls: true
    alert_on_duplicate: true

# 成本追踪
cost_tracking:
  enabled: true

  real_time:
    enabled: true
    show_per_request: true
    show_session_total: true

  reporting:
    daily_summary: true
    weekly_summary: false
    monthly_summary: true

  budget_alerts:
    enabled: true
    daily_limit: 10      # $10/天
    monthly_limit: 300   # $300/月
    alert_at_percentage: 80

# 智能路由（可选）
intelligent_routing:
  enabled: true

  complexity_based:
    enabled: true
    simple_tasks:
      model: gpt-3.5-turbo
      triggers:
        - short_prompt
        - simple_keywords: ["explain", "what is", "define"]
    complex_tasks:
      model: gpt-4-turbo
      triggers:
        - long_prompt
        - complex_keywords: ["refactor", "optimize", "architect"]
        - has_code_blocks: true

  cost_based:
    enabled: true
    prefer_cheaper: true

# 上下文管理
context_management:
  enabled: true
  max_context_tokens: 8000
  truncation_strategy: smart

  smart_truncation:
    priority:
      - system_message
      - recent_messages
      - code_blocks
      - tool_results
    preserve:
      min_recent_messages: 5

# 缓存（可选）
caching:
  enabled: true
  ttl: 3600
  cache_candidates:
    - documentation_queries
    - error_explanations
    - simple_code_snippets

# 日志
logging:
  level: info
  coder_logs:
    log_protocol_translation: true
    log_tool_calls: true
    log_cost_per_request: true
  file:
    enabled: true
    path: ~/.tokligence/coder.log

# 监控
monitoring:
  enabled: true
  metrics:
    - request_latency
    - tokens_per_request
    - cost_per_request
    - tool_call_count
    - duplicate_tool_calls
```

---

## 使用场景示例

### 场景1: Claude Code → OpenAI GPT-4

```bash
# 1. 安装
pip install tokligence

# 2. 初始化 coder profile
tokligence init --profile coder

# 3. 配置 API keys
export OPENAI_API_KEY=sk-...

# 4. 启动 gateway
tokligence-daemon start --background

# 5. 配置 Claude Code
# 在 Claude Code 设置中：
# Base URL: http://localhost:8081/anthropic
# API Key: (可以留空或随意填)

# 6. 在 Claude Code 中选择模型
# 选择 "gpt-4-turbo" 或 "gpt-3.5-turbo"
# Gateway 会自动翻译 Anthropic API 到 OpenAI API
```

**工作流程**:
```
Claude Code (Anthropic SDK)
    ↓
    发送 Anthropic Messages API 请求
    POST http://localhost:8081/anthropic/v1/messages
    {
      "model": "gpt-4-turbo",  # 实际是 OpenAI 模型
      "messages": [...],
      "tools": [...]
    }
    ↓
Tokligence Gateway
    ↓
    检测到 model="gpt-4-turbo" → OpenAI
    ↓
    翻译 Anthropic → OpenAI
    {
      "model": "gpt-4-turbo",
      "messages": [...],
      "functions": [...]  # tools → functions
    }
    ↓
    调用 OpenAI API
    ↓
    翻译响应 OpenAI → Anthropic
    ↓
Claude Code 收到 Anthropic 格式响应
```

### 场景2: Cursor → Anthropic Claude

```bash
# 配置 Cursor
# Settings → Models → Custom OpenAI API
# Base URL: http://localhost:8081/v1
# API Key: (随意填)

# 在 Cursor 中选择模型: claude-3-sonnet-20240229
# Gateway 自动翻译 OpenAI → Anthropic
```

### 场景3: 成本优化 - 智能路由

```python
# 配置智能路由后，Gateway 会自动选择模型

# 简单问题 → 自动用 gpt-3.5-turbo
"What is a Python decorator?"

# 复杂问题 → 自动用 gpt-4-turbo
"Refactor this 500-line class to follow SOLID principles"

# 查看成本
$ tokligence usage --today
Today's usage: $2.34
  - gpt-3.5-turbo: $0.12 (120 requests)
  - gpt-4-turbo: $2.22 (8 requests)
```

---

## CLI 命令扩展

### 专门为 Coder Profile 的命令

```bash
# 查看实时成本
tokligence coder cost --live

# 查看工具调用统计
tokligence coder tools --stats

# 检测到的重复调用
tokligence coder duplicates --last 100

# 性能统计
tokligence coder perf
# Output:
# Average latency: 1.2s
# P95 latency: 3.5s
# Cache hit rate: 45%
# Cost per request: $0.02

# 导出 coding session
tokligence coder export --session <id> --format json
```

---

## Python API 扩展

```python
from tokligence import Gateway
from tokligence.coder import CoderSession, CostTracker, ToolCallMonitor

# 初始化 Coder 优化的 Gateway
gateway = Gateway.from_profile('coder')

# 创建 coding session
session = CoderSession(gateway)

# 实时成本追踪
cost_tracker = CostTracker(session)
print(f"Current session cost: ${cost_tracker.get_current_cost()}")

# 工具调用监控
tool_monitor = ToolCallMonitor(session)
if tool_monitor.has_duplicates():
    print("Warning: Duplicate tool calls detected!")
    tool_monitor.show_duplicates()

# 智能路由配置
from tokligence.coder import IntelligentRouter

router = IntelligentRouter(gateway)
router.set_simple_model('gpt-3.5-turbo')
router.set_complex_model('gpt-4-turbo')
router.enable_cost_based_routing()
```

---

## 实现优先级

基于重要性和难度，建议实现顺序：

| 功能 | 优先级 | 难度 | 预估时间 |
|------|--------|------|---------|
| 双向协议翻译 | P0 | 高 | 2-3天 |
| 工具调用去重 | P0 | 中 | 1-2天 |
| 长超时支持 | P0 | 低 | 0.5天 |
| 成本追踪 | P1 | 中 | 1-2天 |
| 智能路由 | P1 | 中 | 2天 |
| 上下文管理 | P2 | 中 | 1-2天 |
| 缓存优化 | P2 | 低 | 1天 |
| CLI 扩展 | P2 | 低 | 1天 |

**MVP (Minimum Viable Product)**:
- Phase 1: 双向翻译 + 去重 + 长超时 (核心功能)
- Phase 2: 成本追踪 + 智能路由 (增值功能)
- Phase 3: 其他优化功能

---

## 测试计划

### 单元测试
```python
# test_protocol_translation.py
def test_openai_to_anthropic_translation():
    """测试 OpenAI → Anthropic 翻译"""
    pass

def test_anthropic_to_openai_translation():
    """测试 Anthropic → OpenAI 翻译"""
    pass

# test_tool_deduplication.py
def test_exact_match_deduplication():
    """测试精确匹配去重"""
    pass

def test_loop_detection():
    """测试无限循环检测"""
    pass

# test_cost_tracking.py
def test_cost_calculation():
    """测试成本计算"""
    pass
```

### 集成测试
```python
# test_coder_integration.py
def test_claude_code_to_openai():
    """测试 Claude Code → OpenAI 完整流程"""
    # 1. 启动 gateway
    # 2. 模拟 Claude Code 请求
    # 3. 验证翻译正确
    # 4. 验证响应格式
    pass

def test_cursor_to_anthropic():
    """测试 Cursor → Anthropic 完整流程"""
    pass

def test_tool_call_deduplication_e2e():
    """测试工具调用去重端到端"""
    # 模拟重复的 tool calls
    # 验证被正确去重
    pass
```

### 性能测试
```python
def test_translation_latency():
    """测试翻译延迟 < 10ms"""
    pass

def test_high_concurrency():
    """测试高并发场景（20 concurrent requests）"""
    pass
```

---

## 文档需求

1. **Quick Start Guide** - Coder Profile 5分钟上手
2. **Protocol Translation Guide** - 协议翻译详解
3. **Cost Optimization Guide** - 成本优化最佳实践
4. **Troubleshooting** - 常见问题（去重不工作、翻译错误等）
5. **API Reference** - Python API 文档

---

## 总结

Coder Profile 的核心价值：

1. **🔄 协议自由** - 不再被工具锁定协议，想用哪个模型用哪个
2. **🛡️ 防无限循环** - 智能去重，节省token和成本
3. **💰 成本可控** - 实时追踪，智能路由，预算告警
4. **⚡ 性能优化** - 长超时、缓存、上下文管理

下一步：
- 确认这些功能是否符合你的预期
- 决定 MVP 包含哪些功能
- 开始实现 Phase 1 核心功能
