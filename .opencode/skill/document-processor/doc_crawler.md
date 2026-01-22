# doc-crawler Skill - 文档智能爬取

## 功能描述

从多种来源爬取文档内容，支持网页、文件、API等多种输入方式，提供智能解析、去重、质量筛选等功能。

## 核心能力

1. 爬取网页文档内容
2. 解析多种文档格式（PDF、Word、Markdown等）
3. 智能提取正文内容
4. 文档去重和质量筛选
5. 支持增量爬取和断点续传
6. 多线程并发爬取

---

## 数据源支持

| 数据源类型 | 说明 | 特点 |
|-----------|------|------|
| `WEB` | 网页爬取 | 通用爬虫，支持动态页面 |
| `PDF` | PDF文档 | 支持扫描版OCR |
| `DOCX` | Word文档 | 解析文字、表格、图片 |
| `MARKDOWN` | Markdown文件 | 结构化解析 |
| `API` | API接口 | JSON/XML格式支持 |
| `DATABASE` | 数据库 | 支持SQL查询导出 |
| `FILE_SYSTEM` | 本地文件系统 | 批量文件处理 |

---

## 网页爬取规范

### 1. 爬取策略

- ✅ **遵守robots.txt**：尊重网站的爬虫协议
- ✅ **控制爬取频率**：避免对目标网站造成压力
- ✅ **处理动态内容**：支持JavaScript渲染页面
- ✅ **处理反爬虫**：合理使用代理和请求头

### 2. 内容提取

- ✅ **智能正文提取**：使用算法识别正文区域
- ✅ **去除广告噪音**：过滤非正文内容
- ✅ **保持内容结构**：保留段落、标题层级
- ✅ **提取元数据**：标题、作者、发布时间等

### 3. URL处理

```
爬取流程：
1. 输入种子URL
2. 解析页面链接
3. 过滤相关链接（同域名、过滤参数）
4. 去重（已爬取URL集合）
5. 加入爬取队列
6. 循环直到完成
```

---

## 文档解析规范

### 1. PDF解析

| 功能 | 说明 |
|-----|------|
| 文字提取 | 提取可编辑文字内容 |
| 表格识别 | 识别并提取表格数据 |
| 图片提取 | 提取嵌入图片 |
| 结构还原 | 还原文档阅读顺序 |
| OCR识别 | 处理扫描版PDF |

### 2. Word文档解析

| 功能 | 说明 |
|-----|------|
| 文字提取 | 提取正文内容 |
| 表格处理 | 解析表格结构 |
| 图片提取 | 提取嵌入图片 |
| 样式保留 | 保留标题层级格式 |
| 批注处理 | 提取文档批注 |

### 3. 通用处理

- ✅ 支持**编码自动检测**（UTF-8、GBK等）
- ✅ 支持**乱码修复**和**格式标准化**
- ✅ 支持**大文件分块处理**
- ✅ 支持**加密文件解密**

---

## 去重与质量筛选

### 1. 去重策略

| 去重方法 | 说明 | 适用场景 |
|---------|------|---------|
| `EXACT` | 精确匹配 | 完全相同内容 |
| `FINGERPRINT` | 指纹去重 | 近似重复检测 |
| `SIMHASH` | SimHash算法 | 大规模去重 |
| `TITLE_SIMILARITY` | 标题相似度 | 标题党识别 |

### 2. 质量评估

| 评估维度 | 指标 | 权重 |
|---------|------|------|
| 内容质量 | 文字比例、段落长度 | 40% |
| 信息完整 | 标题、正文、元数据 | 30% |
| 格式规范 | 编码、格式、排版 | 15% |
| 原创性 | 重复度、抄袭检测 | 15% |

---

## 增量爬取与断点续传

### 1. 增量爬取

- ✅ **记录爬取状态**：已爬取URL、更新时间
- ✅ **定时增量更新**：只爬取新增或更新的内容
- ✅ **变更检测**：比较内容哈希识别变化
- ✅ **增量策略**：全量/增量/定时任务

### 2. 断点续传

```
续传流程：
1. 保存爬取进度（最后成功URL、已爬URL集合）
2. 检测中断点
3. 从中断处继续爬取
4. 跳过已爬取内容
5. 完成爬取任务
```

---

## 输出格式

### 爬取结果

```json
{
  "task_id": "crawl_123456",
  "status": "completed",
  "statistics": {
    "total_urls": 100,
    "success_count": 85,
    "failed_count": 15,
    "total_size": "50MB"
  },
  "documents": [
    {
      "url": "https://example.com/article1",
      "title": "文章标题",
      "content": "文章正文内容...",
      "metadata": {
        "author": "作者名",
        "publish_time": "2024-01-15",
        "update_time": "2024-01-16"
      },
      "extracted_at": "2024-01-16T10:30:00Z"
    }
  ],
  "errors": [
    {
      "url": "https://example.com/broken",
      "error": "404 Not Found"
    }
  ]
}
```

### 批量爬取结果

```json
{
  "batch_id": "batch_789",
  "source_type": "FILE_SYSTEM",
  "files": [
    {
      "path": "/docs/paper1.pdf",
      "status": "success",
      "content": "PDF文字内容...",
      "pages": 15,
      "size": "2.5MB"
    }
  ],
  "summary": {
    "total": 50,
    "succeeded": 48,
    "failed": 2
  }
}
```

---

## 使用示例

```python
from doc_crawler import DocumentCrawler, SourceType

crawler = DocumentCrawler()

# 爬取网页
result = crawler.crawl(
    source_type=SourceType.WEB,
    urls=[
        "https://example.com/article1",
        "https://example.com/article2"
    ],
    options={
        "max_depth": 3,
        "concurrent": 5,
        "timeout": 30,
        "extract_content": True
    }
)

print(result.statistics)
print(result.documents)

# 爬取PDF文件
pdf_result = crawler.crawl(
    source_type=SourceType.PDF,
    paths=[
        "/docs/paper1.pdf",
        "/docs/paper2.pdf"
    ],
    options={
        "ocr": True,
        "extract_tables": True
    }
)

print(pdf_result.documents)
```

---

## 与其他Skill的配合

- **doc-analyze**：爬取内容可进一步使用文档分析Skill
- **doc-summarize**：分析结果可进一步使用文档总结Skill
- **doc-generate**：爬取内容可作为文档生成的输入
