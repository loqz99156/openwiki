<div align="center">

# OpenWiki — 开放 LLM 知识库

<p align="center"><i>把原始资料持续编译成可读、可链接、可检索的 Markdown Wiki。</i></p>

</div>

---

## 简介

OpenWiki 是一个面向 Obsidian、Claudian、Claude Code、Codex 和 OpenClaw 的本地知识库系统。

它不是把文档简单塞进向量库后等待问答，而是把 PDF、Markdown、Word、PPT、HTML、Excel、文本等资料转换、分类、编译成普通 Markdown Wiki。你可以在 Obsidian 里阅读它，也可以在 Claudian、Claude Code、Codex 或 OpenClaw 中用 OpenWiki skills 添加资料、追问、保存分析和整理分类。

核心能力：

- 生成一个可直接作为 Obsidian vault 打开的知识库目录。
- 用分类、文档页、概念页和探索记录组织知识。
- 用 qmd 从用户可见的 Markdown Wiki 中做本地召回。
- 用 PageIndex 处理 30 页及以上的长 PDF，并保留分页全文追溯能力。
- 把有价值的问答保存到 `wiki/explorations/`，之后还能重新分类。

## qmd 和 PageIndex

OpenWiki 不是只依赖一种检索方式。它把普通 wiki 页面召回和长文档追溯分开处理：qmd 负责快速找到相关 Markdown 页面，PageIndex 负责处理长 PDF。

### qmd：面向 Wiki 的本地召回

qmd 是 OpenWiki 的本地检索层。它搜索的是用户可见、可阅读的 Markdown wiki，而不是隐藏状态目录或原始文件。

qmd 在 OpenWiki 里主要负责：

- 从 `wiki/index.md`、`wiki/categories/`、`wiki/concepts/` 和 `wiki/explorations/` 中召回相关页面。
- 帮助 `/openwiki-chat` 在回答前找到可能相关的文档页、概念页和保存过的探索记录。
- 作为轻量本地搜索层，与 wiki 的分类结构互相补充。

qmd 不会默认搜索 `raw/`、`.openwiki/`、`.codex/`、`.claude/` 或 `wiki/sources/`。这样可以让问答优先基于整理过、用户可读的知识库内容。

### PageIndex：面向长 PDF 的结构化追溯

PageIndex 用来处理 30 页及以上的 PDF。长 PDF 不适合直接把全文一次性塞给模型，所以 OpenWiki 会先用 PageIndex 建立章节结构和分页内容。

PageIndex 在 OpenWiki 里主要负责：

- 为长 PDF 生成结构化目录、章节层级和页码范围。
- 把完整分页正文保存到 `wiki/sources/<文档>.json`。
- 在分类文档页中保留结构页和 `full_text` 指针，方便后续按页追溯原文。
- 让 `/openwiki-chat` 需要细节时能回到具体页码，而不是只依赖摘要。

简单说：qmd 负责“在整理好的 wiki 里找相关页面”，PageIndex 负责“把很长的 PDF 拆成可追溯的结构和分页正文”。

## 快速开始

共同环境要求：

- Python 3.10 或以上版本
- pip
- Git
- Node.js / npm（用于安装必需的 qmd）

### 方式一：Obsidian + Claudian

需要先安装 Obsidian，并在 Obsidian 里安装 Claudian 插件。

#### 安装

```bash
git clone https://github.com/loqz99156/openwiki.git openwiki
cd openwiki
bash install.sh
```

macOS 也可以双击 `install.command`，Windows 可以使用 `install.bat` 或 `install.ps1`。

安装脚本会把 PageIndex 和 qmd 一起准备好：

- 安装 `openwiki` Python 包和 Python 依赖，其中包括 PageIndex、MarkItDown 和 PyMuPDF。
- 通过 npm 安装 qmd。
- 校验 PageIndex、qmd、PyMuPDF 等关键依赖是否可用。
- 创建默认知识库目录 `my-wiki/`。
- 把四个 OpenWiki skills 安装到 `my-wiki/.codex/skills/` 和 `my-wiki/.claude/skills/`。

