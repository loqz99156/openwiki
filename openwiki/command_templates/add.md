将文件添加到知识库：机械转换用 Python 处理，LLM 编译（摘要、概念页、索引）由 Claude 直接完成。

## 步骤

### 1. 确认 KB 目录
检查当前目录是否存在 `.openwiki/`，不存在则提示用户先 `/init`。

### 2. 确定要处理的文件

**如果用户指定了路径**：按指定路径处理单个文件。

**如果用户未指定路径**：扫描 `raw/` 目录，找出未注册的新文件：

```python
import json, sys
from pathlib import Path
from openwiki.state import HashRegistry

kb_dir = Path(sys.argv[1])
raw_dir = kb_dir / "raw"
hashes_path = kb_dir / ".openwiki" / "hashes.json"
registry = HashRegistry(hashes_path)

SUPPORTED = {".pdf", ".md", ".txt", ".docx", ".pptx", ".xlsx", ".html", ".csv", ".json", ".xml", ".rtf", ".epub", ".odt"}
files = []
for f in sorted(raw_dir.iterdir()):
    if f.is_file() and not f.name.startswith(".") and f.suffix.lower() in SUPPORTED:
        h = HashRegistry.hash_file(f)
        if not registry.is_known(h):
            files.append((f, h))
            print(f"NEW: {f.name}|{h}")
if not files:
    print("NO_NEW_FILES")
```

```bash
python3 -c "<上面的代码>" <kb_dir>
```

- 输出 `NO_NEW_FILES` → 告知用户 raw/ 中没有新文件，停止。
- 输出 `NEW: <文件名>|<hash>` → 收集文件列表，逐个处理。

### 3. 机械转换（Python）

对每个待处理文件运行。如果文件已在 `raw/` 中（由扫描模式进入），跳过复制步骤；如果是指定外部路径，先复制到 `raw/`。

```python
import json, shutil, sys
from pathlib import Path
from openwiki.config import load_config
from openwiki.converter import get_pdf_page_count
from openwiki.state import HashRegistry
from markitdown import MarkItDown

src = Path(sys.argv[1])
kb_dir = Path(sys.argv[2])
openwiki_dir = kb_dir / ".openwiki"
config = load_config(openwiki_dir / "config.yaml")
threshold = config.get("pageindex_threshold", 20)
registry = HashRegistry(openwiki_dir / "hashes.json")

file_hash = HashRegistry.hash_file(src)
if registry.is_known(file_hash):
    print(f"SKIP: {file_hash}")
    sys.exit(0)

raw_dir = kb_dir / "raw"
raw_dir.mkdir(parents=True, exist_ok=True)
raw_path = raw_dir / src.name

# 如果文件不在 raw/ 中才复制
if src.resolve() != raw_path.resolve() and not str(src.resolve()).startswith(str(raw_dir.resolve())):
    shutil.copy2(src, raw_path)
    src = raw_path

# markitdown 转换
md = MarkItDown()
result = md.convert(str(src))
sources_dir = kb_dir / "wiki" / "sources"
sources_dir.mkdir(parents=True, exist_ok=True)
source_path = sources_dir / f"{src.stem}.md"
source_path.write_text(result.text_content, encoding="utf-8")

# PDF 检测
doc_type = "short"
is_long = False
pages = 0
if src.suffix.lower() == ".pdf":
    pages = get_pdf_page_count(src)
    if pages >= threshold:
        is_long = True
        doc_type = "pageindex"

print(f"HASH: {file_hash}")
print(f"RAW: {raw_path}")
print(f"SOURCE: {source_path}")
print(f"DOC_TYPE: {doc_type}")
print(f"IS_LONG: {is_long}")
print(f"DOC_NAME: {src.stem}")
print(f"PAGES: {pages}")
```

```bash
python3 -c "<上面的代码>" <文件路径> <kb_dir>
```

如果输出 `SKIP:`，标记为已存在，跳到下一个文件。

### 4. 长文档 PageIndex 索引（如果需要）
如果 `IS_LONG: True`，运行：

```python
from openwiki.indexer import index_long_document
result = index_long_document(Path(sys.argv[1]), Path(sys.argv[2]))
print(f"DOC_ID: {result.doc_id}")
print(f"DESCRIPTION: {result.description}")
```
```bash
python3 -c "<上面的代码>" <raw_path> <kb_dir>
```

### 5. 生成摘要（Claude）
读取 `wiki/AGENTS.md` schema 和源文件内容。生成摘要页写入 `wiki/summaries/<doc_name>.md`：

```markdown
---
doc_type: <short 或 pageindex>
full_text: sources/<doc_name>.<md 或 json>
---

<完整的 Markdown 摘要内容，附 [[wikilinks]]>
```

如果是长文档，先读取 PageIndex 摘要（`wiki/summaries/<doc_name>.md` 中已有 indexer 写入的内容），基于结构化摘要生成概述。

### 6. 规划概念页变更（Claude）
读取 `wiki/concepts/*.md` 的 brief 字段或首 150 字。根据文档内容和现有概念，决定：
- **create**：新概念（跨文档主题，不与现有重叠）
- **update**：有新信息需整合的现有概念
- **related**：仅需交叉引用链接的概念

### 7. 生成/更新概念页（Claude）
对每个 create/update 概念写 `wiki/concepts/<slug>.md`：

```markdown
---
sources: [summaries/<doc_name>.md]
brief: <一句话定义，100 字内>
---

<完整内容，包含 [[wikilinks]] 和 [[summaries/<doc_name>]]>
```

update 时重写全页整合新信息，不尾部追加。

### 8. 添加交叉引用（Claude）
- **摘要**：末尾加 `## Related Concepts`，列出所有相关 `[[concepts/...]]`
- **概念**：末尾加 `## Related Documents`，列出 `[[summaries/<doc_name>]]`
- **related 概念**：末尾加 `See also: [[summaries/<doc_name>]]`，更新 sources frontmatter

### 9. 更新索引（Claude）
更新 `wiki/index.md`。此项只在所有文件处理完成后做一次。

### 10. 写日志 + 注册哈希（Python）
每个文件处理完后立即追加日志和注册哈希：

```python
import json
from datetime import datetime
from pathlib import Path

kb = Path(sys.argv[1])
log = kb / "wiki" / "log.md"
entry = f"## [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ingest | {sys.argv[2]}\n\n"
with log.open("a") as f:
    f.write(entry)

hashes = kb / ".openwiki" / "hashes.json"
data = json.loads(hashes.read_text()) if hashes.exists() else {}
data[sys.argv[3]] = {"name": sys.argv[2], "type": sys.argv[4]}
hashes.write_text(json.dumps(data, indent=2))
```
```bash
python3 -c "<上面的代码>" <kb_dir> <文件名> <hash> <doc_type>
```

### 11. 汇总报告
所有文件处理完毕后汇总：

```
处理 raw/ 中新文件：
  ✓ <文件名> → summaries/<name>.md (<type>)，<概念变更摘要>
  ⊘ <文件名> (已注册，跳过)
```
