<div align="center">

# OpenWiki — 开放 LLM 知识库

<p align="center"><i>支持长文档处理&nbsp; • &nbsp;基于推理的检索&nbsp; • &nbsp;原生多模态&nbsp; • &nbsp;无需向量数据库</i></p>

</div>

***

# 📑 什么是 OpenWiki

**OpenWiki（开放知识库）** 是一个开源系统（命令行工具），它利用 LLM 将原始文档编译成结构化的、相互关联的 Wiki 风格知识库，由 **[PageIndex](https://github.com/VectifyAI/PageIndex)** 提供无向量长文档检索能力。

这个想法源于 Andrej Karpathy 提出的一个[概念](https://x.com/karpathy/status/2039805659525644595)：LLM 自动生成摘要、概念页面和交叉引用。知识会随时间不断累积，而不是每次查询时重新推导。

### 为什么不是传统的 RAG？

传统的 RAG 每次查询都从头开始重新发现知识，没有任何积累。OpenWiki 将知识一次性编译为持久的 Wiki，然后保持其更新。交叉引用已经存在，矛盾之处会被标记，综合结果反映所有已消费的内容。

### 功能特性

* **广泛的格式支持** — PDF、Word、Markdown、PowerPoint、HTML、Excel、文本等，通过 markitdown 实现

* **支持长文档** — 通过 [PageIndex](https://github.com/VectifyAI/PageIndex) 树索引处理长而复杂的文档，实现准确的无向量长上下文检索

* **原生多模态** — 检索和理解图表、表格和图像，而不仅仅是文本

* **编译 Wiki** — LLM 管理并将你的文档编译成摘要、概念页面和交叉链接，所有内容保持同步

* **查询** — 对你的 Wiki 提出一次性问题。LLM 导航你编译的知识来进行回答

* **交互式聊天** — 多轮对话，支持持久化会话，可在不同运行间恢复

* **检查** — 健康检查发现矛盾、缺口、孤立内容和过时内容

* **监听模式** — 将文件放入 `raw/`，Wiki 自动更新

* **兼容 Obsidian** — Wiki 是纯 `.md` 文件，使用 `[[wikilinks]]`。在 Obsidian 中打开可查看图谱视图和浏览

# 🚀 快速开始

### 使用方式

将本仓库放在本地后，先运行安装脚本。安装脚本会创建 `my-wiki/`，它就是你的 **Obsidian vault / OpenWiki 知识库根目录**。随后在 Obsidian 中打开 `my-wiki/`，并通过 Claude Code 插件使用 `.claude/commands/` 提供的斜杠命令。

<details>
<summary><i>从源码准备项目</i></summary>

```bash
git clone <repository-url>
cd OpenWiki

# macOS / Linux 终端
bash install.sh

# macOS 双击运行
# 双击 install.command

# Windows PowerShell
# .\install.ps1

# Windows 双击运行
# 双击 install.bat
```

安装脚本会执行开发安装，并创建独立知识库目录 `my-wiki/`。`my-wiki/` 用作 Obsidian vault；脚本会在其中放入隐藏的 `.claude/commands/`，供 Obsidian 里的 Claude Code 插件加载 `/init`、`/add`、`/query` 等命令。

</details>

### 快速上手

安装后会得到独立的 `my-wiki/` 目录。把 `my-wiki/` 作为 Obsidian vault 打开，然后在 Obsidian 的 Claude Code 插件中运行 `/init` 初始化知识库：

```text
# 1. 用 Obsidian 打开 my-wiki/ 作为 vault

# 2. 在 Obsidian 的 Claude Code 插件中初始化当前 vault
/init

# 3. 把文档放进 raw/，然后处理所有未索引的新文件
/add

# 4. 也可以直接添加指定文件或目录
/add paper.pdf
/add ~/papers/

# 5. 向知识库提问
/query 主要发现是什么？

# 6. 进入持续对话模式
/chat

# 7. 保存最近一次问答
/save 主要发现

# 8. 退出知识库对话模式
/bye
```

初始化后的 vault 结构：

```text
my-wiki/
  .claude/              Claude Code 插件命令（隐藏）
    commands/
  .openwiki/            OpenWiki 状态（隐藏）
  raw/                  原始资料
  wiki/                 Obsidian 中浏览的知识库内容
```

### 配置你的 LLM

OpenWiki 通过 [LiteLLM](https://github.com/BerriAI/litellm)（固定到[安全版本](https://docs.litellm.ai/blog/security-update-march-2026)）支持[多种 LLM](https://docs.litellm.ai/docs/providers)（例如 OpenAI、Claude、Gemini）。

`/init` 会提示你填写模型，使用 `provider/model` 的 LiteLLM 格式（如 `anthropic/claude-sonnet-4-6`）。OpenAI 模型可以省略前缀（如 `gpt-5.4-mini`）。

初始化时也可以输入 LLM API Key，OpenWiki 会将它保存到知识库本地 `.env`：

```bash
LLM_API_KEY=your_llm_api_key
```

如果初始化时跳过了 API Key，之后可以手动把上面的内容写入知识库目录下的 `.env`，也可以写入全局配置文件 `~/.config/openwiki/.env`，或在 shell 中导出 `LLM_API_KEY`。

# 🧩 OpenWiki 工作原理

### 架构

```
raw/                              你在此处放入文件
 │
 ├─ 短文档 ──→ markitdown ──→ LLM 读取全文
 │                                     │
 ├─ 长 PDF ──→ PageIndex ────→ LLM 读取文档树
 │                                     │
 │                                     ▼
 │                          Wiki 编译（使用 LLM）
 │                                     │
 ▼                                     ▼
wiki/
 ├── index.md            知识库概览
 ├── log.md              操作时间线
 ├── AGENTS.md           Wiki 模式（LLM 指令）
 ├── sources/            全文转换
 ├── summaries/          每个文档的摘要
 ├── concepts/           跨文档综合 ← 核心内容
 ├── explorations/       保存的查询结果
 └── reports/            检查报告
```

### 短文档 vs 长文档处理

| <br />     | 短文档                   | 长文档（PDF ≥ 20 页）      |
| ---------- | --------------------- | -------------------- |
| **转换**     | markitdown → Markdown | PageIndex → 树索引 + 摘要 |
| **图像**     | 内联提取（pymupdf）         | 由 PageIndex 提取       |
| **LLM 读取** | 全文                    | 文档树                  |
| **结果**     | 摘要 + 概念               | 摘要 + 概念              |

短文档由 LLM 完整读取。长 PDF 由 PageIndex 索引为包含摘要的分层树。LLM 读取树而非全文，从而实现对长文档更好的检索。

### 知识编译

当你添加文档时，LLM 会：

1. 生成一个**摘要**页面
2. 读取现有的**概念**页面
3. 创建或更新概念，进行跨文档综合
4. 更新**索引**和**日志**

单个源文档可能涉及 10-15 个 Wiki 页面。知识不断积累：每个文档都丰富现有的 Wiki，而不是孤立存在。

# ⚙️ 使用方法

### 命令

| 命令                | 描述                                      |
| ----------------- | --------------------------------------- |
| `/init`           | 在独立目录中初始化一个新的知识库（交互式）                |
| `/add [路径]`      | 添加指定文件/目录；不带路径时处理 `raw/` 中未索引的新文件    |
| `/query <问题>`    | 对知识库提问；回答后可用 `/save` 保存到 `wiki/explorations/` |
| `/chat`           | 进入由 Claude 直接管理的多轮知识库对话模式              |
| `/save [名称]`     | 保存最近一次问答到 `wiki/explorations/`            |
| `/bye`            | 退出知识库对话模式，回到普通 Claude Code 交互          |

### 常见工作流

#### 创建并使用一个知识库

安装后用 Obsidian 打开 `my-wiki/` 作为 vault，再在 Claude Code 插件中运行 `/init` 初始化当前 vault：

```text
/init
```

安装脚本会先准备：

```text
.claude/              Claude Code 插件命令（隐藏）
  commands/
```

`/init` 会继续创建：

```text
.openwiki/           本地配置、哈希注册表、会话状态（隐藏）
raw/                 原始文档
wiki/                可阅读、可编辑的 Markdown Wiki
```

#### 添加单个文件、整个目录，或处理 raw/ 中的新文件

```text
/add paper.pdf
/add notes.md
/add ~/Documents/research
```

也可以先把文件放进 `raw/`，再运行：

```text
/add
```

添加文档时，OpenWiki 会把原始文件保存在 `raw/`，转换或索引内容，然后更新 `wiki/summaries/`、`wiki/concepts/` 和 `wiki/index.md`。

#### 提问并保存结果

```text
/query 这批论文的共同结论是什么？
/save common-findings
```

`/query` 会直接检索 `wiki/index.md`、摘要页、概念页和必要的源文件来回答。`/save` 会把最近一次问答保存到 `wiki/explorations/`，适合沉淀一次探索结果。

#### 进入持续对话模式

```text
/chat
```

在对话模式中可以连续追问，也可以使用：

```text
/add <路径>
/save <名称>
/bye
```

`/bye` 只退出 OpenWiki 对话模式，不会清空 Claude Code 的全局上下文。

### 交互式聊天

`/chat` 会进入基于当前 Wiki 知识库的对话模式。与一次性 `/query` 不同，对话模式会在当前 Claude Code 会话中保留临时问答上下文，适合围绕同一主题连续追问。

```text
/chat          # 进入知识库对话模式
/save 名称     # 保存最近一次问答
/bye           # 退出知识库对话模式
```

对话模式中可用的 OpenWiki 命令：

* `/add <路径>` — 在不离开对话的情况下添加文档或目录

* `/save [名称]` — 将最近问答保存到 `wiki/explorations/`

* `/bye` — 退出 OpenWiki 对话模式

如果要做一次性提问，也可以退出对话模式后使用 `/query <问题>`。

### 配置

设置由 `/init` 初始化，存储在当前 Obsidian vault 的 `.openwiki/config.yaml` 中；按默认流程也就是 `my-wiki/.openwiki/config.yaml`：

```yaml
model: gpt-5.4                   # LLM 模型（任何 LiteLLM 支持的提供商）
language: zh                     # Wiki 输出语言
pageindex_threshold: 20          # PageIndex 的 PDF 页数阈值
```

模型名称使用 `provider/model` 的 LiteLLM [格式](https://docs.litellm.ai/docs/providers)（OpenAI 模型可以省略前缀）：

| 提供商       | 模型示例                            |
| --------- | ------------------------------- |
| OpenAI    | `gpt-5.4`                       |
| Anthropic | `anthropic/claude-sonnet-4-6`   |
| Gemini    | `gemini/gemini-3.1-pro-preview` |

### PageIndex 集成

长文档对 LLM 来说具有挑战性，原因在于上下文限制、上下文退化以及摘要丢失。
[PageIndex](https://github.com/VectifyAI/PageIndex) 通过无向量的、基于推理的检索解决了这个问题——构建一个分层树索引，让 LLM 能够基于索引进行推理，实现上下文感知的检索。

PageIndex 默认使用[开源版本](https://github.com/VectifyAI/PageIndex)在本地运行，无需外部依赖。

#### 可选：云端支持

对于大型或复杂 PDF，可以使用 [PageIndex Cloud](https://docs.pageindex.ai/) 获取额外功能，包括：

* 支持扫描 PDF 的 OCR（通过托管的 VLM 模型）

* 更快的结构生成

* 面向大型文档的可扩展索引

在你的 `.env` 中设置 `PAGEINDEX_API_KEY` 以启用云功能：

```
PAGEINDEX_API_KEY=your_pageindex_api_key
```

### AGENTS.md

`wiki/AGENTS.md` 文件定义了 Wiki 的结构和约定。它是 LLM 维护 Wiki 的操作手册。自定义它来改变你 Wiki 的组织方式。

运行时，LLM 从磁盘读取 `AGENTS.md`，因此你的编辑会立即生效。

### 与 Obsidian 配合使用

OpenWiki 的 Wiki 是一个包含 `[[wikilinks]]` 的 Markdown 文件目录。Obsidian 原生支持渲染。

1. 将 `wiki/` 作为 Obsidian 库打开
2. 浏览摘要、概念和探索记录
3. 使用图谱视图查看知识关联
4. 使用 Obsidian Web Clipper 将网页文章添加到 `raw/`

# 🧭 了解更多

### 与 Karpathy 方法的对比

| <br />  | Karpathy 的工作流     | OpenWiki                             |
| ------- | ----------------- | ---------------------------------- |
| 短文档     | LLM 直接读取          | markitdown → LLM 读取                |
| 长文档     | 上下文限制、上下文退化       | PageIndex 树索引                      |
| 支持的格式   | Web clipper → .md | PDF、Word、PPT、Excel、HTML、文本、CSV、.md |
| Wiki 编译 | LLM 代理            | LLM 代理（相同）                         |
| 问答      | 基于 Wiki 查询        | Wiki + PageIndex 检索                |

### 技术栈

* [PageIndex](https://github.com/VectifyAI/PageIndex) — 无向量、基于推理的文档索引和检索

* [markitdown](https://github.com/microsoft/markitdown) — 通用文件到 Markdown 转换

* [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) — 代理框架（通过 LiteLLM 支持非 OpenAI 模型）

* [LiteLLM](https://github.com/BerriAI/litellm) — 多提供商 LLM 网关

* [Click](https://click.palletsprojects.com/) — CLI 框架

* [watchdog](https://github.com/gorakhargosh/watchdog) — 文件系统监控

### 路线图

* [ ] 将长文档处理扩展到非 PDF 格式

* [ ] 支持嵌套文件夹，扩展到大型文档集合

* [ ] 面向海量知识库的分层概念（主题）索引

* [ ] 基于数据库的存储引擎

* [ ] 用于浏览和管理 Wiki 的 Web 界面

### 发布流程

发布前先确认工作区干净，并运行测试：

```bash
git status
python3 -m pytest tests
```

如果本机没有打包工具，先安装：

```bash
python3 -m pip install build twine
```

构建发布产物：

```bash
rm -rf dist/
python3 -m build
```

构建完成后，`dist/` 中应该出现类似文件：

```text
dist/openwiki-0.1.3.tar.gz
dist/openwiki-0.1.3-py3-none-any.whl
```

不要发布 `openkb-*` 产物。如果文件名仍是 `openkb-*`，说明 `pyproject.toml` 或包目录改名不完整。

发布到 TestPyPI 做预演：

```bash
python3 -m twine upload --repository testpypi dist/*
```

正式发布到 PyPI：

```bash
python3 -m twine upload dist/*
```

发布后打 tag 并推送：

```bash
git tag v0.1.3
git push origin v0.1.3
```

如果同时维护 GitHub Release，用同一个 tag 创建 release，并在说明中列出：

* 包名已改为 `openwiki`
* 状态目录已改为 `.openwiki/`

### 贡献

欢迎贡献！请提交 Pull Request，或为 Bug 和功能请求提交 Issue。对于较大的变更，建议先提交 Issue 讨论方案。

### 许可证

Apache 2.0。详见 [LICENSE](LICENSE)。

### 支持我们

如果你觉得 OpenWiki 有用，请给我们一个 Star 🌟——也欢迎查看 [PageIndex](https://github.com/VectifyAI/PageIndex)！

<div>

[![Twitter](https://img.shields.io/badge/Twitter-000000?style=for-the-badge\&logo=x\&logoColor=white)](https://x.com/PageIndexAI) 
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge\&logo=linkedin\&logoColor=white)](https://www.linkedin.com/company/vectify-ai/) 
[![Contact Us](https://img.shields.io/badge/Contact_Us-3B82F6?style=for-the-badge\&logo=envelope\&logoColor=white)](https://ii2abc2jejf.typeform.com/to/tK3AXl8T)

</div>
