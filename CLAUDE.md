# CLAUDE.md

本文件为 Claude Code（claude.ai/code）在此仓库中工作时提供指导。

## 开发命令

- 本地开发安装：`pip install -e .[dev]`
- 在 Claude Code 中使用 `.claude/commands/` 下的斜杠命令（如 `/init`、`/add`、`/query`、`/chat`）
- 运行全部测试：`pytest`
- 运行单个测试文件：`pytest tests/test_query.py`
- 运行单个测试用例：`pytest tests/test_query.py::TestQuery::test_build_query_agent`
- 构建分发包：`python -m build`

`pyproject.toml` 中未配置格式化、lint、类型检查或覆盖率工具；不要在没有添加工具配置的情况下自行发明一个。

## 项目概述

OpenWiki 是一个由 Claude Code commands 驱动的知识库项目，将原始文档编译为持久化的 Markdown wiki 知识库。用户入口是 `.claude/commands/` 下的 `/init`、`/add`、`/query`、`/chat` 等斜杠命令。

### 目录结构

```
openwiki/
  cli.py           Click 命令组（init, use, add, query, chat, watch, lint, list, status）
  config.py        默认配置 + KB 本地 / 全局 YAML 配置管理
  converter.py     文件哈希校验、复制到 raw/、PDF 检测、MarkItDown/PyMuPDF 转换、图片提取
  indexer.py       PageIndex 长文档索引（页数 >= pageindex_threshold）
  schema.py        默认 wiki/AGENTS.md 内容
  state.py         .openwiki/hashes.json 哈希注册表（编译成功后才注册）
  images.py        图片提取与 base64 相对路径处理
  log.py           wiki/log.md 追加式操作日志
  watcher.py       watchdog 封装，用于监听 raw/ 目录变更的防抖处理器
  lint.py          结构 lint（断链、孤立页面、缺失条目、索引同步）
  tree_renderer.py
  agent/
    compiler.py    LLM 编译管线（摘要 → 概念页规划 → 并发创建/更新 → 反向链接 → 索引更新）
    query.py       OpenAI Agents SDK 查询智能体（LiteLLM 模型）
    chat.py        prompt_toolkit 交互式 REPL（斜杠命令、流式输出）
    chat_session.py 会话持久化到 .openwiki/chats（恢复/列表/删除）
    tools.py       纯函数工具（wiki 文件读取、PageIndex 页面范围、图片读取）
    linter.py      LLM 语义/知识 lint
    _markdown.py   Rich markdown 渲染
```

### 知识库目录结构

一个 KB 目录的内容：

```
<kb-root>/
  .openwiki/              状态目录
    config.yaml          KB 本地配置
    hashes.json          文档哈希注册表
    chats/               对话会话
  raw/                   原始文档（add 时复制到这里）
  wiki/
    AGENTS.md            wiki schema（运行时动态读取）
    index.md             内容目录索引
    log.md               操作日志
    sources/             转换后的文档内容（.md 或 PageIndex .json）+ images/
    summaries/           每个源文档的摘要
    concepts/            跨文档主题合成
    explorations/        保存的查询结果
    reports/             lint 报告
```

## 关键模式

### CLI 与 KB 解析

- `_find_kb_dir()` 按优先级解析当前 KB：`--kb-dir` → `OPENWIKI_DIR` → 向上查找 `.openwiki/` → `~/.config/openwiki/global.yaml` 中的 `default_kb`
- LLM 凭证由 `_setup_llm_key()` 加载：环境变量 → KB 本地 `.env` → `~/.config/openwiki/.env`；自动传播到 `OPENAI_API_KEY`、`ANTHROPIC_API_KEY`、`GEMINI_API_KEY`
- 模型格式为 LiteLLM 格式：`provider/model`（如 `anthropic/claude-sonnet-4-6`）

### 文档摄入管线（`add` 命令）

1. `converter.py`：哈希去重 → 复制到 `raw/` → 检测短/长文档（PDF >= 20 页为长文档）→ MarkItDown/PyMuPDF 转换
2. 长文档 → `indexer.py`：PageIndex 写入 `wiki/sources/<doc>.json` + 摘要
3. 短文档 → Markdown 写入 `wiki/sources/<doc>.md`
4. `agent/compiler.py`：读取 `wiki/AGENTS.md` → 生成摘要 → 规划概念页变更 → 并发创建/更新概念页 → 反向链接 → 更新 `wiki/index.md`
5. 编译成功后才在 `hashes.json` 中注册哈希

### 查询与对话

- `agent/query.py`：OpenAI Agents SDK + LiteLLM，工具限定在 wiki 根目录内
- `agent/chat.py`：prompt_toolkit REPL，支持 `/save`、`/clear`、`/lint`、`/list`、`/status` 等斜杠命令
- `agent/chat_session.py`：会话持久化，支持恢复/列表/删除
- `agent/tools.py`：路径处理必须将读写限制在 wiki 根目录内

### Lint

- `lint.py`：结构 lint（纯 Python）
- `agent/linter.py`：语义/知识 lint（通过 LLM agent）

### 配置

- `DEFAULT_CONFIG`：`model="gpt-5.4-mini"`, `language="en"`, `pageindex_threshold=20`
- `openwiki/config.py` 提供 `load_config`、`save_config`、`load_global_config`、`save_global_config`、`register_kb`

## 测试

- 使用 pytest + pytest-asyncio
- LLM/PageIndex/CLI 路径通过 `unittest.mock.patch`、`AsyncMock` 和 Click `CliRunner` mock 测试
- `tests/conftest.py` 提供最小化的 `kb_dir` fixture（`.openwiki/`、`raw/`、`wiki/`）
- 测试文件与源文件对应：CLI 行为 → `test_*command.py`/`test_cli.py`，智能体行为 → `test_query.py`/`test_chat_*.py`，纯工具函数 → 对应测试文件
