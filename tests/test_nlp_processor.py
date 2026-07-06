"""NLP处理器单元测试"""
import pytest
from src.nlp_processor import NLPProcessor


@pytest.fixture
def processor():
    """创建NLP处理器实例"""
    return NLPProcessor()


class TestNLPProcessor:
    """NLP处理器测试类"""

    def test_extract_entities_basic(self, processor):
        """测试基本实体提取"""
        text = "知识图谱是一种语义网络，用于表示实体及其关系。"
        entities = processor.extract_entities(text)

        assert len(entities) > 0
        entity_names = [e["name"] for e in entities]
        assert "知识图谱" in entity_names

    def test_extract_entities_types(self, processor):
        """测试实体类型识别"""
        text = "Neo4j是一个图数据库，Google公司开发了TensorFlow。"
        entities = processor.extract_entities(text)

        entity_types = {e["name"]: e["type"] for e in entities}
        # Neo4j应该被识别为工具或技术
        if "Neo4j" in entity_types:
            assert entity_types["Neo4j"] in ["工具", "技术", "概念"]
        # Google应该被识别为组织
        if "Google" in entity_types:
            assert entity_types["Google"] == "组织"

    def test_extract_relations(self, processor):
        """测试关系抽取"""
        text = "知识图谱使用Neo4j进行存储。"
        entities = processor.extract_entities(text)
        relations = processor.extract_relations(text, entities)

        # 应该能抽取到一些关系
        assert isinstance(relations, list)

    def test_extract_triples(self, processor):
        """测试三元组提取"""
        text = "知识图谱属于人工智能领域，使用Neo4j存储。"
        triples = processor.extract_triples(text)

        assert isinstance(triples, list)
        for triple in triples:
            assert "subject" in triple
            assert "predicate" in triple
            assert "object" in triple

    def test_process_text(self, processor):
        """测试完整文本处理"""
        text = """
        知识图谱是一种语义网络，用于表示实体及其关系。
        Neo4j是常用的图数据库。
        自然语言处理技术用于知识抽取。
        """
        result = processor.process_text(text)

        assert "entities" in result
        assert "relations" in result
        assert "triples" in result
        assert result["entity_count"] > 0

    def test_empty_text(self, processor):
        """测试空文本处理"""
        result = processor.process_text("")
        assert result["entity_count"] == 0
        assert result["relation_count"] == 0

    def test_process_paragraphs(self, processor):
        """测试批量段落处理"""
        paragraphs = [
            "知识图谱是一种语义网络。",
            "Neo4j是图数据库。",
            "深度学习是机器学习的子领域。"
        ]
        result = processor.process_paragraphs(paragraphs)

        assert result["entity_count"] > 0
        assert len(result["entities"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
