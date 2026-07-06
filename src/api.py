"""Web API模块 - FastAPI接口"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from loguru import logger
from pathlib import Path

from .graph_store import GraphStore
from .query_engine import QueryEngine
from .reasoning_engine import ReasoningEngine

app = FastAPI(
    title="知识图谱 API",
    description="从零构建知识图谱 - 查询与推理引擎",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局实例
gs = None
query_engine = None
reasoning_engine = None

# 图数据文件路径
GRAPH_DATA_PATH = Path(__file__).parent.parent / "output" / "graph_data.json"


class EntityRequest(BaseModel):
    name: str
    type: str = "概念"
    properties: Dict = {}


class RelationRequest(BaseModel):
    subject: str
    predicate: str
    object: str
    properties: Dict = {}


class TripleRequest(BaseModel):
    subject: str
    subject_type: str = "概念"
    predicate: str
    object: str
    object_type: str = "概念"
    confidence: float = 1.0


class QueryRequest(BaseModel):
    question: str


class BatchTripleRequest(BaseModel):
    triples: List[TripleRequest]


@app.on_event("startup")
async def startup():
    """启动时初始化"""
    global gs, query_engine, reasoning_engine
    try:
        gs = GraphStore()

        # 加载已有的图数据
        if GRAPH_DATA_PATH.exists():
            gs.load(str(GRAPH_DATA_PATH))
            stats = gs.get_statistics()
            logger.info(f"已加载图数据: {stats['node_count']}节点, {stats['relation_count']}关系")
        else:
            logger.warning(f"图数据文件不存在: {GRAPH_DATA_PATH}")

        query_engine = QueryEngine(gs)
        reasoning_engine = ReasoningEngine(gs)
        logger.info("API启动完成")
    except Exception as e:
        logger.error(f"API启动失败: {e}")


@app.get("/", response_class=HTMLResponse)
async def root():
    """首页 - 交互式查询界面"""
    return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>知识图谱查询系统</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .card h2 {
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        .search-box {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        input[type="text"] {
            flex: 1;
            padding: 15px 20px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 10px;
            outline: none;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus {
            border-color: #667eea;
        }
        button {
            padding: 15px 30px;
            font-size: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .btn-group {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }
        .btn-small {
            padding: 8px 16px;
            font-size: 14px;
            background: #f0f0f0;
            color: #333;
            border-radius: 20px;
        }
        .btn-small:hover {
            background: #667eea;
            color: white;
        }
        .result-box {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            min-height: 100px;
            max-height: 500px;
            overflow-y: auto;
        }
        .result-box pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: "Consolas", "Monaco", monospace;
            font-size: 14px;
            line-height: 1.6;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .stat-item {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-item .number {
            font-size: 2em;
            font-weight: bold;
        }
        .stat-item .label {
            font-size: 0.9em;
            opacity: 0.9;
            margin-top: 5px;
        }
        .quick-actions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }
        .quick-btn {
            padding: 12px;
            background: #f0f0f0;
            border: 2px solid transparent;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            text-align: left;
        }
        .quick-btn:hover {
            border-color: #667eea;
            background: #f8f9fa;
        }
        .quick-btn .icon {
            font-size: 1.5em;
            margin-bottom: 5px;
        }
        .quick-btn .text {
            font-size: 14px;
            color: #333;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #667eea;
        }
        .entity-card {
            background: white;
            border: 1px solid #eee;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        }
        .entity-name {
            font-size: 1.2em;
            font-weight: bold;
            color: #667eea;
        }
        .entity-type {
            display: inline-block;
            padding: 2px 10px;
            background: #667eea;
            color: white;
            border-radius: 12px;
            font-size: 12px;
            margin-left: 10px;
        }
        .relation-item {
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        .relation-item:last-child {
            border-bottom: none;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .tab {
            padding: 10px 20px;
            background: #f0f0f0;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
        }
        .tab.active {
            background: #667eea;
            color: white;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>知识图谱智能查询系统</h1>

        <!-- 统计信息 -->
        <div class="card">
            <h2>图谱概览</h2>
            <div class="stats-grid" id="stats">
                <div class="stat-item">
                    <div class="number" id="node-count">-</div>
                    <div class="label">知识实体</div>
                </div>
                <div class="stat-item">
                    <div class="number" id="relation-count">-</div>
                    <div class="label">知识关系</div>
                </div>
                <div class="stat-item">
                    <div class="number" id="concept-count">-</div>
                    <div class="label">概念</div>
                </div>
                <div class="stat-item">
                    <div class="number" id="tech-count">-</div>
                    <div class="label">技术</div>
                </div>
                <div class="stat-item">
                    <div class="number" id="tool-count">-</div>
                    <div class="label">工具</div>
                </div>
                <div class="stat-item">
                    <div class="number" id="person-count">-</div>
                    <div class="label">人物</div>
                </div>
            </div>
        </div>

        <!-- 查询区域 -->
        <div class="card">
            <h2>智能查询</h2>
            <div class="tabs">
                <button class="tab active" onclick="switchTab('entity')">实体查询</button>
                <button class="tab" onclick="switchTab('search')">关键词搜索</button>
                <button class="tab" onclick="switchTab('path')">路径查询</button>
                <button class="tab" onclick="switchTab('reason')">推理分析</button>
                <button class="tab" onclick="switchTab('qa')">智能问答</button>
            </div>

            <!-- 实体查询 -->
            <div id="tab-entity" class="tab-content active">
                <div class="search-box">
                    <input type="text" id="entity-input" placeholder="输入实体名称，如：知识图谱、Neo4j、自然语言处理">
                    <button onclick="queryEntity()">查询</button>
                </div>
                <div class="quick-actions">
                    <div class="quick-btn" onclick="quickQuery('知识图谱')">
                        <div class="icon">图</div>
                        <div class="text">知识图谱</div>
                    </div>
                    <div class="quick-btn" onclick="quickQuery('Neo4j')">
                        <div class="icon">库</div>
                        <div class="text">Neo4j</div>
                    </div>
                    <div class="quick-btn" onclick="quickQuery('自然语言处理')">
                        <div class="icon">N</div>
                        <div class="text">自然语言处理</div>
                    </div>
                    <div class="quick-btn" onclick="quickQuery('深度学习')">
                        <div class="icon">D</div>
                        <div class="text">深度学习</div>
                    </div>
                    <div class="quick-btn" onclick="quickQuery('BERT')">
                        <div class="icon">B</div>
                        <div class="text">BERT</div>
                    </div>
                    <div class="quick-btn" onclick="quickQuery('机器学习')">
                        <div class="icon">M</div>
                        <div class="text">机器学习</div>
                    </div>
                </div>
            </div>

            <!-- 关键词搜索 -->
            <div id="tab-search" class="tab-content">
                <div class="search-box">
                    <input type="text" id="search-input" placeholder="输入关键词搜索相关实体">
                    <button onclick="searchEntities()">搜索</button>
                </div>
            </div>

            <!-- 路径查询 -->
            <div id="tab-path" class="tab-content">
                <div class="search-box">
                    <input type="text" id="path-start" placeholder="起点实体">
                    <input type="text" id="path-end" placeholder="终点实体">
                    <button onclick="findPath()">查找路径</button>
                </div>
                <div class="btn-group">
                    <button class="btn-small" onclick="setPath('知识图谱', '深度学习')">知识图谱 → 深度学习</button>
                    <button class="btn-small" onclick="setPath('Neo4j', '自然语言处理')">Neo4j → 自然语言处理</button>
                </div>
            </div>

            <!-- 推理分析 -->
            <div id="tab-reason" class="tab-content">
                <div class="search-box">
                    <input type="text" id="reason-input" placeholder="输入实体名称进行推理分析">
                    <button onclick="reasonEntity()">推理</button>
                </div>
                <div class="btn-group">
                    <button class="btn-small" onclick="setReason('知识图谱')">分析: 知识图谱</button>
                    <button class="btn-small" onclick="setReason('Neo4j')">分析: Neo4j</button>
                    <button class="btn-small" onclick="setReason('BERT')">分析: BERT</button>
                </div>
            </div>

            <!-- 智能问答 -->
            <div id="tab-qa" class="tab-content">
                <div class="search-box">
                    <input type="text" id="qa-input" placeholder="用自然语言提问，如：什么是知识图谱？">
                    <button onclick="askQuestion()">提问</button>
                </div>
                <div class="btn-group">
                    <button class="btn-small" onclick="setQA('什么是知识图谱？')">什么是知识图谱？</button>
                    <button class="btn-small" onclick="setQA('Neo4j有哪些相关技术？')">Neo4j有哪些相关技术？</button>
                    <button class="btn-small" onclick="setQA('知识图谱和深度学习有什么关系？')">知识图谱和深度学习的关系？</button>
                </div>
            </div>

            <!-- 加载提示 -->
            <div class="loading" id="loading">
                <p>正在查询，请稍候...</p>
            </div>

            <!-- 结果显示 -->
            <div class="result-box" id="result" style="display:none;">
                <pre id="result-content"></pre>
            </div>
        </div>

        <!-- 图谱可视化入口 -->
        <div class="card">
            <h2>更多功能</h2>
            <div class="quick-actions">
                <div class="quick-btn" onclick="window.open('/graph/html', '_blank')">
                    <div class="icon">图</div>
                    <div class="text">图谱可视化</div>
                </div>
                <div class="quick-btn" onclick="window.open('/docs', '_blank')">
                    <div class="icon">API</div>
                    <div class="text">API文档</div>
                </div>
                <div class="quick-btn" onclick="window.open('/statistics', '_blank')">
                    <div class="icon">统</div>
                    <div class="text">详细统计</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // 加载统计信息
        fetch('/statistics')
            .then(r => r.json())
            .then(data => {
                document.getElementById('node-count').textContent = data.node_count;
                document.getElementById('relation-count').textContent = data.relation_count;
                document.getElementById('concept-count').textContent = data.entity_types['概念'] || 0;
                document.getElementById('tech-count').textContent = data.entity_types['技术'] || 0;
                document.getElementById('tool-count').textContent = data.entity_types['工具'] || 0;
                document.getElementById('person-count').textContent = data.entity_types['人物'] || 0;
            });

        // 切换标签
        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('tab-' + tab).classList.add('active');
        }

        // 显示结果
        function showResult(data) {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('result').style.display = 'block';
            document.getElementById('result-content').textContent = JSON.stringify(data, null, 2);
        }

        function showLoading() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').style.display = 'none';
        }

        // 快捷查询
        function quickQuery(name) {
            document.getElementById('entity-input').value = name;
            queryEntity();
        }

        function setPath(start, end) {
            document.getElementById('path-start').value = start;
            document.getElementById('path-end').value = end;
            findPath();
        }

        function setReason(name) {
            document.getElementById('reason-input').value = name;
            reasonEntity();
        }

        function setQA(q) {
            document.getElementById('qa-input').value = q;
            askQuestion();
        }

        // 实体查询
        function queryEntity() {
            const name = document.getElementById('entity-input').value.trim();
            if (!name) return alert('请输入实体名称');
            showLoading();
            fetch('/entity/' + encodeURIComponent(name))
                .then(r => r.json())
                .then(data => showResult(data))
                .catch(e => showResult({error: '查询失败: ' + e.message}));
        }

        // 搜索
        function searchEntities() {
            const keyword = document.getElementById('search-input').value.trim();
            if (!keyword) return alert('请输入关键词');
            showLoading();
            fetch('/search?keyword=' + encodeURIComponent(keyword) + '&limit=20')
                .then(r => r.json())
                .then(data => showResult(data))
                .catch(e => showResult({error: '搜索失败: ' + e.message}));
        }

        // 路径查询
        function findPath() {
            const start = document.getElementById('path-start').value.trim();
            const end = document.getElementById('path-end').value.trim();
            if (!start || !end) return alert('请输入起点和终点');
            showLoading();
            fetch('/path?start=' + encodeURIComponent(start) + '&end=' + encodeURIComponent(end))
                .then(r => r.json())
                .then(data => showResult(data))
                .catch(e => showResult({error: '查询失败: ' + e.message}));
        }

        // 推理分析
        function reasonEntity() {
            const name = document.getElementById('reason-input').value.trim();
            if (!name) return alert('请输入实体名称');
            showLoading();
            fetch('/reasoning/explain/' + encodeURIComponent(name))
                .then(r => r.json())
                .then(data => showResult(data))
                .catch(e => showResult({error: '推理失败: ' + e.message}));
        }

        // 智能问答
        function askQuestion() {
            const question = document.getElementById('qa-input').value.trim();
            if (!question) return alert('请输入问题');
            showLoading();
            fetch('/query', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({question: question})
            })
            .then(r => r.json())
            .then(data => showResult(data))
            .catch(e => showResult({error: '问答失败: ' + e.message}));
        }

        // 回车查询
        document.getElementById('entity-input').addEventListener('keypress', e => {
            if (e.key === 'Enter') queryEntity();
        });
        document.getElementById('search-input').addEventListener('keypress', e => {
            if (e.key === 'Enter') searchEntities();
        });
        document.getElementById('qa-input').addEventListener('keypress', e => {
            if (e.key === 'Enter') askQuestion();
        });
    </script>
</body>
</html>
"""


