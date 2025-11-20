# TGW Chat Feature Implementation Plan

## 已完成的工作

### 1. 基础架构 ✅
- ✅ 添加 `tgw` 命令别名到 `pyproject.toml`
- ✅ 修改 CLI 以识别 `tgw` 调用
- ✅ 添加 `chat` 命令到 CLI
- ✅ 创建文档同步脚本 `scripts/sync_docs.py`
- ✅ 同步主项目文档到 `tokligence/knowledge/` 目录

### 2. 文档同步 ✅
已同步的文档文件：
- `README.md` - 项目概述
- `QUICK_START.md` - 快速开始指南
- `USER_GUIDE.md` - 用户指南
- `configuration_guide.md` - 配置指南

元数据文件 `_meta.json` 包含：
- 版本信息 (v0.3.4)
- Git commit hash
- 文件哈希值
- 同步时间戳
- 相关链接

## 需要实现的功能

### 3. Chat 模块核心功能 🚧

#### 3.1 知识库加载器 (`tokligence/chat/knowledge.py`)
```python
class KnowledgeBase:
    """加载和管理文档知识库"""

    def load_knowledge() -> dict:
        """加载所有 .md 文档和元数据"""
        pass

    def search_docs(query: str) -> list:
        """搜索文档内容"""
        pass

    def get_doc(name: str) -> str:
        """获取特定文档内容"""
        pass

    def build_system_prompt(knowledge: dict) -> str:
        """构建系统提示词"""
        pass
```

#### 3.2 LLM 检测器 (`tokligence/chat/detector.py`)
```python
class LLMDetector:
    """检测可用的 LLM 端点"""

    async def detect_all(self):
        """检测所有可用端点（OpenAI, Anthropic, Gemini, Ollama等）"""
        pass

    def select_endpoint(self, preference: str = None):
        """选择最佳端点"""
        pass
```

支持的端点：
- OpenAI API (通过 TOKLIGENCE_OPENAI_API_KEY)
- Anthropic API (通过 TOKLIGENCE_ANTHROPIC_API_KEY)
- Google Gemini API (通过 TOKLIGENCE_GOOGLE_API_KEY)
- 本地 Ollama (http://localhost:11434)
- 本地 vLLM (http://localhost:8000)
- 本地 LM Studio (http://localhost:1234)

#### 3.3 LLM 客户端 (`tokligence/chat/client.py`)
```python
def create_client(endpoint: dict):
    """根据端点类型创建合适的客户端"""
    pass

async def create_streaming_chat(client, endpoint, model, messages, options):
    """创建流式聊天会话"""
    pass
```

支持的客户端：
- OpenAI SDK
- Anthropic SDK
- Google Generative AI SDK
- 通用 HTTP 客户端（for Ollama等）

#### 3.4 工具调用系统 (`tokligence/chat/tools.py`)
```python
# 工具定义
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "set_config",
            "description": "更新网关配置",
            "parameters": {...}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_config",
            "description": "获取当前配置",
            "parameters": {...}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_status",
            "description": "检查网关状态",
            "parameters": {...}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "start_gateway",
            "description": "启动网关守护进程",
            "parameters": {...}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "stop_gateway",
            "description": "停止网关守护进程",
            "parameters": {...}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "搜索文档",
            "parameters": {...}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_doc",
            "description": "获取完整文档",
            "parameters": {...}
        }
    }
]

async def execute_tool(tool_name: str, args: dict):
    """执行工具调用"""
    pass

def mask_sensitive_value(value: str) -> str:
    """遮蔽敏感信息（API keys等）"""
    pass
```

#### 3.5 聊天会话 (`tokligence/chat/session.py`)
```python
class ChatSession:
    """交互式聊天会话"""

    def __init__(self, endpoint, client, model, knowledge):
        self.endpoint = endpoint
        self.client = client
        self.model = model
        self.knowledge = knowledge
        self.messages = []

    async def start(self):
        """启动聊天循环"""
        # 1. 显示欢迎信息和 Logo
        # 2. 显示隐私提示
        # 3. 进入交互循环
        pass

    async def get_response(self):
        """获取 AI 响应（支持流式输出和工具调用）"""
        pass

async def start_chat(model: str = None):
    """Chat 入口函数"""
    # 1. 检测 LLM 端点
    # 2. 加载知识库
    # 3. 创建并启动聊天会话
    pass
```

### 4. 依赖管理

需要在 `pyproject.toml` 中添加可选依赖：

```toml
[project.optional-dependencies]
chat = [
    "openai>=1.0.0",
    "anthropic>=0.18.0",
    "google-generativeai>=0.4.0",
    "httpx>=0.24.0",
    "prompt-toolkit>=3.0.0"  # 用于更好的输入体验
]
```

### 5. 测试

创建测试用例 `tests/test_chat.py`：
- 知识库加载测试
- LLM 检测测试
- 工具调用测试
- 敏感信息遮蔽测试

## 使用方式

安装聊天功能：
```bash
pip install tokligence[chat]
# 或
pip install "tokligence[chat]"
```

使用聊天助手：
```bash
# 使用默认模型
tgw chat

# 指定模型
tgw chat --model gpt-4
tgw chat --model claude-sonnet-4.5
tgw chat --model gemini-2.0-flash-exp
```

环境变量配置：
```bash
# OpenAI
export TOKLIGENCE_OPENAI_API_KEY=sk-...

# Anthropic
export TOKLIGENCE_ANTHROPIC_API_KEY=sk-ant-...

# Google Gemini
export TOKLIGENCE_GOOGLE_API_KEY=...

# 或使用本地模型（无需 API key）
# Ollama: http://localhost:11434
# vLLM: http://localhost:8000
# LM Studio: http://localhost:1234
```

## 特性亮点

1. **多端点支持** - 自动检测并使用可用的 LLM 端点
2. **文档集成** - 内置官方文档，提供准确的配置帮助
3. **工具调用** - 可以直接执行配置命令
4. **隐私保护** - 自动遮蔽敏感信息（API keys, secrets等）
5. **流式输出** - 实时显示 AI 响应
6. **跨平台** - 支持 Windows, macOS, Linux

## 参考实现

完整的 Node.js 实现位于：
- `/home/alejandroseaah/tokligence/tokligence-gateway-npm/lib/chat/`
  - `index.js` - 主聊天循环
  - `knowledge.js` - 知识库加载
  - `detector.js` - LLM 检测
  - `client.js` - 客户端创建
  - `agent.js` - 工具调用

可以参考这些文件的逻辑来实现 Python 版本。

## 下一步

1. 实现 `knowledge.py` - 知识库加载和搜索
2. 实现 `detector.py` - LLM 端点检测
3. 实现 `client.py` - 多协议客户端
4. 实现 `tools.py` - 工具定义和执行
5. 实现 `session.py` - 主聊天会话
6. 添加单元测试
7. 更新文档和示例

## 简化版实现

如果需要快速原型，可以先实现一个简化版本：
- 只支持 OpenAI API
- 不支持工具调用，仅作为问答助手
- 使用简单的 input/print 而非高级终端 UI

后续再逐步添加完整功能。
