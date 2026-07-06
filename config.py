"""知识图谱项目配置"""
import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOG_DIR = PROJECT_ROOT / "logs"

# PDF文件路径
PDF_PATH = DATA_DIR / "book.pdf"

# Neo4j配置
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "knowledge_graph_2024")

# API配置
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# NLP配置
NLP_MODEL = "bert-base-chinese"
MAX_TEXT_LENGTH = 512

# 知识图谱实体类型
ENTITY_TYPES = [
    "概念", "技术", "工具", "方法", "人物", "组织", "事件", "应用"
]

# 知识图谱关系类型
RELATION_TYPES = [
    "属于", "包含", "使用", "依赖", "对比", "创建", "发展", "应用"
]

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}"