@app.get("/statistics")
async def get_statistics():
    """获取图谱统计"""
    if not gs:
        raise HTTPException(status_code=500, detail="知识图谱未初始化")
    return gs.get_statistics()


# ========== 实体接口 ==========

@app.post("/entity")
async def add_entity(request: EntityRequest):
    """添加实体"""
    success = gs.add_entity(request.name, request.type, request.properties)
    if success:
        return {"status": "success", "message": f"实体 {request.name} 添加成功"}
    raise HTTPException(status_code=400, detail="添加实体失败")


@app.get("/entity/{name}")
async def get_entity(name: str):
    """获取实体信息"""
    entity = query_engine.query_entity(name)
    if entity:
        return entity
    raise HTTPException(status_code=404, detail=f"未找到实体: {name}")


@app.get("/entity/{name}/neighbors")
async def get_neighbors(name: str, depth: int = Query(1, ge=1, le=5)):
    """获取邻居节点"""
    return query_engine.query_neighbors(name, depth)


@app.get("/entity/{name}/relations")
async def get_entity_relations(name: str):
    """获取实体关系"""
    return query_engine.query_relations(name)


@app.get("/entities")
async def get_entities_by_type(
    type: str = Query(None, description="实体类型"),
    limit: int = Query(50, ge=1, le=500)
):
    """按类型获取实体"""
    if type:
        return query_engine.query_by_type(type, limit)
    return gs.get_statistics().get("entity_types", {})


