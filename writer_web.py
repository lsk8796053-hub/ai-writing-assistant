"""
AI写作助手-前端(Streamlit)

功能:
     - 用户选择写作场景
     - 通过流式接收后端响应,实现打字机效果

依赖:
     - streamlit
     - requests

启动:
     python -m streamlit run writer_web.py
     (依赖后端先启动在http://127.0.0.1:8001)

"""
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8001"

st.set_page_config(
    page_title="AI 写作助手",
    page_icon="✍️",
    layout="centered"
)

st.title("✍️ AI 写作助手")
st.caption("选择场景，输入主题，一键生成高质量文案")


@st.cache_data(ttl=60)  # 使用缓存装饰器,ttl=60是60秒内不刷新，方便加载
def get_scenes():
    
    
    try:
        
        response = requests.get(f"{API_URL}/scenes", timeout=5)
        
        response.raise_for_status()
        
        result = response.json()["scenes"]
        
        return result
    except requests.ConnectionError:
        
        st.error("❌ 无法连接后端，请确认后端服务已启动（端口 8001)")
        st.stop()
    except requests.Timeout:
        
        st.error("⏰ 后端响应超时，请稍后重试")
        st.stop()
    except (KeyError,TypeError):
        st.error("⚠️ 后端返回的数据格式异常")
        st.stop()
    except Exception as e:
        
        st.error(f"❓ 未知错误：{type(e).__name__}: {e}")
        st.stop()
    return []
scenes = get_scenes()



scene = st.selectbox("1. 选择场景", scenes)
topic = st.text_input("2. 输入主题", placeholder="例如：周末去爬山、新品上市...")


if st.button("✨ 生成文案", type="primary"):  #st.button只有在点击的一瞬间才会执行，用户切换其他组件后这块将不会重复执行
    if not topic:
        st.warning("请先输入主题")
    else:
        st.subheader(f"📝 {scene}")
        
        placeholder = st.empty()  #创建容器，后续placeholder.markdown会覆盖而非新增
        full_text = ""
        
        with requests.post(
            f"{API_URL}/generate",
            json={"scene": scene, "topic": topic},
            stream=True
        ) as response:
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):# 后端 yield 多少就接多少, 自动把字节解码为字符串
                if chunk:
                    full_text += chunk
                    placeholder.markdown(full_text + "▌")
        
        placeholder.markdown(full_text)  # ⚠️ 循环结束后再不带 ▌，告诉用户"生成完成"