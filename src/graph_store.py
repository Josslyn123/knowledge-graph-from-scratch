"""图存储模块 - 基于NetworkX的内存图数据库"""
import json
import networkx as nx
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from loguru import logger
from collections import defaultdict


class GraphStore:
    """基于NetworkX的图存储"""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.entity_types = {}  # name -> type
        logger.info("图存储初始化完成")

    def clear(self):
        """清空图"""
        self.graph.clear()
        self.entity_types.clear()

    def add_entity(self, name: str, entity_type: str, properties: Dict = None) -> bool:
        """添加实体节点"""
        if not name or not name.strip():
            return False

        name = name.strip()
        props = properties or {}
        props["name"] = name
        props["type"] = entity_type

        self.graph.add_node(name, **props)
        self.entity_types[name] = entity_type
        return True

    def add_relation(self, subject: str, predicate: str, obj: str,
                     properties: Dict = None) -> bool:
        """添加关系"""
        if not subject or not obj:
            return False

        subject = subject.strip()
        obj = obj.strip()
        props = properties or {}
        props["type"] = predicate

        self.graph.add_edge(subject, obj, **props)
        return True

    def add_triple(self, triple: Dict) -> bool:
        """添加三元组"""
        self.add_entity(triple["subject"], triple.get("subject_type", "概念"))
        self.add_entity(triple["object"], triple.get("object_type", "概念"))
        return self.add_relation(
            triple["subject"],
            triple["predicate"],
            triple["object"],
            {"confidence": triple.get("confidence", 1.0)}
        )

    def batch_add_triples(self, triples: List[Dict]) -> Tuple[int, int]:
        """批量添加三元组"""
        success = 0
        fail = 0
        for triple in triples:
            if self.add_triple(triple):
                success += 1
            else:
                fail += 1
        logger.info(f"批量添加完成: 成功{success}, 失败{fail}")
        return success, fail

    def get_entity(self, name: str) -> Optional[Dict]:
        """获取实体信息"""
        if name not in self.graph:
            return None

        node_data = dict(self.graph.nodes[name])
        relations = []

        # 出边
        for _, target, data in self.graph.out_edges(name, data=True):
            relations.append({
                "type": data.get("type", "RELATED_TO"),
                "target": target,
                "direction": "outgoing"
            })

        # 入边
        for source, _, data in self.graph.in_edges(name, data=True):
            relations.append({
                "type": data.get("type", "RELATED_TO"),
                "target": source,
                "direction": "incoming"
            })

        return {
            "name": name,
            "type": node_data.get("type", "未知"),
            "properties": node_data,
            "relations": relations
        }

    def get_neighbors(self, name: str, depth: int = 1) -> Dict:
        """获取邻居节点"""
        if name not in self.graph:
            return {"center": name, "neighbors": []}

        neighbors = []
        visited = set()

        def _dfs(node, current_depth):
            if current_depth > depth or node in visited:
                return
            visited.add(node)
            for neighbor in self.graph.neighbors(node):
                if neighbor not in visited:
                    neighbors.append({
                        "name": neighbor,
                        "type": self.entity_types.get(neighbor, "未知"),
                        "depth": current_depth
                    })
                    _dfs(neighbor, current_depth + 1)
            # 也检查入边
            for predecessor in self.graph.predecessors(node):
                if predecessor not in visited:
                    neighbors.append({
                        "name": predecessor,
                        "type": self.entity_types.get(predecessor, "未知"),
                        "depth": current_depth
                    })
                    _dfs(predecessor, current_depth + 1)

        _dfs(name, 1)
        return {"center": name, "neighbors": neighbors}

    def find_path(self, start: str, end: str, max_depth: int = 5) -> List[List[str]]:
        """查找路径"""
        if start not in self.graph or end not in self.graph:
            return []

        try:
            # 使用NetworkX的最短路径
            paths = list(nx.all_simple_paths(
                self.graph, start, end, cutoff=max_depth
            ))
            return paths[:10]  # 最多返回10条路径
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []

    def search_entities(self, keyword: str, limit: int = 20) -> List[Dict]:
        """搜索实体"""
        results = []
        for node in self.graph.nodes():
            if keyword in node:
                results.append({
                    "name": node,
                    "type": self.entity_types.get(node, "未知")
                })
                if len(results) >= limit:
                    break
        return results

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        type_stats = defaultdict(int)
        for name, etype in self.entity_types.items():
            type_stats[etype] += 1

        rel_stats = defaultdict(int)
        for _, _, data in self.graph.edges(data=True):
            rel_stats[data.get("type", "UNKNOWN")] += 1

        return {
            "node_count": self.graph.number_of_nodes(),
            "relation_count": self.graph.number_of_edges(),
            "entity_types": dict(type_stats),
            "relation_types": dict(rel_stats)
        }

    def get_most_connected(self, limit: int = 10) -> List[Dict]:
        """获取连接最多的实体"""
        degrees = []
        for node in self.graph.nodes():
            in_degree = self.graph.in_degree(node)
            out_degree = self.graph.out_degree(node)
            total = in_degree + out_degree
            degrees.append({
                "name": node,
                "type": self.entity_types.get(node, "未知"),
                "connections": total,
                "in_degree": in_degree,
                "out_degree": out_degree
            })

        degrees.sort(key=lambda x: x["connections"], reverse=True)
        return degrees[:limit]

    def query_by_type(self, entity_type: str, limit: int = 50) -> List[Dict]:
        """按类型查询实体"""
        results = []
        for name, etype in self.entity_types.items():
            if etype == entity_type:
                results.append({"name": name, "type": etype})
                if len(results) >= limit:
                    break
        return results

    def get_subgraph(self, center: str, depth: int = 2) -> Dict:
        """获取子图"""
        if center not in self.graph:
            return {"center": center, "nodes": [], "relations": []}

        # BFS获取子图节点
        visited = set()
        queue = [(center, 0)]
        nodes = []

        while queue:
            node, d = queue.pop(0)
            if node in visited or d > depth:
                continue
            visited.add(node)
            nodes.append({
                "name": node,
                "type": self.entity_types.get(node, "未知")
            })

            for neighbor in self.graph.neighbors(node):
                if neighbor not in visited:
                    queue.append((neighbor, d + 1))
            for predecessor in self.graph.predecessors(node):
                if predecessor not in visited:
                    queue.append((predecessor, d + 1))

        # 获取子图关系
        relations = []
        for u, v, data in self.graph.subgraph(visited).edges(data=True):
            relations.append({
                "source": u,
                "target": v,
                "type": data.get("type", "RELATED_TO")
            })

        return {"center": center, "nodes": nodes, "relations": relations}

    def export_to_json(self, output_path: str) -> Dict:
        """导出为JSON"""
        nodes = []
        for node in self.graph.nodes():
            nodes.append({
                "id": node,
                "name": node,
                "type": self.entity_types.get(node, "未知")
            })

        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "type": data.get("type", "RELATED_TO")
            })

        data = {"nodes": nodes, "edges": edges}

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"图谱已导出: {output_path} ({len(nodes)}节点, {len(edges)}关系)")
        return data

    def import_from_json(self, json_path: str):
        """从JSON导入"""
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for node in data.get("nodes", []):
            self.add_entity(node["name"], node.get("type", "概念"))

        for edge in data.get("edges", []):
            self.add_relation(edge["source"], edge["type"], edge["target"])

        logger.info(f"导入完成: {len(data.get('nodes', []))}节点, {len(data.get('edges', []))}关系")

    def save(self, path: str):
        """保存图到文件"""
        data = {
            "nodes": [],
            "edges": []
        }
        for node in self.graph.nodes():
            data["nodes"].append({
                "name": node,
                "type": self.entity_types.get(node, "未知"),
                "properties": dict(self.graph.nodes[node])
            })
        for u, v, d in self.graph.edges(data=True):
            data["edges"].append({
                "source": u,
                "target": v,
                "properties": d
            })

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"图已保存: {path}")

    def load(self, path: str):
        """从文件加载图"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.clear()
        for node in data.get("nodes", []):
            self.add_entity(node["name"], node.get("type", "概念"),
                          node.get("properties", {}))
        for edge in data.get("edges", []):
            self.add_relation(edge["source"],
                            edge["properties"].get("type", "RELATED_TO"),
                            edge["target"],
                            edge.get("properties", {}))
        logger.info(f"图已加载: {path}")
