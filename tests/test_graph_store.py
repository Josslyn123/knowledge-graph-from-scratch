"""图存储单元测试"""
import pytest
from src.graph_store import GraphStore


@pytest.fixture
def graph_store():
    """创建图存储实例"""
    return GraphStore()


class TestGraphStore:
    """图存储测试类"""

    def test_add_entity(self, graph_store):
        """测试添加实体"""
        result = graph_store.add_entity("知识图谱", "概念")
        assert result is True

        # 验证实体已添加
        entity = graph_store.get_entity("知识图谱")
        assert entity is not None
        assert entity["name"] == "知识图谱"
        assert entity["type"] == "概念"

    def test_add_relation(self, graph_store):
        """测试添加关系"""
        graph_store.add_entity("知识图谱", "概念")
        graph_store.add_entity("Neo4j", "工具")

        result = graph_store.add_relation("Neo4j", "用于", "知识图谱")
        assert result is True

    def test_add_triple(self, graph_store):
        """测试添加三元组"""
        triple = {
            "subject": "知识图谱",
            "subject_type": "概念",
            "predicate": "使用",
            "object": "Neo4j",
            "object_type": "工具"
        }
        result = graph_store.add_triple(triple)
        assert result is True

    def test_batch_add_triples(self, graph_store):
        """测试批量添加三元组"""
        triples = [
            {"subject": "A", "subject_type": "概念", "predicate": "属于", "object": "B", "object_type": "概念"},
            {"subject": "B", "subject_type": "概念", "predicate": "包含", "object": "C", "object_type": "技术"},
        ]
        success, fail = graph_store.batch_add_triples(triples)
        assert success == 2
        assert fail == 0

    def test_get_entity(self, graph_store):
        """测试获取实体"""
        graph_store.add_entity("测试实体", "概念")
        entity = graph_store.get_entity("测试实体")

        assert entity is not None
        assert entity["name"] == "测试实体"
        assert entity["type"] == "概念"

    def test_get_entity_not_found(self, graph_store):
        """测试获取不存在的实体"""
        entity = graph_store.get_entity("不存在的实体")
        assert entity is None

    def test_get_neighbors(self, graph_store):
        """测试获取邻居节点"""
        graph_store.add_entity("A", "概念")
        graph_store.add_entity("B", "技术")
        graph_store.add_entity("C", "工具")
        graph_store.add_relation("A", "使用", "B")
        graph_store.add_relation("A", "包含", "C")

        neighbors = graph_store.get_neighbors("A", depth=1)
        assert neighbors["center"] == "A"
        assert len(neighbors["neighbors"]) >= 2

    def test_find_path(self, graph_store):
        """测试路径查找"""
        graph_store.add_entity("A", "概念")
        graph_store.add_entity("B", "概念")
        graph_store.add_entity("C", "概念")
        graph_store.add_relation("A", "连接", "B")
        graph_store.add_relation("B", "连接", "C")

        paths = graph_store.find_path("A", "C")
        assert len(paths) > 0
        assert paths[0] == ["A", "B", "C"]

    def test_search_entities(self, graph_store):
        """测试实体搜索"""
        graph_store.add_entity("知识图谱", "概念")
        graph_store.add_entity("知识表示", "概念")
        graph_store.add_entity("知识抽取", "技术")

        results = graph_store.search_entities("知识")
        assert len(results) >= 3

    def test_get_statistics(self, graph_store):
        """测试获取统计信息"""
        graph_store.add_entity("A", "概念")
        graph_store.add_entity("B", "技术")
        graph_store.add_relation("A", "使用", "B")

        stats = graph_store.get_statistics()
        assert stats["node_count"] == 2
        assert stats["relation_count"] == 1
        assert "概念" in stats["entity_types"]
        assert "技术" in stats["entity_types"]

    def test_export_to_json(self, graph_store, tmp_path):
        """测试导出JSON"""
        graph_store.add_entity("A", "概念")
        graph_store.add_entity("B", "技术")
        graph_store.add_relation("A", "使用", "B")

        output_path = str(tmp_path / "test_export.json")
        data = graph_store.export_to_json(output_path)

        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) == 2
        assert len(data["edges"]) == 1

    def test_clear(self, graph_store):
        """测试清空图"""
        graph_store.add_entity("A", "概念")
        graph_store.add_entity("B", "技术")
        graph_store.clear()

        stats = graph_store.get_statistics()
        assert stats["node_count"] == 0
        assert stats["relation_count"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
