"""NLP处理模块 - 实体识别和关系抽取"""
import re
import jieba
import jieba.posseg as pseg
from typing import List, Dict, Tuple, Set
from loguru import logger
from collections import defaultdict


# 知识图谱相关领域词典
DOMAIN_TERMS = [
    "知识图谱", "实体识别", "关系抽取", "命名实体", "自然语言处理",
    "深度学习", "机器学习", "神经网络", "图数据库", "Neo4j",
    "本体", "语义网络", "RDF", "OWL", "SPARQL",
    "信息抽取", "文本挖掘", "词向量", "预训练模型", "BERT",
    "TransE", "TransR", "知识表示", "知识推理", "知识融合",
    "三元组", "属性", "关系", "实体", "概念",
    "Schema", "数据模型", "图谱构建", "图谱应用",
]

# 初始化jieba词典
for term in DOMAIN_TERMS:
    jieba.add_word(term)


class NLPProcessor:
    """NLP处理器 - 实体识别和关系抽取"""

    def __init__(self):
        self.entity_patterns = self._build_entity_patterns()
        self.relation_patterns = self._build_relation_patterns()
        logger.info("NLP处理器初始化完成")

    def _build_entity_patterns(self) -> Dict[str, List[str]]:
        """构建实体识别模式"""
        return {
            "技术": [
                r"[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*",  # 英文技术名
                r"[一-龥]{2,8}(?:技术|算法|模型|方法|框架|系统)",
            ],
            "工具": [
                r"[A-Z][a-zA-Z]+(?:\.[a-zA-Z]+)*",  # 工具名
                r"[一-龥]{2,6}(?:工具|平台|软件|库)",
            ],
            "概念": [
                r"[一-龥]{2,10}(?:图谱|网络|模型|表示|知识)",
                r"(?:知识|语义|信息|数据)[一-龥]{2,6}",
            ],
            "人物": [
                r"[一-龥]{2,4}(?:教授|博士|先生|老师)",
                r"[A-Z][a-z]+\s+[A-Z][a-z]+",  # 英文人名
            ],
            "组织": [
                r"[一-龥]{2,10}(?:大学|公司|研究院|实验室|协会|联盟)",
                r"(?:Google|Microsoft|Facebook|Amazon|Apple|Baidu|Alibaba|Tencent)",
            ],
        }

    def _build_relation_patterns(self) -> List[Tuple[str, str, str]]:
        """构建关系抽取模式 (主语模式, 关系, 宾语模式)"""
        return [
            (r"(.+?)(?:是|为|属于)", "属于", r"(.+?)(?:的|。|，|；)"),
            (r"(.+?)(?:包含|包括|涵盖)", "包含", r"(.+?)(?:的|。|，|；)"),
            (r"(.+?)(?:使用|采用|利用|基于)", "使用", r"(.+?)(?:进行|来|。|，)"),
            (r"(.+?)(?:依赖|基于|建立在)", "依赖", r"(.+?)(?:之上|。|，)"),
            (r"(.+?)(?:创建|提出|开发|发明)", "创建", r"(.+?)(?:了|。|，)"),
            (r"(.+?)(?:应用于|用于|用在)", "应用", r"(.+?)(?:中|领域|。|，)"),
        ]

    def extract_entities(self, text: str) -> List[Dict]:
        """提取实体"""
        entities = []
        seen = set()

        # 方法1: 基于词性标注
        words = pseg.cut(text)
        for word, flag in words:
            if len(word) >= 2 and word not in seen:
                entity_type = self._get_entity_type(word, flag)
                if entity_type:
                    entities.append({
                        "name": word,
                        "type": entity_type,
                        "source": "pos_tag"
                    })
                    seen.add(word)

        # 方法2: 基于正则模式
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    name = match.group().strip()
                    if len(name) >= 2 and name not in seen:
                        entities.append({
                            "name": name,
                            "type": entity_type,
                            "source": "regex"
                        })
                        seen.add(name)

        # 方法3: 基于领域词典
        for term in DOMAIN_TERMS:
            if term in text and term not in seen:
                entities.append({
                    "name": term,
                    "type": "概念",
                    "source": "dict"
                })
                seen.add(term)

        return entities

    def _get_entity_type(self, word: str, flag: str) -> str:
        """根据词性判断实体类型"""
        type_mapping = {
            "nr": "人物",
            "ns": "地点",
            "nt": "组织",
            "nz": "概念",
            "vn": "技术",
            "n": "概念",
        }
        return type_mapping.get(flag, None)

    def extract_relations(self, text: str, entities: List[Dict]) -> List[Dict]:
        """抽取实体间关系"""
        relations = []
        entity_names = {e["name"] for e in entities}

        # 方法1: 基于模式匹配
        for subj_pattern, relation, obj_pattern in self.relation_patterns:
            combined_pattern = f"{subj_pattern}{relation}{obj_pattern}"
            matches = re.finditer(combined_pattern, text)
            for match in matches:
                subj = match.group(1).strip() if match.group(1) else ""
                obj = match.group(2).strip() if match.group(2) else ""
                if subj in entity_names and obj in entity_names:
                    relations.append({
                        "subject": subj,
                        "predicate": relation,
                        "object": obj
                    })

        # 方法2: 基于共现关系 (在同一句中出现的实体)
        sentences = re.split(r'[。！？\n]', text)
        for sentence in sentences:
            sentence_entities = [e for e in entities if e["name"] in sentence]
            for i, e1 in enumerate(sentence_entities):
                for e2 in sentence_entities[i+1:]:
                    # 跳过同类型实体的共现关系
                    if e1["type"] != e2["type"]:
                        relations.append({
                            "subject": e1["name"],
                            "predicate": "相关",
                            "object": e2["name"],
                            "confidence": 0.5
                        })

        return relations

    def extract_triples(self, text: str) -> List[Dict]:
        """提取三元组 (主语, 谓语, 宾语)"""
        triples = []

        # 提取实体
        entities = self.extract_entities(text)

        # 提取关系
        relations = self.extract_relations(text, entities)

        # 构建三元组
        for rel in relations:
            triples.append({
                "subject": rel["subject"],
                "subject_type": self._find_entity_type(entities, rel["subject"]),
                "predicate": rel["predicate"],
                "object": rel["object"],
                "object_type": self._find_entity_type(entities, rel["object"]),
                "confidence": rel.get("confidence", 0.8)
            })

        return triples

    def _find_entity_type(self, entities: List[Dict], name: str) -> str:
        """查找实体类型"""
        for entity in entities:
            if entity["name"] == name:
                return entity["type"]
        return "未知"

    def process_text(self, text: str) -> Dict:
        """处理文本，返回完整的NLP分析结果"""
        entities = self.extract_entities(text)
        relations = self.extract_relations(text, entities)
        triples = self.extract_triples(text)

        return {
            "entities": entities,
            "relations": relations,
            "triples": triples,
            "entity_count": len(entities),
            "relation_count": len(relations),
            "triple_count": len(triples)
        }

    def process_paragraphs(self, paragraphs: List[str]) -> Dict:
        """批量处理段落"""
        all_entities = []
        all_relations = []
        all_triples = []
        seen_entities = set()
        seen_relations = set()

        for i, para in enumerate(paragraphs):
            result = self.process_text(para)

            # 去重合并实体
            for entity in result["entities"]:
                key = entity["name"]
                if key not in seen_entities:
                    all_entities.append(entity)
                    seen_entities.add(key)

            # 去重合并关系
            for rel in result["relations"]:
                key = (rel["subject"], rel["predicate"], rel["object"])
                if key not in seen_relations:
                    all_relations.append(rel)
                    seen_relations.add(key)

            for triple in result["triples"]:
                all_triples.append(triple)

            if (i + 1) % 100 == 0:
                logger.info(f"已处理 {i+1}/{len(paragraphs)} 段落")

        return {
            "entities": all_entities,
            "relations": all_relations,
            "triples": all_triples,
            "entity_count": len(all_entities),
            "relation_count": len(all_relations),
            "triple_count": len(all_triples)
        }


if __name__ == "__main__":
    processor = NLPProcessor()
    test_text = """
    知识图谱是一种语义网络，用于表示实体及其关系。
    Neo4j是一种常用的图数据库，广泛应用于知识图谱存储。
    自然语言处理技术可以用于知识抽取。
    """
    result = processor.process_text(test_text)
    print(f"实体: {result['entity_count']}")
    print(f"关系: {result['relation_count']}")
    for e in result["entities"]:
        print(f"  - {e['name']} ({e['type']})")
