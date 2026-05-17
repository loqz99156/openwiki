保存当前对话中最新的问答到知识库的 explorations/ 目录。

## 步骤

### 1. 确认 KB 目录
检查当前目录是否存在 `.openwiki/`，不存在则向上查找，仍找不到则提示用户先 `/init`。

### 2. 确定名称
如果用户提供了名称（如 `/save 四阶段指南`），使用该名称作为 slug。

如果未提供名称，不要询问用户，直接根据最近一次问答的主题自动生成一个简短英文 slug（小写、连字符、去除特殊字符），例如：`ai-native-startup-four-stages`。

### 3. 保存问答
将当前对话中最近一轮完整的 Q&A（用户问题 + 回答内容）写入 `wiki/explorations/<slug>.md`，格式：

```markdown
# <标题>

## 问题
<用户的问题>

## 回答
<回答内容>

## 来源
- [[summaries/...]]
- [[concepts/...]]
```

### 4. 更新索引
在 `wiki/index.md` 的 Explorations 部分追加新条目：
```
- [[explorations/<slug>]] — <一句话描述>
```

### 5. 确认
告知用户保存路径。
