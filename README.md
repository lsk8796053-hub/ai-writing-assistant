# AI 写作助手（流式输出）

选择写作场景、输入主题，系统调用大模型生成对应风格的文案，并以打字机效果实时显示。

## 功能

- **场景化 Prompt 模板**：内置朋友圈、工作邮件、小红书笔记、产品描述、微博 5 种场景，分别约束字数、语气、emoji、话题标签等格式要求。
- **场景动态下发**：前端通过 `/scenes` 接口获取场景列表，新增场景只需修改后端模板，前端无需改动。
- **流式生成**：后端调用模型时开启 `stream=True`，用生成器逐段 `yield`，通过 FastAPI 的 `StreamingResponse` 实时推送；前端边接收边刷新，实现打字机效果，减少等待时间。
- **健壮性**：跳过中转接口返回的空 `choices` 数据块；前端分别处理连接失败、超时和返回格式异常；用 `st.cache_data` 缓存场景列表，减少重复请求。

## 技术栈

Python、FastAPI、Streamlit、OpenAI 兼容 API

## 项目结构

| 文件 | 说明 |
|---|---|
| `writer_api.py` | 后端：`GET /scenes` 返回场景列表，`POST /generate` 流式生成文案 |
| `writer_web.py` | 前端：Streamlit 界面，选择场景、输入主题、实时显示生成内容 |

## 运行方法

```bash
# 1. 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. 安装依赖
pip install fastapi uvicorn streamlit requests openai

# 3. 设置环境变量（OpenAI 兼容接口的 key 和地址）
export GPT_RELAY_KEY="你的 key"
export GPT_RELAY_URL="接口地址"

# 4. 启动后端和前端（两个终端）
python -m uvicorn writer_api:app --reload --port 8001
python -m streamlit run writer_web.py
```

模型名称在 `writer_api.py` 中设置，可按所用接口自行修改。

## 流式输出的实现

```
大模型（stream=True）
   ↓ 一小块一小块返回
后端生成器 yield → StreamingResponse
   ↓ HTTP 分块传输
前端 requests(stream=True) → iter_content 边收边拼
   ↓
st.empty() 占位容器不断覆盖刷新，末尾显示光标；结束后去掉光标
```

## 不足与改进方向

- 传入不存在的场景时，后端会返回 500 错误；应先校验场景，再返回明确的提示。
- 前端生成文案时还没有做异常处理，后端出错时页面可能直接报错。
- 所有场景共用 300 的 token 上限，较长的文案（如小红书笔记）可能被截断；应按场景设置不同的上限。
- 模型不一定严格遵守字数等格式要求；可以在 Prompt 中加入示例，或在代码中做后处理和校验。
