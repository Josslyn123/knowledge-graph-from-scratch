# 从零构建知识图谱 - 完整知识图谱系统

基于《从零构建知识图谱》书籍内容构建的多维度知识图谱系统，包含完整的数据处理、知识抽取、图谱构建、查询推理和智能问答功能。

## 功能特性

### 1. PDF内容提取
- 自动提取PDF书籍内容
- 支持章节结构识别
- 段落分割和清洗

### 2. NLP处理
- 实体识别（基于词性标注、正则模式、领域词典）
- 关系抽取（基于模式匹配、共现分析）
- 三元组自动提取

### 3. 知识图谱构建
- 多维度实体类型：概念、技术、工具、方法、人物、组织等
- 多种关系类型：属于、包含、使用、依赖、对比等
- 基于NetworkX的图存储（可选Neo4j）

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

### 6. 智能问答系统
- 对话式交互界面
- 基于知识图谱的问答
- 支持集成大语言模型

## 项目结构

```
kg_project/
├── main.py                 # 主程序入口
├── config.py               # 配置文件
├── requirements.txt        # Python依赖
├── README.md               # 项目说明
├── deploy.sh               # 部署脚本
├── .gitignore
├── src/                    # 源代码
│   ├── __init__.py
│   ├── pdf_extractor.py    # PDF内容提取
│   ├── nlp_processor.py    # NLP处理
│   ├── graph_store.py      # 图存储（NetworkX）
│   ├── knowledge_graph.py  # 图谱存储（Neo4j）
│   ├── query_engine.py     # 查询引擎
│   ├── reasoning_engine.py # 推理引擎
│   ├── api.py              # 基础API
│   ├── chat_api.py         # 智能问答API
│   └── dataset_builder.py  # 数据集构建工具
├── dataset/                # 数据集
│   ├── entities.json/csv   # 实体数据集
│   ├── relations.json/csv  # 关系数据集
│   ├── triples.json/csv    # 三元组数据集
│   ├── triples_train.txt   # TransE训练格式
│   ├── knowledge_graph_dataset.json  # 完整数据集
│   └── by_type/            # 按类型分类的数据集
└── data/                   # 原始数据（需自行添加）
    └── book.pdf            # PDF书籍
```

## 快速开始

### 环境要求
- Python 3.9+
- 操作系统：Windows/Linux/macOS

### 安装

```bash
# 克隆项目
git clone https://github.com/YOUR_USERNAME/knowledge-graph-from-scratch.git
cd knowledge-graph-from-scratch

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 使用

#### 方式1：使用已有数据集（推荐）

项目已包含从《从零构建知识图谱》书籍提取的数据集，可以直接使用：

```bash
# 启动智能问答服务
python main.py serve
```

然后访问 http://localhost:8000 即可使用智能问答界面。

#### 方式2：从PDF重新构建

1. 将PDF书籍放入 `data/` 目录，命名为 `book.pdf`

2. 执行完整流程：
```bash
python main.py all
```

或分步执行：
```bash
python main.py extract   # 提取PDF内容
python main.py process   # NLP处理
python main.py build     # 构建知识图谱
python main.py serve     # 启动服务
```

#### 方式3：构建数据集

```bash
python src/dataset_builder.py
```

## API接口

### 智能问答
```
POST /chat
{
  "message": "什么是知识图谱？",
  "session_id": "user1"
}
```

### 实体查询
```
GET /entity/{name}
GET /entity/{name}/neighbors
GET /entity/{name}/relations
```

### 搜索
```
GET /search?keyword=知识图谱&limit=20
```

### 推理
```
GET /reasoning/transitive?entity=知识图谱
GET /reasoning/similar?entity=Neo4j
GET /reasoning/explain/{name}
```

完整API文档：启动服务后访问 http://localhost:8000/docs

## 数据集

项目包含从《从零构建知识图谱》书籍提取的完整数据集：

| 类型 | 数量 |
|------|------|
| 实体 | 9,335 |
| 关系 | 26,495 |
| 三元组 | 34,459 |

### 实体类型分布

| 类型 | 数量 |
|------|------|
| 概念 | 5,090 |
| 技术 | 2,638 |
| 工具 | 977 |
| 人物 | 365 |
| 组织 | 204 |
| 地点 | 61 |

## 技术栈

- **PDF处理**: PyMuPDF
- **NLP**: jieba
- **图存储**: NetworkX (可选Neo4j)
- **Web框架**: FastAPI
- **可视化**: ECharts

## 扩展

### 集成大语言模型

在环境变量中配置API密钥：

```bash
export SILICONFLOW_API_KEY="your_key"  # 硅基流动API
export DEEPSEEK_API_KEY="your_key"     # DeepSeek API
```

### 使用Neo4j

修改 `config.py` 中的配置：

```python
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your_password"
```

## 许可证

MIT License

## 致谢

- 《从零构建知识图谱》作者：邵浩、张凯、李方圆、张云柯、戴锡强
- OpenKG社区
