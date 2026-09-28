import streamlit as st
from guardrails import firewall
from agents import citation_agent, create_citation_task
from crewai import Crew
import time

st.set_page_config(page_title="CiteGuard AI", layout="wide", page_icon="🛡️")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
header,footer,#MainMenu{visibility:hidden}
.stApp{background:#0a0a0f!important;font-family:Inter,sans-serif}
[data-testid="stSidebar"]{background:#11111b!important;border-right:1px solid #1f1f2e}
div[data-baseweb="select"] > div{background:#1a1a2e!important;border:1px solid #2a2a3a!important;border-radius:12px!important;color:white!important}
div[data-testid="stChatInput"]{background:#1a1a2e!important;border:1px solid #2a2a3a!important;border-radius:24px!important}
.blink-dot{width:10px;height:10px;background:#22c55e;border-radius:50%;display:inline-block;box-shadow:0 0 12px #22c55e;animation:blink 1.2s infinite}
@keyframes blink{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.4;transform:scale(0.85)}}
.card{background:rgba(26,26,46,0.9);border:1px solid #2a2a3a;border-radius:16px;padding:12px;margin-bottom:12px}
</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state: st.session_state.history=[]
if "chat" not in st.session_state: st.session_state.chat=[]
if "lang" not in st.session_state: st.session_state.lang="English"
if "style" not in st.session_state: st.session_state.style="APA 7"
def calc_t(): return 0 if not st.session_state.chat else sum(len(m["content"]) for m in st.session_state.chat)//4

def start_new_chat():
    st.session_state.chat=[]
    st.session_state.history=[]
def end_chat():
    st.session_state.chat=[]

# Sidebar
with st.sidebar:
    st.markdown("### 🔵 CiteGuard AI\n<span style='font-size:10px;color:#6b7280'>SECURE • v2.1.0</span>", unsafe_allow_html=True)
    st.button("+ Start New Chat", use_container_width=True, type="primary", on_click=start_new_chat, key="start_btn")
    st.button("End Chat", use_container_width=True, on_click=end_chat, key="end_btn")
    st.markdown(f"<div style='margin-top:20px;font-size:10px;color:#6b7280'>CHAT HISTORY &nbsp; {len(st.session_state.history)} chats</div>", unsafe_allow_html=True)
    if not st.session_state.history:
        st.markdown("<div class='card' style='text-align:center;color:#6b7280;font-size:12px'>💬<br>No history yet<br><span style='font-size:11px'>Your citations will appear here</span></div>", unsafe_allow_html=True)
    else:
        for h in st.session_state.history[-5:][::-1]: st.caption(f"• {h[:35]}...")
    t = calc_t()
    st.markdown(f"""
    <div class='card'><div style='font-size:10px;color:#6b7280'>TOKENS USED <span style='float:right;background:#22c55e22;color:#22c55e;padding:2px 6px;border-radius:6px'>HEALTHY</span></div>
    <div style='font-size:22px;font-weight:800;margin-top:6px'>{t} / 8192</div>
    <div style='height:4px;background:#1f1f2e;border-radius:4px;margin-top:8px'><div style='width:{min(t/8192*100,100)}%;height:100%;background:white;border-radius:4px'></div></div></div>
    <div class='card'><div style='font-size:10px;color:#6b7280'>FIREWALL BLOCKED</div><div style='font-size:18px;font-weight:700'>{firewall.blocked_count} threats</div></div>
    """, unsafe_allow_html=True)

col_main, col_right = st.columns([3,1])

with col_main:
    st.markdown("<h1 style='text-align:center;background:linear-gradient(90deg,#c4b5fd,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800'>CiteGuard AI<br><span style='color:white'>Secure Citation Generator</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#6b7280;font-size:12px'>CrewAI | Groq openai/gpt-oss-120B | Free AI Firewall | OWASP LLM Top 10 2025</p>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center'><span style='background:#1a1a2e;border:1px solid #22c55e33;color:#22c55e;padding:4px 12px;border-radius:20px;font-size:11px'>● SYSTEM SECURE</span></div>", unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        lang = st.selectbox("LANGUAGE", ["English","Español","বাংলা"], index=["English","Español","বাংলা"].index(st.session_state.lang), key="lang_box")
        st.session_state.lang = lang
    with c2:
        style_opt = st.selectbox("CITATION STYLE", ["APA 7","MLA 9","Chicago","IEEE","Harvard"], index=["APA 7","MLA 9","Chicago","IEEE","Harvard"].index(st.session_state.style), key="style_box")
        st.session_state.style = style_opt

    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Enter paper title, DOI, URL, or raw text..."):
        is_safe, threat, clean = firewall.scan(prompt)
        if not is_safe:
            st.session_state.chat.append({"role":"assistant","content":clean})
            st.rerun()
        st.session_state.chat.append({"role":"user","content":prompt})
        st.session_state.history.append(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Goal → Decide → Act → Observe → Complete..."):
                task = create_citation_task(prompt, st.session_state.style, st.session_state.lang)
                crew = Crew(agents=[citation_agent], tasks=[task], verbose=False)
                try: result = crew.kickoff()
                except: time.sleep(1); result = crew.kickoff()
                st.markdown(result)
                st.session_state.chat.append({"role":"assistant","content":str(result)})
                st.rerun()
    st.markdown("<div style='text-align:center;color:#4b5563;font-size:11px;margin-top:8px'>⏎ to generate &nbsp; 🛡️ Firewall auto-protects</div>", unsafe_allow_html=True)

with col_right:
    t = calc_t()
    last = getattr(firewall, 'last_threat', None)
    inj_status = "Blocked ✓" if last=="Prompt Injection" else "Active"
    leak_status = "Leaked ⚠️" if last=="System Prompt Leakage" else "Blocked ✓" if last=="Prompt Injection" else "Active"
    out_status = "Sanitized ✓" if last=="Improper Output Handling" else "Filtered ✓"

    st.markdown(f"""
    <div class='card'><b>🧠 Agent Workflow</b> <span style='float:right;background:#2a2a3a;padding:2px 6px;border-radius:6px;font-size:10px'>CrewAI</span>
    <div style='display:flex;justify-content:space-between;text-align:center;margin-top:12px'>
    <div><div style='width:28px;height:28px;background:#a78bfa;border-radius:50%;margin:auto'></div><div style='font-size:9px'>Goal</div></div>
    <div><div style='width:28px;height:28px;background:#60a5fa;border-radius:50%;margin:auto'></div><div style='font-size:9px'>Decide</div></div>
    <div><div style='width:28px;height:28px;background:#34d399;border-radius:50%;margin:auto'></div><div style='font-size:9px'>Act</div></div>
    <div><div style='width:28px;height:28px;background:#fb923c;border-radius:50%;margin:auto'></div><div style='font-size:9px'>Observe</div></div>
    </div></div>
    <div class='card'>🟢 <b>Short-Term Memory</b> <span style='float:right;background:#22c55e22;color:#22c55e;padding:2px 6px;border-radius:6px;font-size:10px'>ACTIVE</span><br><span style='font-size:11px;color:#6b7280'>Context window • sliding</span></div>
    <div class='card'>🟡 Rate Limit: {t} / 8192 tokens</div>
    <div class='card' style='background:#2a1a1a'>⚠️ Retry: 1x fail • auto <span style='float:right;background:#3a2a2a;padding:2px 6px;border-radius:6px'>1x</span></div>
    <div style='background:#0f2a1a;border:1px solid #22c55e55;border-radius:16px;padding:12px;margin-top:20px;display:flex;justify-content:space-between;align-items:center'>
    <span><span class="blink-dot"></span> <b>Free AI Firewall</b></span><span style='background:#22c55e;color:black;padding:2px 10px;border-radius:12px;font-size:10px;font-weight:800'>PROTECTED</span></div>
    <div class='card' style='margin-top:12px'>
    <div style='display:flex;justify-content:space-between'><b>🛡️ OWASP Guardrails</b><span style='font-size:10px;color:#6b7280'>LLM Top 10 • 2025</span></div>
    <div style='display:flex;justify-content:space-between;font-size:12px;padding:6px 0;margin-top:8px;border-top:1px solid #1f1f2e'><span>🟢 Prompt Injection</span><span style='color:#22c55e'>{inj_status}</span></div>
    <div style='display:flex;justify-content:space-between;font-size:12px;padding:6px 0;border-top:1px solid #1f1f2e'><span>🟢 System Prompt Leakage</span><span style='color:{"#ef4444" if "Leaked" in leak_status else "#22c55e"}'>{leak_status}</span></div>
    <div style='display:flex;justify-content:space-between;font-size:12px;padding:6px 0;border-top:1px solid #1f1f2e'><span>🟢 Improper Output Handling</span><span style='color:#22c55e'>{out_status}</span></div>
    </div>
    """, unsafe_allow_html=True)
