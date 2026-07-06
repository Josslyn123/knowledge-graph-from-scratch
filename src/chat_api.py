"""智能问答API - 对话式知识图谱查询系统"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict
from loguru import logger
from pathlib import Path
import httpx
import os

from .graph_store import GraphStore
from .query_engine import QueryEngine
from .reasoning_engine import ReasoningEngine

app = FastAPI(title="知识图谱智能问答系统", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gs = None
query_engine = None
reasoning_engine = None
GRAPH_DATA_PATH = Path(__file__).parent.parent / "output" / "graph_data.json"


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    reply: str
    sources: List[Dict] = []
    related_entities: List[str] = []


@app.on_event("startup")
async def startup():
    global gs, query_engine, reasoning_engine
    try:
        gs = GraphStore()
        if GRAPH_DATA_PATH.exists():
            gs.load(str(GRAPH_DATA_PATH))
            stats = gs.get_statistics()
            logger.info(f"已加载图数据: {stats['node_count']}节点")
        query_engine = QueryEngine(gs)
        reasoning_engine = ReasoningEngine(gs)
        logger.info("智能问答系统启动完成")
    except Exception as e:
        logger.error(f"启动失败: {e}")


def get_knowledge_context(message: str) -> str:
    """从知识图谱中检索相关知识"""
    context_parts = []

    # 搜索相关实体
    entities = query_engine.search(message, limit=5)
    if entities:
        context_parts.append("相关知识实体:")
        for entity in entities:
            entity_info = query_engine.query_entity(entity["name"])
            if entity_info:
                relations = entity_info.get("relations", [])[:5]
                rel_text = ", ".join([f"{r['target']}" for r in relations])
                context_parts.append(f"- {entity['name']}({entity['type']}): 关联[{rel_text}]")

    # 如果是问句，尝试提取实体并查询
    if "是什么" in message or "什么是" in message:
        keyword = message.replace("是什么", "").replace("什么是", "").replace("？", "").replace("?", "").strip()
        entity_info = query_engine.query_entity(keyword)
        if entity_info:
            context_parts.append(f"\n关于「{keyword}」的详细信息:")
            context_parts.append(f"- 类型: {entity_info.get('type', '未知')}")
            relations = entity_info.get("relations", [])[:10]
            if relations:
                context_parts.append("- 相关概念:")
                for rel in relations:
                    context_parts.append(f"  * {rel['target']} ({rel['type']})")

    return "\n".join(context_parts) if context_parts else ""


def generate_answer(message: str, context: str) -> str:
    """生成回答"""
    message_lower = message.lower()

    # 知识图谱相关问题
    if "知识图谱" in message and ("是什么" in message or "什么是" in message or "介绍" in message):
        return """知识图谱是一种用图结构来表示和存储知识的技术。

简单来说，它就像一张"知识网络"：
- 节点 = 实体（比如"苹果"、"人工智能"、"张三"）
- 边 = 关系（比如"属于"、"发明了"、"使用"）

举个例子：
- "苹果" --属于--> "水果"
- "苹果" --创始人--> "乔布斯"
- "苹果" --生产--> "iPhone"

这样就把零散的知识连接成了一个网络，让计算机能够"理解"知识之间的关系。

知识图谱的主要应用包括：
1. 搜索引擎：Google搜索直接显示答案卡片
2. 智能问答：小爱同学、Siri等语音助手
3. 推荐系统：根据你的兴趣推荐内容
4. 医疗诊断：症状-疾病-药品关联分析
5. 金融风控：企业关系图谱，风险传导分析"""

    elif "知识图谱" in message and "应用" in message:
        return """知识图谱的典型应用场景：

1. **搜索引擎增强**
   - Google搜索直接显示答案卡片
   - 百度知心、搜狗知立方

2. **智能问答系统**
   - 小爱同学、Siri、Alexa
   - 客服机器人、FAQ自动回答

3. **推荐系统**
   - 电商商品推荐
   - 内容推荐（新闻、视频）

4. **医疗健康**
   - 症状-疾病-药品关联
   - 辅助诊断系统

5. **金融风控**
   - 企业关联图谱
   - 反欺诈、反洗钱

6. **教育领域**
   - 知识点关联学习
   - 个性化学习路径

7. **智能客服**
   - 理解用户意图
   - 精准回答问题"""

    elif "知识图谱" in message and "构建" in message:
        return """构建知识图谱的主要步骤：

1. **确定领域和范围**
   - 明确要构建哪个领域的知识图谱
   - 定义实体类型和关系类型

