import streamlit as st
from guardrails import firewall
from agents import citation_agent, create_citation_task
from crewai import Crew
import time

st.set_page_config(page_title="CiteGuard AI", layout="wide", page_icon="🛡️")

# --- FINAL PRODUCTION CSS (king.PNG replica) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
header,footer,#MainMenu{visibility:hidden}
.stApp{background:#07070c!important;font-family:Inter,sans-serif}
[data-testid="stSidebar"]{background:#0f0f18!important;border-right:1px solid #1e1e2e}

/* ORANGE GRADIENT Start New Chat - FIXES YOUR still_missing.PNG */
div[data-testid="stSidebar"] div[data-testid="stButton"]:first-of-type button{
  background: linear-gradient(90deg,#FF4D1F 0%,#FF8C1F 100%)!important;
  color:white!important; border:none!important; border-radius:12px!important;
  font-weight:800!important; height:44px!important;
  box-shadow:0 4px 24px rgba(255,77,31,0.45)!important;
}
div[data-testid="stSidebar"] div[data-testid="stButton"]:nth-of-type(2) button{
  background:#171725!important; color:#9ca3af!important;
  border:1px solid #2a2a3a!important; border-radius:12px!important; height:40px!important;
}
div[data-baseweb="select"] > div{
  background:#1e1e2e!important; border:1px solid #2a2a3a!important;
  border-radius:12px!important; color:white!important;
}
div[data-testid="stChatInput"]{
  background:#1c1c2b!important; border:1px solid #2e2e44!important;
  border-radius:28px!important; box-shadow:0 0 0 4px rgba(139,92,246,0.08)!important;
}
.blink-dot{width:8px;height:8px;background:#22c55e;border-radius:50%;display:inline-block;box-shadow:0 0 12px #22c55e;animation:blink 1.2s infinite}
@keyframes blink{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.3;transform:scale(0.8)}}
.card{background:rgba(24,24,40,0.9);border:1px solid #252542;border-radius:16px;padding:12px;margin-bottom:12px}
.glow{position:absolute;top:-100px;left:50%;transform:translateX(-50%);width:600px;height:300px;background:radial-gradient(ellipse,rgba(99,102,241,0.18) 0%,transparent 70%);pointer-events:none}
</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state: st.session_state.history=[]
if "chat" not in st.session_state: st.session_state.chat=[]
if "lang" not in st.session_state: st.session_state.lang="English"
if "style" not in st.session_state: st.session_state.style="APA 7"

def calc_t(): return 0 if not st.session_state.chat else sum(len(m["content"]) for m in st.session_state.chat)//4
def start_new(): st.session_state.chat=[]; st.session_state.history=[]; firewall.last_threat=None
def end_chat(): st.session_state.chat=[]

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("""
    <div style='display:flex;align-items:center;gap:8px'>
      <div style='width:28px;height:28px;background:#3b82f6;border-radius:8px;display:flex;align-items:center;justify-content:center'>🛡️</div>
      <b style='color:white;line-height:1.1'>CiteGuard AI<br><span style='font-size:9px;color:#6b7280;font-weight:400'>SECURE • v2.1.0</span></b>
      <span style='margin-left:auto'><span class='blink-dot'></span></span>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    st.button("+ Start New Chat", use_container_width=True, on_click=start_new, key="start")
    st.button("End Chat", use_container_width=True, on_click=end_chat, key="end")
    st.markdown(f"<div style='margin-top:16px;font-size:10px;color:#5a5a6e;letter-spacing:0.6px'>CHAT HISTORY &nbsp; {len(st.session_state.history)} chats</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:#141422;border:1px solid #1e1e2e;border-radius:16px;padding:28px 10px;text-align:center;margin-top:8px'>
      <div style='width:36px;height:36px;background:#1e1e2e;border-radius:10px;margin:0 auto;line-height:36px'>💬</div>
      <div style='color:#6b7280;font-size:12px;margin-top:12px'>No history yet</div>
      <div style='color:#3a3a4a;font-size:10px;margin-top:4px'>Your citations will appear<br>here after generation</div>
    </div>
    """, unsafe_allow_html=True)
    t=calc_t()
    st.markdown(f"""
    <div class='card' style='margin-top:16px'>
      <div style='font-size:9px;color:#5a5a6e;display:flex;justify-content:space-between'><span>⚡ TOKENS USED</span><span style='background:#16a34a22;color:#22c55e;padding:2px 6px;border-radius:6px'>HEALTHY</span></div>
      <div style='font-size:20px;font-weight:800;color:white;margin-top:6px'>{t} / 8192</div>
      <div style='display:flex;justify-content:space-between;font-size:9px;color:#3a3a4a;margin-top:6px'><span>0% used</span><span>8192 max</span></div>
      <div style='height:3px;background:#1e1e2e;border-radius:3px;margin-top:6px'><div style='width:{min(t/8192*100,100)}%;height:100%;background:white;border-radius:3px'></div></div>
    </div>
    <div style='background:#141422;border:1px solid #1e1e2e;border-radius:12px;padding:10px;margin-top:10px'>
      <div style='font-size:9px;color:#5a5a6e'>FIREWALL BLOCKED</div><div style='font-size:13px;font-weight:700;color:white'>{firewall.blocked_count} threats</div>
    </div>
    """, unsafe_allow_html=True)

# ============ MAIN + RIGHT ============
col_main, col_right = st.columns([3,1])

with col_main:
    st.markdown("""
    <div style='position:relative;text-align:center;padding-top:10px'>
      <div class='glow'></div>
      <h1 style='font-size:40px;font-weight:800;line-height:1.05;margin:0;position:relative'>
        <span style='background:linear-gradient(90deg,#d8b4fe 0%,#a78bfa 50%,#93c5fd 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent'>CiteGuard AI</span><br>
        <span style='color:white'>Secure Citation Generator</span>
      </h1>
      <p style='color:#6b7280;font-size:11px;margin-top:10px'>CrewAI | Groq openai/gpt-oss-120B | Free AI Firewall | OWASP LLM Top 10 2025</p>
      <div style='margin:10px auto;background:#1c1c2b;border:1px solid rgba(34,197,94,0.2);color:#22c55e;padding:3px 10px;border-radius:16px;width:fit-content;font-size:10px'><span class='blink-dot' style='width:6px;height:6px'></span> SYSTEM SECURE</div>
    </div>
    """, unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        lang = st.selectbox("LANGUAGE", ["🇺🇸 English","🇪🇸 Español","🇧🇩 বাংলা"], index=0, key="lang")
        st.session_state.lang = "English" if "English" in lang else lang
    with c2:
        style_opt = st.selectbox("CITATION STYLE", ["APA 7","MLA 9","Chicago","IEEE","Harvard"], index=0, key="style")
        st.session_state.style = style_opt

    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Enter paper title, DOI, URL, or raw text..."):
        ok, threat, clean = firewall.scan(prompt)
        if not ok:
            st.session_state.chat.append({"role":"assistant","content":clean})
            st.rerun()
        st.session_state.chat.append({"role":"user","content":prompt})
        st.session_state.history.append(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Goal → Decide → Act → Observe → Complete..."):
                task = create_citation_task(prompt, st.session_state.style, st.session_state.lang)
                crew = Crew(agents=[citation_agent], tasks=[task], verbose=False)
                try: res = crew.kickoff()
                except Exception:
                    time.sleep(1)
                    try: res = crew.kickoff()
                    except Exception as e: res = f"⚠️ Error: {e}"
                st.markdown(res)
                st.session_state.chat.append({"role":"assistant","content":str(res)})
                st.rerun()

    st.markdown("""
    <div style='text-align:center;margin-top:8px;color:#3a3a4a;font-size:11px'>↩ to generate &nbsp; 🛡️ Firewall auto-protects</div>
    <div style='display:flex;gap:8px;justify-content:center;margin-top:14px'>
      <div style='background:#1a1a28;border:1px solid #252542;border-radius:10px;padding:6px 12px;font-size:11px;color:#6b7280'>🔗 DOI<br><span style='color:#9ca3af'>10.1234/examp...</span></div>
      <div style='background:#1a1a28;border:1px solid #252542;border-radius:10px;padding:6px 12px;font-size:11px;color:#6b7280'>🌐 URL<br><span style='color:#9ca3af'>arxiv.org/abs/...</span></div>
      <div style='background:#1a1a28;border:1px solid #252542;border-radius:10px;padding:6px 12px;font-size:11px;color:#6b7280'>📄 RAW<br><span style='color:#9ca3af'>Paste abstract..</span></div>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    last = getattr(firewall,'last_threat',None)
    inj_text = "Blocked ✓" if last=="Prompt Injection" else "Active"
    leak_text = "Leaked ⚠️" if last=="System Prompt Leakage" else "Filtered ✓"
    t=calc_t()
    st.markdown(f"""
    <div class='card'><div style='display:flex;justify-content:space-between;font-size:11px'><b>🧩 Agent Workflow</b><span style='background:#1e1e2e;padding:2px 6px;border-radius:6px;font-size:9px'>CrewAI</span></div>
      <div style='display:flex;justify-content:space-between;text-align:center;margin-top:12px'>
        <div><div style='width:30px;height:30px;background:#c4b5fd;border-radius:50%;margin:auto'></div><div style='font-size:8px;color:#9ca3af;margin-top:4px'>Goal</div></div>
        <div><div style='width:30px;height:30px;background:#93c5fd;border-radius:50%;margin:auto'></div><div style='font-size:8px;color:#9ca3af;margin-top:4px'>Decide</div></div>
        <div><div style='width:30px;height:30px;background:#6ee7b7;border-radius:50%;margin:auto'></div><div style='font-size:8px;color:#9ca3af;margin-top:4px'>Act</div></div>
        <div><div style='width:30px;height:30px;background:#fdba74;border-radius:50%;margin:auto'></div><div style='font-size:8px;color:#9ca3af;margin-top:4px'>Observe</div></div>
      </div>
      <div style='background:#1e1e2e;border-radius:8px;padding:4px;text-align:center;margin-top:10px;font-size:10px;color:#60a5fa'>↻ Continue / Complete</div>
      <div style='display:flex;justify-content:space-between;font-size:8px;color:#5a5a6e;margin-top:8px'><span>Running ReAct</span><span>Loop: max 5</span><span>Tools: 4 active</span></div>
    </div>
    <div class='card'><div style='font-size:11px'><span class='blink-dot'></span> Short-Term Memory <span style='float:right;background:#22c55e22;color:#22c55e;padding:2px 6px;border-radius:6px;font-size:9px'>ACTIVE</span></div><div style='font-size:9px;color:#5a5a6e;margin-top:4px'>Context window • sliding</div></div>
    <div class='card' style='background:#1a1a0a'><span style='width:8px;height:8px;background:#eab308;border-radius:50%;display:inline-block'></span> Rate Limit: {t} / 8192 tokens</div>
    <div class='card' style='background:#221515'>⚠️ Retry: 1x fail • auto <span style='float:right;background:#2a1a1a;padding:2px 6px;border-radius:6px'>1x</span></div>
    <div style='background:#0f2318;border:1px solid #1a3a24;border-radius:16px;padding:10px;margin-top:12px;display:flex;justify-content:space-between;align-items:center;font-size:11px'>
      <span><span class='blink-dot'></span> Free AI Firewall</span><span style='background:#22c55e;color:black;padding:2px 8px;border-radius:10px;font-size:9px;font-weight:800'>PROTECTED</span>
    </div>
    <div class='card' style='margin-top:12px'>
      <div style='display:flex;justify-content:space-between'><b>🛡️ OWASP Guardrails</b><span style='font-size:8px;color:#5a5a6e'>LLM Top 10 • 2025</span></div>
      <div style='display:flex;justify-content:space-between;font-size:11px;margin-top:10px;padding-top:8px;border-top:1px solid #1e1e2e'><span><span class='blink-dot'></span> Prompt Injection</span><span style='color:#22c55e'>{inj_text}</span></div>
      <div style='display:flex;justify-content:space-between;font-size:11px;margin-top:8px'><span><span class='blink-dot'></span> Sensitive Data Disclosure</span><span style='color:#22c55e'>{leak_text}</span></div>
      <div style='display:flex;justify-content:space-between;font-size:11px;margin-top:8px'><span><span class='blink-dot'></span> Improper Output Handling</span><span style='color:#22c55e'>Filtered ✓</span></div>
    </div>
    """, unsafe_allow_html=True)
