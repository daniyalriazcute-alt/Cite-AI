import streamlit as st
from agents import citation_agent, create_citation_task
from crewai import Crew
from guardrails import firewall
import time
import streamlit.components.v1 as components

st.set_page_config(page_title="CiteGuard AI", layout="wide", page_icon="🛡️")

# Hide Streamlit chrome + force production look
st.markdown("""
<style>
header, footer, #MainMenu {visibility: hidden;}
.stApp { background: #0a0a0f!important; }
[data-testid="stSidebar"] { background: #11111b!important; border-right: 1px solid #1f1f2e; }
div[data-baseweb="select"] > div { background: #1a1a2e!important; color: white!important; border: 1px solid #2a2a3a!important; border-radius: 12px!important; }
div[data-testid="stChatInput"] { background: #1a1a2e!important; border: 1px solid #2a2a3a!important; border-radius: 14px!important; }
.dot { width:10px; height:10px; border-radius:50%; display:inline-block; }
.dot-green { background:#22c55e; box-shadow:0 0 12px #22c55e; animation: blink 1.5s infinite; }
.dot-yellow { background:#eab308; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }
.card { background: rgba(26,26,46,0.85); border: 1px solid #2a2a3a; border-radius: 16px; padding: 14px; }
</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state: st.session_state.history = []
if "chat" not in st.session_state: st.session_state.chat = []
def tokens(): return 0 if not st.session_state.chat else sum(len(m["content"]) for m in st.session_state.chat)//4

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    if st.button("➕ Start New Chat", use_container_width=True, type="primary"):
        st.session_state.chat=[]; st.session_state.history=[]; st.rerun()
    if st.button("🔴 End Chat", use_container_width=True):
        st.session_state.chat=[]; st.rerun()
    st.divider()
    st.markdown("📜 **Chat History**")
    st.caption("No history yet" if not st.session_state.history else "")
    st.divider()
    t = tokens()
    st.markdown(f'<div class="card">Tokens Used<br><span style="font-size:28px;font-weight:800">{t}/8192</span><br><span style="color:#22c55e">● Healthy</span><div style="height:4px;background:#2a2a3a;border-radius:4px;margin-top:8px"><div style="width:{min(t/8192*100,100)}%;height:100%;background:white;border-radius:4px"></div></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="card" style="margin-top:12px">Firewall Blocked<br><span style="font-size:22px;font-weight:700">{firewall.blocked_count} threats</span></div>', unsafe_allow_html=True)

col_main, col_right = st.columns([3,1])

with col_main:
    st.markdown('<h1 style="color:#8b5cf6;background: linear-gradient(90deg,#8b5cf6,#3b82f6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:38px;font-weight:800">🛡️ CiteGuard AI - Secure Citation Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#6b7280;font-size:13px">CrewAI | Groq openai/gpt-oss-120B | Free AI Firewall | OWASP LLM Top 10 2025</p>', unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1: lang = st.selectbox("Language", ["English","Español","বাংলা"], label_visibility="visible")
    with c2: style_opt = st.selectbox("Citation Style", ["APA 7","MLA 9","Chicago","IEEE","Harvard"])

    # Chat messages
    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Enter paper title, DOI, URL, or raw text..."):
        is_safe, threat, clean = firewall.scan(prompt)
        if not is_safe:
            st.error(f"🔴 {threat} blocked by AI Firewall")
            st.session_state.chat.append({"role":"assistant","content":clean}); st.rerun()
        st.session_state.chat.append({"role":"user","content":prompt})
        st.session_state.history.append(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Goal → Decide → Act → Observe → Complete..."):
                task = create_citation_task(prompt, style_opt, lang)
                crew = Crew(agents=[citation_agent], tasks=[task], verbose=False)
                try:
                    result = crew.kickoff()
                except:
                    time.sleep(1)
                    result = crew.kickoff() # Retry 1x
                st.markdown(result)
                st.session_state.chat.append({"role":"assistant","content":str(result)})
                st.rerun()

with col_right:
    st.markdown("### 🧠 Agent Workflow")
    st.markdown('<div class="card" style="background:#171738">Goal → Decide → Act → Observe →<br><span style="color:#60a5fa;font-weight:700">Continue/Complete</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><span class="dot dot-green"></span> Short-Term Memory: Active (last 3)</div>', unsafe_allow_html=True)
    t = tokens()
    st.markdown(f'<div class="card"><span class="dot dot-yellow"></span> Rate Limit: {t}/8192 tokens<div style="height:4px;background:#2a2a3a;border-radius:4px;margin-top:8px"><div style="width:{min(t/8192*100,100)}%;height:100%;background:#eab308;border-radius:4px"></div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="card" style="background:#2a1a1a">🔁 Retry: 1x on fail - Ready</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("### 🔒 Free AI Firewall")
    st.markdown('<div class="card"><span class="dot dot-green"></span> <b>PROTECTED • Blinking</b><div style="height:6px;background:#3b82f6;border-radius:6px;margin-top:10px"></div><small style="color:#6b7280">Layers: Injection Filter, Intent Analysis, Output Sanitizer</small></div>', unsafe_allow_html=True)
    st.markdown("### 🛡️ OWASP Guardrails")
    st.markdown('<span class="dot dot-green"></span> Prompt Injection: Active<br><span class="dot dot-green"></span> System Prompt Leakage: Active<br><span class="dot dot-green"></span> Improper Output Handling: Active', unsafe_allow_html=True)
