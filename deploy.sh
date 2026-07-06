#!/bin/bash
# 知识图谱项目部署脚本

set -e

echo "=========================================="
echo "知识图谱项目部署"
echo "=========================================="

# 配置（请根据实际情况修改）
PROJECT_DIR="${PROJECT_DIR:-$HOME/kg_project}"
NEO4J_VERSION="5.15.0"

# 更新系统
echo "[1/6] 更新系统..."
sudo apt-get update -qq
sudo apt-get install -y -qq openjdk-17-jdk curl wget

# 安装Neo4j
echo "[2/6] 安装Neo4j..."
if ! command -v neo4j &> /dev/null; then
    wget -q -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo gpg --dearmor -o /usr/share/keyrings/neo4j-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/neo4j-archive-keyring.gpg] https://debian.neo4j.com stable latest" | sudo tee /etc/apt/sources.list.d/neo4j.list
    sudo apt-get update -qq
    sudo apt-get install -y -qq neo4j
    sudo systemctl enable neo4j
    sudo systemctl start neo4j
    echo "Neo4j 已安装并启动"
else
    echo "Neo4j 已存在"
fi

# 安装Python依赖
echo "[3/6] 安装Python依赖..."
cd $PROJECT_DIR
pip install -r requirements.txt -q

# 配置Neo4j密码
echo "[4/6] 配置Neo4j..."
# 等待Neo4j启动
sleep 10
# 修改默认密码（如果需要）
# cypher-shell -u neo4j -p neo4j "ALTER CURRENT USER SET PASSWORD FROM 'neo4j' TO 'knowledge_graph_2024'"

# 创建目录
echo "[5/6] 创建项目目录..."
mkdir -p $PROJECT_DIR/{data,output,logs}

# 运行项目
echo "[6/6] 启动项目..."
cd $PROJECT_DIR

echo "=========================================="
echo "部署完成！"
echo ""
echo "运行命令："
echo "  cd $PROJECT_DIR"
echo "  python main.py all"
echo ""
echo "API地址: http://$(hostname -I | awk '{print $1}'):8000"
echo "API文档: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo "=========================================="
