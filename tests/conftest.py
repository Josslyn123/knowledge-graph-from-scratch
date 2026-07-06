"""Pytest配置文件"""
import pytest
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def project_root():
    """项目根目录"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def sample_text():
    """示例文本"""
    return """
    知识图谱是一种语义网络，用于表示实体及其关系。
    Neo4j是一个流行的图数据库，广泛应用于知识图谱存储。
    自然语言处理（NLP）技术用于从文本中抽取知识。
    深度学习是机器学习的一个子领域，BERT是基于深度学习的预训练模型。
    Google在2012年提出了知识图谱的概念。
    """
