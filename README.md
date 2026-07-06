# 从零构建知识图谱 - 完整知识图谱系统

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](tests/)

基于《从零构建知识图谱》书籍内容构建的多维度知识图谱系统，包含完整的数据处理、知识抽取、图谱构建、查询推理和智能问答功能。

## 功能特性

### 核心功能

| 功能模块 | 说明 | 技术实现 |
|---------|------|----------|
| PDF内容提取 | 自动提取PDF书籍内容 | PyMuPDF |
| NLP处理 | 实体识别、关系抽取 | jieba + 规则引擎 |
| 知识图谱构建 | 多维度图谱构建 | NetworkX |
| 查询引擎 | 多种查询方式 | 图遍历算法 |
| 推理引擎 | 知识推理与发现 | 规则推理 |
| 智能问答 | 对话式交互界面 | FastAPI |

### 详细功能

#### 1. NLP处理
- **实体识别**
  - 基于词性标注
  - 基于正则模式
  - 基于领域词典
- **关系抽取**
  - 基于模式匹配
  - 基于共现分析
- **三元组自动提取**

#### 2. 查询引擎
- 实体查询
- 关系查询
- 路径查询
- 子图查询
- 自然语言查询
- 关键词搜索

#### 3. 推理引擎
- 传递性推理：A属于B，B属于C → A属于C
- 对称性推理：A与B相关 → B与A相关
- 组合推理：A使用B，B使用C → A间接依赖C
- 相似性推理：基于结构相似度
- 因果推理：发现因果关系链

## 项目结构

```
kg_project/
├── main.py                 # 主程序入口
├── config.py               # 配置文件
├── requirements.txt        # Python依赖
├── pytest.ini              # 测试配置
├── deploy.sh               # 部署脚本
├── README.md               # 项目说明
├── CONTRIBUTING.md          # 贡献指南
├── CHANGELOG.md            # 更新日志
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
├── tests/                  # 单元测试
│   ├── conftest.py
│   ├── test_nlp_processor.py
│   ├── test_graph_store.py
│   ├── test_query_engine.py
│   └── test_reasoning_engine.py
└── dataset/                # 数据集
    ├── entities.json/csv   # 实体数据集
    ├── relations.json/csv  # 关系数据集
    ├── triples.json/csv    # 三元组数据集
    ├── triples_train.txt   # TransE训练格式
    ├── knowledge_graph_dataset.json  # 完整数据集
    └── by_type/            # 按类型分类的数据集
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

### 运行测试

```bash
# 运行所有测试
pytest

# 运行并显示详细输出
pytest -v

# 运行并生成覆盖率报告
pytest --cov=src tests/
```

## API接口

### 智能问答

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "什么是知识图谱？", "session_id": "user1"}'
```

### 实体查询

```bash
# 查询实体
curl http://localhost:8000/entity/知识图谱

# 获取邻居节点
curl http://localhost:8000/entity/知识图谱/neighbors

# 获取实体关系
curl http://localhost:8000/entity/知识图谱/relations
```

### 搜索

```bash
curl "http://localhost:8000/search?keyword=知识图谱&limit=20"
```

### 推理

```bash
# 传递性推理
curl "http://localhost:8000/reasoning/transitive?entity=知识图谱"

# 相似性推理
curl "http://localhost:8000/reasoning/similar?entity=Neo4j"

# 实体解释
curl http://localhost:8000/reasoning/explain/知识图谱
```

完整API文档：启动服务后访问 http://localhost:8000/docs

## 数据集

项目包含从《从零构建知识图谱》书籍提取的完整数据集：

### 统计信息

| 类型 | 数量 |
|------|------|
| 实体总数 | 9,335 |
| 关系总数 | 26,495 |
| 三元组总数 | 34,459 |

### 实体类型分布

| 类型 | 数量 | 说明 |
|------|------|------|
| 概念 | 5,090 | 知识概念 |
| 技术 | 2,638 | 技术方法 |
| 工具 | 977 | 软件工具 |
| 人物 | 365 | 相关人物 |
| 组织 | 204 | 机构组织 |
| 地点 | 61 | 地理位置 |

### 数据格式

#### 实体数据 (entities.json)
```json
{
  "id": "E00000",
  "name": "知识图谱",
  "type": "概念",
  "source": "dict",
  "count": 156
}
```

#### 三元组数据 (triples_train.txt)
```
知识图谱    属于    人工智能
Neo4j      使用    图数据库
自然语言处理  包含    实体识别
```

## 技术栈

| 类别 | 技术 | 用途 |
|------|------|------|
| PDF处理 | PyMuPDF | 提取PDF内容 |
| NLP | jieba | 中文分词、词性标注 |
| 图存储 | NetworkX | 图数据结构 |
| Web框架 | FastAPI | RESTful API |
| 可视化 | ECharts | 图谱可视化 |
| 测试 | pytest | 单元测试 |

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

## 部署

### 本地部署

```bash
python main.py serve
```

### 服务器部署

```bash
# 使用部署脚本
chmod +x deploy.sh
./deploy.sh

# 或手动部署
pip install -r requirements.txt
python main.py serve --host 0.0.0.0 --port 8000
```

### Docker部署（可选）

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py", "serve"]
```

## 贡献

欢迎贡献代码！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新历史。

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 致谢

- 《从零构建知识图谱》作者：邵浩、张凯、李方圆、张云柯、戴锡强
- OpenKG社区
- 所有贡献者

## 联系方式

如有问题，请通过GitHub Issues联系。
