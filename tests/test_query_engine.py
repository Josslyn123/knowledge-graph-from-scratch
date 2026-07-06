"""查询引擎单元测试"""
import pytest
from src.graph_store import GraphStore
from src.query_engine import QueryEngine


@pytest.fixture
def query_engine():
    """创建查询引擎实例"""
    gs = GraphStore()
    # 添加测试数据
    gs.add_entity("知识图谱", "概念")
    gs.add_entity("Neo4j", "工具")
    gs.add_entity("自然语言处理", "技术")
    gs.add_entity("深度学习", "技术")
    gs.add_entity("BERT", "技术")

    gs.add_relation("Neo4j", "用于", "知识图谱")
    gs.add_relation("知识图谱", "使用", "自然语言处理")
    gs.add_relation("深度学习", "属于", "机器学习")
    gs.add_relation("BERT", "基于", "深度学习")

    return QueryEngine(gs)


class TestQueryEngine:
    """查询引擎测试类"""

    def test_query_entity(self, query_engine):
        """测试实体查询"""
        entity = query_engine.query_entity("知识图谱")
        assert entity is not None
        assert entity["name"] == "知识图谱"
        assert entity["type"] == "概念"

    def test_query_entity_not_found(self, query_engine):
        """测试查询不存在的实体"""
        entity = query_engine.query_entity("不存在")
        assert entity is None

    def test_query_relations(self, query_engine):
        """测试关系查询"""
        relations = query_engine.query_relations("知识图谱")
        assert len(relations) > 0

    def test_query_neighbors(self, query_engine):
        """测试邻居查询"""
        neighbors = query_engine.query_neighbors("知识图谱", depth=1)
        assert neighbors["center"] == "知识图谱"
        assert len(neighbors["neighbors"]) > 0

    def test_query_path(self, query_engine):
        """测试路径查询"""
        paths = query_engine.query_path("Neo4j", "自然语言处理")
        assert isinstance(paths, list)

    def test_search(self, query_engine):
        """测试搜索"""
        results = query_engine.search("知识")
        assert len(results) > 0
        entity_names = [r["name"] for r in results]
        assert "知识图谱" in entity_names

    def test_query_most_connected(self, query_engine):
        """测试查询连接最多的实体"""
        results = query_engine.query_most_connected(limit=5)
        assert len(results) > 0
        assert "connections" in results[0]

    def test_natural_language_query(self, query_engine):
        """测试自然语言查询"""
        # 测试实体查询
        result = query_engine.natural_language_query("什么是知识图谱？")
        assert "type" in result
        assert "result" in result

    def test_query_subgraph(self, query_engine):
        """测试子图查询"""
        subgraph = query_engine.query_subgraph("知识图谱", depth=1)
        assert subgraph["center"] == "知识图谱"
        assert len(subgraph["nodes"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
