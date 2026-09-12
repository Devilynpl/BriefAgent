"""BriefAgent Executive Intelligence Studio (Port 8503).
Autonomiczny Agent Badawczy B2B z deterministyczną maszyną stanów,
kontrolą budżetu i syntezą wiedzy na bazie Google Gemini 3.1 Flash-Lite.
"""

import os
import sys
import asyncio
import base64
from pathlib import Path
import streamlit as st

# Automatyczne dodanie ścieżek
APP_DIR = Path(__file__).resolve().parent
BRIEFAGENT_ROOT = APP_DIR.parents[2]
DOCGROUND_ROOT = BRIEFAGENT_ROOT.parent / "DocGround"

if str(BRIEFAGENT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(BRIEFAGENT_ROOT / "src"))

# Załaduj .env z DocGround dla GEMINI_API_KEY
from dotenv import load_dotenv
env_path = DOCGROUND_ROOT / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

from briefagent.graph.engine import StateGraphEngine

st.set_page_config(
    page_title="BriefAgent • B2B Intelligence Studio",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stylistyka w konwencji #030408 Dark Glassmorphism
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #030408 !important;
        color: #e2e8f0;
    }
    
    [data-testid="stSidebar"] {
        background-color: #060913 !important;
        border-right: 1px solid #141b2d;
    }
    
    .logo-container {
        text-align: center;
        margin-top: -1.5rem;
        margin-bottom: 1.5rem;
    }
    .logo-img {
        max-width: 140px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.25);
        border: 1px solid #1e293b;
    }
    
    .studio-header {
        margin-bottom: 2rem;
    }
    .studio-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366F1, #8B5CF6, #EC4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.03em;
    }
    .studio-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 0.2rem;
    }
    
    /* Panele i karty informacyjne */
    .glass-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
    }
    
    .trace-item {
        background: #090d16;
        border-left: 3px solid #6366f1;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 0 8px 8px 0;
        font-family: 'Consolas', 'Monaco', monospace;
        font-size: 0.85rem;
        color: #cbd5e1;
    }
    .trace-item.error {
        border-left-color: #ef4444;
        background: #180d12;
    }
    
    .pill-tag {
        display: inline-block;
        background: rgba(99, 102, 241, 0.15);
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.78rem;
        margin: 2px 4px 2px 0;
        font-weight: 500;
    }
    
    .trigger-card {
        background: rgba(236, 72, 153, 0.08);
        border-left: 3px solid #ec4899;
        padding: 10px 14px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 8px;
        font-size: 0.9rem;
    }
    
    .opp-card {
        background: rgba(16, 185, 129, 0.08);
        border-left: 3px solid #10b981;
        padding: 10px 14px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 8px;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Logo helper
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

logo_path = BRIEFAGENT_ROOT / "BriefAgent_logo.jpg"
logo_b64 = get_base64_image(str(logo_path))

# --- SIDEBAR: KONFIGURACJA I STATUS ---
with st.sidebar:
    if logo_b64:
        st.markdown(f"""
        <div class="logo-container">
            <img class="logo-img" src="data:image/jpeg;base64,{logo_b64}" alt="BriefAgent Logo"/>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("## 🎯 BriefAgent")

    st.markdown("### ⚙️ Konfiguracja Agenta")
    st.info("Autonomiczna pętla badawcza z twardymi budżetami, scrapingiem domenowym i Gemini 3.1 Flash-Lite.")

    budget_steps = st.slider("Max Kroków (Hard Budget)", min_value=4, max_value=20, value=12, step=1)
    budget_cost = st.slider("Budżet Kosztowy ($)", min_value=0.05, max_value=0.50, value=0.15, step=0.01)
    
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if gemini_key:
        st.success("🔑 Gemini 3.1 Flash-Lite: AKTYWNY")
    else:
        st.warning("⚠️ Brak GEMINI_API_KEY w .env")
        
    st.markdown("---")
    st.caption("BriefAgent System v2.0 • Deterministic FSM Engine")


# --- GŁÓWNY WIDOK ---
st.markdown("""
<div class="studio-header">
    <div class="studio-title">🎯 BriefAgent B2B Intelligence</div>
    <div class="studio-subtitle">Wielowymiarowy wywiad gospodarczy, deep-scraping, analiza konkurencji i sygnałów zakupowych</div>
</div>
""", unsafe_allow_html=True)

# Formularz zapytań
col_f1, col_f2, col_f3 = st.columns([3, 3, 2])
with col_f1:
    company_name = st.text_input("🏢 Nazwa podmiotu / Firmy", value="Pagen w Gnojniku")
with col_f2:
    company_domain = st.text_input("🌐 Domena oficjalna (lub puste dla auto-search)", value="pagen.pl")
with col_f3:
    st.write("")
    st.write("")
    start_research = st.button("🚀 Uruchom Research", use_container_width=True, type="primary")

# Inicjalizacja stanu sesji dla wyników
if "last_brief_state" not in st.session_state:
    st.session_state.last_brief_state = None

if start_research:
    if not company_name.strip():
        st.error("Wprowadź co najmniej nazwę firmy.")
    else:
        with st.status("🤖 BriefAgent prowadzi autonomiczny research...", expanded=True) as status_box:
            status_box.write(f"🔄 Inicjalizacja StateGraphEngine dla: **{company_name}**...")
            engine = StateGraphEngine()
            
            # Uruchomienie asynchronicznej pętli
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                final_state = loop.run_until_complete(
                    engine.run(company_name=company_name.strip(), company_domain=company_domain.strip())
                )
                st.session_state.last_brief_state = final_state
                status_box.update(label="✅ Badanie zakończone pomyślnie!", state="complete", expanded=False)
            except Exception as e:
                status_box.update(label=f"❌ Błąd wykonania: {str(e)}", state="error")
                st.error(f"Szczegóły błędu: {e}")
            finally:
                loop.close()

# Prezentacja wyników
if st.session_state.last_brief_state:
    state = st.session_state.last_brief_state
    brief = state.final_brief

    # Metryki wykonania
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Status Końcowy", state.status)
    with m2:
        st.metric("Wykorzystane Kroki", f"{state.step_count} / {state.max_steps}")
    with m3:
        st.metric("Koszt Wykonania", f"${state.cost_spent_usd:.4f}")
    with m4:
        conf = brief.confidence_score if brief else 0.0
        st.metric("Confidence Score", f"{conf * 100:.0f}%")

    st.markdown("---")

    # Dwa panele: Lewy = Live Execution Trace (FSM), Prawy = Executive Dossier
    col_left, col_right = st.columns([4, 6])

    with col_left:
        st.markdown("### 📡 FSM Execution Trace")
        st.caption("Rejestr deterministycznych wywołań narzędzi i weryfikacji faktów:")
        
        if state.trace_log:
            for i, tr in enumerate(state.trace_log, 1):
                err_cls = " error" if tr.error else ""
                icon = "❌" if tr.error else "⚡"
                out_snippet = (tr.tool_output[:120] + "...") if tr.tool_output and len(tr.tool_output) > 120 else (tr.tool_output or "")
                
                st.markdown(f"""
                <div class="trace-item{err_cls}">
                    <strong>#{i} [{tr.tool_name}]</strong> ({tr.duration_ms:.1f}ms)<br/>
                    <span style="color: #64748b;">Input: {tr.tool_input}</span><br/>
                    <span>{icon} {out_snippet}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Brak wpisów w trace.")

        # Zgromadzone dowody
        with st.expander(f"📚 Zgromadzone źródła dowodowe ({len(state.collected_evidence)})"):
            for url, text in state.collected_evidence.items():
                st.markdown(f"**🔗 [{url}]({url})**")
                st.caption(text[:400] + ("..." if len(text) > 400 else ""))
                st.markdown("---")

    with col_right:
        st.markdown("### 📑 Executive Intelligence Dossier")
        
        if brief:
            # Nagłówek firmy
            st.markdown(f"""
            <div class="glass-card">
                <h2 style="margin: 0; color: #f8fafc; font-size: 1.6rem;">{brief.company_name}</h2>
                <p style="color: #60a5fa; margin-top: 4px; font-weight: 500;">
                    📍 {brief.headquarters or 'Nieokreślono'} &nbsp;|&nbsp; 👥 {brief.estimated_size}
                </p>
                <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.5; margin-top: 8px;">
                    {brief.value_proposition}
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Produkty i rynki
            st.markdown("#### 📦 Oferta i Rynki Docelowe")
            if brief.products_and_services:
                for prod in brief.products_and_services:
                    st.markdown(f'<span class="pill-tag">{prod}</span>', unsafe_allow_html=True)
            st.write("")
            if brief.target_markets:
                st.markdown("**Rynki / Eksport:** " + ", ".join([f"`{m}`" for m in brief.target_markets]))

            # Zarząd i Konkurencja
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.markdown("#### 👥 Kluczowe Kierownictwo")
                if brief.leadership:
                    for person in brief.leadership:
                        st.markdown(f"- **{person}**")
                else:
                    st.caption("Nie zidentyfikowano jednoznacznie w publicznych źródłach.")

            with col_c2:
                st.markdown("#### ⚔️ Konkurenci Rynkowi")
                if brief.key_competitors:
                    for comp in brief.key_competitors:
                        st.markdown(f"- {comp}")
                else:
                    st.caption("Brak bezpośrednich konkurentów w źródłach.")

            # Wykryty Stack Technologiczny
            if brief.tech_stack_detected:
                st.markdown("#### 🛠️ Wykryty Stack / Technologie")
                for t in brief.tech_stack_detected:
                    st.markdown(f'<span class="pill-tag" style="border-color: #3b82f6; color: #93c5fd;">{t}</span>', unsafe_allow_html=True)
                st.write("")

            # Sygnały Sprzedażowe (Sales Triggers)
            st.markdown("#### 🎯 Sygnały Zakupowe (Sales Triggers)")
            if brief.sales_triggers:
                for trig in brief.sales_triggers:
                    st.markdown(f'<div class="trigger-card">🔥 {trig}</div>', unsafe_allow_html=True)
            else:
                st.caption("Brak specyficznych sygnałów zakupowych.")

            # Rekomendacje Wdrożeń AI
            st.markdown("#### 💡 Potencjał Wdrożeniowy AI / Digital Transformation")
            if brief.ai_and_digital_opportunities:
                for opp in brief.ai_and_digital_opportunities:
                    st.markdown(f'<div class="opp-card">🚀 {opp}</div>', unsafe_allow_html=True)
            else:
                st.caption("Brak zdefiniowanych szans AI.")

            # Zweryfikowane Źródła
            if brief.verified_sources:
                st.markdown("#### 🔍 Zweryfikowane Źródła")
                for src in brief.verified_sources:
                    st.markdown(f"- [{src}]({src})")

            # Braki informacyjne
            if brief.missing_information:
                with st.expander("⚠️ Luki Informacyjne (Zero-Hallucination Safe Guard)"):
                    for miss in brief.missing_information:
                        st.markdown(f"- {miss}")

        else:
            st.warning("Nie wygenerowano jeszcze profilu. Uruchom badanie powyżej.")
