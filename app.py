import streamlit as st
import requests
from datetime import datetime
from mcp_tools import record_diet

# ====================== 模型 ======================
API_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.1:8b"

# ====================== 记忆 ======================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "diet_log" not in st.session_state:
    st.session_state.diet_log = []

# ====================== MCP 工具调用 ======================
def call_mcp(name, **kwargs):
    if name == "record":
        res = record_diet(**kwargs)
        st.session_state.diet_log.append({
            "time": datetime.now().strftime("%H:%M"),
            "type": kwargs["meal_type"],
            "food": kwargs["food"]
        })
        return res
    return ""

# ====================== 意图识别 ======================
# ====================== 意图识别（彻底修复版） ======================
def run_tool(user_input):
    ui = user_input.strip()
    
    # 只在同时满足以下所有条件时才记录：
    # 1. 包含“吃了”关键词
    # 2. 不包含问号（排除问句）
    # 3. 不包含“什么”“谁”“哪”等疑问词
    # 4. 提取的食物不是空或无意义词
    if "吃了" in ui and "?" not in ui and "什么" not in ui and "谁" not in ui and "哪" not in ui:
        meal = None
        if "早上" in ui or "早餐" in ui:
            meal = "早餐"
        elif "中午" in ui or "午餐" in ui:
            meal = "午餐"
        elif "晚上" in ui or "晚餐" in ui:
            meal = "晚餐"
        
        # 提取食物并过滤无意义内容
        food = (ui
                .replace("我", "")
                .replace("吃了", "")
                .replace("早上", "")
                .replace("中午", "")
                .replace("晚上", "")
                .replace("早餐", "")
                .replace("午餐", "")
                .replace("晚餐", "")
                .strip())
        
        if meal and food and len(food) > 1:
            return call_mcp("record", meal_type=meal, food=food)
    return None

# ====================== 纯大模型思考 ======================
def agent(prompt):
    history = "\n".join([f"{x['time']} | {x['type']}：{x['food']}" for x in st.session_state.diet_log])
    
    sys = f"""
你是专业饮食助手。
所有回答必须**完全由你自己思考**。

规则：
1. 问吃了什么 → 根据今日饮食记录回答。
2. 问热量 → **你自己给出合理热量，不要编造，不要矛盾**。
3. 推荐菜谱 → **你自己自由推荐**，不使用任何预设菜单。
4. 回答简洁、自然、真实、合理。

今日饮食记录：
{history}
"""
    messages = [
        {"role": "system", "content": sys},
        *st.session_state.messages[-5:],
        {"role": "user", "content": prompt}
    ]
    
    try:
        r = requests.post(API_URL, json={
            "model": MODEL,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.2, "max_tokens": 300}
        })
        return r.json()["message"]["content"].strip()
    except:
        return "❌ 模型连接失败"

# ====================== 界面 ======================
st.set_page_config(page_title="饮食助手", layout="wide")
st.title("🍽️AI饮食助手")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("聊天、记录饮食、查热量、推荐菜")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        tool_msg = run_tool(user_input)
        reply = agent(user_input)
        if tool_msg:
            st.success(tool_msg)
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

# ====================== 侧边栏 ======================
with st.sidebar:
    st.subheader("📝 饮食记录")
    for item in st.session_state.diet_log:
        st.write(f"🕒 {item['time']} | {item['type']}：{item['food']}")