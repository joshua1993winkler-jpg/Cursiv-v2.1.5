"""
Cursiv v2.1.5 — Sacred UI

The Recoding Temple aesthetic: Black • Rose Gold • Glowing Lapis Eye

Sections:
  The Forge        — Create agents from JSON packets
  The Academy      — Track agent evolution
  The Council      — Deliberate and synthesize
  The Dugout       — Browse agent lineage
  The Weave        — Transitionary composition
  The Wiki         — Living knowledge base
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Relative imports fail when Streamlit runs this file as __main__.
# Add the repo root to sys.path so cursiv_v215 is importable absolutely.
_REPO_ROOT = Path(__file__).parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    import streamlit as st
except ImportError:
    print("Streamlit not installed. Run: pip install streamlit")
    sys.exit(1)


# ── Sacred Color Palette ──────────────────────────────────────────────────────
SACRED = {
    "void":       "#0A0B0D",
    "rose_gold":  "#C9A227",
    "gold":       "#D4AF37",
    "lapis":      "#1E4D8C",
    "lapis_glow": "#2E6DC7",
    "cream":      "#F5EFE4",
    "deep":       "#12131A",
    "surface":    "#1A1B23",
}

EYE_SVG = """<svg viewBox="0 0 100 50" xmlns="http://www.w3.org/2000/svg" width="120" height="60">
  <ellipse cx="50" cy="25" rx="48" ry="22" fill="none" stroke="#C9A227" stroke-width="1.5"/>
  <circle cx="50" cy="25" r="14" fill="none" stroke="#1E4D8C" stroke-width="1.5"/>
  <circle cx="50" cy="25" r="8" fill="#1E4D8C" opacity="0.8"/>
  <circle cx="50" cy="25" r="4" fill="#2E6DC7"/>
  <circle cx="46" cy="22" r="2" fill="white" opacity="0.6"/>
  <line x1="2" y1="25" x2="22" y2="25" stroke="#C9A227" stroke-width="0.8" opacity="0.6"/>
  <line x1="78" y1="25" x2="98" y2="25" stroke="#C9A227" stroke-width="0.8" opacity="0.6"/>
</svg>"""

SACRED_CSS = f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=EB+Garamond:ital,wght@0,400;0,500;1,400&display=swap');

  .stApp {{
    background-color: {SACRED['void']};
    color: {SACRED['cream']};
  }}

  .stSidebar {{
    background-color: {SACRED['deep']} !important;
    border-right: 1px solid {SACRED['rose_gold']}44;
  }}

  h1, h2, h3 {{
    font-family: 'Cinzel', serif !important;
    color: {SACRED['rose_gold']} !important;
    letter-spacing: 0.05em;
  }}

  p, li, label {{
    font-family: 'EB Garamond', serif !important;
    color: {SACRED['cream']} !important;
    font-size: 1.05rem;
  }}

  .stButton > button {{
    background: linear-gradient(135deg, {SACRED['lapis']}, {SACRED['lapis_glow']});
    color: {SACRED['cream']};
    border: 1px solid {SACRED['rose_gold']}88;
    border-radius: 4px;
    font-family: 'Cinzel', serif;
    letter-spacing: 0.08em;
    transition: all 0.3s ease;
  }}

  .stButton > button:hover {{
    background: linear-gradient(135deg, {SACRED['lapis_glow']}, {SACRED['lapis']});
    border-color: {SACRED['rose_gold']};
    box-shadow: 0 0 12px {SACRED['lapis_glow']}66;
  }}

  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea {{
    background-color: {SACRED['surface']};
    color: {SACRED['cream']};
    border: 1px solid {SACRED['rose_gold']}44;
    font-family: 'EB Garamond', serif;
    border-radius: 4px;
  }}

  .stSelectbox > div > div {{
    background-color: {SACRED['surface']};
    color: {SACRED['cream']};
    border: 1px solid {SACRED['rose_gold']}44;
  }}

  .stTab > button {{
    font-family: 'Cinzel', serif !important;
    color: {SACRED['cream']}88 !important;
    letter-spacing: 0.05em;
  }}

  .stTab > button[aria-selected="true"] {{
    color: {SACRED['rose_gold']} !important;
    border-bottom: 2px solid {SACRED['rose_gold']};
  }}

  .agent-card {{
    background: {SACRED['surface']};
    border: 1px solid {SACRED['rose_gold']}33;
    border-radius: 6px;
    padding: 1rem;
    margin: 0.5rem 0;
    font-family: 'EB Garamond', serif;
  }}

  .phase-badge {{
    display: inline-block;
    background: {SACRED['lapis']};
    color: {SACRED['cream']};
    border-radius: 3px;
    padding: 2px 8px;
    font-size: 0.8rem;
    font-family: 'Cinzel', serif;
    margin: 2px;
  }}

  .seal {{
    font-family: monospace;
    color: {SACRED['rose_gold']};
    font-size: 0.8rem;
    letter-spacing: 0.05em;
  }}

  .state-nascent   {{ color: #888; }}
  .state-learning  {{ color: {SACRED['gold']}; }}
  .state-alive     {{ color: #4CAF50; }}
  .state-evolved   {{ color: {SACRED['rose_gold']}; }}
  .state-sovereign {{ color: {SACRED['lapis_glow']}; font-weight: bold; }}

  .divider {{
    border: none;
    border-top: 1px solid {SACRED['rose_gold']}22;
    margin: 1.5rem 0;
  }}

  blockquote {{
    border-left: 3px solid {SACRED['rose_gold']};
    padding-left: 1rem;
    color: {SACRED['cream']}aa;
    font-style: italic;
  }}
</style>
"""