# ========== 关系接口 ==========

@app.post("/relation")
async def add_relation(request: RelationRequest):
    """添加关系"""
    success = gs.add_relation(
        request.subject, request.predicate, request.object,
        request.properties
    )
    if success:
        return {"status": "success", "message": "关系添加成功"}
    raise HTTPException(status_code=400, detail="添加关系失败")


# ========== 三元组接口 ==========

@app.post("/triple")
async def add_triple(request: TripleRequest):
    """添加三元组"""
    triple = {
        "subject": request.subject,
        "subject_type": request.subject_type,
        "predicate": request.predicate,
        "object": request.object,
        "object_type": request.object_type,
        "confidence": request.confidence
    }
    success = gs.add_triple(triple)
    if success:
        return {"status": "success", "message": "三元组添加成功"}
    raise HTTPException(status_code=400, detail="添加三元组失败")


@app.post("/triples/batch")
async def batch_add_triples(request: BatchTripleRequest):
    """批量添加三元组"""
    triples = [t.dict() for t in request.triples]
    success, fail = gs.batch_add_triples(triples)
    return {"status": "success", "success": success, "fail": fail}


# ========== 查询接口 ==========

@app.get("/search")
async def search_entities(
    keyword: str = Query(..., description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100)
):
    """搜索实体"""
    return query_engine.search(keyword, limit)


