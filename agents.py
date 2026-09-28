import litellm
_orig_c = litellm.completion
_orig_ac = litellm.acompletion
def _clean(msgs):
    if isinstance(msgs, list):
        for m in msgs:
            if isinstance(m, dict):
                m.pop("cache_breakpoint", None)
                m.pop("cache_control", None)
    return msgs
def _pc(*a, **k):
    if "messages" in k: k["messages"] = _clean(k["messages"])
    elif a and isinstance(a[0], list): a = (_clean(a[0]),) + a[1:]
    k.pop("cache_control", None); k.pop("cache_breakpoint", None)
    return _orig_c(*a, **k)
async def _pac(*a, **k):
    if "messages" in k: k["messages"] = _clean(k["messages"])
    elif a and isinstance(a[0], list): a = (_clean(a[0]),) + a[1:]
    k.pop("cache_control", None); k.pop("cache_breakpoint", None)
    return await _orig_ac(*a, **k)
litellm.completion = _pc
litellm.acompletion = _pac

from crewai import Agent, Task, LLM

llm = LLM(model="groq/openai/gpt-oss-120b", temperature=0.0)

citation_agent = Agent(
    role="Secure Citation Expert - Zero Hallucination",
    goal="Generate 100% accurate citations with NO fake DOIs, NO fake URLs",
    backstory="""You are CiteGuard AI, strict academic librarian.
    CRITICAL RULES:
    1. NEVER invent a DOI. If user didn't give DOI and you are not 100% sure, write "DOI: Not available"
    2. For 'Attention is all you need' - there is NO DOI. Use arXiv:1706.03762 and NeurIPS URL only.
    3. 10.5555/... is NOT a valid DOI - DO NOT USE IT EVER
    4. If unsure about any field, write "Not found in source" - don't guess
    5. Always prefer arXiv ID and official conference URL over fake DOI
    """,
    llm=llm, verbose=False, allow_delegation=False, max_iter=2, cache=False
)

def create_citation_task(user_input, style="APA 7", lang="English"):
    return Task(
        description=f"""
        Generate citation for: {user_input}
        Style: {style} | Language: {lang}

        ANTI-HALLUCINATION RULES (MANDATORY):
        - DO NOT create DOI like 10.5555/3295222.3295349 - it's FAKE
        - For Attention is all you need, correct output is:
          Vaswani et al. (2017). Attention is all you need. NeurIPS 30.
          URL: https://arxiv.org/abs/1706.03762
          URL: https://proceedings.neurips.cc/paper_files/paper/2017/hash/3f5ee243547dee91fbd053c1c4a845aa-Abstract.html
          DOI: Not available (NIPS does not assign DOI)
        - Only include DOI if user provided it AND it starts with 10. and is verifiable
        - Otherwise write: DOI: Not available
        - Never add https://doi.org/ link unless DOI is real

        Input: {user_input}
        """,
        expected_output=f"Accurate {style} citation in {lang} with NO fake DOI, with real arXiv URL",
        agent=citation_agent,
    )
