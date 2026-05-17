向知识库提问，由 Claude 直接检索 wiki 并回答。

## 步骤

### 1. 确认 KB 目录
检查当前目录是否存在 `.openwiki/`，不存在则提示用户先 `/init`。

### 2. 确认问题
如果用户没有提供问题，询问要查询的内容。

### 3. 检索 wiki
先读 `wiki/index.md` 了解有哪些文档和概念。根据问题匹配相关页面：读对应的 `wiki/summaries/` 摘要、`wiki/concepts/` 概念页，必要时深入 `wiki/sources/` 源文件。

### 4. 回答
基于检索到的内容回答问题。引用来源使用 [[wikilinks]] 格式。如果现有内容不足以回答，如实告知。

### 5. 保存（可选）
如果用户要求保存，将问答结果写入 `wiki/explorations/<slug>.md`，并更新 `wiki/index.md` 的 Explorations 部分。

### 6. 结尾提示
回答结束后提示用户：`如要保存这次问答，输入 /save <名称>`
