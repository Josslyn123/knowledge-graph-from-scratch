"""推理引擎单元测试"""
import pytest
from src.graph_store import GraphStore
from src.reasoning_engine import ReasoningEngine


@pytest.fixture
def reasoning_engine():
    """创建推理引擎实例"""
    gs = GraphStore()
    # 添加测试数据
    gs.add_entity("人工智能", "概念")
    gs.add_entity("机器学习", "技术")
    gs.add_entity("深度学习", "技术")
    gs.add_entity("知识图谱", "概念")
    gs.add_entity("Neo4j", "工具")
    gs.add_entity("自然语言处理", "技术")

    gs.add_relation("机器学习", "属于", "人工智能")
    gs.add_relation("深度学习", "属于", "机器学习")
    gs.add_relation("知识图谱", "属于", "人工智能")
    gs.add_relation("Neo4j", "用于", "知识图谱")
    gs.add_relation("自然语言处理", "属于", "人工智能")
    gs.add_relation("知识图谱", "使用", "自然语言处理")

    return ReasoningEngine(gs)


class TestReasoningEngine:
    """推理引擎测试类"""

    def test_transitive_reasoning(self, reasoning_engine):
        """测试传递性推理"""
        results = reasoning_engine.transitive_reasoning("深度学习", "属于")
        assert len(results) > 0
        # 深度学习 -> 机器学习 -> 人工智能
        paths = [r["path"] for r in results]
        assert any("人工智能" in path for path in paths)

    def test_symmetric_reasoning(self, reasoning_engine):
        """测试对称性推理"""
        results = reasoning_engine.symmetric_reasoning("知识图谱")
        assert len(results) > 0
        # 应该能找到与知识图谱相关的实体
        related_names = [r["entity"] for r in results]
        assert "Neo4j" in related_names or "自然语言处理" in related_names

    def test_composition_reasoning(self, reasoning_engine):
        """测试组合推理"""
        results = reasoning_engine.composition_reasoning("深度学习")
        assert isinstance(results, list)
        # 应该能发现间接关系

    def test_similarity_reasoning(self, reasoning_engine):
        """测试相似性推理"""
        results = reasoning_engine.similarity_reasoning("机器学习", top_k=3)
        assert len(results) > 0
        # 应该返回相似的实体
        for result in results:
            assert "name" in result
            assert "similarity" in result

    def test_causal_reasoning(self, reasoning_engine):
        """测试因果推理"""
        results = reasoning_engine.causal_reasoning("人工智能")
        assert isinstance(results, list)

    def test_analogy_reasoning(self, reasoning_engine):
        """测试类比推理"""
        results = reasoning_engine.analogy_reasoning(
            "机器学习", "人工智能", "深度学习"
        )
        assert isinstance(results, list)

    def test_infer_new_relations(self, reasoning_engine):
        """测试推断新关系"""
        inferred = reasoning_engine.infer_new_relations(confidence_threshold=0.5)
        assert isinstance(inferred, list)
        for rel in inferred:
            assert "subject" in rel
            assert "predicate" in rel
            assert "object" in rel
            assert "confidence" in rel
            assert "reason" in rel

    def test_explain(self, reasoning_engine):
        """测试实体解释"""
        explanation = reasoning_engine.explain("知识图谱")
        assert "entity" in explanation
        assert "type" in explanation
        assert "explanation" in explanation
        assert explanation["entity"] == "知识图谱"
        assert explanation["type"] == "概念"

    def test_explain_not_found(self, reasoning_engine):
        """测试解释不存在的实体"""
        explanation = reasoning_engine.explain("不存在")
        assert "error" in explanation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
