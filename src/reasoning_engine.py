"""知识图谱推理引擎"""
from typing import List, Dict, Set, Tuple
from loguru import logger
from collections import defaultdict
from .graph_store import GraphStore


class ReasoningEngine:
    """知识图谱推理引擎"""

    def __init__(self, graph_store: GraphStore):
        self.gs = graph_store
        self.rules = self._load_rules()
        logger.info("推理引擎初始化完成")

    def _load_rules(self) -> List[Dict]:
        """加载推理规则"""
        return [
            {
                "name": "传递性推理",
                "description": "如果A属于B，B属于C，则A属于C",
                "pattern": "transitive"
            },
            {
                "name": "对称性推理",
                "description": "如果A与B相关，则B与A相关",
                "pattern": "symmetric"
            },
            {
                "name": "组合推理",
                "description": "如果A使用B，B使用C，则A间接依赖C",
                "pattern": "composition"
            },
        ]

    def transitive_reasoning(self, entity: str, relation: str,
                             max_depth: int = 3) -> List[Dict]:
        """传递性推理"""
        if entity not in self.gs.graph:
            return []

        results = []
        visited = set()

        def _dfs(node, path, depth):
            if depth > max_depth or node in visited:
                return
            visited.add(node)

            for _, target, data in self.gs.graph.out_edges(node, data=True):
                if data.get("type") == relation:
                    new_path = path + [target]
                    if len(new_path) > 1:
                        results.append({
                            "path": new_path,
                            "conclusion": f"{entity} -> {target}"
                        })
                    _dfs(target, new_path, depth + 1)

        _dfs(entity, [entity], 0)
        return results

    def symmetric_reasoning(self, entity: str) -> List[Dict]:
        """对称性推理"""
        if entity not in self.gs.graph:
            return []

        results = []
        # 入边
        for source, _, data in self.gs.graph.in_edges(entity, data=True):
            results.append({
                "entity": source,
                "relation": data.get("type", "RELATED_TO")
            })
        # 出边
        for _, target, data in self.gs.graph.out_edges(entity, data=True):
            results.append({
                "entity": target,
                "relation": data.get("type", "RELATED_TO")
            })
        return results

    def composition_reasoning(self, entity: str) -> List[Dict]:
        """组合推理 - 发现间接关系"""
        if entity not in self.gs.graph:
            return []

        results = []
        # A -> B -> C
        for _, b, data1 in self.gs.graph.out_edges(entity, data=True):
            for _, c, data2 in self.gs.graph.out_edges(b, data=True):
                if c != entity:
                    results.append({
                        "source": entity,
                        "path": f"{entity} -> {b} -> {c}",
                        "intermediate": b,
                        "target": c,
                        "relations": [data1.get("type"), data2.get("type")]
                    })
        return results

    def similarity_reasoning(self, entity: str, top_k: int = 5) -> List[Dict]:
        """相似性推理 - 基于结构相似度"""
        if entity not in self.gs.graph:
            return []

        # 获取实体的邻居特征
        entity_profile = self._get_node_profile(entity)

        # 计算与其他实体的相似度
        similarities = []
        for node in self.gs.graph.nodes():
            if node == entity:
                continue
            other_profile = self._get_node_profile(node)
            similarity = self._calculate_similarity(entity_profile, other_profile)
            if similarity > 0:
                similarities.append({
                    "name": node,
                    "type": self.gs.entity_types.get(node, "未知"),
                    "similarity": similarity
                })

        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_k]

    def _get_node_profile(self, node: str) -> Dict:
        """获取节点的特征向量"""
        profile = defaultdict(int)
        for _, target, data in self.gs.graph.out_edges(node, data=True):
            key = f"out_{data.get('type', 'UNKNOWN')}_{self.gs.entity_types.get(target, '未知')}"
            profile[key] += 1
        for source, _, data in self.gs.graph.in_edges(node, data=True):
            key = f"in_{data.get('type', 'UNKNOWN')}_{self.gs.entity_types.get(source, '未知')}"
            profile[key] += 1
        return dict(profile)

    def _calculate_similarity(self, profile1: Dict, profile2: Dict) -> float:
        """计算相似度"""
        keys1 = set(profile1.keys())
        keys2 = set(profile2.keys())
        intersection = keys1 & keys2
        union = keys1 | keys2
        if not union:
            return 0.0
        return len(intersection) / len(union)

    def causal_reasoning(self, entity: str) -> List[Dict]:
        """因果推理 - 发展关系链"""
        if entity not in self.gs.graph:
            return []

        results = []
        visited = set()

        def _dfs(node, chain, depth):
            if depth > 3 or node in visited:
                return
            visited.add(node)

            for _, target, data in self.gs.graph.out_edges(node, data=True):
                rel_type = data.get("type", "")
                if rel_type in ["DEVELOPS", "CREATES", "CAUSES"]:
                    new_chain = chain + [target]
                    results.append({"causal_chain": new_chain})
                    _dfs(target, new_chain, depth + 1)

        _dfs(entity, [entity], 0)
        return results

    def analogy_reasoning(self, entity_a: str, entity_b: str,
                          entity_c: str) -> List[Dict]:
        """类比推理 - A之于B，如C之于？"""
        # 找到A到B的关系类型
        a_relations = set()
        for _, target, data in self.gs.graph.out_edges(entity_a, data=True):
            if target == entity_b:
                a_relations.add(data.get("type"))

        if not a_relations:
            return []

        # 用相同的关系类型找C的类比
        results = []
        for _, target, data in self.gs.graph.out_edges(entity_c, data=True):
            if data.get("type") in a_relations:
                results.append({
                    "analogy": target,
                    "relation": data.get("type"),
                    "pattern": f"{entity_a} --{data.get('type')}--> {entity_b}, "
                              f"{entity_c} --{data.get('type')}--> {target}"
                })
        return results

    def infer_new_relations(self, confidence_threshold: float = 0.7) -> List[Dict]:
        """推断新关系"""
        inferred = []

        # 规则1: 传递性推断
        for node in self.gs.graph.nodes():
            for _, b, d1 in self.gs.graph.out_edges(node, data=True):
                if d1.get("type") == "BELONGS_TO":
                    for _, c, d2 in self.gs.graph.out_edges(b, data=True):
                        if d2.get("type") == "BELONGS_TO":
                            # 检查是否已存在直接关系
                            if not self.gs.graph.has_edge(node, c):
                                inferred.append({
                                    "subject": node,
                                    "predicate": "BELONGS_TO",
                                    "object": c,
                                    "confidence": 0.8,
                                    "reason": "传递性推理"
                                })

        # 规则2: 共同使用推断
        usage_groups = defaultdict(list)
        for u, v, data in self.gs.graph.edges(data=True):
            if data.get("type") == "USES":
                usage_groups[v].append(u)

        for tool, users in usage_groups.items():
            for i, user1 in enumerate(users):
                for user2 in users[i+1:]:
                    if not self.gs.graph.has_edge(user1, user2):
                        inferred.append({
                            "subject": user1,
                            "predicate": "RELATED_TO",
                            "object": user2,
                            "confidence": 0.6,
                            "reason": f"共同使用 {tool}"
                        })

        # 过滤低置信度
        inferred = [i for i in inferred if i["confidence"] >= confidence_threshold]
        logger.info(f"推断出 {len(inferred)} 个新关系")
        return inferred

    def apply_inference(self, confidence_threshold: float = 0.7) -> int:
        """应用推断结果到图谱"""
        inferred = self.infer_new_relations(confidence_threshold)
        count = 0
        for rel in inferred:
            success = self.gs.add_relation(
                rel["subject"], rel["predicate"], rel["object"],
                {"confidence": rel["confidence"], "inferred": True}
            )
            if success:
                count += 1
        logger.info(f"已应用 {count} 个推断关系")
        return count

    def explain(self, entity: str) -> Dict:
        """生成实体的知识解释"""
        entity_info = self.gs.get_entity(entity)
        if not entity_info:
            return {"error": f"未找到实体: {entity}"}

        direct_relations = entity_info.get("relations", [])
        transitive = self.transitive_reasoning(entity, "BELONGS_TO")
        composition = self.composition_reasoning(entity)

        explanation_parts = [f"{entity}是一个{entity_info.get('type', '概念')}。"]

        if direct_relations:
            rel_texts = []
            for rel in direct_relations[:5]:
                rel_texts.append(f"与{rel['target']}有{rel['type']}关系")
            explanation_parts.append("它" + "，".join(rel_texts) + "。")

        if transitive:
            explanation_parts.append(f"通过传递性推理，它属于{transitive[0]['path'][-1]}等上位概念。")

        if composition:
            explanation_parts.append(f"通过组合推理，它与{composition[0]['target']}等有间接关联。")

        return {
            "entity": entity,
            "type": entity_info.get("type"),
            "explanation": "".join(explanation_parts),
            "direct_relations": direct_relations,
            "transitive_inferences": transitive[:3],
            "composition_inferences": composition[:3]
        }


if __name__ == "__main__":
    gs = GraphStore()
    engine = ReasoningEngine(gs)
    print("推理引擎测试完成")