@app.get("/path")
async def find_path(
    start: str = Query(..., description="起始实体"),
    end: str = Query(..., description="目标实体"),
    max_depth: int = Query(5, ge=1, le=10)
):
    """查找路径"""
    paths = query_engine.query_path(start, end, max_depth)
    return {"start": start, "end": end, "paths": paths}


@app.get("/subgraph/{name}")
async def get_subgraph(name: str, depth: int = Query(2, ge=1, le=4)):
    """获取子图"""
    return query_engine.query_subgraph(name, depth)


@app.get("/most-connected")
async def get_most_connected(limit: int = Query(10, ge=1, le=50)):
    """获取连接最多的实体"""
    return query_engine.query_most_connected(limit)


@app.post("/query")
async def natural_language_query(request: QueryRequest):
    """自然语言查询"""
    return query_engine.natural_language_query(request.question)


# ========== 推理接口 ==========

@app.get("/reasoning/transitive")
async def transitive_reasoning(
    entity: str = Query(..., description="实体名称"),
    relation: str = Query("BELONGS_TO", description="关系类型"),
    depth: int = Query(3, ge=1, le=5)
):
    """传递性推理"""
    return reasoning_engine.transitive_reasoning(entity, relation, depth)


@app.get("/reasoning/similar")
async def similar_reasoning(
    entity: str = Query(..., description="实体名称"),
    top_k: int = Query(5, ge=1, le=20)
):
    """相似性推理"""
    return reasoning_engine.similarity_reasoning(entity, top_k)