安装完成后，在 Obsidian 中完成插件准备：

1. 打开 Obsidian。
2. 点击左下角 `Obsidian vault`，选择“管理仓库”。
3. 选择“打开本地仓库”。
4. 选择安装脚本创建的 `my-wiki/` 作为仓库文件夹。
5. 进入 Obsidian 设置，打开第三方插件。
6. 浏览社区插件市场，搜索并安装 Claudian。
7. 启用 Claudian 插件。
8. 在 Claudian 插件的 Claude 标签栏中找到 `Commands and Skills`，确认已经加载 `openwiki-init`、`openwiki-add`、`openwiki-chat`、`openwiki-category` 四个 skills。

#### 使用

用 Obsidian 打开整个知识库目录：

```text
my-wiki/
```

它既是 Obsidian vault，也是 OpenWiki 知识库根目录。初始化后，主要阅读 `wiki/index.md`、`wiki/categories/`、`wiki/concepts/` 和 `wiki/explorations/`。

不要在 OpenWiki 源码仓库根目录里初始化知识库。

初始化知识库：

在 Obsidian 的 Claudian 对话框中输入：

```text
/openwiki-init
```

然后根据提示填写知识库用途和分类。也可以一次性写完整：

```text
/openwiki-init 初始化这个知识库，用途是个人知识库，分类包括 AI、历史、投资
```

`openwiki-init` 会创建 `.openwiki/`、`raw/`、`wiki/`，写入分类体系，并保留一个默认的 `未分类` 分类。

添加资料：

把原始文件放进：

```text
my-wiki/raw/
```

然后输入：

```text
/openwiki-add
```

`/openwiki-add` 会自动处理 `raw/` 里还没有添加过的新文档。也可以指定文件或目录：

```text
/openwiki-add 添加 paper.pdf
/openwiki-add 添加 ~/Documents/research 目录里的文档
```

提问和保存：

```text
/openwiki-chat
```

`/openwiki-chat` 会进入知识库问答流程，然后根据你的问题连续追问。也可以一次性带上问题：

```text
/openwiki-chat 根据这个知识库回答：这些资料的主要发现是什么？
```

`/openwiki-chat` 会先看知识库结构，再用 qmd 召回相关 Markdown 页面。它不会在聊天时重新运行 PageIndex；只有当命中的长 PDF 文档页带有 `full_text` 指针、且回答需要更多细节时，才会读取 PageIndex 已经生成的分页全文。答案应该来自本地 wiki；如果证据不足，它应该直接说明。

如果某次回答值得留下，用户只需要回复“保存”。系统会继续提示要保存到哪个分类目录下，然后把这次问答写成一篇 wiki 笔记，保存到 `wiki/explorations/<分类>/`，并更新探索记录和对应分类页。保存完成后仍然停留在这次 `/openwiki-chat` 对话中，可以继续追问；不需要重新输入 `/openwiki-chat`。

整理分类：

```text
/openwiki-category
/openwiki-category 查看有哪些分类
/openwiki-category 把 paper 移到 AI
/openwiki-category 新增一个分类叫 产品
```

如果只输入 `/openwiki-category`，系统会先列出可以做的分类操作，再让你选择下一步。

分类调整只移动用户可见的文档页或探索记录，不会移动 `wiki/sources/` 里的稳定源内容。

### 方式二：OpenClaw

OpenClaw 不需要进入 Obsidian，也不需要安装 Claudian。它的角色是在自己的交互窗口里替你调用同一套 OpenWiki skills。

OpenClaw 可以使用 4 个 OpenWiki skills：

