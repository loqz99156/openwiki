<div align="center">

# OpenWiki — 开放 LLM 知识库

<p align="center"><i>支持长文档处理&nbsp; • &nbsp;基于推理的检索&nbsp; • &nbsp;原生多模态&nbsp; • &nbsp;无需向量数据库</i></p>

</div>

***

# 📑 什么是 OpenWiki

**OpenWiki（开放知识库）** 是一个面向 Obsidian 和 Claude Code 的开源知识库系统。它利用 LLM 将原始文档编译成结构化、相互关联的 Wiki 风格知识库，并由 **[PageIndex](https://github.com/VectifyAI/PageIndex)** 提供无向量长文档检索能力。

它的核心思想是：知识不应该在每次提问时重新检索、重新总结，而应该被持续编译成可阅读、可维护、可链接的 Markdown Wiki。OpenWiki 会为文档生成摘要、概念页、交叉引用和查询沉淀，让知识随着文档增加而不断积累。

OpenWiki 的默认工作目录是 `my-wiki/`，它既是 **Obsidian vault**，也是 OpenWiki 的知识库根目录。用户可以在 Obsidian 中浏览 `wiki/` 内容，并通过 Claude Code 插件使用 `/init`、`/add`、`/query`、`/chat` 等命令维护知识库。

主要能力：

* **广泛格式支持** — PDF、Word、Markdown、PowerPoint、HTML、Excel、文本等，通过 markitdown 转换。
* **长文档处理** — 通过 PageIndex 树索引处理长 PDF，实现无向量、基于推理的长文档检索。
* **Wiki 编译** — LLM 将文档编译成摘要、概念页和交叉链接。
* **查询与聊天** — 支持一次性问答和围绕知识库的多轮对话。
* **Obsidian 兼容** — 输出为普通 Markdown 文件，并使用 `[[wikilinks]]`。

# 🚀 快速开始

### 1. 获取项目并运行安装脚本

```bash
git clone https://github.com/loqz99156/openwiki.git openwiki
cd openwiki

# macOS / Linux 终端
bash install.sh

# macOS 双击运行
# 双击 install.command

# Windows PowerShell
# .\install.ps1

# Windows 双击运行
# 双击 install.bat
```

安装脚本会：

1. 执行开发安装：`python3 -m pip install -e .`
2. 创建 `my-wiki/` 目录
3. 将 Claude Code commands 安装到 `my-wiki/.claude/commands/`

### 2. 用 Obsidian 打开 my-wiki

安装完成后，用 Obsidian 打开：

```text
my-wiki/
```

它就是你的 Obsidian vault / OpenWiki 知识库根目录。

### 3. 在 Claude Code 插件中初始化知识库

在 Obsidian 的 Claude Code 插件中运行：

```text
/init
```

`/init` 会在当前 vault 中创建：

```text
my-wiki/
  .claude/              Claude Code 插件命令（隐藏）
    commands/
  .openwiki/            OpenWiki 状态（隐藏）
    config.yaml
    hashes.json
  raw/                  原始资料
  wiki/                 Obsidian 中浏览的知识库内容
    AGENTS.md
    index.md
    log.md
    sources/
    summaries/
    concepts/
```

### 4. 添加文档

把文件放进 `my-wiki/raw/` 后运行：

```text
/add
```

也可以直接添加指定文件或目录：

```text
/add paper.pdf
/add ~/Documents/research
```

### 5. 提问或聊天

一次性提问：

```text
/query 主要发现是什么？
```

进入持续对话模式：

```text
/chat
```

保存最近一次问答：

```text
/save 主要发现
```

退出 OpenWiki 对话模式：

```text
/bye
```

# 🧩 OpenWiki 工作原理

OpenWiki 将文档处理分为两个阶段：**机械转换 / 索引** 和 **LLM 知识编译**。

### 目录结构

```text
my-wiki/
  raw/                              你放入原始文档
  wiki/
    AGENTS.md                       Wiki 结构规则和 LLM 操作说明
    index.md                        知识库索引
    log.md                          操作日志
    sources/                        转换后的源内容
      images/                       提取出的图片
    summaries/                      每个文档的摘要
    concepts/                       跨文档概念页
    explorations/                   保存的查询结果
    reports/                        检查报告
  .openwiki/                        配置、哈希注册表、会话状态
  .claude/commands/                 Claude Code 插件命令
```

### 文档处理流程

```text
raw/ 原始文档
  │
  ├─ 短文档 ──→ markitdown ──→ LLM 读取全文
  │
  ├─ 长 PDF ──→ PageIndex ───→ LLM 读取文档树
  │
  ▼
LLM 编译 Wiki
  │
  ├─ summaries/   每个文档的摘要
  ├─ concepts/    跨文档主题综合
  ├─ index.md     内容索引
  └─ log.md       操作记录
```

### 短文档与长文档

| 类型 | 处理方式 | LLM 读取内容 | 输出 |
| --- | --- | --- | --- |
| 短文档 | markitdown 转 Markdown | 全文 | 摘要 + 概念页 |
| 长 PDF | PageIndex 树索引 | 文档树 / 摘要节点 | 摘要 + 概念页 |

短文档会被完整转换为 Markdown 并交给 LLM 编译。长 PDF 会先由 PageIndex 构建分层树索引，LLM 通过文档树进行检索和推理，避免长上下文直接塞入模型导致的信息退化。

### 知识如何积累

每次添加文档时，OpenWiki 会：

1. 生成文档摘要页
2. 阅读已有概念页
3. 创建或更新跨文档概念
4. 更新 `wiki/index.md`
5. 追加 `wiki/log.md`

因此，知识不是孤立地存在于每个文档中，而是逐步沉淀为可浏览、可链接、可查询的 Wiki。

# ⚙️ 使用方法

### 命令

| 命令 | 作用 |
| --- | --- |
| `/init` | 在当前 Obsidian vault 中初始化 OpenWiki 知识库 |
| `/add [路径]` | 添加指定文件/目录；不带路径时处理 `raw/` 中未索引的新文件 |
| `/query <问题>` | 对知识库进行一次性提问 |
| `/chat` | 进入基于知识库的持续对话模式 |
| `/save [名称]` | 保存最近一次问答到 `wiki/explorations/` |
| `/bye` | 退出 OpenWiki 对话模式 |

### 配置 LLM

`/init` 会提示填写模型和可选 API Key。配置文件位于当前 vault 下：

```text
my-wiki/.openwiki/config.yaml
```

示例：

```yaml
model: gpt-5.4-mini
language: en
pageindex_threshold: 20
```

模型名称使用 LiteLLM 的 `provider/model` 格式，例如：

| 提供商 | 模型示例 |
| --- | --- |
| OpenAI | `gpt-5.4-mini` |
| Anthropic | `anthropic/claude-sonnet-4-6` |
| Gemini | `gemini/gemini-3.1-pro-preview` |

API Key 可以在 `/init` 时输入，也可以手动写入：

```text
my-wiki/.env
```

```bash
LLM_API_KEY=your_llm_api_key
```

### 在 Obsidian 中使用

推荐用 Obsidian 打开整个 `my-wiki/` 目录。用户主要浏览：

```text
wiki/
  index.md
  summaries/
  concepts/
  explorations/
```

`.claude/` 和 `.openwiki/` 是隐藏目录，分别用于 Claude Code commands 和 OpenWiki 状态管理，通常不需要手动编辑。

# 📄 许可证

Apache 2.0。详见 [LICENSE](LICENSE)。