@app.get("/reasoning/composition")
async def composition_reasoning(entity: str = Query(..., description="实体名称")):
    """组合推理"""
    return reasoning_engine.composition_reasoning(entity)


@app.get("/reasoning/explain/{name}")
async def explain_entity(name: str):
    """生成实体解释"""
    return reasoning_engine.explain(name)


@app.post("/reasoning/infer")
async def apply_inference(threshold: float = Query(0.7, ge=0, le=1)):
    """应用推理"""
    count = reasoning_engine.apply_inference(threshold)
    return {"status": "success", "inferred_count": count}


# ========== 图谱接口 ==========

@app.get("/graph")
async def get_graph_data():
    """获取图谱可视化数据"""
    return gs.export_to_json("/tmp/graph_export.json")


@app.get("/graph/html", response_class=HTMLResponse)
async def get_graph_html():
    """获取图谱可视化页面"""
    stats = gs.get_statistics()
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>知识图谱可视化</title>
        <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
        <style>
            body {{ margin: 0; padding: 20px; font-family: Arial; }}
            #chart {{ width: 100%; height: calc(100vh - 120px); border: 1px solid #ccc; }}
            .header {{ padding: 10px; background: #f5f5f5; margin-bottom: 10px; }}
            .stats {{ display: flex; gap: 20px; }}
            .stat-item {{ padding: 5px 15px; background: #e8f4f8; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>知识图谱可视化</h2>
            <div class="stats">
                <div class="stat-item">节点: {stats['node_count']}</div>
                <div class="stat-item">关系: {stats['relation_count']}</div>
            </div>
        </div>
        <div id="chart"></div>
        <script>
            fetch('/graph')
                .then(r => r.json())
                .then(data => {{
                    const chart = echarts.init(document.getElementById('chart'));
                    const categories = [...new Set(data.nodes.map(n => n.type))].map(t => ({{name: t}}));
                    const nodes = data.nodes.map(n => ({{
                        id: n.id,
                        name: n.name,
                        category: categories.findIndex(c => c.name === n.type),
                        symbolSize: 20
                    }}));
                    const links = data.edges.map(e => ({{
                        source: e.source,
                        target: e.target,
                        label: {{ show: true, formatter: e.type }}
                    }}));
                    chart.setOption({{
                        tooltip: {{}},
                        legend: {{ data: categories.map(c => c.name) }},
                        series: [{{
                            type: 'graph',
                            layout: 'force',
                            data: nodes,
                            links: links,
                            categories: categories,
                            roam: true,
                            label: {{ show: true }},
                            force: {{ repulsion: 100 }}
                        }}]
                    }});
                }});
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
