"""数据集构建模块 - 生成标准格式数据集"""
import json
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger
import csv


class DatasetBuilder:
    """数据集构建器"""

    def __init__(self, nlp_result_path: str, output_dir: str):
        self.nlp_result_path = Path(nlp_result_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 加载NLP结果
        with open(self.nlp_result_path, "r", encoding="utf-8") as f:
            self.nlp_result = json.load(f)

        logger.info(f"加载NLP结果: {self.nlp_result['entity_count']}实体, "
                    f"{self.nlp_result['relation_count']}关系, "
                    f"{self.nlp_result['triple_count']}三元组")

    def build_entity_dataset(self) -> List[Dict]:
        """构建实体数据集"""
        entities = self.nlp_result.get("entities", [])

        # 去重并统计
        entity_map = {}
        for entity in entities:
            name = entity["name"]
            if name not in entity_map:
                entity_map[name] = {
                    "id": f"E{len(entity_map):05d}",
                    "name": name,
                    "type": entity["type"],
                    "source": entity.get("source", "unknown"),
                    "count": 1
                }
            else:
                entity_map[name]["count"] += 1

        entity_list = list(entity_map.values())
        logger.info(f"实体数据集: {len(entity_list)}个实体")
        return entity_list

    def build_relation_dataset(self) -> List[Dict]:
        """构建关系数据集"""
        relations = self.nlp_result.get("relations", [])

        # 去重并统计
        relation_map = {}
        for rel in relations:
            key = (rel["subject"], rel["predicate"], rel["object"])
            if key not in relation_map:
                relation_map[key] = {
                    "id": f"R{len(relation_map):05d}",
                    "subject": rel["subject"],
                    "predicate": rel["predicate"],
                    "object": rel["object"],
                    "confidence": rel.get("confidence", 1.0),
                    "count": 1
                }
            else:
                relation_map[key]["count"] += 1

        relation_list = list(relation_map.values())
        logger.info(f"关系数据集: {len(relation_list)}个关系")
        return relation_list

    def build_triple_dataset(self) -> List[Dict]:
        """构建三元组数据集"""
        triples = self.nlp_result.get("triples", [])
        logger.info(f"三元组数据集: {len(triples)}个三元组")
        return triples

    def build_knowledge_graph_dataset(self) -> Dict:
        """构建完整的知识图谱数据集"""
        entities = self.build_entity_dataset()
        relations = self.build_relation_dataset()
        triples = self.build_triple_dataset()

        dataset = {
            "metadata": {
                "name": "从零构建知识图谱 - 知识图谱数据集",
                "description": "基于《从零构建知识图谱》书籍内容构建的多维度知识图谱数据集",
                "version": "1.0.0",
                "entity_count": len(entities),
                "relation_count": len(relations),
                "triple_count": len(triples),
                "entity_types": self._count_types(entities, "type"),
                "relation_types": self._count_types(relations, "predicate")
            },
            "entities": entities,
            "relations": relations,
            "triples": triples
        }

        return dataset

    def _count_types(self, items: List[Dict], key: str) -> Dict[str, int]:
        """统计类型分布"""
        counts = {}
        for item in items:
            t = item.get(key, "未知")
            counts[t] = counts.get(t, 0) + 1
        return counts

    def save_json(self, data: Any, filename: str):
        """保存为JSON格式"""
        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"已保存: {filepath}")
        return filepath

    def save_csv(self, data: List[Dict], filename: str):
        """保存为CSV格式"""
        if not data:
            return

        filepath = self.output_dir / filename
        keys = data[0].keys()

        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)

        logger.info(f"已保存: {filepath}")
        return filepath

    def save_triples_for_training(self, triples: List[Dict], filename: str):
        """保存为训练格式的三元组文件"""
        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            for triple in triples:
                # TransE格式: head \t relation \t tail
                f.write(f"{triple['subject']}\t{triple['predicate']}\t{triple['object']}\n")
        logger.info(f"已保存训练三元组: {filepath}")
        return filepath

    def build_all(self):
        """构建所有数据集"""
        logger.info("=" * 50)
        logger.info("开始构建数据集")
        logger.info("=" * 50)

        # 1. 完整知识图谱数据集
        kg_dataset = self.build_knowledge_graph_dataset()
        self.save_json(kg_dataset, "knowledge_graph_dataset.json")

        # 2. 实体数据集
        entities = self.build_entity_dataset()
        self.save_json(entities, "entities.json")
        self.save_csv(entities, "entities.csv")

        # 3. 关系数据集
        relations = self.build_relation_dataset()
        self.save_json(relations, "relations.json")
        self.save_csv(relations, "relations.csv")

        # 4. 三元组数据集
        triples = self.build_triple_dataset()
        self.save_json(triples, "triples.json")
        self.save_csv(triples, "triples.csv")

        # 5. 训练用三元组（TransE格式）
        self.save_triples_for_training(triples, "triples_train.txt")

        # 6. 按类型分类的数据集
        self._build_typed_datasets(entities, relations)

        # 7. 数据集统计报告
        self._build_statistics_report(kg_dataset)

        logger.info("=" * 50)
        logger.info("数据集构建完成!")
        logger.info("=" * 50)

    def _build_typed_datasets(self, entities: List[Dict], relations: List[Dict]):
        """按类型构建分类数据集"""
        typed_dir = self.output_dir / "by_type"
        typed_dir.mkdir(exist_ok=True)

        # 按实体类型分组
        entity_by_type = {}
        for entity in entities:
            t = entity["type"]
            if t not in entity_by_type:
                entity_by_type[t] = []
            entity_by_type[t].append(entity)

        for etype, elist in entity_by_type.items():
            self.save_json(elist, f"by_type/entities_{etype}.json")

        # 按关系类型分组
        relation_by_type = {}
        for rel in relations:
            t = rel["predicate"]
            if t not in relation_by_type:
                relation_by_type[t] = []
            relation_by_type[t].append(rel)

        for rtype, rlist in relation_by_type.items():
            self.save_json(rlist, f"by_type/relations_{rtype}.json")

        logger.info(f"已生成 {len(entity_by_type)} 种实体类型, {len(relation_by_type)} 种关系类型的数据集")

    def _build_statistics_report(self, dataset: Dict):
        """生成统计报告"""
        report = {
            "dataset_name": dataset["metadata"]["name"],
            "total_entities": dataset["metadata"]["entity_count"],
            "total_relations": dataset["metadata"]["relation_count"],
            "total_triples": dataset["metadata"]["triple_count"],
            "entity_type_distribution": dataset["metadata"]["entity_types"],
            "relation_type_distribution": dataset["metadata"]["relation_types"],
            "files_generated": [
                "knowledge_graph_dataset.json - 完整知识图谱数据集",
                "entities.json/csv - 实体数据集",
                "relations.json/csv - 关系数据集",
                "triples.json/csv - 三元组数据集",
                "triples_train.txt - TransE训练格式三元组",
                "by_type/ - 按类型分类的数据集",
                "statistics.json - 统计报告"
            ]
        }

        self.save_json(report, "statistics.json")

        # 打印报告
        print("\n" + "=" * 60)
        print("[Dataset Statistics Report]")
        print("=" * 60)
        print(f"Dataset Name: {report['dataset_name']}")
        print(f"Total Entities: {report['total_entities']}")
        print(f"Total Relations: {report['total_relations']}")
        print(f"Total Triples: {report['total_triples']}")
        print("\nEntity Type Distribution:")
        for etype, count in sorted(report['entity_type_distribution'].items(),
                                     key=lambda x: x[1], reverse=True):
            print(f"   - {etype}: {count}")
        print("\nRelation Type Distribution:")
        for rtype, count in sorted(report['relation_type_distribution'].items(),
                                     key=lambda x: x[1], reverse=True):
            print(f"   - {rtype}: {count}")
        print("\nGenerated Files:")
        for f in report['files_generated']:
            print(f"   [OK] {f}")
        print("=" * 60)


if __name__ == "__main__":
    import sys
    nlp_result = sys.argv[1] if len(sys.argv) > 1 else "../output/nlp_result.json"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "../dataset"

    builder = DatasetBuilder(nlp_result, output_dir)
    builder.build_all()
