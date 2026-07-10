# ✍️ AI 写作助手

> 基于 Claude API 的多场景 AI 写作工具，前后端分离架构，支持流式输出（打字机效果）。

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.39+-FF4B4B.svg)](https://streamlit.io/)

---

## 📖 项目简介

一款轻量级 AI 写作助手，针对中文场景做了专门的 Prompt 优化。用户选择写作场景（朋友圈 / 工作邮件 / 小红书笔记 / 产品描述 / 微博文案），输入主题，AI 自动生成对应风格的高质量文案。

**核心特点**：
- ⚡ **流式输出**：文字像 ChatGPT 那样一个字一个字蹦出来，首字响应 < 1 秒
- 🎯 **场景化 Prompt**：每种场景都有专门优化的提示词模板
- 🏗️ **前后端分离**：UI 与业务解耦，后端可独立服务多种前端
- 🛡️ **完整异常处理**：连接错误、超时、数据格式异常均有针对性提示

## 🎬 演示

```
[用户操作]
1. 选择场景：朋友圈
2. 输入主题：周末爬山
3. 点击 ✨ 生成文案

[AI 输出（实时流式）]
今天和朋友去爬了山，山顶的风超大～
吹得人心情瞬间舒展开 🏔️
原来逃离城市这么治愈，下周还要再来！
```

---

## 🛠️ 技术栈

| 层级 | 技术 | 用途 |
|---|---|---|
| **前端** | Streamlit | UI 渲染、流式显示 |
| **后端** | FastAPI | API 路由、数据验证 |
| **AI 模型** | Claude (Anthropic) | 文案生成 |
| **数据验证** | Pydantic | 请求体类型校验 |
| **流式响应** | StreamingResponse + 生成器 | 边生成边推送 |
| **HTTP 客户端** | requests | 前端调后端 |

---

## 📦 项目结构

```
ai-writing-assistant/
├── writer_api.py          # FastAPI 后端（端口 8001）
├── writer_web.py          # Streamlit 前端（端口 8501）
├── start_backend.bat      # 一键启动后端（Windows）
├── start_frontend.bat     # 一键启动前端（Windows）
├── requirements.txt       # 依赖清单
└── README.md              # 项目说明
```

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Anthropic API Key（[申请地址](https://www.anthropic.com/)）

### 1. 克隆项目

```bash
git clone https://github.com/your-username/ai-writing-assistant.git
cd ai-writing-assistant
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

设置你的 Anthropic API Key（**Windows PowerShell**）：

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-xxxxxxxxxxxx"
$env:ANTHROPIC_BASE_URL = "https://api.anthropic.com"  # 可选：自定义代理地址
```

> 💡 长期生效：在 Windows 系统设置 → 环境变量中添加，避免每次重新设置。

### 4. 启动后端

```bash
python -m uvicorn writer_api:app --reload --port 8001
```

或双击运行 `start_backend.bat`。

启动成功后，浏览器打开 http://127.0.0.1:8001/docs 可看到自动生成的 API 文档。

### 5. 启动前端

**新开一个终端窗口**：

```bash
python -m streamlit run writer_web.py
```

或双击运行 `start_frontend.bat`。

浏览器自动打开 http://127.0.0.1:8501，开始使用！

---

## 🏗️ 架构说明

### 前后端通信流程

```
┌─────────────┐        GET /scenes        ┌──────────────┐
│             │ ─────────────────────────► │              │
│  Streamlit  │ ◄───────── [scenes] ────── │   FastAPI    │
│   前端       │                            │    后端       │
│             │   POST /generate (JSON)    │              │
│ 端口 8501    │ ─────────────────────────► │  端口 8001    │
│             │ ◄── HTTP chunks (流式) ──── │              │
└─────────────┘                            └──────┬───────┘
                                                   │
                                                   ▼
                                           ┌──────────────┐
                                           │  Claude API  │
                                           │  (流式响应)   │
                                           └──────────────┘
```

### 流式输出工作原理

1. **后端**：用 `client.messages.stream()` 调用 Claude，通过**生成器函数 + yield** 把每段文字"推送"出去
2. **FastAPI**：用 `StreamingResponse` 把生成器包装成 HTTP 流式响应
3. **前端**：用 `requests.post(stream=True)` + `iter_content` 逐块接收
4. **UI**：用 `st.empty()` + `placeholder.markdown` 实现"覆盖式更新"，模拟打字机效果

**核心代码片段**：

```python
# 后端：生成器函数
def stream_generator():
    with client.messages.stream(...) as stream:
        for text in stream.text_stream:
            yield text  # 每段文字立即推送

return StreamingResponse(stream_generator(), media_type="text/plain")
```

```python
# 前端：流式接收
with requests.post(..., stream=True) as response:
    for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
        if chunk:
            full_text += chunk
            placeholder.markdown(full_text + "▌")  # 带光标
placeholder.markdown(full_text)  # 结束后去掉光标
```

---

## 🎨 支持的写作场景

| 场景 | 风格特点 | 字数 |
|---|---|---|
| **朋友圈** | 随性生动，含 emoji | 100 字左右 |
| **工作邮件** | 正式简洁，结构完整 | 灵活 |
| **小红书笔记** | 标题吸引人，分段清晰，含话题标签 | 300 字左右 |
| **产品描述** | 突出卖点，语言精炼 | 150 字左右 |
| **微博文案** | 简短有力，含话题标签 | 140 字内 |

---

## 🔧 扩展场景

新增写作场景非常简单——只需在 `writer_api.py` 的 `templates` 字典中加一项：

```python
templates = {
    "朋友圈": "...",
    "工作邮件": "...",
    "新场景": "写一段关于'{topic}'的新场景文案，要求 xxx",  # 加这行
}
```

前端会在 60 秒内（缓存 TTL）自动同步新场景。**无需改前端代码**。

---

## 📚 学习收获

本项目是我自学转行 AI 应用工程师的第二个完整项目，深度实践了以下技术点：

- ✅ **生成器与 yield**：理解"按需产出"机制，与 `iter_content` 形成端到端的流式管道
- ✅ **FastAPI 路由 + Pydantic**：通过类型注解实现声明式数据验证
- ✅ **上下文管理器（with）**：保证流式连接被自动关闭
- ✅ **Streamlit 渲染机制**：rerun、widget state、`st.empty` 覆盖式更新
- ✅ **异常分类处理**：ConnectionError / Timeout / KeyError 各有针对性提示
- ✅ **前后端协作**：每个 chunk 在两端的对应关系，是流式应用的核心

---

## 📝 待优化点

- [ ] 支持自定义场景模板（前端可视化编辑）
- [ ] 添加历史记录功能（保存生成结果）
- [ ] 支持多轮对话式优化（"再写得活泼一点"）
- [ ] 部署到云端（Vercel / Railway）
- [ ] 添加单元测试

---

## 📄 License

MIT License

---

## 🔗 相关项目

- [doc-qa-system](https://github.com/your-username/doc-qa-system) — 我的第一个 AI 项目：文档问答系统
