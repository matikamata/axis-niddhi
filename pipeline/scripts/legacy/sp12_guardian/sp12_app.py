# /beng-fut/pipeline/scripts/sp12_guardian/sp12_app.py
"""
💎 BRASILEIRINHO ENGINE — SP12 Guardian Review Tool
====================================================
Versão:  V5.3.0 — AXIS-NIDDHI
Módulo:  sp12_app.py — interface Streamlit

USO:
    streamlit run sp12_app.py
    # ou via alias:
    axis sp12
"""

import sys
from pathlib import Path

import streamlit as st

# ── Bootstrap path ────────────────────────────────────────────────
_HERE    = Path(__file__).resolve().parent
_SCRIPTS = _HERE.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from sp12_logic import (
    load_posts_for_review,
    action_approve,
    action_edit,
    action_add_note,
    action_fix_title_hash,
    world_map_status,
    bootstrap_status_column,
    VALID_STATUSES,
)

# ==============================================================================
# CONFIG
# ==============================================================================

st.set_page_config(
    page_title="SP12 — Guardião Review Tool",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS personalizado — tons indigo/dourado
st.markdown("""
<style>
    /* Fundo e tipografia base */
    .stApp { background-color: #0f0f1a; color: #e8e0ff; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #1a1a2e; }
    
    /* Títulos */
    h1, h2, h3 { color: #b8860b !important; font-family: Arial, sans-serif; }
    
    /* Botões de ação */
    .stButton > button {
        border-radius: 6px;
        font-weight: bold;
        border: 1px solid #3d0a91;
        background-color: #1a1a2e;
        color: #e8e0ff;
        width: 100%;
        padding: 8px;
        margin: 2px 0;
    }
    .stButton > button:hover { background-color: #3d0a91; color: white; }

    /* Áreas de texto */
    .stTextArea textarea {
        background-color: #1a1a2e;
        color: #e8e0ff;
        font-family: 'Georgia', serif;
        font-size: 14px;
        border: 1px solid #3d0a91;
    }

    /* Status badges */
    .badge-pending    { background:#555; color:white; padding:2px 8px; border-radius:10px; font-size:12px; }
    .badge-translated { background:#1a4a8a; color:white; padding:2px 8px; border-radius:10px; font-size:12px; }
    .badge-reviewed   { background:#7a4a00; color:white; padding:2px 8px; border-radius:10px; font-size:12px; }
    .badge-approved   { background:#1a5a2a; color:white; padding:2px 8px; border-radius:10px; font-size:12px; }

    /* Progress bars */
    .stProgress > div > div { background-color: #b8860b; }

    /* Separadores */
    hr { border-color: #3d0a91; }

    /* Coluna EN */
    .en-panel { background-color: #0d1117; border-left: 3px solid #3d0a91;
                padding: 12px; border-radius: 4px; }
    /* Coluna PT */
    .pt-panel { background-color: #0d1a0d; border-left: 3px solid #b8860b;
                padding: 12px; border-radius: 4px; }

    /* Mensagens de sucesso/erro */
    .msg-ok  { color: #50fa7b; font-weight: bold; }
    .msg-err { color: #ff5555; font-weight: bold; }

    /* PDPN tag */
    .pdpn-tag { font-family: monospace; font-size: 20px; color: #b8860b;
                font-weight: bold; letter-spacing: 2px; }
    .section-tag { font-size: 13px; color: #8888aa; margin-top: -8px; }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# SESSION STATE
# ==============================================================================

def init_state():
    if "posts" not in st.session_state:
        st.session_state.posts = []
    if "idx" not in st.session_state:
        st.session_state.idx = 0
    if "reviewer_id" not in st.session_state:
        st.session_state.reviewer_id = "guardian"
    if "last_msg" not in st.session_state:
        st.session_state.last_msg = None
    if "filter_status" not in st.session_state:
        st.session_state.filter_status = "translated"
    if "bootstrapped" not in st.session_state:
        n = bootstrap_status_column()
        st.session_state.bootstrapped = True
        st.session_state.bootstrap_msg = f"STATUS inicializado em {n} posts" if n else None

init_state()


# ==============================================================================
# SIDEBAR
# ==============================================================================

with st.sidebar:
    st.markdown("## 💎 SP12 · Guardião")
    st.markdown("---")

    # Reviewer ID
    reviewer_id = st.text_input(
        "🧑 Guardião ID",
        value=st.session_state.reviewer_id,
        help="Seu nome ou ID para registro no CLS"
    )
    st.session_state.reviewer_id = reviewer_id

    st.markdown("---")

    # Filtro de status
    st.markdown("**Filtrar por status**")
    filter_status = st.selectbox(
        "Status",
        options=["todos", "translated", "reviewed", "approved"],
        index=["todos","translated","reviewed","approved"].index(
            st.session_state.filter_status
        ),
        label_visibility="collapsed"
    )
    st.session_state.filter_status = filter_status

    # Carregar / recarregar posts
    if st.button("🔄 Carregar Posts", use_container_width=True):
        filt = None if filter_status == "todos" else filter_status
        posts = load_posts_for_review(status_filter=filt)
        st.session_state.posts = posts
        st.session_state.idx   = 0
        st.session_state.last_msg = f"✅ {len(posts)} posts carregados"

    st.markdown("---")

    # Navegação
    posts = st.session_state.posts
    n     = len(posts)

    if n > 0:
        st.markdown(f"**Post {st.session_state.idx + 1} de {n}**")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("◀ Anterior") and st.session_state.idx > 0:
                st.session_state.idx -= 1
                st.session_state.last_msg = None
        with col2:
            if st.button("Próximo ▶") and st.session_state.idx < n - 1:
                st.session_state.idx += 1
                st.session_state.last_msg = None

        # Mini índice
        st.markdown("---")
        st.markdown("**Posts neste lote:**")
        for i, p in enumerate(posts):
            label = f"{'▶ ' if i == st.session_state.idx else ''}{p['pdpn']} · {p['status']}"
            if st.button(label, key=f"nav_{i}", use_container_width=True):
                st.session_state.idx = i
                st.session_state.last_msg = None

    st.markdown("---")
    st.markdown("---")

    # ── World Map Status ──────────────────────────────────────────
    st.markdown("## 🗺️ World Map")
    if st.button("Atualizar mapa", use_container_width=True):
        wms = world_map_status()
        for sec in wms:
            if sec["total"] == 0:
                continue
            label = f"{sec['code']} · {sec['name'][:20]}"
            st.markdown(f"**{label}**")
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.progress(sec["translated_pct"] / 100,
                            text=f"{sec['translated_pct']}% trad · {sec['approved_pct']}% aprov")
            with col_b:
                st.markdown(f"<small>{sec['translated']}/{sec['total']}</small>",
                            unsafe_allow_html=True)


# ==============================================================================
# MAIN — PAINEL DE REVISÃO
# ==============================================================================

st.markdown("# 💎 SP12 — Guardião Review Tool")
st.markdown(f"*Sprint AXIS-NIDDHI V5.3 · Guardião: **{st.session_state.reviewer_id}***")

# Mensagem de bootstrap
if st.session_state.get("bootstrap_msg"):
    st.info(st.session_state.bootstrap_msg)

# Mensagem de ação anterior
if st.session_state.last_msg:
    if st.session_state.last_msg.startswith("✅"):
        st.success(st.session_state.last_msg)
    else:
        st.error(st.session_state.last_msg)

st.markdown("---")

posts = st.session_state.posts
if not posts:
    st.markdown("""
    ### 👋 Bem-vindo ao Console do Guardião
    
    Use o painel lateral para:
    1. Definir seu **Guardião ID**
    2. Escolher o filtro de status
    3. Clicar em **Carregar Posts**
    
    O sistema carregará os posts prontos para revisão.
    """)
    st.stop()

# Post atual
idx  = st.session_state.idx
post = posts[idx]

# ── Header do post ────────────────────────────────────────────────
col_id, col_sec, col_status = st.columns([2, 3, 2])
with col_id:
    st.markdown(f'<div class="pdpn-tag">{post["pdpn"]}</div>', unsafe_allow_html=True)
with col_sec:
    st.markdown(f'<div class="section-tag">📂 {post["section"]}</div>', unsafe_allow_html=True)
with col_status:
    badge = f'<span class="badge-{post["status"]}">{post["status"].upper()}</span>'
    st.markdown(badge, unsafe_allow_html=True)

# Títulos
st.markdown("---")
col_en_title, col_pt_title = st.columns(2)
with col_en_title:
    st.markdown(f"**🇬🇧 EN:** {post['en_title']}")
with col_pt_title:
    pt_title_input = st.text_input(
        "🇧🇷 PT (título editável):",
        value=post["pt_title"],
        key=f"title_{idx}",
        label_visibility="collapsed",
    )

st.markdown("---")

# ── Painel EN | PT ────────────────────────────────────────────────
col_en, col_pt = st.columns(2)

with col_en:
    st.markdown("### 🇬🇧 Original (EN)")
    # Strip HTML tags para leitura mais limpa
    import re as _re
    en_clean = _re.sub(r'<[^>]+>', '', post["en_content"])
    en_clean = _re.sub(r'<!--.*?-->', '', en_clean, flags=_re.DOTALL).strip()
    st.text_area(
        "EN",
        value=en_clean[:8000],  # limitar para não travar a UI
        height=500,
        disabled=True,
        key=f"en_{idx}",
        label_visibility="collapsed",
    )

with col_pt:
    st.markdown("### 🇧🇷 Tradução (PT) — editável")
    pt_clean = _re.sub(r'<[^>]+>', '', post["pt_content"])
    pt_clean = _re.sub(r'<!--.*?-->', '', pt_clean, flags=_re.DOTALL).strip()
    pt_edited = st.text_area(
        "PT",
        value=pt_clean[:8000],
        height=500,
        key=f"pt_{idx}",
        label_visibility="collapsed",
    )

st.markdown("---")

# ── Nota do Guardião ──────────────────────────────────────────────
note_text = st.text_input(
    "💬 Nota (opcional — registrada no CLS sem alterar status):",
    key=f"note_{idx}",
    placeholder="Ex: 'kāmachanda' deixado em Pāli — correto conforme glossário V5"
)

# ── Ações ─────────────────────────────────────────────────────────
st.markdown("### ⚡ Ações")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("✅ Approve", use_container_width=True):
        # Fix title hash antes de aprovar (se necessário)
        action_fix_title_hash(post)
        result = action_approve(post, reviewer_id=st.session_state.reviewer_id)
        st.session_state.last_msg = ("✅ " if result["ok"] else "❌ ") + result["msg"]
        if result["ok"]:
            post["status"] = "approved"
            # Avançar para próximo automaticamente
            if idx < len(posts) - 1:
                st.session_state.idx += 1
        st.rerun()

with col2:
    if st.button("✏️ Save Edit", use_container_width=True):
        result = action_edit(
            post,
            new_pt_content=pt_edited,
            new_pt_title=pt_title_input,
            reviewer_id=st.session_state.reviewer_id,
            note=note_text or "",
        )
        st.session_state.last_msg = ("✅ " if result["ok"] else "❌ ") + result["msg"]
        if result["ok"]:
            post["status"] = "reviewed"
        st.rerun()

with col3:
    if st.button("🔄 Fix Hash", use_container_width=True):
        result = action_fix_title_hash(post)
        st.session_state.last_msg = ("✅ " if result["ok"] else "❌ ") + result["msg"]
        st.rerun()

with col4:
    if st.button("💬 Add Note", use_container_width=True):
        if note_text.strip():
            result = action_add_note(post, note_text, reviewer_id=st.session_state.reviewer_id)
            st.session_state.last_msg = ("✅ " if result["ok"] else "❌ ") + result["msg"]
        else:
            st.session_state.last_msg = "❌ Digite uma nota antes de clicar"
        st.rerun()

with col5:
    if st.button("⏭️ Skip", use_container_width=True):
        if idx < len(posts) - 1:
            st.session_state.idx += 1
            st.session_state.last_msg = None
        else:
            st.session_state.last_msg = "✅ Último post do lote"
        st.rerun()

# ── Lineage atual ─────────────────────────────────────────────────
with st.expander("🔍 Lineage CLS atual (read-only)"):
    try:
        lin = post["identity"].get("lineage", {})
        st.json(lin)
    except Exception as e:
        st.error(str(e))
