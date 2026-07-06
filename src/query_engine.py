"""知识图谱查询引擎"""
from typing import List, Dict, Optional
from loguru import logger
from .graph_store import GraphStore


class QueryEngine:
    """知识图谱查询引擎"""

    def __init__(self, graph_store: GraphStore):
        self.gs = graph_store
        logger.info("查询引擎初始化完成")

    def query_entity(self, name: str) -> Optional[Dict]:
        """查询实体详细信息"""
        return self.gs.get_entity(name)

    def query_relations(self, name: str) -> List[Dict]:
        """查询实体的所有关系"""
        entity = self.gs.get_entity(name)
        if entity:
            return entity.get("relations", [])
        return []

    def query_neighbors(self, name: str, depth: int = 1) -> Dict:
        """查询邻居节点"""
        return self.gs.get_neighbors(name, depth)

    def query_path(self, start: str, end: str, max_depth: int = 5) -> List[List[str]]:
        """查询两实体间路径"""
        return self.gs.find_path(start, end, max_depth)

    def query_by_type(self, entity_type: str, limit: int = 50) -> List[Dict]:
        """按类型查询实体"""
        return self.gs.query_by_type(entity_type, limit)

    def query_related_by_relation(self, name: str, relation_type: str) -> List[Dict]:
        """查询具有特定关系的实体"""
        entity = self.gs.get_entity(name)
        if not entity:
            return []

        results = []
        for rel in entity.get("relations", []):
            if rel["type"] == relation_type:
                results.append({
                    "name": rel["target"],
                    "type": self.gs.entity_types.get(rel["target"], "未知")
                })
        return results

    def query_subgraph(self, center: str, depth: int = 2) -> Dict:
        """查询子图"""
        return self.gs.get_subgraph(center, depth)

    def search(self, keyword: str, limit: int = 20) -> List[Dict]:
        """搜索实体"""
        return self.gs.search_entities(keyword, limit)

    def query_most_connected(self, limit: int = 10) -> List[Dict]:
        """查询连接最多的实体"""
        return self.gs.get_most_connected(limit)

    def natural_language_query(self, question: str) -> Dict:
        """自然语言查询"""
        question = question.strip()

        if "是什么" in question or "什么是" in question:
            entity = self._extract_entity_from_question(question)
            if entity:
                result = self.query_entity(entity)
                return {"type": "entity", "query": entity, "result": result}

        elif "关系" in question or "联系" in question:
            entities = self._extract_entities_from_question(question)
            if len(entities) >= 2:
                paths = self.query_path(entities[0], entities[1])
                return {"type": "path", "query": entities, "result": paths}

        elif "有哪些" in question or "包括" in question:
            entity = self._extract_entity_from_question(question)
            if entity:
                neighbors = self.query_neighbors(entity, depth=1)
                return {"type": "neighbors", "query": entity, "result": neighbors}

        keyword = self._extract_keyword(question)
        results = self.search(keyword)
        return {"type": "search", "query": keyword, "result": results}

    def _extract_entity_from_question(self, question: str) -> Optional[str]:
        """从问题中提取实体"""
        remove_words = ["是什么", "什么是", "有哪些", "包括", "的", "？", "?"]
        text = question
        for word in remove_words:
            text = text.replace(word, "")
        return text.strip() if text.strip() else None

    def _extract_entities_from_question(self, question: str) -> List[str]:
        """从问题中提取多个实体"""
        import re
        entities = re.split(r'[和与跟]', question)
        return [e.strip() for e in entities if e.strip()]

    def _extract_keyword(self, question: str) -> str:
        """提取关键词"""
        remove_words = ["有哪些", "包括", "什么", "的", "？", "?", "请", "告诉", "我"]
        text = question
        for word in remove_words:
            text = text.replace(word, "")
        return text.strip() if text.strip() else question


if __name__ == "__main__":
    gs = GraphStore()
    engine = QueryEngine(gs)
    print("查询引擎测试完成")
