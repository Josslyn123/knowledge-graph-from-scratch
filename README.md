# 从零构建知识图谱 - 技术、方法与案例

基于《从零构建知识图谱》书籍内容，构建多维度知识图谱系统，包含查询引擎和推理引擎。

## 项目结构

```
kg_project/
├── main.py                 # 主程序入口
├── config.py               # 配置文件
├── requirements.txt        # Python依赖
├── README.md               # 项目说明
├── src/                    # 源代码
│   ├── __init__.py
│   ├── pdf_extractor.py    # PDF内容提取
│   ├── nlp_processor.py    # NLP处理（实体识别、关系抽取）
│   ├── knowledge_graph.py  # 知识图谱构建与存储
│   ├── query_engine.py     # 查询引擎
│   ├── reasoning_engine.py # 推理引擎
│   └── api.py              # Web API接口
├── data/                   # 数据目录
│   └── book.pdf            # 原始PDF书籍
├── output/                 # 输出目录
└── logs/                   # 日志目录
```

## 功能特性

### 1. PDF内容提取
- 支持PDF文本提取
- 自动识别章节结构
- 段落分割和清洗

### 2. NLP处理
- 实体识别（基于词性标注、正则模式、领域词典）
- 关系抽取（基于模式匹配、共现分析）
- 三元组提取

### 3. 知识图谱构建
- 多维度实体类型（概念、技术、工具、方法、人物、组织等）
- 多种关系类型（属于、包含、使用、依赖、对比等）
- 基于Neo4j图数据库存储

### 4. 查询引擎
- 实体查询
- 关系查询
- 路径查询
- 子图查询
- 自然语言查询
- 关键词搜索

### 5. 推理引擎
- 传递性推理
- 对称性推理
- 组合推理
- 相似性推理
- 因果推理
- 类比推理

### 6. Web API
- RESTful API接口
- 图谱可视化页面
- Swagger API文档

## 快速开始

### 环境要求
- Python 3.9+
- Neo4j 5.x

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置Neo4j

1. 安装Neo4j数据库
2. 修改 `config.py` 中的连接配置
3. 或设置环境变量：
   ```bash
   export NEO4J_URI=bolt://localhost:7687
   export NEO4J_USER=neo4j
   export NEO4J_PASSWORD=your_password
   ```

### 运行

```bash
# 执行全部步骤
python main.py all

# 或分步执行
python main.py extract   # 提取PDF
python main.py process   # NLP处理
python main.py build     # 构建图谱
python main.py serve     # 启动API
```

### 访问

- API文档: http://localhost:8000/docs
- 图谱可视化: http://localhost:8000/graph/html
- 统计信息: http://localhost:8000/statistics

## API接口

### 实体接口
- `POST /entity` - 添加实体
- `GET /entity/{name}` - 获取实体
- `GET /entity/{name}/neighbors` - 获取邻居节点
- `GET /entity/{name}/relations` - 获取实体关系

### 关系接口
- `POST /relation` - 添加关系

### 三元组接口
- `POST /triple` - 添加三元组
- `POST /triples/batch` - 批量添加三元组

### 查询接口
- `GET /search?keyword=xxx` - 搜索实体
- `GET /path?start=xxx&end=xxx` - 查找路径
- `GET /subgraph/{name}` - 获取子图
- `GET /most-connected` - 获取连接最多的实体
- `POST /query` - 自然语言查询

### 推理接口
- `GET /reasoning/transitive` - 传递性推理
- `GET /reasoning/similar` - 相似性推理
- `GET /reasoning/composition` - 组合推理
- `GET /reasoning/explain/{name}` - 实体解释
- `POST /reasoning/infer` - 应用推理

## 技术栈

- **PDF处理**: PyMuPDF
- **NLP**: jieba
- **图数据库**: Neo4j
- **Web框架**: FastAPI
- **可视化**: ECharts

## 许可证

MIT License