def setup_page() -> None:
    st.set_page_config(
        page_title="Cursiv — The Sovereign Temple",
        page_icon="👁",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(SACRED_CSS, unsafe_allow_html=True)


def render_header() -> None:
    col1, col2 = st.columns([1, 8])
    with col1:
        st.markdown(EYE_SVG, unsafe_allow_html=True)
    with col2:
        st.markdown("# Cursiv v2.1.5")
        st.markdown(
            f'<p style="color: {SACRED["rose_gold"]}88; font-style: italic; margin-top: -0.5rem;">'
            "The Sovereign Agent Temple — Black • Rose Gold • Glowing Lapis Eye"
            "</p>",
            unsafe_allow_html=True,
        )
    st.markdown('<hr class="divider">', unsafe_allow_html=True)


def render_forge() -> None:
    st.markdown("## The Forge")
    st.markdown("> *Create agents from JSON knowledge. Every agent begins as raw strand.*")

    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("### Upload Knowledge Packet")
        uploaded = st.file_uploader("JSON knowledge packet", type=["json"])
        agent_name = st.text_input("Agent name (optional — uses packet name if empty)")
        mode = st.selectbox("Academy mode", ["Full (8 phases)", "Quick (4 phases)"])

        if uploaded and st.button("Forge Agent"):
            try:
                knowledge = json.loads(uploaded.read().decode("utf-8"))
                name = agent_name or uploaded.name.replace(".json", "")
                with st.spinner("Forging... The Academy is running."):
                    from cursiv_v215.forge.factory import AgentFactory
                    from cursiv_v215.forge.router import OracleRouter
                    router = OracleRouter()
                    factory = AgentFactory(router=router)
                    progress_container = st.empty()

                    phases_completed = []

                    def on_phase(phase: str, num: int) -> None:
                        phases_completed.append(phase)
                        progress_container.markdown(
                            " ".join(f'<span class="phase-badge">{p}</span>' for p in phases_completed),
                            unsafe_allow_html=True,
                        )

                    if "Quick" in mode:
                        agent = factory.quick_create(knowledge, name)
                    else:
                        agent = factory.create_from_dict(knowledge, name, on_phase=on_phase)

                st.success(f"Agent forged: **{agent.name}** [{agent.state.value}]")
                st.markdown(f'<span class="seal">Seal: {agent.sovereign_seal[:32]}...</span>', unsafe_allow_html=True)
                st.session_state["last_agent_id"] = agent.id
            except Exception as e:
                st.error(f"Forge failed: {e}")

    with col2:
        st.markdown("### Quick Create from Text")
        knowledge_text = st.text_area("Paste knowledge (JSON or plain text)", height=200)
        quick_name = st.text_input("Name", key="quick_name")
        if knowledge_text and quick_name and st.button("Quick Forge"):
            try:
                try:
                    knowledge = json.loads(knowledge_text)
                except Exception:
                    knowledge = {"content": knowledge_text}
                from cursiv_v215.forge.factory import AgentFactory
                factory = AgentFactory()
                agent = factory.quick_create(knowledge, quick_name)
                st.success(f"Quick-forged: {agent.name}")
            except Exception as e:
                st.error(f"Error: {e}")


def render_academy() -> None:
    st.markdown("## The Academy")
    st.markdown("> *8 phases of evolution. Phase 8 has context from all 7 prior. This is genuine learning.*")

    from cursiv_v215.dugout.vault import AgentVault
    vault = AgentVault()
    agents = vault.list_agents()

    if not agents:
        st.info("No agents in the vault yet. Visit The Forge to create your first agent.")
        return

    for agent_meta in agents:
        state = agent_meta.get("state", "nascent")
        state_class = f"state-{state}"
        with st.expander(f"**{agent_meta['name']}** — [{state}]"):
            agent = vault.load(agent_meta["id"])
            if not agent:
                continue
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Above:** {agent.above or '—'}")
                st.markdown(f"**Beneath:** {agent.beneath or '—'}")
                st.markdown(f"**Council position:** {agent.council_position or '—'}")
            with col2:
                st.markdown(f"**Capabilities ({len(agent.capabilities)}):**")
                for cap in agent.capabilities[:5]:
                    st.markdown(f"  - {cap}")
            if agent.academy_phases:
                st.markdown("**Academy phases completed:**")
                phases = list(agent.academy_phases.keys())
                st.markdown(
                    " ".join(f'<span class="phase-badge">{p}</span>' for p in phases),
                    unsafe_allow_html=True,
                )
            quality = agent.memory.get("quality_score", 0)
            if quality:
                st.progress(quality, text=f"Quality: {quality:.1%}")


def render_council() -> None:
    st.markdown("## The Council")
    st.markdown("> *14 agents deliberate. 4 synthesize. The rest advise in silence.*")

    from cursiv_v215.dugout.vault import AgentVault
    vault = AgentVault()
    agents = vault.list_agents()

    if not agents:
        st.info("No agents available for council deliberation.")
        return

    agent_options = {f"{a['name']} ({a['id'][:8]})": a["id"] for a in agents}
    selected = st.selectbox("Select agent", list(agent_options.keys()))
    query = st.text_area("Query for council deliberation", height=100)

    col1, col2 = st.columns(2)
    with col1:
        use_council = st.checkbox("Full 14-agent council", value=True)
    with col2:
        pass

    if query and st.button("Deliberate"):
        agent_id = agent_options[selected]
        with st.spinner("Council in session..."):
            from cursiv_v215.forge.chat import AgentChat
            chat = AgentChat(use_council=use_council)
            result = chat.chat(agent_id, query)

        st.markdown("### Council Response")
        st.markdown(result.get("response", "No response"))
        st.caption(f"Provider: {result.get('provider', 'unknown')} | Quality: {result.get('quality', 0):.2f} | Memory hits: {result.get('memory_hits', 0)}")

        if use_council and result.get("council"):
            with st.expander("Internal perspectives (the 10 advising agents)"):
                for name, perspective in result["council"].get("internal_perspectives", {}).items():
                    st.markdown(f"**{name}:** {perspective}")


def render_dugout() -> None:
    st.markdown("## The Dugout")
    st.markdown("> *Every agent version preserved. No work is ever lost.*")

    from cursiv_v215.dugout.vault import AgentVault
    vault = AgentVault()
    agents = vault.list_agents()

    if not agents:
        st.info("The vault is empty.")
        return

    for agent_meta in agents:
        lineage = vault.get_lineage(agent_meta["id"])
        with st.expander(f"**{agent_meta['name']}** — {len(lineage)} version(s)"):
            for v in lineage:
                st.markdown(
                    f"  `{v['version']}` — {v['state']} — seal: `{v['seal']}...`"
                )
            if st.button(f"Revert {agent_meta['name']}", key=f"revert_{agent_meta['id']}"):
                st.warning("Revert: select version number")
                version = st.number_input("Version number", min_value=1, max_value=len(lineage), key=f"v_{agent_meta['id']}")
                if st.button("Confirm revert", key=f"confirm_{agent_meta['id']}"):
                    reverted = vault.revert(agent_meta["id"], int(version))
                    if reverted:
                        st.success(f"Reverted to v{version}")


def render_weave() -> None:
    st.markdown("## The Transitionary Weave")
    st.markdown("> *7 stages. Human approval at Stage 5 and Stage 7. No agent enters production without your hand.*")

    stages = [
        ("1. Intent Declaration", "State the purpose of this composition"),
        ("2. Constitutional Check", "Automated — Codex V2 alignment verified"),
        ("3. Council Deliberation", "Automated — 14 agents deliberate"),
        ("4. Synthesis", "Automated — 4 synthesizing agents compile output"),
        ("5. Sovereign Review", "**YOU** review the synthesis — real pause"),
        ("6. Seal", "Automated — cryptographic proof generated"),
        ("7. Commit", "**YOU** give final approval — agent enters production"),
    ]

    for stage, desc in stages:
        st.markdown(f"**{stage}** — {desc}")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("### Begin a Weave")

    from cursiv_v215.dugout.vault import AgentVault
    vault = AgentVault()
    agents = vault.list_agents()

    if not agents:
        st.info("Create agents in The Forge before running a weave.")
        return

    agent_options = {f"{a['name']} ({a['id'][:8]})": a["id"] for a in agents}
    selected = st.selectbox("Agent to compose", list(agent_options.keys()), key="weave_agent")
    intent = st.text_area("Intent declaration — why is this composition needed?", height=80)

    if intent and st.button("Begin Weave"):
        agent_id = agent_options[selected]
        agent = vault.load(agent_id)
        if not agent:
            st.error("Agent not found")
            return

        from cursiv_v215.weave.transitionary import TransitionaryWeave
        weave = TransitionaryWeave()
        session = weave.begin(agent_id, intent)

        session = weave.constitutional_check(session, agent.to_dict())
        if session.constitutional_ok:
            st.success("Stage 2: Constitutional check PASSED")
        else:
            st.error(f"Stage 2: Constitutional violations: {session.constitutional_violations}")
            return

        st.info("Stage 3 + 4: Council deliberating...")
        session = weave.council_deliberate(session, {
            "name": agent.name, "domain": agent.knowledge_map.get("domain", ""),
        })
        session = weave.synthesize(session)
        st.markdown("### Stage 4 Synthesis")
        st.markdown(session.synthesis or "[No synthesis]")

        st.markdown("---")
        st.markdown("### Stage 5: Sovereign Review")
        st.markdown("Review the synthesis above. Do you approve?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Approve — proceed to seal"):
                try:
                    session = weave.sovereign_review(session, human_approved=True)
                    session = weave.seal_agent(session, agent.to_dict())
                    st.success(f"Stage 6: Seal generated — `{session.seal[:32]}...`")
                    st.session_state["pending_weave"] = session
                except Exception as e:
                    st.error(str(e))
        with col2:
            if st.button("Reject — restart weave"):
                st.warning("Weave rejected. Begin again.")

    if "pending_weave" in st.session_state:
        st.markdown("### Stage 7: Final Commit")
        session = st.session_state["pending_weave"]
        col1, col2 = st.columns(2)
        with col1:
            if st.button("COMMIT — enter production"):
                try:
                    weave = TransitionaryWeave()
                    weave._sessions[session.weave_id] = session
                    session = weave.commit(session, human_final_approved=True)
                    st.success("Agent committed to production. The weave is complete.")
                    del st.session_state["pending_weave"]
                except Exception as e:
                    st.error(str(e))
        with col2:
            if st.button("Abort commit"):
                del st.session_state["pending_weave"]
                st.warning("Commit aborted.")


def render_wiki() -> None:
    st.markdown("## The Living Wiki")
    st.markdown("> *Knowledge that links itself. Add an entry — the wiki finds its connections.*")

    from cursiv_v215.knowledge.wiki import KnowledgeWiki
    wiki = KnowledgeWiki()

    col1, col2 = st.columns([2, 3])
    with col1:
        st.markdown("### Add Entry")
        title = st.text_input("Title")
        content = st.text_area("Content", height=150)
        tags_raw = st.text_input("Tags (comma-separated)")
        source = st.text_input("Source (optional)")
        if title and content and st.button("Add to Wiki"):
            tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
            entry_id = wiki.add_entry(title, content, tags=tags, source=source)
            wiki.save()
            st.success(f"Added: {entry_id}")

    with col2:
        st.markdown("### Search")
        query = st.text_input("Search wiki", key="wiki_search")
        if query:
            results = wiki.search(query)
            if results:
                for r in results:
                    with st.expander(f"**{r['title']}**"):
                        st.markdown(r["content"][:500])
                        if r["tags"]:
                            st.markdown(f"Tags: {', '.join(r['tags'])}")
                        if r["linked_to"]:
                            st.markdown(f"Linked to: {len(r['linked_to'])} entries")
            else:
                st.info("No results found.")

        stats = wiki.stats()
        st.markdown(f"Wiki: **{stats['entries']}** entries • **{stats['links']}** links • **{stats['index_terms']}** indexed terms")


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown(EYE_SVG, unsafe_allow_html=True)
        st.markdown("### Navigation")
        section = st.radio(
            "",
            ["The Forge", "The Academy", "The Council", "The Dugout", "The Weave", "The Wiki"],
            label_visibility="collapsed",
        )
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown(f"""
<div style="font-size:0.75rem; color: {SACRED['rose_gold']}88;">
<strong>Permanent Central Leader</strong><br>
Joshua Winkler<br><br>
<strong>Constitutional Status</strong><br>
✓ Local-first active<br>
✓ Human sovereignty enforced<br>
✓ Identity drift monitoring ON
</div>
""", unsafe_allow_html=True)
        return section


def main() -> None:
    setup_page()
    section = render_sidebar()
    render_header()

    if section == "The Forge":
        render_forge()
    elif section == "The Academy":
        render_academy()
    elif section == "The Council":
        render_council()
    elif section == "The Dugout":
        render_dugout()
    elif section == "The Weave":
        render_weave()
    elif section == "The Wiki":
        render_wiki()


if __name__ == "__main__":
    main()