- `/openwiki-init` 初始化指定知识库目录，创建 `.openwiki/`、`raw/`、`wiki/`、分类体系和 OpenWiki skills。
- `/openwiki-add` 添加资料，把用户上传或指定的文件放入当前知识库的 `raw/`，再转换、分类并写入 `wiki/categories/<分类>/`、`wiki/sources/`、`wiki/concepts/` 和索引页。
- `/openwiki-chat` 基于当前知识库的 `wiki/` 内容提问、追问和比较；回答来自本地 wiki，值得保留时保存到 `wiki/explorations/<分类>/`。
- `/openwiki-category` 整理当前知识库的分类，移动的是用户可见的文档页或探索记录，不移动 `wiki/sources/` 里的稳定源内容。

#### 安装

把下面这段话直接发给 OpenClaw：

```text
请帮我安装 OpenWiki：克隆 https://github.com/loqz99156/openwiki.git 到本地 openwiki 文件夹，进入这个文件夹，按当前系统运行一键安装脚本。安装完成后确认 my-wiki/ 已创建，并把 my-wiki/ 作为我要操作的知识库。后续请通过 OpenWiki skills 初始化和使用这个知识库。
```

#### 使用

OpenClaw 使用 OpenWiki 时，要先确定当前知识库。用户明确说了知识库目录时，就操作那个目录；没有特别说明时，就使用默认知识库。

OpenClaw 收到自然语言需求后，应把需求路由到对应 skill：

- 添加文件、保存上传文件、导入资料：调用 `/openwiki-add`。
- 基于知识库提问、追问、总结、比较：调用 `/openwiki-chat`。
- 保存当前问答：继续留在当前 `/openwiki-chat`，询问分类后写入探索记录。
- 查看、移动、新增、重命名、删除分类：调用 `/openwiki-category`。

常见用法：

初始化：

```text
使用 my-wiki/ 作为当前知识库，调用 /openwiki-init 初始化这个知识库，并在初始化过程中询问我知识库用途和分类。
```

OpenClaw 应调用 `/openwiki-init`，并让用户填写知识库用途和分类。

添加上传文件：

```text
把我刚上传的这个文件存到 my-wiki/ 知识库。
```

OpenClaw 应把上传文件放入 `my-wiki/raw/`，然后调用 `/openwiki-add` 处理新文档。处理完成后告诉用户生成了哪个分类文档页。

添加指定路径的文件或目录：

```text
把 ~/Downloads/paper.pdf 添加到 my-wiki/ 知识库。
```

OpenClaw 应调用 `/openwiki-add`，把文件复制到 `my-wiki/raw/` 后再添加。

基于知识库提问：

```text
在 my-wiki/ 知识库里回答：中国历代皇帝在位多少年？
```

OpenClaw 应调用 `/openwiki-chat`，基于 `my-wiki/wiki/` 的本地内容回答。进入 `/openwiki-chat` 后，如果没有切换到其他 skill，就继续保持同一次知识库问答状态。

保存回答：

```text
保存
```

OpenClaw 应继续停留在当前 `/openwiki-chat` 状态，询问保存到哪个分类，然后把这次问答写入 `my-wiki/wiki/explorations/<分类>/`，并更新 `wiki/explorations.md` 和对应分类页。

整理分类：

```text
在 my-wiki/ 知识库里整理分类。
```

OpenClaw 应调用 `/openwiki-category`。如果没有进一步描述，就先列出可做的分类操作，让用户选择下一步。

移动文档分类：

```text
把 my-wiki/ 知识库里的 paper 移到 AI 分类。
```

OpenClaw 应调用 `/openwiki-category`，移动 `wiki/categories/` 下的用户可见文档页，并更新索引、frontmatter 和链接。

## 结构

一个初始化后的知识库大致长这样：

