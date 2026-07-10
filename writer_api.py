"""
AI 写作助手 · 后端 (FastAPI)

提供两个接口：
    GET  /scenes     → 返回可用的写作场景列表
    POST /generate   → 流式生成文案

依赖:fastapi、uvicorn、pydantic、openai
环境变量:GPT_RELAY_KEY、GPT_RELAY_URL
启动:python -m uvicorn writer_api:app --reload --port 8001
"""

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import os
from openai import OpenAI

app = FastAPI(title="AI 写作助手")
client = OpenAI(api_key=os.environ["GPT_RELAY_KEY"],
    base_url=os.environ["GPT_RELAY_URL"])


templates = {
    "朋友圈": "写一条关于'{topic}'的朋友圈文案,100字左右,风格随性生动,可以带1-2个emoji,不要使用Markdown格式",
    "工作邮件": "写一封关于'{topic}'的工作邮件,语气正式简洁,包含开头问候、正文、结尾,不要使用Markdown格式",
    "小红书笔记": "写一篇关于'{topic}'的小红书笔记,开头有吸引人的标题,内容分段,带emoji和话题标签,300字左右",
    "产品描述": "为'{topic}'写一段产品描述,突出3个核心卖点,语言精炼有吸引力,150字左右,不要使用Markdown格式",
    "微博文案": "写一条关于'{topic}'的微博,140字内,带2-3个话题标签"
}


class WriteRequest(BaseModel):
    scene: str    
    topic: str    



@app.get("/scenes")   # 让前端能查询当前可用的场景列表
def get_scenes():
    """获取所有可用的写作场景"""
    return {"scenes": list(templates.keys())}


@app.post("/generate")  #POST 接口，接收前端发来的 JSON（scene + topic），调用 GPT 流式生成对应风格的文案，通过 StreamingResponse 把文案分段流式返回给前端
def generate(req: WriteRequest):
    """生成文案,流式返回"""
    prompt = templates[req.scene].format(topic=req.topic)
    
    def stream_generator():
        """生成器函数：每产出一段文字就 yield 出去"""
        response = client.chat.completions.create(
            model="gpt-5.5",
            max_completion_tokens=300,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        ) 
        for chunk in response:
            if not chunk.choices:          # 货架为空 → 跳过这个 chunk
                continue
            text = chunk.choices[0].delta.content
            if text is not None:
                yield text
    
    return StreamingResponse(stream_generator(), media_type="text/plain")