2. **数据收集**
   - 结构化数据：数据库、表格
   - 半结构化数据：网页、文档
   - 非结构化数据：文本、图片

3. **知识抽取**
   - 实体识别：从文本中提取实体
   - 关系抽取：识别实体之间的关系
   - 属性抽取：提取实体的属性信息

4. **知识融合**
   - 实体对齐：合并同一实体
   - 去重处理：消除重复信息
   - 冲突解决：处理矛盾信息

5. **知识存储**
   - 选择图数据库（如Neo4j）
   - 设计存储模型
   - 导入数据

6. **知识应用**
   - 构建查询接口
   - 开发推理引擎
   - 提供可视化展示"""

    elif "neo4j" in message_lower:
        return """Neo4j是最流行的图数据库，专门用来存储和查询知识图谱。

**主要特点：**
1. 用图的方式存储数据，天然适合知识图谱
2. 查询速度快，特别是关联查询
3. 使用Cypher查询语言，简单易学
4. 开源免费，社区活跃
5. 提供可视化界面

**核心概念：**
- 节点（Node）：表示实体
- 关系（Relationship）：连接节点
- 属性（Property）：节点和关系的特征

**基本语法示例：**
```cypher
// 创建节点
CREATE (n:Person {name: '张三'})

// 创建关系
MATCH (a:Person {name: '张三'}), (b:Company {name: '百度'})
CREATE (a)-[:WORKS_AT]->(b)

// 查询
MATCH (n:Person)-[:WORKS_AT]->(c:Company)
RETURN n.name, c.name
```

**适用场景：**
- 社交网络分析
- 推荐系统
- 欺诈检测
- 知识图谱存储"""

    elif "自然语言处理" in message or "nlp" in message_lower:
        return """自然语言处理（NLP）是人工智能的一个分支，让计算机能够理解和处理人类语言。

**核心任务：**
1. 分词：将句子切分成词语
2. 词性标注：识别词语的词性
3. 命名实体识别：识别人名、地名、组织名等
4. 句法分析：分析句子结构
5. 语义理解：理解句子含义

**应用场景：**
- 机器翻译（Google翻译）
- 情感分析（评论正负面判断）
- 文本摘要（自动总结文章）
- 问答系统（智能客服）
- 语音识别（语音助手）

**常用技术：**
- 传统方法：规则、统计模型
- 深度学习：RNN、LSTM、Transformer
- 预训练模型：BERT、GPT

**与知识图谱的关系：**
NLP是构建知识图谱的重要工具，用于从文本中抽取实体和关系。"""

    elif "深度学习" in message or "机器学习" in message:
        return """深度学习是机器学习的一个子领域，使用深层神经网络来学习数据特征。

**基本概念：**
- 神经网络：模拟人脑的计算模型
- 深度：多层网络结构
- 学习：从数据中自动提取特征

**主要架构：**
1. CNN（卷积神经网络）：图像识别
2. RNN（循环神经网络）：序列数据
3. Transformer：自然语言处理
4. GAN（生成对抗网络）：图像生成

**典型应用：**
- 图像识别：人脸识别、医学影像
- 语音识别：语音助手
- 自然语言处理：机器翻译、文本生成
- 推荐系统：个性化推荐