```text
my-wiki/
  .openwiki/                    OpenWiki 内部状态和配置
    config.yaml                 知识库配置
    hashes.json                 已处理文档的哈希记录
    taxonomy.yaml               分类体系
    chats/                      聊天会话记录
  .codex/                       Codex 可用的本地 skills
    skills/openwiki-init/       初始化知识库
    skills/openwiki-add/        添加资料
    skills/openwiki-chat/       知识库问答
    skills/openwiki-category/   分类整理
  .claude/                      Claude Code / Claudian 可用的本地 skills
    skills/openwiki-init/       初始化知识库
    skills/openwiki-add/        添加资料
    skills/openwiki-chat/       知识库问答
    skills/openwiki-category/   分类整理
  raw/                          原始资料放这里
  wiki/                         用户阅读和检索的 Markdown 知识库
    AGENTS.md                   知识库 schema 和 LLM 编辑规则
    index.md                    知识库总索引
    explorations.md             已保存探索记录的入口
    log.md                      操作日志
    sources/                    转换后的稳定源内容
      images/                   从文档中提取的图片
    concepts/                   跨文档概念页
    categories/                 分类后的用户可见文档页
      uncategorized/            未分类内容
        index.md                未分类入口页
    explorations/               保存的问答、分析和比较
```

几个重要边界：

- `raw/` 放原始资料。
- `wiki/` 是用户可读的 Markdown 知识库。
- `wiki/sources/` 存放转换后的稳定源内容，分类时不要移动它。
- `wiki/categories/<category>/` 存放用户可见的分类文档页。
- `wiki/concepts/` 存放跨文档概念页。
- `wiki/explorations/` 存放保存下来的问答、分析和比较。
- `.openwiki/` 存放配置、哈希、会话和状态。
- 知识库里的 `wiki/AGENTS.md` 是运行时 wiki schema，由 OpenWiki 初始化时生成。

## 原理

OpenWiki 把知识库维护拆成三层。

第一层是机械转换。短文档会被转换成 Markdown；文本和 Markdown 会做安全解码，Office/HTML 等格式通过 MarkItDown 转换，短 PDF 会提取文本和图片。30 页及以上的 PDF 会交给 PageIndex，生成结构页和分页全文。

第二层是 LLM 编译。模型会根据转换后的内容和当前分类体系，生成用户可读的分类文档页、简短索引说明、概念页和交叉链接。长 PDF 不会把完整正文重复塞进文档页，而是在分类页里保留结构、页码范围和 `full_text: sources/<document>.json` 指针。

第三层是检索和追溯。`openwiki-chat` 先沿着 `index.md`、分类页、概念页理解知识库，再用 qmd 在用户可见 Markdown 层召回候选页面。qmd 不搜索 `raw/`、`.openwiki/`、`.codex/`、`.claude/` 或 `wiki/sources/`。需要长 PDF 细节时，再根据文档页中的指针读取分页源内容。

默认配置保存在：

```text
my-wiki/.openwiki/config.yaml
```

常见字段：

```yaml
language: en
model: gpt-5.4-mini
pageindex_threshold: 30
retrieval:
  engine: auto
  qmd_mode: search
  fallback: wiki_structure
```

普通 Claudian、Claude Code 和 Codex skill 使用路径不需要你手动填写模型或 API key；模型能力来自当前会话。

## 流程

```text
安装 OpenWiki
  |
  v
创建或进入知识库目录
  |
  v
/openwiki-init
  |
  v
raw/ 放入原始资料
  |
  v
/openwiki-add
  |
  +-- 短文档 -> Markdown -> 分类文档页
  |
  +-- 长 PDF -> PageIndex -> 结构页 + 分页全文
  |
  v
更新 categories/、concepts/、index.md、log.md
  |
  v
/openwiki-chat 提问、比较、总结
  |
  +-- 先读 index.md、categories/、concepts/
  |
  +-- 再用 qmd 召回相关 Markdown 页面
  |
  +-- 如需长 PDF 细节，通过 PageIndex 分页全文追溯
  |
  v
保存到 explorations/，必要时用 /openwiki-category 重新整理
```

添加文档时，OpenWiki 只会在转换、索引和 LLM 编译全部成功之后注册哈希。这样失败的半成品不会被误认为已经完成。

## License

Apache License 2.0。详见 [LICENSE](LICENSE)。
