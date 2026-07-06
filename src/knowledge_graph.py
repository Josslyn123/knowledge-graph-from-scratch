"""知识图谱构建与存储模块"""
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from loguru import logger
from neo4j import GraphDatabase


class KnowledgeGraph:
    """知识图谱管理器"""

    def __init__(self, uri: str = "bolt://localhost:7687",
                 user: str = "neo4j", password: str = "knowledge_graph_2024"):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        self._connect()

    def _connect(self):
        """连接Neo4j数据库"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self.driver.verify_connectivity()
            logger.info(f"已连接Neo4j: {self.uri}")
        except Exception as e:
            logger.error(f"连接Neo4j失败: {e}")
            raise

    def close(self):
        """关闭连接"""
        if self.driver:
            self.driver.close()

    def clear(self):
        """清空数据库"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("已清空数据库")

    def create_indexes(self):
        """创建索引"""
        indexes = [
            "CREATE INDEX entity_name IF NOT EXISTS FOR (n:Entity) ON (n.name)",
            "CREATE INDEX entity_type IF NOT EXISTS FOR (n:Entity) ON (n.type)",
            "CREATE INDEX concept_name IF NOT EXISTS FOR (n:Concept) ON (n.name)",
            "CREATE INDEX technology_name IF NOT EXISTS FOR (n:Technology) ON (n.name)",
            "CREATE INDEX tool_name IF NOT EXISTS FOR (n:Tool) ON (n.name)",
            "CREATE INDEX person_name IF NOT EXISTS FOR (n:Person) ON (n.name)",
            "CREATE INDEX organization_name IF NOT EXISTS FOR (n:Organization) ON (n.name)",
        ]
        with self.driver.session() as session:
            for index in indexes:
                try:
                    session.run(index)
                except Exception as e:
                    logger.warning(f"创建索引失败: {e}")
        logger.info("索引创建完成")

    def add_entity(self, name: str, entity_type: str, properties: Dict = None) -> bool:
        """添加实体节点"""
        if not name or not name.strip():
            return False

        label = self._type_to_label(entity_type)
        props = properties or {}
        props["name"] = name.strip()
        props["type"] = entity_type

        query = f"""
        MERGE (n:{label} {{name: $name}})
        SET n += $props
        RETURN n
        """

        with self.driver.session() as session:
            try:
                result = session.run(query, name=name.strip(), props=props)
                return result.single() is not None
            except Exception as e:
                logger.error(f"添加实体失败 [{name}]: {e}")
                return False

    def add_relation(self, subject: str, predicate: str, obj: str,
                     properties: Dict = None) -> bool:
        """添加关系"""
        if not subject or not obj:
            return False

        rel_type = self._predicate_to_rel_type(predicate)
        props = properties or {}

        query = f"""
        MATCH (a:Entity {{name: $subject}})
        MATCH (b:Entity {{name: $object}})
        MERGE (a)-[r:{rel_type}]->(b)
        SET r += $props
        RETURN r
        """

        with self.driver.session() as session:
            try:
                result = session.run(query, subject=subject.strip(),
                                     object=obj.strip(), props=props)
                return result.single() is not None
            except Exception as e:
                logger.error(f"添加关系失败 [{subject}-{predicate}-{obj}]: {e}")
                return False

    def add_triple(self, triple: Dict) -> bool:
        """添加三元组"""
        # 先添加实体
        self.add_entity(triple["subject"], triple.get("subject_type", "概念"))
        self.add_entity(triple["object"], triple.get("object_type", "概念"))

        # 再添加关系
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

        for i, triple in enumerate(triples):
            if self.add_triple(triple):
                success += 1
            else:
                fail += 1

            if (i + 1) % 100 == 0:
                logger.info(f"已处理 {i+1}/{len(triples)} 三元组")

        logger.info(f"批量添加完成: 成功{success}, 失败{fail}")
        return success, fail

    def _type_to_label(self, entity_type: str) -> str:
        """实体类型转Neo4j标签"""
        mapping = {
            "概念": "Concept",
            "技术": "Technology",
            "工具": "Tool",
            "方法": "Method",
            "人物": "Person",
            "组织": "Organization",
            "事件": "Event",
            "应用": "Application",
        }
        return mapping.get(entity_type, "Entity")

    def _predicate_to_rel_type(self, predicate: str) -> str:
        """谓词转Neo4j关系类型"""
        mapping = {
            "属于": "BELONGS_TO",
            "包含": "CONTAINS",
            "使用": "USES",
            "依赖": "DEPENDS_ON",
            "对比": "COMPARES_WITH",
            "创建": "CREATED",
            "发展": "DEVELOPS",
            "应用": "APPLIES_TO",
            "相关": "RELATED_TO",
        }
        return mapping.get(predicate, "RELATED_TO")

    def get_entity(self, name: str) -> Optional[Dict]:
        """获取实体信息"""
        query = """
        MATCH (n:Entity {name: $name})
        OPTIONAL MATCH (n)-[r]-(m)
        RETURN n, collect({type: type(r), target: m.name}) as relations
        """
        with self.driver.session() as session:
            result = session.run(query, name=name)
            record = result.single()
            if record:
                node = record["n"]
                return {
                    "name": node["name"],
                    "type": node.get("type", "未知"),
                    "properties": dict(node),
                    "relations": record["relations"]
                }
        return None

    def get_neighbors(self, name: str, depth: int = 1) -> Dict:
        """获取邻居节点"""
        query = f"""
        MATCH path = (n:Entity {{name: $name}})-[*1..{depth}]-(m)
        RETURN path
        LIMIT 50
        """
        with self.driver.session() as session:
            result = session.run(query, name=name)
            neighbors = []
            for record in result:
                path = record["path"]
                for node in path.nodes:
                    neighbors.append({
                        "name": node["name"],
                        "type": node.get("type", "未知")
                    })
            return {"center": name, "neighbors": neighbors}

    def find_path(self, start: str, end: str, max_depth: int = 5) -> List[List[str]]:
        """查找两个实体间的路径"""
        query = f"""
        MATCH path = shortestPath(
            (a:Entity {{name: $start}})-[*..{max_depth}]-(b:Entity {{name: $end}})
        )
        RETURN [node IN nodes(path) | node.name] as path
        """
        with self.driver.session() as session:
            result = session.run(query, start=start, end=end)
            paths = []
            for record in result:
                paths.append(record["path"])
            return paths

    def search_entities(self, keyword: str, limit: int = 20) -> List[Dict]:
        """搜索实体"""
        query = """
        MATCH (n:Entity)
        WHERE n.name CONTAINS $keyword
        RETURN n.name as name, n.type as type
        LIMIT $limit
        """
        with self.driver.session() as session:
            result = session.run(query, keyword=keyword, limit=limit)
            return [{"name": r["name"], "type": r["type"]} for r in result]

    def get_statistics(self) -> Dict:
        """获取图谱统计信息"""
        with self.driver.session() as session:
            node_count = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
            rel_count = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]

            # 按类型统计实体
            type_stats = {}
            result = session.run("""
                MATCH (n:Entity)
                RETURN n.type as type, count(n) as count
                ORDER BY count DESC
            """)
            for record in result:
                type_stats[record["type"]] = record["count"]

            # 按类型统计关系
            rel_stats = {}
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count
                ORDER BY count DESC
            """)
            for record in result:
                rel_stats[record["type"]] = record["count"]

        return {
            "node_count": node_count,
            "relation_count": rel_count,
            "entity_types": type_stats,
            "relation_types": rel_stats
        }

    def export_to_json(self, output_path: str):
        """导出图谱为JSON"""
        with self.driver.session() as session:
            # 获取所有节点
            nodes = []
            result = session.run("MATCH (n:Entity) RETURN n")
            for record in result:
                node = record["n"]
                nodes.append({
                    "id": node["name"],
                    "name": node["name"],
                    "type": node.get("type", "未知")
                })

            # 获取所有关系
            edges = []
            result = session.run("""
                MATCH (a:Entity)-[r]->(b:Entity)
                RETURN a.name as source, type(r) as type, b.name as target
            """)
            for record in result:
                edges.append({
                    "source": record["source"],
                    "target": record["target"],
                    "type": record["type"]
                })

        data = {"nodes": nodes, "edges": edges}
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"图谱已导出: {output_path} ({len(nodes)}节点, {len(edges)}关系)")
        return data

    def import_from_json(self, json_path: str):
        """从JSON导入图谱"""
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 导入节点
        for node in data.get("nodes", []):
            self.add_entity(node["name"], node.get("type", "概念"))

        # 导入关系
        for edge in data.get("edges", []):
            self.add_relation(edge["source"], edge["type"], edge["target"])

        logger.info(f"导入完成: {len(data.get('nodes', []))}节点, {len(data.get('edges', []))}关系")


if __name__ == "__main__":
    kg = KnowledgeGraph()
    kg.create_indexes()

    # 测试添加
    kg.add_entity("知识图谱", "概念")
    kg.add_entity("Neo4j", "工具")
    kg.add_relation("Neo4j", "用于", "知识图谱")

    stats = kg.get_statistics()
    print(f"统计: {stats}")

    kg.close()
