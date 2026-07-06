"""知识图谱项目 - 主程序入口"""
import sys
import json
from pathlib import Path
from loguru import logger

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from config import *
from src.pdf_extractor import extract_pdf_content
from src.nlp_processor import NLPProcessor
from src.graph_store import GraphStore


def setup_logging():
    """配置日志"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger.add(LOG_DIR / "app.log", rotation="10 MB", level=LOG_LEVEL)


def step1_extract_pdf():
    """步骤1: 提取PDF内容"""
    logger.info("=" * 50)
    logger.info("步骤1: 提取PDF内容")
    logger.info("=" * 50)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    result = extract_pdf_content(str(PDF_PATH), str(OUTPUT_DIR))

    logger.info(f"PDF元数据: {result['metadata']}")
    logger.info(f"提取段落数: {len(result['paragraphs'])}")
    logger.info(f"章节数: {len(result['chapters'])}")

    return result


def step2_nlp_process(text_data):
    """步骤2: NLP处理 - 实体识别和关系抽取"""
    logger.info("=" * 50)
    logger.info("步骤2: NLP处理")
    logger.info("=" * 50)

    processor = NLPProcessor()

    paragraphs = text_data.get("paragraphs", [])
    if not paragraphs:
        paragraphs = [text_data.get("full_text", "")]

    result = processor.process_paragraphs(paragraphs)

    # 保存结果
    output_file = OUTPUT_DIR / "nlp_result.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    logger.info(f"识别实体数: {result['entity_count']}")
    logger.info(f"抽取关系数: {result['relation_count']}")
    logger.info(f"三元组数: {result['triple_count']}")
    logger.info(f"NLP结果已保存: {output_file}")

    return result


def step3_build_graph(nlp_result):
    """步骤3: 构建知识图谱"""
    logger.info("=" * 50)
    logger.info("步骤3: 构建知识图谱")
    logger.info("=" * 50)

    gs = GraphStore()

    # 添加三元组
    triples = nlp_result.get("triples", [])
    if triples:
        success, fail = gs.batch_add_triples(triples)
        logger.info(f"三元组导入: 成功{success}, 失败{fail}")

    # 获取统计
    stats = gs.get_statistics()
    logger.info(f"图谱统计: {stats}")

    # 导出JSON
    gs.export_to_json(str(OUTPUT_DIR / "graph.json"))

    # 保存图数据
    gs.save(str(OUTPUT_DIR / "graph_data.json"))

    return stats


def step4_run_chat():
    """步骤4: 启动智能问答服务"""
    logger.info("=" * 50)
    logger.info("步骤4: 启动智能问答服务")
    logger.info("=" * 50)

    import uvicorn
    from src.chat_api import app

    logger.info(f"智能问答服务启动: http://{API_HOST}:{API_PORT}")
    logger.info(f"API文档: http://{API_HOST}:{API_PORT}/docs")

    uvicorn.run(app, host=API_HOST, port=API_PORT)


def main():
    """主函数"""
    setup_logging()
    logger.info("知识图谱项目启动")

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "extract":
            step1_extract_pdf()

        elif command == "process":
            with open(OUTPUT_DIR / "full_text.txt", "r", encoding="utf-8") as f:
                text = f.read()
            text_data = {"full_text": text, "paragraphs": text.split("\n\n")}
            step2_nlp_process(text_data)

        elif command == "build":
            with open(OUTPUT_DIR / "nlp_result.json", "r", encoding="utf-8") as f:
                nlp_result = json.load(f)
            step3_build_graph(nlp_result)

        elif command == "serve":
            step4_run_chat()

        elif command == "all":
            text_data = step1_extract_pdf()
            nlp_result = step2_nlp_process(text_data)
            step3_build_graph(nlp_result)
            step4_run_chat()

        else:
            print(f"未知命令: {command}")
            print("可用命令: extract, process, build, serve, all")
    else:
        print("用法: python main.py <命令>")
        print("命令:")
        print("  extract  - 提取PDF内容")
        print("  process  - NLP处理")
        print("  build    - 构建知识图谱")
        print("  serve    - 启动智能问答服务")
        print("  all      - 执行全部步骤")


if __name__ == "__main__":
    main()