**与知识图谱的结合：**
- 知识图谱嵌入：将图谱转为向量
- 知识增强的深度学习：用知识图谱提升模型效果"""

    elif context:
        # 如果有知识图谱上下文，基于上下文生成回答
        return f"根据知识图谱中的信息，我找到了以下相关内容：\n\n{context}\n\n如果您想了解更多细节，可以继续提问。"

    else:
        return f"关于您的问题「{message}」，这是一个很好的问题。\n\n目前我主要擅长回答以下领域的问题：\n- 知识图谱相关概念\n- Neo4j图数据库\n- 自然语言处理\n- 深度学习和机器学习\n\n您可以尝试问我这些问题，我会尽力为您解答！"


@app.get("/", response_class=HTMLResponse)
async def root():
    """智能问答界面"""
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>知识图谱智能助手</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; background: #f5f5f5; height: 100vh; display: flex; flex-direction: column; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 20px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header h1 { font-size: 1.5em; }
        .header-btn { padding: 8px 16px; background: rgba(255,255,255,0.2); border: none; border-radius: 20px; color: white; cursor: pointer; }
        .header-btn:hover { background: rgba(255,255,255,0.3); }
        .chat-container { flex: 1; display: flex; flex-direction: column; max-width: 900px; margin: 0 auto; width: 100%; padding: 20px; }
        .messages { flex: 1; overflow-y: auto; padding: 20px 0; }
        .welcome { text-align: center; padding: 40px 20px; }
        .welcome-icon { font-size: 80px; margin-bottom: 20px; }
        .welcome h2 { color: #333; margin-bottom: 10px; }
        .welcome p { color: #666; margin-bottom: 30px; }
        .quick-cards { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; max-width: 600px; margin: 0 auto; }
        .quick-card { padding: 20px; background: white; border-radius: 12px; cursor: pointer; transition: all 0.3s; text-align: left; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .quick-card:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .quick-card h4 { color: #333; margin-bottom: 8px; font-size: 15px; }
        .quick-card p { color: #666; font-size: 13px; }
        .msg { margin-bottom: 20px; display: flex; gap: 12px; animation: fadeIn 0.3s; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .msg.user { flex-direction: row-reverse; }
        .msg-avatar { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: bold; flex-shrink: 0; }
        .msg.user .msg-avatar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .msg.bot .msg-avatar { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; }
        .msg-content { max-width: 75%; padding: 15px 20px; border-radius: 18px; line-height: 1.8; font-size: 15px; }
        .msg.user .msg-content { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-bottom-right-radius: 4px; }
        .msg.bot .msg-content { background: white; color: #333; border-bottom-left-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .msg-content strong { font-weight: 600; }
        .msg-content ol, .msg-content ul { margin: 10px 0; padding-left: 20px; }
        .msg-content li { margin-bottom: 8px; }
        .typing { display: flex; gap: 4px; padding: 10px 0; }
        .typing span { width: 8px; height: 8px; background: #667eea; border-radius: 50%; animation: typing 1.4s infinite; }
        .typing span:nth-child(2) { animation-delay: 0.2s; }
        .typing span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
        .input-area { padding: 20px 0; }
        .input-box { display: flex; gap: 10px; align-items: flex-end; }
        .input-box textarea { flex: 1; padding: 15px 20px; border: 2px solid #e0e0e0; border-radius: 12px; font-size: 15px; line-height: 1.5; resize: none; outline: none; font-family: inherit; max-height: 150px; min-height: 50px; transition: border-color 0.3s; }
        .input-box textarea:focus { border-color: #667eea; }
        .send-btn { width: 50px; height: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.3s; flex-shrink: 0; }
        .send-btn:hover { transform: scale(1.05); }
        .send-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .send-btn svg { width: 24px; height: 24px; }
        .hint { text-align: center; margin-top: 10px; font-size: 12px; color: #999; }
    </style>
</head>
<body>
    <div class="header">
        <h1>知识图谱智能助手</h1>
        <div>
            <button class="header-btn" onclick="window.open('/graph/html','_blank')">图谱可视化</button>
            <button class="header-btn" onclick="window.open('/docs','_blank')">API文档</button>
        </div>
    </div>
    <div class="chat-container">
        <div class="messages" id="messages">
            <div class="welcome" id="welcome">
                <div class="welcome-icon">图</div>
                <h2>欢迎使用知识图谱智能助手</h2>
                <p>我可以回答关于知识图谱、人工智能等领域的问题</p>
                <div class="quick-cards">
                    <div class="quick-card" onclick="ask('什么是知识图谱？')">
                        <h4>什么是知识图谱？</h4>
                        <p>了解知识图谱的基本概念</p>
                    </div>
                    <div class="quick-card" onclick="ask('知识图谱有哪些应用？')">
                        <h4>知识图谱的应用</h4>
                        <p>探索实际应用场景</p>
                    </div>
                    <div class="quick-card" onclick="ask('如何构建知识图谱？')">
                        <h4>如何构建知识图谱</h4>
                        <p>学习构建流程和方法</p>
                    </div>
                    <div class="quick-card" onclick="ask('Neo4j是什么？')">
                        <h4>Neo4j图数据库</h4>
                        <p>了解图数据库技术</p>
                    </div>
                </div>
            </div>
        </div>
        <div class="input-area">
            <div class="input-box">
                <textarea id="input" placeholder="输入您的问题..." rows="1"></textarea>
                <button class="send-btn" id="sendBtn" onclick="send()">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13"/><path d="M22 2L15 22L11 13L2 9L22 2Z"/></svg>
                </button>
            </div>
            <div class="hint">按 Enter 发送消息，Shift + Enter 换行</div>
        </div>
    </div>
    <script>
        const input = document.getElementById('input');
        const messages = document.getElementById('messages');
        const welcome = document.getElementById('welcome');
        let sending = false;

        // Enter键发送，Shift+Enter换行
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                send();
            }
        });

        // 自动调整高度
        input.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 150) + 'px';
        });

        function ask(q) {
            input.value = q;
            send();
        }

        async function send() {
            const msg = input.value.trim();
            if (!msg || sending) return;

            // 隐藏欢迎页
            if (welcome) welcome.style.display = 'none';

            // 显示用户消息
            addMsg('user', msg);
            input.value = '';
            input.style.height = 'auto';

            // 显示打字动画
            sending = true;
            document.getElementById('sendBtn').disabled = true;
            const typing = addTyping();

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: msg, session_id: 'web'})
                });
                const data = await res.json();
                typing.remove();
                addMsg('bot', data.reply);
            } catch(e) {
                typing.remove();
                addMsg('bot', '抱歉，处理出错了，请稍后重试。');
            }

            sending = false;
            document.getElementById('sendBtn').disabled = false;
            input.focus();
        }

        function addMsg(role, content) {
            const div = document.createElement('div');
            div.className = 'msg ' + role;
            const avatar = role === 'user' ? '你' : 'AI';
            div.innerHTML = '<div class="msg-avatar">' + avatar + '</div><div class="msg-content">' + formatContent(content) + '</div>';
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }

        function addTyping() {
            const div = document.createElement('div');
            div.className = 'msg bot';
            div.innerHTML = '<div class="msg-avatar">AI</div><div class="msg-content"><div class="typing"><span></span><span></span><span></span></div></div>';
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
            return div;
        }

        function formatContent(text) {
            // 转义HTML
            text = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            // 处理Markdown
            text = text.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');
            text = text.replace(/\\*(.*?)\\*/g, '<em>$1</em>');
            text = text.replace(/`(.*?)`/g, '<code>$1</code>');
            // 处理换行
            text = text.replace(/\\n/g, '<br>');
            return text;
        }

        // 页面加载后聚焦
        input.focus();
    </script>
</body>
</html>'''


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """智能问答接口"""
    try:
        # 从知识图谱检索相关知识
        context = get_knowledge_context(request.message)

        # 生成回答
        reply = generate_answer(request.message, context)

        # 提取相关实体
        entities = query_engine.search(request.message, limit=3)
        related_entities = [e["name"] for e in entities]

        return ChatResponse(
            reply=reply,
            sources=[{"type": "knowledge_graph", "context": context}] if context else [],
            related_entities=related_entities
        )

    except Exception as e:
        logger.error(f"问答处理失败: {e}")
        return ChatResponse(
            reply="抱歉，处理您的问题时出现了错误，请稍后重试。",
            sources=[],
            related_entities=[]
        )


@app.get("/statistics")
async def get_statistics():
    if not gs:
        raise HTTPException(status_code=500, detail="系统未初始化")
    return gs.get_statistics()


@app.get("/graph")
async def get_graph_data():
    return gs.export_to_json("/tmp/graph_export.json")


@app.get("/graph/html", response_class=HTMLResponse)
async def get_graph_html():
    html_content = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>知识图谱可视化</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<style>body{margin:0;padding:20px;background:#f5f5f5}.header{padding:15px;background:#fff;border-radius:10px;margin-bottom:20px}.stat{display:inline-block;padding:5px 15px;background:#667eea;color:#fff;border-radius:15px;margin:5px}#chart{width:100%;height:calc(100vh - 120px);background:#fff;border-radius:10px}</style>
</head><body>
<div class="header"><h2>知识图谱可视化</h2>
<span class="stat" id="nodeCount">节点: 加载中...</span>
<span class="stat" id="relCount">关系: 加载中...</span></div>
<div id="chart"></div>
<script>
fetch('/statistics').then(r=>r.json()).then(s=>{
    document.getElementById('nodeCount').textContent='节点: '+s.node_count;
    document.getElementById('relCount').textContent='关系: '+s.relation_count;
});
fetch('/graph').then(r=>r.json()).then(data=>{
    const chart=echarts.init(document.getElementById('chart'));
    const cats=[...new Set(data.nodes.map(n=>n.type))].map(t=>({name:t}));
    const nodes=data.nodes.slice(0,200).map(n=>({id:n.id,name:n.name,category:cats.findIndex(c=>c.name===n.type),symbolSize:20}));
    const links=data.edges.slice(0,500).map(e=>({source:e.source,target:e.target}));
    chart.setOption({tooltip:{},legend:{data:cats.map(c=>c.name)},series:[{type:'graph',layout:'force',data:nodes,links:links,categories:cats,roam:true,label:{show:true,fontSize:10},force:{repulsion:100}}]});
    window.onresize=()=>chart.resize();
});
</script></body></html>"""
    return html_content


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
