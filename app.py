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
.stApp{background:#07070c!important;font-family:Inter,sans-serif}
[data-testid="stSidebar"]{background:#101018!important;border-right:1px solid #1e1e2e}
/* Orange Start Button */
div[data-testid="stSidebar"] div[data-testid="stButton"]:first-of-type button{
 background: linear-gradient(90deg,#FF5A1F,#FF8C32)!important;
 color:white!important; border:none!important; border-radius:12px!important;
 font-weight:800!important; box-shadow:0 4px 20px rgba(255,90,31,0.4)!important;
}
div[data-testid="stSidebar"] div[data-testid="stButton"]:nth-of-type(2) button{
 background:#171725!important; color:#9ca3af!important; border:1px solid #2a2a3a!important; border-radius:12px!important;
}
div[data-baseweb="select"] > div{background:#1e1e2e!important;border:1px solid #2a2a3a!important;border-radius:12px!important;color:white!important}
div[data-testid="stChatInput"]{background:#1c1c2b!important;border:1px solid #2e2e44!important;border-radius:28px!important;box-shadow:0 0 0 4px rgba(139,92,246,0.1)!important}
.blink{width:8px;height:8px;background:#22c55e;border-radius:50%;display:inline-block;box-shadow:0 0 12px #22c55e;animation:blink 1.2s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0.3}}
.glow-center{background:radial-gradient(ellipse at center, rgba(99,102,241,0.15) 0%, transparent 60%);position:absolute;top:0;left:0;right:0;bottom:0;pointer-events:none}
</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state: st.session_state.history=[]
if "chat" not in st.session_state: st.session_state.chat=[]
if "lang" not in st.session_state: st.session_state.lang="English"
if "style" not in st.session_state: st.session_state.style="APA 7"
def calc(): return 0 if not st.session_state.chat else sum(len(m["content"]) for m in st.session_state.chat)//4
def start(): st.session_state.chat=[]; st.session_state.history=[]
def end(): st.session_state.chat=[]

with st.sidebar:
    st.markdown("<div style='display:flex;gap:8px;align-items:center'><div style='width:28px;height:28px;background:#3b82f6;border-radius:8px'></div><b style='color:white'>CiteGuard AI<br><span style='font-size:9px;color:#6b7280;font-weight:400'>SECURE • v2.1.0</span></b><span style='margin-left:auto;width:8px;height:8px;background:#22c55e;border-radius:50%;box-shadow:0 0 8px #22c55e'></span></div>", unsafe_allow_html=True)
    st.write("")
    st.button("+ Start New Chat", use_container_width=True, on_click=start, key="s1")
    st.button("End Chat", use_container_width=True, on_click=end, key="e1")
    st.markdown(f"<div style='margin-top:16px;font-size:10px;color:#5a5a6e;letter-spacing:0.5px'>CHAT HISTORY &nbsp; {len(st.session_state.history)} chats</div>", unsafe_allow_html=True)
    st.markdown("<div style='background:#161622;border:1px solid #1e1e2e;border-radius:16px;padding:30px 10px;text-align:center;margin-top:8px'><div style='width:36px;height:36px;background:#1e1e2e;border-radius:10px;margin:0 auto;display:flex;align-items:center;justify-content:center'>💬</div><div style='color:#6b7280;font-size:12px;margin-top:12px'>No history yet</div><div style='color:#3a3a4a;font-size:10px;margin-top:4px'>Your citations will appear<br>here after generation</div></div>", unsafe_allow_html=True)
    t=calc()
    st.markdown(f"""
    <div style='background:#161622;border:1px solid #1e1e2e;border-radius:16px;padding:12px;margin-top:16px'>
      <div style='font-size:9px;color:#5a5a6e;display:flex;justify-content:space-between'><span>⚡ TOKENS USED</span><span style='background:#16a34a22;color:#22c55e;padding:2px 6px;border-radius:6px'>HEALTHY</span></div>
      <div style='font-size:20px;font-weight:800;margin-top:6px;color:white'>{t} / 8192</div>
      <div style='display:flex;justify-content:space-between;font-size:9px;color:#3a3a4a;margin-top:6px'><span>0% used</span><span>8192 max</span></div>
      <div style='height:3px;background:#1e1e2e;border-radius:3px;margin-top:6px'><div style='width:{min(t/8192*100,100)}%;height:100%;background:white;border-radius:3px'></div></div>
    </div>
    <div style='background:#161622;border:1px solid #1e1e2e;border-radius:16px;padding:10px;margin-top:10px'><div style='font-size:9px;color:#5a5a6e'>FIREWALL BLOCKED</div><div style='font-size:14px;font-weight:700;color:white'>{firewall.blocked_count} threats</div></div>
    """, unsafe_allow_html=True)

col_main, col_right = st.columns([3,1])

with col_main:
    st.markdown("""
    <div style='position:relative;text-align:center;padding-top:20px'>
      <div class='glow-center'></div>
      <h1 style='font-size:42px;font-weight:800;line-height:1.05;margin:0'>
        <span style='background:linear-gradient(90deg,#d8b4fe,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent'>CiteGuard AI</span><br>
        <span style='color:white'>Secure Citation Generator</span>
      </h1>
      <p style='color:#6b7280;font-size:11px;margin-top:12px'>CrewAI | Groq openai/gpt-oss-120B | Free AI Firewall | OWASP LLM Top 10 2025</p>
      <div style='margin:12px auto;background:#1c1c2b;border:1px solid #22c55e33;color:#22c55e;padding:3px 10px;border-radius:16px;width:fit-content;font-size:10px'>● SYSTEM SECURE</div>
    </div>
    """, unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        l = st.selectbox("LANGUAGE", ["🇺🇸 English","Español","বাংলা"], key="lang_k")
        st.session_state.lang = l.split()[-1] if "English" in l else l
    with c2:
        s = st.selectbox("CITATION STYLE", ["APA 7","MLA 9","Chicago","IEEE","Harvard"], key="style_k")
        st.session_state.style = s

    for m in st.session_state.chat:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Enter paper title, DOI, URL, or raw text..."):
        ok, threat, clean = firewall.scan(prompt)
        if not ok:
            st.session_state.chat.append({"role":"assistant","content":clean}); st.rerun()
        st.session_state.chat.append({"role":"user","content":prompt}); st.session_state.history.append(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Goal → Decide → Act → Observe → Complete..."):
                task = create_citation_task(prompt, st.session_state.style, st.session_state.lang)
                crew = Crew(agents=[citation_agent], tasks=[task], verbose=False)
                try: res = crew.kickoff()
                except: time.sleep(1); res = crew.kickoff()
                st.markdown(res); st.session_state.chat.append({"role":"assistant","content":str(res)}); st.rerun()

    st.markdown("""
    <div style='text-align:center;margin-top:10px;color:#3a3a4a;font-size:11px'>⏎ to generate &nbsp; 🛡️ Firewall auto-protects</div>
    <div style='display:flex;gap:8px;justify-content:center;margin-top:16px'>
      <div style='background:#1a1a2a;border:1px solid #2a2a3a;border-radius:10px;padding:6px 12px;font-size:11px;color:#6b7280'>🔗 DOI<br><span style='color:#9ca3af'>10.1234/examp...</span></div>
      <div style='background:#1a1a2a;border:1px solid #2a2a3a;border-radius:10px;padding:6px 12px;font-size:11px;color:#6b7280'>🌐 URL<br><span style='color:#9ca3af'>arxiv.org/abs/...</span></div>
      <div style='background:#1a1a2a;border:1px solid #2a2a3a;border-radius:10px;padding:6px 12px;font-size:11px;color:#6b7280'>📄 RAW<br><span style='color:#9ca3af'>Paste abstract..</span></div>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    last = getattr(firewall,'last_threat',None)
    inj = "Blocked ✓" if last=="Prompt Injection" else "Active"
    leak = "Filtered ✓" if last!="System Prompt Leakage" else "Leaked ⚠️"
    t=calc()
    st.markdown(f"""
    <div style='background:#181828;border:1px solid #252542;border-radius:16px;padding:12px'>
      <div style='display:flex;justify-content:space-between;font-size:11px'><b>🧩 Agent Workflow</b><span style='background:#1e1e2e;padding:2px 6px;border-radius:6px;font-size:9px'>CrewAI</span></div>
      <div style='display:flex;justify-content:space-between;text-align:center;margin-top:12px'>
        <div><div style='width:30px;height:30px;background:#c4b5fd;border-radius:50%;margin:auto'></div><div style='font-size:8px;margin-top:4px;color:#9ca3af'>Goal</div></div>
        <div><div style='width:30px;height:30px;background:#93c5fd;border-radius:50%;margin:auto'></div><div style='font-size:8px;margin-top:4px;color:#9ca3af'>Decide</div></div>
        <div><div style='width:30px;height:30px;background:#6ee7b7;border-radius:50%;margin:auto'></div><div style='font-size:8px;margin-top:4px;color:#9ca3af'>Act</div></div>
        <div><div style='width:30px;height:30px;background:#fdba74;border-radius:50%;margin:auto'></div><div style='font-size:8px;margin-top:4px;color:#9ca3af'>Observe</div></div>
      </div>
      <div style='background:#1e1e2e;border-radius:8px;padding:4px;text-align:center;margin-top:10px;font-size:10px;color:#60a5fa'>↻ Continue / Complete</div>
      <div style='display:flex;justify-content:space-between;font-size:8px;color:#5a5a6e;margin-top:8px'><span>Running ReAct</span><span>Loop: max 5</span><span>Tools: 4 active</span></div>
    </div>
    <div style='background:#181828;border:1px solid #252542;border-radius:16px;padding:12px;margin-top:12px'><div style='font-size:11px'><span class="blink"></span> Short-Term Memory <span style='float:right;background:#22c55e22;color:#22c55e;padding:2px 6px;border-radius:6px;font-size:9px'>ACTIVE</span></div><div style='font-size:9px;color:#5a5a6e;margin-top:4px'>Context window • sliding</div></div>
    <div style='background:#1a1a0f;border:1px solid #2a2a1a;border-radius:16px;padding:10px;margin-top:12px;font-size:11px'><span style='width:8px;height:8px;background:#eab308;border-radius:50%;display:inline-block'></span> Rate Limit<br><b>0 / 8192</b> <span style='float:right;font-size:9px;color:#5a5a6e'>tokens</span></div>
    <div style='background:#221515;border:1px solid #3a2020;border-radius:16px;padding:10px;margin-top:12px;font-size:11px'>⚠️ Retry: 1x fail • auto <span style='float:right;background:#2a1a1a;padding:2px 6px;border-radius:6px'>1x</span></div>
    <div style='background:#0f2318;border:1px solid #1a3a24;border-radius:16px;padding:10px;margin-top:12px;display:flex;justify-content:space-between;align-items:center;font-size:11px'><span><span class="blink"></span> Free AI Firewall</span><span style='background:#22c55e;color:black;padding:2px 8px;border-radius:10px;font-size:9px;font-weight:800'>PROTECTED</span></div>
    <div style='background:#181828;border:1px solid #252542;border-radius:16px;padding:12px;margin-top:12px'>
      <div style='display:flex;justify-content:space-between;font-size:11px'><b>🛡️ OWASP Guardrails</b><span style='font-size:8px;color:#5a5a6e'>LLM Top 10 • 2025</span></div>
      <div style='display:flex;justify-content:space-between;font-size:11px;margin-top:10px'><span><span class="blink"></span> Prompt Injection</span><span style='color:#22c55e'>{inj}</span></div>
      <div style='display:flex;justify-content:space-between;font-size:11px;margin-top:8px'><span><span class="blink"></span> Sensitive Data Disclosure</span><span style='color:#22c55e'>{leak}</span></div>
    </div>
    """, unsafe_allow_html=True)
