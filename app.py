import streamlit as st
from agents import citation_agent, create_citation_task
from crewai import Crew
from guardrails import firewall
import time

st.set_page_config(page_title="CiteGuard AI", layout="wide", page_icon="🛡️")

# Production glassmorphism CSS - makes Streamlit look like artifact above
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
.stApp { background: #0a0a0f!important; font-family: 'Inter', sans-serif; }
[data-testid="stSidebar"] { background: #11111b!important; border-right: 1px solid #2a2a3a; }
h1 { font-weight: 800!important; }
.dot-green { width:10px; height:10px; background:#22c55e; border-radius:50%; display:inline-block; box-shadow:0 0 12px #22c55e; animation: blink 1.5s infinite; }
.dot-yellow { width:10px; height:10px; background:#eab308; border-radius:50%; display:inline-block; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.4} }
.card { background: rgba(26,26,46,0.8); backdrop-filter: blur(12px); border: 1px solid #2a2a3a; border-radius: 16px; padding: 16px; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state: st.session_state.history = []
if "chat" not in st.session_state: st.session_state.chat = []

def calc_tokens():
    return 0 if not st.session_state.chat else sum(len(m["content"]) for m in st.session_state.chat)//4

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    if st.button("➕ Start New Chat", use_container_width=True, type="primary"):
        st.session_state.chat = []; st.rerun()
    if st.button("🔴 End Chat", use_container_width=True):
        st.session_state.chat = []; st.rerun()
    st.divider()
    st.markdown("📜 **Chat History**")
    st.caption("No history yet" if not st.session_state.history else "")
    st.divider()
    tokens = calc_tokens()
    st.markdown(f'<div class="card">Tokens Used<br><b style="font-size:28px">{tokens}/8192</b><br><span style="color:#22c55e">● Healthy</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="card">Firewall Blocked<br><b style="font-size:24px">{firewall.blocked_count} threats</b></div>', unsafe_allow_html=True)

col_main, col_right = st.columns([3, 1])

with col_main:
    st.markdown('<h1 style="background: linear-gradient(90deg, #8b5cf6, #3b82f6); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">🛡️ CiteGuard AI - Secure Citation Generator</h1>', unsafe_allow_html=True)
    st.caption("CrewAI | Groq openai/gpt-oss-120B | Free AI Firewall | OWASP LLM Top 10 2025")
    c1,c2 = st.columns(2)
    lang = c1.selectbox("Language", ["English", "Español", "বাংলা"])
    style_opt = c2.selectbox("Citation Style", ["APA 7", "MLA 9", "Chicago", "IEEE", "Harvard"])
    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if prompt := st.chat_input("Enter paper title, DOI, URL, or raw text..."):
        is_safe, threat, clean = firewall.scan(prompt)
        if not is_safe:
            st.error(f"Firewall blocked: {threat}")
            st.session_state.chat.append({"role":"assistant","content":clean}); st.rerun()
        st.session_state.chat.append({"role":"user","content":prompt})
        st.session_state.history.append(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Goal → Decide → Act → Observe → Complete..."):
                task = create_citation_task(prompt, style_opt, lang)
                crew = Crew(agents=[citation_agent], tasks=[task], verbose=False)
                try: result = crew.kickoff()
                except:
                    time.sleep(1); result = crew.kickoff() # retry 1x
                st.markdown(result)
                st.session_state.chat.append({"role":"assistant","content":str(result)}); st.rerun()

with col_right:
    st.markdown("### 🧠 Agent Workflow")
    st.markdown('<div class="card" style="background:#1a1a3e">Goal → Decide → Act → Observe →<br><b style="color:#60a5fa">Continue/Complete</b></div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><span class="dot-green"></span> Short-Term Memory: Active (last 3)</div>', unsafe_allow_html=True)
    tokens = calc_tokens()
    st.markdown(f'<div class="card"><span class="dot-yellow"></span> Rate Limit: {tokens}/8192 tokens</div>', unsafe_allow_html=True)
    st.markdown('<div class="card" style="background:#2a1a1a"><span>🔁</span> Retry: 1x on fail - Ready</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("### 🔒 Free AI Firewall")
    st.markdown('<div class="card"><span class="dot-green"></span> <b>PROTECTED • Blinking</b><br><div style="height:6px;background:#3b82f6;border-radius:6px;margin-top:8px"></div><br><small>Layers: Injection Filter, Intent Analysis, Output Sanitizer</small></div>', unsafe_allow_html=True)
    st.markdown("### 🛡️ OWASP Guardrails")
    st.markdown('<span class="dot-green"></span> Prompt Injection: Active<br><span class="dot-green"></span> System Prompt Leakage: Active<br><span class="dot-green"></span> Improper Output Handling: Active', unsafe_allow_html=True)
