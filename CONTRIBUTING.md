# 贡献指南

感谢您对本项目的关注！欢迎贡献代码、报告问题或提出改进建议。

## 如何贡献

### 1. 报告问题

如果您发现了bug或有改进建议，请在GitHub Issues中提交：
- 使用清晰的标题描述问题
- 详细描述复现步骤
- 提供错误日志或截图
- 说明您的运行环境（Python版本、操作系统等）

### 2. 提交代码

1. Fork本仓库
2. 创建您的特性分支：`git checkout -b feature/AmazingFeature`
3. 提交您的修改：`git commit -m 'Add some AmazingFeature'`
4. 推送到分支：`git push origin feature/AmazingFeature`
5. 创建Pull Request

### 3. 开发环境

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/knowledge-graph-from-scratch.git
cd knowledge-graph-from-scratch

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest
```

## 代码规范

### 1. Python代码风格
- 遵循PEP 8规范
- 使用4个空格缩进
- 行长度限制在120字符以内
- 使用有意义的变量名和函数名

### 2. 文档字符串
```python
def function_name(param1: str, param2: int) -> bool:
    """
    函数功能简述

    Args:
        param1: 参数1说明
        param2: 参数2说明

    Returns:
        返回值说明

    Raises:
        ValueError: 异常说明
    """
    pass
```

### 3. 类型注解
```python
def process_text(text: str) -> Dict[str, Any]:
    """处理文本"""
    pass
```

### 4. 注释
- 复杂逻辑添加注释
- 使用中文注释
- 保持注释与代码同步

## 测试

### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_nlp_processor.py

# 运行并显示详细输出
pytest -v

# 运行并生成覆盖率报告
pytest --cov=src tests/
```

### 编写测试
- 每个模块对应一个测试文件
- 测试函数以`test_`开头
- 使用pytest fixtures管理测试数据
- 测试应覆盖正常和异常情况

## 提交规范

### Commit Message格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type类型
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

### 示例
```
feat(nlp): 添加实体识别功能

- 增加基于BERT的实体识别
- 支持中文实体识别
- 添加单元测试

Closes #123
```

## 分支管理

- `main`: 主分支，保持稳定
- `develop`: 开发分支
- `feature/*`: 特性分支
- `fix/*`: 修复分支
- `release/*`: 发布分支

## 发布流程

1. 更新版本号
2. 更新CHANGELOG.md
3. 创建Release Tag
4. 发布到PyPI（可选）

## 行为准则

- 尊重每位贡献者
- 接受建设性批评
- 专注于对社区最有利的事情
- 对他人表示同理心

## 联系方式

如有任何问题，请通过GitHub Issues联系。

感谢您的贡献！
