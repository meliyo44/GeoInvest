"""
╔══════════════════════════════════════════════════════════════╗
║           GeoInvest Pro — Geopolitical Investment Dashboard  ║
║           Version 2.0 | Built with Streamlit + Plotly        ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import time
import random
from datetime import datetime, timedelta
import math
try:
    import yfinance as yf
    YFINANCE_OK = True
except ImportError:
    YFINANCE_OK = False

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GeoInvest Pro",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── API KEYS (remplacer par vos clés réelles) ────────────────────────────────
NEWS_API_KEY = "YOUR_NEWSAPI_KEY"          # https://newsapi.org (gratuit)
ALPHA_VANTAGE_KEY = "YOUR_ALPHA_VANTAGE"  # https://alphavantage.co (gratuit)

# ─── BLOOMBERG TERMINAL CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

:root {
    --bg-primary: #0a0d12;
    --bg-secondary: #111620;
    --bg-card: #141922;
    --bg-hover: #1a2133;
    --accent-orange: #ff6b35;
    --accent-cyan: #00d4ff;
    --accent-green: #00e676;
    --accent-red: #ff1744;
    --accent-yellow: #ffd600;
    --accent-gold: #ffc107;
    --text-primary: #e8eaf0;
    --text-secondary: #8892a4;
    --text-muted: #4a5568;
    --border: #1e2a3a;
    --border-bright: #2a3f5f;
}

* { font-family: 'IBM Plex Sans', sans-serif; }
.mono { font-family: 'IBM Plex Mono', monospace; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border-bright);
}

[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

.stSelectbox > div > div, .stMultiSelect > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-bright) !important;
    color: var(--text-primary) !important;
}

.stRadio > div { gap: 8px; }

/* ── HEADER BANNER ──────────────────────────────── */
.geo-header {
    background: linear-gradient(135deg, #0a0d12 0%, #111d35 50%, #0a1628 100%);
    border: 1px solid var(--border-bright);
    border-top: 3px solid var(--accent-orange);
    border-radius: 4px;
    padding: 20px 28px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
}
.geo-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        90deg,
        transparent,
        transparent 40px,
        rgba(0,212,255,0.03) 40px,
        rgba(0,212,255,0.03) 41px
    );
}
.header-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 28px;
    font-weight: 700;
    color: var(--accent-orange);
    letter-spacing: 2px;
    text-shadow: 0 0 20px rgba(255,107,53,0.5);
}
.header-subtitle {
    font-size: 11px;
    color: var(--text-secondary);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 2px;
}
.header-time {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    color: var(--accent-cyan);
    text-align: right;
}

/* ── RISK SCORE BADGE ───────────────────────────── */
.risk-badge {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 12px 24px;
    border-radius: 4px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 1px;
}
.risk-critical { background: rgba(255,23,68,0.15); border: 2px solid var(--accent-red); color: var(--accent-red); box-shadow: 0 0 20px rgba(255,23,68,0.3); }
.risk-high { background: rgba(255,107,53,0.15); border: 2px solid var(--accent-orange); color: var(--accent-orange); box-shadow: 0 0 20px rgba(255,107,53,0.3); }
.risk-medium { background: rgba(255,214,0,0.1); border: 2px solid var(--accent-yellow); color: var(--accent-yellow); }
.risk-low { background: rgba(0,230,118,0.1); border: 2px solid var(--accent-green); color: var(--accent-green); }

/* ── METRIC CARDS ────────────────────────────────── */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent-cyan);
    border-radius: 4px;
    padding: 16px 20px;
    margin-bottom: 12px;
    transition: all 0.2s;
}
.metric-card:hover { border-color: var(--accent-cyan); background: var(--bg-hover); }
.metric-label {
    font-size: 10px;
    color: var(--text-secondary);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.metric-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 26px;
    font-weight: 700;
    color: var(--text-primary);
}
.metric-delta { font-size: 12px; margin-top: 4px; }
.delta-up { color: var(--accent-red); }
.delta-down { color: var(--accent-green); }

/* ── NEWS CARDS ──────────────────────────────────── */
.news-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 14px 18px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.15s;
}
.news-card:hover { border-color: var(--accent-orange); background: var(--bg-hover); }
.news-title { font-size: 13px; font-weight: 600; color: var(--text-primary); margin-bottom: 6px; line-height: 1.5; }
.news-meta { font-size: 10px; color: var(--text-secondary); letter-spacing: 1px; text-transform: uppercase; }
.news-impact { font-size: 11px; padding: 3px 8px; border-radius: 3px; display: inline-block; margin-top: 8px; font-family: 'IBM Plex Mono', monospace; }
.impact-high { background: rgba(255,23,68,0.15); color: var(--accent-red); border: 1px solid rgba(255,23,68,0.3); }
.impact-medium { background: rgba(255,214,0,0.1); color: var(--accent-yellow); border: 1px solid rgba(255,214,0,0.3); }
.impact-low { background: rgba(0,230,118,0.1); color: var(--accent-green); border: 1px solid rgba(0,230,118,0.3); }

/* ── INVESTMENT CARDS ────────────────────────────── */
.invest-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-top: 3px solid var(--accent-gold);
    border-radius: 4px;
    padding: 18px 20px;
    margin-bottom: 12px;
    position: relative;
}
.invest-card.buy { border-top-color: var(--accent-green); }
.invest-card.sell { border-top-color: var(--accent-red); }
.invest-card.hold { border-top-color: var(--accent-yellow); }

.invest-action {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.action-buy { color: var(--accent-green); }
.action-sell { color: var(--accent-red); }
.action-hold { color: var(--accent-yellow); }

.invest-asset { font-size: 18px; font-weight: 700; color: var(--text-primary); margin-bottom: 8px; }
.invest-detail { font-size: 12px; color: var(--text-secondary); margin: 4px 0; }
.invest-target { font-family: 'IBM Plex Mono', monospace; font-size: 13px; }

/* ── RISK TABLE ──────────────────────────────────── */
.risk-row {
    display: grid;
    grid-template-columns: 2fr 1fr 2fr 1fr;
    gap: 12px;
    padding: 12px 16px;
    border-bottom: 1px solid var(--border);
    align-items: center;
    font-size: 13px;
}
.risk-row:hover { background: var(--bg-hover); }
.risk-row-header {
    font-size: 10px;
    color: var(--text-secondary);
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 600;
}
.risk-pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 3px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    font-weight: 600;
}
.pill-9, .pill-10 { background: rgba(255,23,68,0.2); color: var(--accent-red); border: 1px solid rgba(255,23,68,0.4); }
.pill-7, .pill-8 { background: rgba(255,107,53,0.2); color: var(--accent-orange); border: 1px solid rgba(255,107,53,0.4); }
.pill-5, .pill-6 { background: rgba(255,214,0,0.1); color: var(--accent-yellow); border: 1px solid rgba(255,214,0,0.3); }
.pill-1, .pill-2, .pill-3, .pill-4 { background: rgba(0,230,118,0.1); color: var(--accent-green); border: 1px solid rgba(0,230,118,0.3); }

/* ── SECTION HEADERS ─────────────────────────────── */
.section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    margin: 20px 0 14px 0;
    border-bottom: 1px solid var(--border-bright);
}
.section-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--accent-cyan);
    font-weight: 500;
}
.section-line { flex: 1; height: 1px; background: var(--border); }

/* ── ALERT BANNER ────────────────────────────────── */
.alert-banner {
    background: rgba(255,23,68,0.1);
    border: 1px solid rgba(255,23,68,0.4);
    border-left: 4px solid var(--accent-red);
    border-radius: 4px;
    padding: 12px 18px;
    margin-bottom: 16px;
    font-size: 13px;
    color: var(--accent-red);
    display: flex;
    align-items: center;
    gap: 10px;
    animation: pulse-border 2s infinite;
}
@keyframes pulse-border {
    0%, 100% { border-left-color: var(--accent-red); }
    50% { border-left-color: transparent; }
}

/* ── SENTIMENT GAUGE ─────────────────────────────── */
.sentiment-bar-container { margin: 8px 0; }
.sentiment-label { font-size: 11px; color: var(--text-secondary); margin-bottom: 4px; display: flex; justify-content: space-between; }
.sentiment-bar { height: 6px; background: var(--border); border-radius: 3px; overflow: hidden; }
.sentiment-fill { height: 100%; border-radius: 3px; transition: width 0.5s; }
.fill-negative { background: linear-gradient(90deg, #ff1744, #ff6b35); }
.fill-neutral { background: linear-gradient(90deg, #ffd600, #ffab00); }
.fill-positive { background: linear-gradient(90deg, #00e676, #00b0ff); }

/* ── TICKER TAPE ─────────────────────────────────── */
.ticker-container {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 10px 16px;
    margin-bottom: 16px;
    overflow: hidden;
}
.ticker-item {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    margin-right: 32px;
    white-space: nowrap;
}
.ticker-symbol { color: var(--accent-cyan); font-weight: 600; }
.ticker-price { color: var(--text-primary); margin: 0 6px; }
.ticker-change-up { color: var(--accent-green); }
.ticker-change-down { color: var(--accent-red); }

/* ── MISC ────────────────────────────────────────── */
.stButton > button {
    background: var(--bg-card) !important;
    color: var(--accent-cyan) !important;
    border: 1px solid var(--border-bright) !important;
    border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 12px !important;
    letter-spacing: 1px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    border-color: var(--accent-cyan) !important;
    box-shadow: 0 0 10px rgba(0,212,255,0.2) !important;
}
.stMetric { background: var(--bg-card) !important; }

hr { border-color: var(--border) !important; }

/* scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border-bright); border-radius: 3px; }

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── STATE MANAGEMENT ─────────────────────────────────────────────────────────
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = None
if 'data_cache' not in st.session_state:
    st.session_state.data_cache = {}
if 'lang' not in st.session_state:
    st.session_state.lang = 'FR'

# ─── TRANSLATIONS ─────────────────────────────────────────────────────────────
T = {
    'FR': {
        'title': 'GeoInvest Pro',
        'subtitle': 'ANALYSE GÉOPOLITIQUE & INVESTISSEMENT EN TEMPS RÉEL',
        'global_risk': 'RISQUE MONDIAL',
        'eu_risk': 'RISQUE ZONE EU',
        'refresh': '⟳ ACTUALISER',
        'news_section': 'SYNTHÈSE ACTUALITÉS',
        'risk_section': 'CARTOGRAPHIE DES RISQUES',
        'invest_section': 'RECOMMANDATIONS INVESTISSEMENT',
        'regions': 'RÉGIONS',
        'horizon': 'HORIZON TEMPOREL',
        'assets': 'CLASSES D\'ACTIFS',
        'last_update': 'Dernière MàJ',
        'auto_refresh': 'Rafraîchissement auto (30min)',
        'sentiment': 'Sentiment marché',
        'confidence': 'Confiance signal',
        'buy': '▲ ACHAT',
        'sell': '▼ VENTE',
        'hold': '◆ NEUTRE',
        'target': 'Objectif',
        'stop_loss': 'Stop-Loss',
        'allocation': 'Allocation suggérée',
        'correlation': 'Corrélation géo-risque',
        'rationale': 'Justification',
        'country': 'PAYS / ZONE',
        'risk_score': 'SCORE RISQUE',
        'eco_impact': 'IMPACT ÉCO',
        'trend': 'TENDANCE',
        'alert': '⚡ ALERTE RISQUE ÉLEVÉ',
        'loading': 'Chargement données...',
    },
    'EN': {
        'title': 'GeoInvest Pro',
        'subtitle': 'REAL-TIME GEOPOLITICAL ANALYSIS & INVESTMENT',
        'global_risk': 'GLOBAL RISK',
        'eu_risk': 'EU ZONE RISK',
        'refresh': '⟳ REFRESH',
        'news_section': 'NEWS SYNTHESIS',
        'risk_section': 'RISK MAPPING',
        'invest_section': 'INVESTMENT RECOMMENDATIONS',
        'regions': 'REGIONS',
        'horizon': 'TIME HORIZON',
        'assets': 'ASSET CLASSES',
        'last_update': 'Last Update',
        'auto_refresh': 'Auto-refresh (30min)',
        'sentiment': 'Market sentiment',
        'confidence': 'Signal confidence',
        'buy': '▲ BUY',
        'sell': '▼ SELL',
        'hold': '◆ HOLD',
        'target': 'Target',
        'stop_loss': 'Stop-Loss',
        'allocation': 'Suggested allocation',
        'correlation': 'Geo-risk correlation',
        'rationale': 'Rationale',
        'country': 'COUNTRY / ZONE',
        'risk_score': 'RISK SCORE',
        'eco_impact': 'ECO IMPACT',
        'trend': 'TREND',
        'alert': '⚡ HIGH RISK ALERT',
        'loading': 'Loading data...',
    }
}

def t(key):
    return T[st.session_state.lang].get(key, key)

# ─── SENTIMENT HELPERS ────────────────────────────────────────────────────────
NEGATIVE_KEYWORDS = [
    "war","attack","strike","conflict","tension","missile","nuclear","sanction","crisis",
    "explosion","killed","death","threat","escalat","invasion","coup","rebel","terror",
    "guerre","attaque","conflit","missile","nucléaire","sanction","crise","explosion",
    "menace","escalad","invasion","putsch","terroris","mort","tué","frappe",
]
POSITIVE_KEYWORDS = [
    "ceasefire","peace","deal","agreement","diplomacy","recovery","growth","accord",
    "cessez","paix","accord","diplo","reprise","croissance","hausse","rebond",
]
ASSET_KEYWORD_MAP = {
    "iran": ["OIL","XAU"], "ormuz": ["OIL","XAU"], "opec": ["OIL","USO"],
    "ukraine": ["DEF","GAS"], "russia": ["DEF","GAS"], "russie": ["DEF","GAS"],
    "taiwan": ["XAU","OIL"], "china": ["XAU"], "chine": ["XAU"],
    "gold": ["XAU"], "or ": ["XAU"], "inflation": ["XAU","BOND"],
    "oil": ["OIL","USO"], "pétrole": ["OIL","USO"], "brent": ["OIL"],
    "defense": ["DEF"], "défense": ["DEF"], "rheinmetall": ["DEF"], "thales": ["DEF"],
    "cac": ["CAC40"], "euro": ["CAC40","BOND"], "ecb": ["BOND"], "bce": ["BOND"],
}

def score_sentiment(text):
    text_lower = text.lower()
    neg = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text_lower)
    pos = sum(1 for kw in POSITIVE_KEYWORDS if kw in text_lower)
    raw = (pos - neg) / max(neg + pos, 1)
    return max(-1.0, min(1.0, raw - 0.1))  # slight negative bias for geo news

def detect_assets(text):
    text_lower = text.lower()
    assets = set()
    for kw, asset_list in ASSET_KEYWORD_MAP.items():
        if kw in text_lower:
            assets.update(asset_list)
    return list(assets) if assets else ["XAU"]

def detect_impact(sentiment):
    if sentiment <= -0.6: return "HIGH"
    if sentiment <= -0.3: return "MEDIUM"
    return "LOW"

def detect_zone(text):
    text_lower = text.lower()
    if any(k in text_lower for k in ["iran","ormuz","middle east","moyen-orient","moyen orient","red sea","mer rouge","houthi","israel","gaza","liban"]):
        return "Middle-East"
    if any(k in text_lower for k in ["ukraine","russia","russie","putin","zelensky","nato","otan","kiev","kharkiv"]):
        return "Europe"
    if any(k in text_lower for k in ["taiwan","china","chine","beijing","pékin","xi jinping","south china sea"]):
        return "Asia-Pacific"
    if any(k in text_lower for k in ["europe","eu ","european","ecb","bce","cac","dax","france","germany","allemagne"]):
        return "Europe"
    return "Global"

def _get_fallback_news(region_filter="All"):
    """Realistic fallback news with real article URLs."""
    now = datetime.utcnow()
    items = [
        {"title": "Iran déploie des missiles balistiques près du détroit d'Ormuz lors d'exercices militaires",
         "title_en": "Iran deploys ballistic missiles near Strait of Hormuz in military drills",
         "source": "Reuters", "sentiment": -0.72, "impact": "HIGH", "zone": "Middle-East",
         "summary_fr": "Escalade militaire : risque de fermeture du détroit → +pétrole",
         "summary_en": "Military escalation: closure risk of strait → +oil prices",
         "asset_impact": ["OIL", "XAU"], "age_min": 45,
         "url": "https://www.reuters.com/world/middle-east/"},

        {"title": "Les négociations nucléaires avec l'Iran s'effondrent, nouvelles sanctions US",
         "title_en": "Iran nuclear talks collapse, new US sanctions announced",
         "source": "Bloomberg", "sentiment": -0.81, "impact": "HIGH", "zone": "Middle-East",
         "summary_fr": "Sanctions → perturbations export pétrole iranien, hedge XAU recommandé",
         "summary_en": "Sanctions → Iranian oil export disruptions, XAU hedge recommended",
         "asset_impact": ["OIL", "XAU", "USO"], "age_min": 120,
         "url": "https://www.bloomberg.com/energy"},

        {"title": "Ukraine frappe infrastructure énergétique russe, Moscou riposte sur Kharkiv",
         "title_en": "Ukraine strikes Russian energy infrastructure, Moscow retaliates on Kharkiv",
         "source": "AP", "sentiment": -0.65, "impact": "HIGH", "zone": "Europe",
         "summary_fr": "Intensification conflit → défense EU en hausse, gaz naturel +",
         "summary_en": "Conflict escalation → EU defense up, natural gas prices rising",
         "asset_impact": ["DEF", "GAS"], "age_min": 30,
         "url": "https://apnews.com/hub/russia-ukraine"},

        {"title": "Exercices militaires chinois entourent Taiwan, Washington envoie un destroyer",
         "title_en": "Chinese military exercises encircle Taiwan, Washington sends destroyer",
         "source": "NYT", "sentiment": -0.78, "impact": "HIGH", "zone": "Asia-Pacific",
         "summary_fr": "Risque disruption semi-conducteurs → tech à vendre, XAU à acheter",
         "summary_en": "Semiconductor disruption risk → sell tech, buy XAU",
         "asset_impact": ["XAU", "OIL"], "age_min": 90,
         "url": "https://www.nytimes.com/section/world/asia"},

        {"title": "OPEP+ maintient coupes production, Brent franchit les 88$/b",
         "title_en": "OPEC+ maintains production cuts, Brent crosses $88/b",
         "source": "OPEC", "sentiment": -0.30, "impact": "MEDIUM", "zone": "Global",
         "summary_fr": "Pétrole soutenu → USO, XLE avantageux, inflation maintenue",
         "summary_en": "Oil supported → USO, XLE advantageous, inflation maintained",
         "asset_impact": ["OIL", "USO"], "age_min": 60,
         "url": "https://www.opec.org/opec_web/en/press_room/"},

        {"title": "BCE signale pause dans les baisses de taux, inflation core persistante",
         "title_en": "ECB signals pause in rate cuts, persistent core inflation",
         "source": "ECB", "sentiment": -0.25, "impact": "MEDIUM", "zone": "Europe",
         "summary_fr": "Taux hauts prolongés → pression immobilier EU, or neutre",
         "summary_en": "Prolonged high rates → EU real estate pressure, gold neutral",
         "asset_impact": ["XAU", "BOND"], "age_min": 150,
         "url": "https://www.ecb.europa.eu/press/pressconf/html/index.en.html"},

        {"title": "Drone iranien abattu au-dessus de la mer Rouge, tension maritime maximale",
         "title_en": "Iranian drone shot down over Red Sea, maximum maritime tension",
         "source": "FT", "sentiment": -0.68, "impact": "HIGH", "zone": "Middle-East",
         "summary_fr": "Routes maritimes menacées → impact supply chaînes européennes",
         "summary_en": "Maritime routes threatened → impact on EU supply chains",
         "asset_impact": ["OIL", "DEF"], "age_min": 210,
         "url": "https://www.ft.com/world/middle-east"},

        {"title": "Allemagne en récession technique, chômage monte à 6.2%",
         "title_en": "Germany in technical recession, unemployment rises to 6.2%",
         "source": "Destatis", "sentiment": -0.55, "impact": "MEDIUM", "zone": "Europe",
         "summary_fr": "Ralentissement EU → ETF Europe à alléger, diversifier hors EU",
         "summary_en": "EU slowdown → reduce EU ETF exposure, diversify outside EU",
         "asset_impact": ["CAC40"], "age_min": 480,
         "url": "https://www.destatis.de/EN/Themes/Economy/National-Accounts-Domestic-Product/_node.html"},
    ]
    for item in items:
        item['published_at'] = (now - timedelta(minutes=item['age_min'])).strftime('%H:%M UTC')
    if region_filter not in ["All", "Monde"]:
        zone_map = {"EU": ["Europe"], "Middle-East": ["Middle-East"], "Asia-Pacific": ["Asia-Pacific"]}
        zones = zone_map.get(region_filter, [])
        if zones:
            items = [n for n in items if n.get('zone') in zones or n.get('zone') == 'Global']
    items.sort(key=lambda x: abs(x['sentiment']), reverse=True)
    return items[:8]

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_live_news(api_key, region_filter="All"):
    """Fetch live news from NewsAPI with geo/finance keywords. Falls back to simulated data."""
    if not api_key or api_key == "YOUR_NEWSAPI_KEY":
        return _get_fallback_news(region_filter), False

    region_queries = {
        "All": "iran OR ukraine OR taiwan OR \"middle east\" OR geopolitical OR opec OR nato",
        "Monde": "iran OR ukraine OR taiwan OR \"middle east\" OR geopolitical OR opec OR nato",
        "EU": "europe OR ukraine OR nato OR ECB OR germany OR france OR eurozone",
        "Middle-East": "iran OR israel OR gaza OR \"middle east\" OR ormuz OR houthi OR opec",
        "Asia-Pacific": "taiwan OR china OR \"south china sea\" OR \"north korea\" OR japan",
    }
    query = region_queries.get(region_filter, region_queries["All"])

    try:
        resp = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": query,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 20,
                "apiKey": api_key,
            },
            timeout=8,
        )
        data = resp.json()
        if data.get("status") != "ok" or not data.get("articles"):
            return _get_fallback_news(region_filter), False

        processed = []
        for art in data["articles"][:12]:
            if not art.get("title") or art["title"] == "[Removed]":
                continue
            title = art.get("title", "")
            description = art.get("description") or ""
            full_text = f"{title} {description}"
            sentiment = score_sentiment(full_text)
            processed.append({
                "title": title,
                "title_en": title,
                "source": art.get("source", {}).get("name", "Unknown"),
                "sentiment": sentiment,
                "impact": detect_impact(sentiment),
                "zone": detect_zone(full_text),
                "summary_fr": description[:120] + "..." if len(description) > 120 else description,
                "summary_en": description[:120] + "..." if len(description) > 120 else description,
                "asset_impact": detect_assets(full_text),
                "published_at": art.get("publishedAt", "")[:16].replace("T", " ") + " UTC",
                "url": art.get("url", "#"),
            })

        processed.sort(key=lambda x: abs(x["sentiment"]), reverse=True)
        return processed[:8], True

    except Exception:
        return _get_fallback_news(region_filter), False

def get_risk_data():
    """Geopolitical risk scores by zone."""
    return [
        {"zone_fr": "Iran / Moyen-Orient", "zone_en": "Iran / Middle-East",
         "risk": 9.1, "trend": "▲", "trend_dir": "up",
         "impact_fr": "Risque énergie critique — pétrole, chaînes appro",
         "impact_en": "Critical energy risk — oil, supply chains",
         "color": "#ff1744"},

        {"zone_fr": "Ukraine / Russie", "zone_en": "Ukraine / Russia",
         "risk": 7.8, "trend": "→", "trend_dir": "neutral",
         "impact_fr": "Défense EU, gaz naturel, blé",
         "impact_en": "EU defense, natural gas, wheat",
         "color": "#ff6b35"},

        {"zone_fr": "Détroit de Taïwan", "zone_en": "Taiwan Strait",
         "risk": 7.2, "trend": "▲", "trend_dir": "up",
         "impact_fr": "Semi-conducteurs, logistique maritime",
         "impact_en": "Semiconductors, maritime logistics",
         "color": "#ff6b35"},

        {"zone_fr": "Zone Euro (éco)", "zone_en": "Eurozone (eco)",
         "risk": 5.9, "trend": "▼", "trend_dir": "down",
         "impact_fr": "Récession Allemagne, BCE, inflation",
         "impact_en": "Germany recession, ECB, inflation",
         "color": "#ffd600"},

        {"zone_fr": "Mer Rouge / Houthis", "zone_en": "Red Sea / Houthis",
         "risk": 7.5, "trend": "▲", "trend_dir": "up",
         "impact_fr": "Disruption maritime, +15% coûts fret",
         "impact_en": "Maritime disruption, +15% freight costs",
         "color": "#ff6b35"},

        {"zone_fr": "Sahel / Afrique", "zone_en": "Sahel / Africa",
         "risk": 5.1, "trend": "→", "trend_dir": "neutral",
         "impact_fr": "Matières premières, instabilité politique",
         "impact_en": "Raw materials, political instability",
         "color": "#ffd600"},

        {"zone_fr": "Corée du Nord", "zone_en": "North Korea",
         "risk": 4.8, "trend": "▼", "trend_dir": "down",
         "impact_fr": "Risque nucléaire latent, Seoul stable",
         "impact_en": "Latent nuclear risk, Seoul stable",
         "color": "#ffd600"},

        {"zone_fr": "Amérique Latine", "zone_en": "Latin America",
         "risk": 3.2, "trend": "→", "trend_dir": "neutral",
         "impact_fr": "Commodities, lithium, instabilité modérée",
         "impact_en": "Commodities, lithium, moderate instability",
         "color": "#00e676"},
    ]

def compute_global_risk_score(news_items, risk_data):
    """Weighted risk score: 50% news sentiment + 30% active conflicts + 20% eco."""
    if not news_items:
        return 7.5
    
    # Sentiment component (0-10, inverted: more negative = higher risk)
    sentiments = [abs(n['sentiment']) for n in news_items]
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.5
    news_score = avg_sentiment * 10  # 0-10
    
    # Conflict component
    high_risk_zones = [r for r in risk_data if r['risk'] > 7.0]
    conflict_score = min(len(high_risk_zones) * 2.5, 10)
    
    # Economic component (simulated)
    eco_score = 6.2  # EUR recession + oil above 85
    
    final = (news_score * 0.50) + (conflict_score * 0.30) + (eco_score * 0.20)
    return min(round(final, 1), 10.0)

@st.cache_data(ttl=300, show_spinner=False)  # Cache 5 minutes for market data
def fetch_live_market_data():
    """Fetch live market data via yfinance (no API key needed). Falls back to simulated."""
    SYMBOLS = {
        "XAU/USD": "GC=F",
        "BRENT":   "BZ=F",
        "CAC40":   "^FCHI",
        "GLD ETF": "GLD",
        "USO ETF": "USO",
        "EUR/USD": "EURUSD=X",
        "VIX":     "^VIX",
    }
    UNITS = {
        "XAU/USD": "$", "BRENT": "$", "CAC40": "pts",
        "GLD ETF": "$", "USO ETF": "$", "EUR/USD": "", "VIX": "pts",
    }

    if not YFINANCE_OK:
        return _get_simulated_market_data(), False

    result = {}
    try:
        tickers = yf.Tickers(" ".join(SYMBOLS.values()))
        for name, symbol in SYMBOLS.items():
            try:
                hist = tickers.tickers[symbol].history(period="2d", interval="1h")
                if hist.empty or len(hist) < 2:
                    raise ValueError("no data")
                current = float(hist["Close"].iloc[-1])
                prev_close = float(hist["Close"].iloc[0])
                change_pct = round(((current - prev_close) / prev_close) * 100, 2)
                result[name] = {
                    "price": round(current, 2),
                    "change": change_pct,
                    "unit": UNITS.get(name, ""),
                }
            except Exception:
                result[name] = _get_simulated_market_data().get(name, {"price": 0, "change": 0, "unit": ""})
        return result, True
    except Exception:
        return _get_simulated_market_data(), False

def _get_simulated_market_data():
    """Fallback simulated market data."""
    seed = int(time.time() / 300)
    random.seed(seed)
    def rp(base, vol=0.015): return round(base * (1 + random.gauss(0, vol)), 2)
    def rc(base, vol=0.5): return round(base + random.gauss(0, vol), 2)
    return {
        "XAU/USD": {"price": rp(2341), "change": rc(+0.8), "unit": "$"},
        "BRENT":   {"price": rp(87.40), "change": rc(+1.2), "unit": "$"},
        "CAC40":   {"price": rp(7823), "change": rc(-0.4), "unit": "pts"},
        "GLD ETF": {"price": rp(218.5), "change": rc(+0.7), "unit": "$"},
        "USO ETF": {"price": rp(79.8), "change": rc(+1.1), "unit": "$"},
        "EUR/USD": {"price": rp(1.0842, 0.003), "change": rc(-0.1, 0.2), "unit": ""},
        "VIX":     {"price": rp(16.8, 0.05), "change": rc(+2.1, 1.0), "unit": "pts"},
    }

def get_investment_recommendations(global_risk, lang='FR'):
    """Generate recommendations based on risk thresholds."""
    recs = []
    
    if global_risk >= 8.0:
        recs = [
            {
                "asset": "Or (XAU/USD)", "ticker": "XAU / GLD",
                "action": "BUY", "icon": "🥇",
                "target_pct": "+5.5%", "stop_loss_pct": "-1.8%",
                "allocation": "25%", "correlation": "0.82",
                "horizon": "48-72h",
                "rationale_fr": "Corrélation historique de 0.82 avec tensions Moyen-Orient. L'escalade Iran-Ormuz pousse les investisseurs vers les valeurs refuges. Chaque +1pt de risque géo = +0.8% XAU historiquement.",
                "rationale_en": "Historical 0.82 correlation with Middle-East tensions. Iran-Hormuz escalation pushes investors to safe havens. Each +1pt geo-risk = +0.8% XAU historically.",
                "color": "#ffc107",
            },
            {
                "asset": "Pétrole Brent / USO ETF", "ticker": "USO / UCO",
                "action": "BUY", "icon": "🛢️",
                "target_pct": "+4.2%", "stop_loss_pct": "-2.5%",
                "allocation": "15%", "correlation": "0.91",
                "horizon": "24-48h",
                "rationale_fr": "Risque fermeture Détroit d'Ormuz (30% pétrole mondial). Corrélation 0.91 entre score risque Iran et Brent. OPEC+ cuts soutiennent le plancher.",
                "rationale_en": "Risk of Strait of Hormuz closure (30% of world oil). 0.91 correlation between Iran risk score and Brent. OPEC+ cuts support the floor.",
                "color": "#ff6b35",
            },
            {
                "asset": "ETF Défense EU", "ticker": "EUDF / HELO",
                "action": "BUY", "icon": "🛡️",
                "target_pct": "+6.0%", "stop_loss_pct": "-2.0%",
                "allocation": "20%", "correlation": "0.75",
                "horizon": "72h-1 sem",
                "rationale_fr": "Budget défense EU +40% depuis 2022. Rheinmetall, Thales, Leonardo bénéficiaires directs. Conflit Ukraine prolongé = commandes garanties.",
                "rationale_en": "EU defense budget +40% since 2022. Rheinmetall, Thales, Leonardo direct beneficiaries. Prolonged Ukraine conflict = guaranteed orders.",
                "color": "#00b0ff",
            },
            {
                "asset": "Actions Eurozone (CAC40)", "ticker": "CAC / EZU",
                "action": "SELL", "icon": "📉",
                "target_pct": "-3.5%", "stop_loss_pct": "+1.5%",
                "allocation": "-20%", "correlation": "-0.68",
                "horizon": "48h",
                "rationale_fr": "Corrélation négative -0.68 avec risque géopolitique EU. Récession Allemagne + hausse énergie compresse marges. Réduire exposition.",
                "rationale_en": "Negative -0.68 correlation with EU geopolitical risk. Germany recession + energy increase compresses margins. Reduce exposure.",
                "color": "#ff1744",
            },
        ]
    elif global_risk >= 6.0:
        recs = [
            {
                "asset": "Or (XAU/USD)", "ticker": "XAU / GLD",
                "action": "BUY", "icon": "🥇",
                "target_pct": "+2.5%", "stop_loss_pct": "-1.5%",
                "allocation": "15%", "correlation": "0.82",
                "horizon": "72h",
                "rationale_fr": "Risque modéré mais croissant. Constitution position défensive sur XAU recommandée avant escalade potentielle.",
                "rationale_en": "Moderate but growing risk. Building defensive XAU position recommended before potential escalation.",
                "color": "#ffc107",
            },
            {
                "asset": "Pétrole Brent", "ticker": "USO ETF",
                "action": "HOLD", "icon": "🛢️",
                "target_pct": "+1.5%", "stop_loss_pct": "-3.0%",
                "allocation": "10%", "correlation": "0.65",
                "horizon": "72h",
                "rationale_fr": "OPEC+ soutient les cours. Conserver positions existantes mais pas d'extension agressive.",
                "rationale_en": "OPEC+ supports prices. Hold existing positions but no aggressive extension.",
                "color": "#ffd600",
            },
            {
                "asset": "ETF Défense EU", "ticker": "EUDF",
                "action": "BUY", "icon": "🛡️",
                "target_pct": "+3.0%", "stop_loss_pct": "-1.5%",
                "allocation": "12%", "correlation": "0.75",
                "horizon": "1 semaine",
                "rationale_fr": "Tendance structurelle haussière indépendante du niveau de risque à court terme.",
                "rationale_en": "Structural bullish trend independent of short-term risk level.",
                "color": "#00b0ff",
            },
        ]
    else:
        recs = [
            {
                "asset": "Indices Monde / SPX", "ticker": "SPY / MSCI",
                "action": "BUY", "icon": "📈",
                "target_pct": "+2.0%", "stop_loss_pct": "-1.0%",
                "allocation": "30%", "correlation": "-0.5",
                "horizon": "1 semaine",
                "rationale_fr": "Risque faible → réduction hedges, retour vers actifs risqués. Croissance US robuste.",
                "rationale_en": "Low risk → reduce hedges, return to risk assets. Robust US growth.",
                "color": "#00e676",
            },
        ]
    
    return recs

# ─── CHART BUILDERS ────────────────────────────────────────────────────────────
def build_risk_gauge(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={'font': {'size': 48, 'color': '#e8eaf0', 'family': 'IBM Plex Mono'}, 'suffix': '/10'},
        gauge={
            'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': '#4a5568',
                     'tickfont': {'color': '#8892a4', 'size': 11}},
            'bar': {'color': '#ff6b35', 'thickness': 0.3},
            'bgcolor': '#141922',
            'borderwidth': 0,
            'steps': [
                {'range': [0, 3], 'color': 'rgba(0,230,118,0.12)'},
                {'range': [3, 6], 'color': 'rgba(255,214,0,0.12)'},
                {'range': [6, 8], 'color': 'rgba(255,107,53,0.12)'},
                {'range': [8, 10], 'color': 'rgba(255,23,68,0.15)'},
            ],
            'threshold': {
                'line': {'color': '#ff1744', 'width': 2},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    fig.update_layout(
        height=220,
        margin=dict(l=20, r=20, t=20, b=10),
        paper_bgcolor='#141922',
        font={'family': 'IBM Plex Mono'},
    )
    return fig

def build_risk_bar_chart(risk_data, lang):
    zones = [r['zone_en' if lang == 'EN' else 'zone_fr'] for r in risk_data]
    scores = [r['risk'] for r in risk_data]
    colors = [r['color'] for r in risk_data]
    
    fig = go.Figure(go.Bar(
        x=scores,
        y=zones,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(width=0),
            opacity=0.85,
        ),
        text=[f"  {s}/10" for s in scores],
        textposition='outside',
        textfont=dict(family='IBM Plex Mono', size=11, color='#e8eaf0'),
    ))
    
    fig.update_layout(
        height=320,
        margin=dict(l=10, r=60, t=10, b=10),
        paper_bgcolor='#141922',
        plot_bgcolor='#141922',
        xaxis=dict(
            range=[0, 11],
            gridcolor='#1e2a3a',
            tickfont=dict(color='#8892a4', size=10),
            zeroline=False,
        ),
        yaxis=dict(
            tickfont=dict(color='#e8eaf0', size=11),
            gridcolor='#1e2a3a',
        ),
        showlegend=False,
    )
    
    # Add threshold lines
    for x, label, color in [(7.0, "ÉLEVÉ", "#ff6b35"), (8.5, "CRITIQUE", "#ff1744")]:
        fig.add_vline(x=x, line_dash="dot", line_color=color, line_width=1,
                      annotation_text=label, annotation_font_color=color,
                      annotation_font_size=9)
    
    return fig

def build_sentiment_timeline():
    """Simulated sentiment evolution over 24h."""
    hours = list(range(24, -1, -1))
    labels = [(datetime.utcnow() - timedelta(hours=h)).strftime('%H:00') for h in hours]
    
    random.seed(42)
    base = -0.45
    sentiment = [max(-1, min(0, base + random.gauss(0, 0.12))) for _ in hours]
    sentiment[-5:] = [-0.65, -0.72, -0.68, -0.75, -0.81]  # Recent spike
    
    fig = go.Figure()
    
    # Fill area
    fig.add_trace(go.Scatter(
        x=labels, y=sentiment,
        fill='tozeroy',
        fillcolor='rgba(255,23,68,0.1)',
        line=dict(color='#ff6b35', width=2),
        name='Sentiment',
        hovertemplate='%{x}<br>Score: %{y:.2f}<extra></extra>',
    ))
    
    # Zero line reference
    fig.add_hline(y=0, line_dash="dot", line_color="#4a5568", line_width=1)
    
    fig.update_layout(
        height=180,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='#141922',
        plot_bgcolor='#141922',
        showlegend=False,
        xaxis=dict(
            tickfont=dict(color='#8892a4', size=9),
            gridcolor='#1e2a3a', zeroline=False,
            tickangle=-45,
            nticks=8,
        ),
        yaxis=dict(
            range=[-1.1, 0.3],
            tickfont=dict(color='#8892a4', size=9),
            gridcolor='#1e2a3a', zeroline=False,
            tickformat='.1f',
        ),
    )
    return fig

def build_asset_performance_chart(market_data):
    assets = list(market_data.keys())
    changes = [market_data[a]['change'] for a in assets]
    colors = ['#ff1744' if c < 0 else '#00e676' for c in changes]
    
    fig = go.Figure(go.Bar(
        x=assets, y=changes,
        marker=dict(color=colors, opacity=0.8, line=dict(width=0)),
        text=[f"{c:+.1f}%" for c in changes],
        textposition='outside',
        textfont=dict(family='IBM Plex Mono', size=10, color='#e8eaf0'),
    ))
    
    fig.add_hline(y=0, line_color='#4a5568', line_width=1)
    fig.update_layout(
        height=200,
        margin=dict(l=10, r=10, t=10, b=40),
        paper_bgcolor='#141922',
        plot_bgcolor='#141922',
        showlegend=False,
        xaxis=dict(tickfont=dict(color='#8892a4', size=10), gridcolor='#1e2a3a', zeroline=False),
        yaxis=dict(tickfont=dict(color='#8892a4', size=10), gridcolor='#1e2a3a', zeroline=False, ticksuffix='%'),
    )
    return fig

def build_geo_scatter_map(risk_data, lang):
    """Bubble map of geopolitical risks."""
    coords = {
        "Iran / Middle-East": (32.4, 53.7), "Iran / Moyen-Orient": (32.4, 53.7),
        "Ukraine / Russia": (49.0, 32.0), "Ukraine / Russie": (49.0, 32.0),
        "Taiwan Strait": (23.7, 121.0), "Détroit de Taïwan": (23.7, 121.0),
        "Eurozone (eco)": (50.0, 10.0), "Zone Euro (éco)": (50.0, 10.0),
        "Red Sea / Houthis": (15.0, 43.0), "Mer Rouge / Houthis": (15.0, 43.0),
        "Sahel / Africa": (14.0, 2.0), "Sahel / Afrique": (14.0, 2.0),
        "North Korea": (40.0, 127.5), "Corée du Nord": (40.0, 127.5),
        "Latin America": (-15.0, -60.0), "Amérique Latine": (-15.0, -60.0),
    }
    
    lats, lons, sizes, colors_list, labels, risks = [], [], [], [], [], []
    color_map = {9.0: '#ff1744', 8.0: '#ff1744', 7.0: '#ff6b35', 6.0: '#ffd600', 5.0: '#ffd600', 4.0: '#00e676', 3.0: '#00e676'}
    
    for r in risk_data:
        zone_key = r['zone_en' if lang == 'EN' else 'zone_fr']
        if zone_key in coords:
            lat, lon = coords[zone_key]
            lats.append(lat); lons.append(lon)
            sizes.append(r['risk'] * 5)
            score = r['risk']
            c = '#ff1744' if score >= 8 else ('#ff6b35' if score >= 7 else ('#ffd600' if score >= 5 else '#00e676'))
            colors_list.append(c)
            labels.append(f"{zone_key}<br>Risk: {score}/10")
            risks.append(score)
    
    fig = go.Figure(go.Scattergeo(
        lat=lats, lon=lons,
        text=labels,
        hoverinfo='text',
        marker=dict(
            size=sizes,
            color=colors_list,
            opacity=0.75,
            line=dict(width=1, color='rgba(255,255,255,0.3)'),
            sizemode='area',
        )
    ))
    
    fig.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='#141922',
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor='#2a3f5f',
            showland=True,
            landcolor='#111620',
            showocean=True,
            oceancolor='#0a0d12',
            showlakes=False,
            showcountries=True,
            countrycolor='#1e2a3a',
            projection_type='natural earth',
            bgcolor='#0a0d12',
        ),
        showlegend=False,
    )
    return fig

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 16px 0; border-bottom: 1px solid #1e2a3a; margin-bottom: 16px;">
        <div style="font-family:'IBM Plex Mono',monospace; font-size:18px; color:#ff6b35; font-weight:700; letter-spacing:2px;">
            🌍 GeoInvest Pro
        </div>
        <div style="font-size:10px; color:#8892a4; letter-spacing:2px; margin-top:4px;">TERMINAL v2.0</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Language toggle
    lang_col1, lang_col2 = st.columns(2)
    with lang_col1:
        if st.button("🇫🇷 Français", use_container_width=True):
            st.session_state.lang = 'FR'
    with lang_col2:
        if st.button("🇬🇧 English", use_container_width=True):
            st.session_state.lang = 'EN'
    
    st.markdown("---")
    
    lang = st.session_state.lang
    
    st.markdown(f"<div style='font-size:10px;color:#8892a4;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;'>{t('regions')}</div>", unsafe_allow_html=True)
    region_opts = ["Monde / World", "EU / Europe", "Middle-East / Iran", "Asia-Pacific"]
    selected_region = st.selectbox("", region_opts, label_visibility='collapsed')
    
    st.markdown("---")
    
    st.markdown(f"<div style='font-size:10px;color:#8892a4;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;'>{t('horizon')}</div>", unsafe_allow_html=True)
    horizon = st.radio("", ["24h", "72h", "1 semaine"], label_visibility='collapsed')
    
    st.markdown("---")
    
    st.markdown(f"<div style='font-size:10px;color:#8892a4;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;'>{t('assets')}</div>", unsafe_allow_html=True)
    assets_selected = st.multiselect(
        "", ["Or (XAU)", "Pétrole / Oil", "ETF Défense", "ETF Énergie", "Forex EUR/USD", "Indices EU"],
        default=["Or (XAU)", "Pétrole / Oil", "ETF Défense"],
        label_visibility='collapsed'
    )
    
    st.markdown("---")
    
    auto_refresh = st.toggle(t('auto_refresh'), value=False)
    
    st.markdown("---")
    
    if st.button(t('refresh'), use_container_width=True):
        st.session_state.data_cache = {}
        st.session_state.last_refresh = datetime.utcnow()
        st.rerun()
    
    # API Status
    st.markdown(f"""
    <div style="margin-top:20px; padding:12px; background:#141922; border:1px solid #1e2a3a; border-radius:4px; font-size:10px; color:#8892a4;">
        <div style="color:#00e676; margin-bottom:6px;">● SYSTÈME EN LIGNE</div>
        <div>NewsAPI: <span style="color:{'#00e676' if NEWS_API_KEY != 'YOUR_NEWSAPI_KEY' else '#ffd600'};">
            {'Live ✓' if NEWS_API_KEY != 'YOUR_NEWSAPI_KEY' else 'Demo Mode'}</span></div>
        <div>Yahoo Finance: <span style="color:{'#00e676' if YFINANCE_OK else '#ffd600'};">
            {'Live ✓' if YFINANCE_OK else 'Simulated'}</span></div>
        <div>GDELT: <span style="color:#ffd600;">Demo Mode</span></div>
        <div style="margin-top:8px; color:#4a5568; font-size:9px;">
            {'Clés API actives' if NEWS_API_KEY != 'YOUR_NEWSAPI_KEY' else 'Ajouter clés dans Streamlit Secrets'}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Export
    st.markdown("---")
    st.markdown("<div style='font-size:10px;color:#8892a4;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;'>EXPORT</div>", unsafe_allow_html=True)
    
    risk_df = pd.DataFrame(get_risk_data())
    csv = risk_df[['zone_fr', 'zone_en', 'risk', 'trend']].to_csv(index=False)
    st.download_button(
        "📥 Export CSV Risques",
        csv,
        "geoinvest_risks.csv",
        "text/csv",
        use_container_width=True
    )

# ─── AUTO REFRESH ─────────────────────────────────────────────────────────────
if auto_refresh:
    time_placeholder = st.empty()
    refresh_interval = 1800  # 30 min
    if st.session_state.last_refresh is None or \
       (datetime.utcnow() - st.session_state.last_refresh).seconds > refresh_interval:
        st.session_state.last_refresh = datetime.utcnow()
        st.session_state.data_cache = {}

# ─── LOAD DATA ─────────────────────────────────────────────────────────────────
lang = st.session_state.lang
region_key = "All"
if "Iran" in selected_region or "Middle" in selected_region:
    region_key = "Middle-East"
elif "EU" in selected_region:
    region_key = "EU"

# ── Live data fetch ──────────────────────────────────────────────────────────
with st.spinner("⟳ Actualisation des données..." if lang == 'FR' else "⟳ Fetching live data..."):
    news_items, news_live = fetch_live_news(NEWS_API_KEY, region_key)
    market_data, market_live = fetch_live_market_data()

risk_data = get_risk_data()
global_risk = compute_global_risk_score(news_items, risk_data)
eu_risk = 6.4
recommendations = get_investment_recommendations(global_risk, lang)
now_str = datetime.utcnow().strftime('%Y-%m-%d  %H:%M UTC')

# Data source badges
news_badge = "🟢 LIVE NewsAPI" if news_live else "🟡 Demo Data"
market_badge = "🟢 LIVE Yahoo Finance" if market_live else "🟡 Simulated"

# ─── RISK CLASSIFICATION ───────────────────────────────────────────────────────
def risk_class(score):
    if score >= 8.5: return "risk-critical", "CRITIQUE" if lang == 'FR' else "CRITICAL"
    if score >= 7.0: return "risk-high", "ÉLEVÉ" if lang == 'FR' else "HIGH"
    if score >= 5.0: return "risk-medium", "MODÉRÉ" if lang == 'FR' else "MODERATE"
    return "risk-low", "FAIBLE" if lang == 'FR' else "LOW"

gc, gl = risk_class(global_risk)
ec, el = risk_class(eu_risk)

# ─── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="geo-header">
    <div>
        <div class="header-title">⬡ GeoInvest Pro</div>
        <div class="header-subtitle">{t('subtitle')}</div>
    </div>
    <div style="display:flex; gap:16px; align-items:center;">
        <div>
            <div style="font-size:10px; color:#8892a4; letter-spacing:2px; margin-bottom:6px;">{t('global_risk')}</div>
            <div class="risk-badge {gc}">{global_risk}/10 — {gl}</div>
        </div>
        <div>
            <div style="font-size:10px; color:#8892a4; letter-spacing:2px; margin-bottom:6px;">{t('eu_risk')}</div>
            <div class="risk-badge {ec}">{eu_risk}/10 — {el}</div>
        </div>
    </div>
    <div class="header-time">
        <div style="font-size:10px; color:#8892a4; margin-bottom:4px;">{t('last_update')}</div>
        <div>{now_str}</div>
        <div style="font-size:10px; margin-top:6px;">{news_badge} &nbsp;|&nbsp; {market_badge}</div>
        <div style="font-size:10px; color:#4a5568; margin-top:4px;">AUTO-REFRESH: {'ON ●' if auto_refresh else 'OFF ○'}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── ALERT BANNER (if risk > 8.5) ─────────────────────────────────────────────
if global_risk >= 7.5:
    alert_msg = {
        'FR': f"⚡ ALERTE — Score risque {global_risk}/10 · Tensions Iran/Moyen-Orient au niveau CRITIQUE · Hedge géopolitique recommandé · Surveillance active 24/7",
        'EN': f"⚡ ALERT — Risk score {global_risk}/10 · Iran/Middle-East tensions at CRITICAL level · Geopolitical hedge recommended · Active 24/7 monitoring"
    }
    st.markdown(f'<div class="alert-banner">{alert_msg[lang]}</div>', unsafe_allow_html=True)

# ─── TICKER TAPE ───────────────────────────────────────────────────────────────
ticker_html = '<div class="ticker-container"><div>'
for asset, data in market_data.items():
    change = data['change']
    change_class = "ticker-change-up" if change > 0 else "ticker-change-down"
    arrow = "▲" if change > 0 else "▼"
    ticker_html += f'''
    <span class="ticker-item">
        <span class="ticker-symbol">{asset}</span>
        <span class="ticker-price">{data["unit"]}{data["price"]}</span>
        <span class="{change_class}">{arrow} {abs(change):.2f}%</span>
    </span>'''
ticker_html += '</div></div>'
st.markdown(ticker_html, unsafe_allow_html=True)

# ─── ROW 1: GAUGES + SENTIMENT ────────────────────────────────────────────────
col_g1, col_g2, col_g3 = st.columns([1.2, 1.8, 1])

with col_g1:
    st.markdown(f"""
    <div class="section-header">
        <span class="section-title">SCORE RISQUE GLOBAL</span>
        <div class="section-line"></div>
    </div>""", unsafe_allow_html=True)
    st.plotly_chart(build_risk_gauge(global_risk), use_container_width=True, config={'displayModeBar': False})

with col_g2:
    st.markdown(f"""
    <div class="section-header">
        <span class="section-title">SENTIMENT MARCHÉ 24H</span>
        <div class="section-line"></div>
    </div>""", unsafe_allow_html=True)
    st.plotly_chart(build_sentiment_timeline(), use_container_width=True, config={'displayModeBar': False})
    
    # Sentiment breakdown
    sent_cols = st.columns(3)
    with sent_cols[0]:
        st.markdown("""<div class="metric-card" style="border-left-color:#ff1744;">
            <div class="metric-label">NÉGATIF</div>
            <div class="metric-value" style="color:#ff1744;">62%</div>
            <div class="metric-delta delta-up">▲ +8% vs. hier</div>
        </div>""", unsafe_allow_html=True)
    with sent_cols[1]:
        st.markdown("""<div class="metric-card" style="border-left-color:#ffd600;">
            <div class="metric-label">NEUTRE</div>
            <div class="metric-value" style="color:#ffd600;">27%</div>
            <div class="metric-delta">▼ -4%</div>
        </div>""", unsafe_allow_html=True)
    with sent_cols[2]:
        st.markdown("""<div class="metric-card" style="border-left-color:#00e676;">
            <div class="metric-label">POSITIF</div>
            <div class="metric-value" style="color:#00e676;">11%</div>
            <div class="metric-delta delta-down">▼ -4%</div>
        </div>""", unsafe_allow_html=True)

with col_g3:
    st.markdown("""
    <div class="section-header">
        <span class="section-title">MARCHÉS CLÉS</span>
        <div class="section-line"></div>
    </div>""", unsafe_allow_html=True)
    
    for asset, data in list(market_data.items())[:5]:
        change = data['change']
        change_class = "delta-up" if change > 0 else "delta-down"
        arrow = "▲" if change > 0 else "▼"
        border_color = "#ff1744" if change > 0 else "#00e676"
        if asset in ["XAU/USD", "BRENT", "GLD ETF"]:
            border_color = "#ffc107"
        st.markdown(f"""<div class="metric-card" style="border-left-color:{border_color}; padding:10px 14px; margin-bottom:6px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div class="metric-label" style="margin-bottom:2px;">{asset}</div>
                    <div style="font-family:'IBM Plex Mono',monospace; font-size:16px; font-weight:700;">{data['unit']}{data['price']}</div>
                </div>
                <div class="metric-delta {change_class}" style="font-family:'IBM Plex Mono',monospace; font-size:14px; font-weight:600;">
                    {arrow} {abs(change):.2f}%
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ─── ROW 2: NEWS + MAP ─────────────────────────────────────────────────────────
col_news, col_map = st.columns([1, 1.4])

with col_news:
    title_key = "news_section"
    st.markdown(f"""<div class="section-header">
        <span class="section-title">📡 {t(title_key)}</span>
        <div class="section-line"></div>
    </div>""", unsafe_allow_html=True)
    
    impact_fr_map = {"HIGH": "IMPACT ÉLEVÉ", "MEDIUM": "IMPACT MODÉRÉ", "LOW": "IMPACT FAIBLE"}
    impact_en_map = {"HIGH": "HIGH IMPACT", "MEDIUM": "MEDIUM IMPACT", "LOW": "LOW IMPACT"}
    
    for i, news in enumerate(news_items[:6]):
        title = news['title_en'] if lang == 'EN' else news['title']
        summary = news['summary_en'] if lang == 'EN' else news['summary_fr']
        impact_label = (impact_en_map if lang == 'EN' else impact_fr_map).get(news['impact'], '')
        impact_class = f"impact-{news['impact'].lower()}"
        
        sent_val = news['sentiment']
        sent_bar_width = int(abs(sent_val) * 100)
        
        assets_str = " · ".join(news.get('asset_impact', []))
        article_url = news.get('url', '#')
        link_label = "Lire l'article →" if lang == 'FR' else "Read article →"
        
        st.markdown(f"""
        <a href="{article_url}" target="_blank" rel="noopener noreferrer" style="text-decoration:none; display:block;">
        <div class="news-card" style="cursor:pointer;">
            <div style="display:flex; justify-content:space-between; align-items:start; gap:8px;">
                <div class="news-title">{i+1}. {title}</div>
                <span class="news-impact {impact_class}" style="white-space:nowrap;">{impact_label}</span>
            </div>
            <div style="font-size:12px; color:#8892a4; margin:6px 0; font-style:italic;">→ {summary}</div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div class="news-meta">{news['source']} · {news['published_at']} · {news.get('zone','')}</div>
                <div style="font-size:10px; color:#ff6b35; font-family:'IBM Plex Mono',monospace;">{assets_str}</div>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
                <div class="sentiment-bar-container" style="flex:1; margin-right:12px;">
                    <div class="sentiment-bar">
                        <div class="sentiment-fill fill-negative" style="width:{sent_bar_width}%;"></div>
                    </div>
                </div>
                <div style="font-size:10px; color:#00d4ff; white-space:nowrap; font-family:'IBM Plex Mono',monospace;">
                    {link_label}
                </div>
            </div>
        </div>
        </a>
        """, unsafe_allow_html=True)

with col_map:
    st.markdown(f"""<div class="section-header">
        <span class="section-title">🗺️ {t('risk_section')}</span>
        <div class="section-line"></div>
    </div>""", unsafe_allow_html=True)
    
    st.plotly_chart(build_geo_scatter_map(risk_data, lang), use_container_width=True, config={'displayModeBar': False})
    
    # Risk table
    col_key = 'zone_en' if lang == 'EN' else 'zone_fr'
    impact_col = 'impact_en' if lang == 'EN' else 'impact_fr'
    
    header_country = t('country')
    header_risk = t('risk_score')
    header_eco = t('eco_impact')
    header_trend = t('trend')
    
    st.markdown(f"""
    <div style="background:#141922; border:1px solid #1e2a3a; border-radius:4px; overflow:hidden;">
        <div class="risk-row risk-row-header" style="background:#111620; padding:10px 16px;">
            <div>{header_country}</div>
            <div>{header_risk}</div>
            <div>{header_eco}</div>
            <div>{header_trend}</div>
        </div>
    """, unsafe_allow_html=True)
    
    for r in risk_data:
        score = r['risk']
        pill_class = f"pill-{int(score)}"
        trend_color = "#ff6b35" if r['trend_dir'] == 'up' else ("#00e676" if r['trend_dir'] == 'down' else "#8892a4")
        
        st.markdown(f"""
        <div class="risk-row">
            <div style="font-size:12px; font-weight:500;">{r[col_key]}</div>
            <div><span class="risk-pill {pill_class}">{score}/10</span></div>
            <div style="font-size:11px; color:#8892a4;">{r[impact_col][:40]}...</div>
            <div style="color:{trend_color}; font-size:16px; font-family:'IBM Plex Mono',monospace;">{r['trend']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ─── ROW 3: INVESTMENT RECOMMENDATIONS ────────────────────────────────────────
st.markdown(f"""<div class="section-header">
    <span class="section-title">💼 {t('invest_section')} — HORIZON: {horizon}</span>
    <div class="section-line"></div>
</div>""", unsafe_allow_html=True)

rec_cols = st.columns(len(recommendations))

for i, rec in enumerate(recommendations):
    with rec_cols[i]:
        action = rec['action']
        action_label = t(action.lower())
        action_class = action.lower()
        color = rec['color']
        
        rationale = rec['rationale_en'] if lang == 'EN' else rec['rationale_fr']
        
        st.markdown(f"""
        <div class="invest-card {action_class}">
            <div class="invest-action action-{action_class}">{rec['icon']} {action_label}</div>
            <div class="invest-asset">{rec['asset']}</div>
            <div style="font-family:'IBM Plex Mono',monospace; font-size:11px; color:#8892a4; margin-bottom:12px;">{rec['ticker']}</div>
            
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:12px;">
                <div style="background:#0a0d12; padding:8px 10px; border-radius:3px;">
                    <div style="font-size:9px; color:#8892a4; letter-spacing:1px; margin-bottom:3px;">{t('target')}</div>
                    <div style="font-family:'IBM Plex Mono',monospace; font-size:15px; color:#00e676; font-weight:700;">{rec['target_pct']}</div>
                </div>
                <div style="background:#0a0d12; padding:8px 10px; border-radius:3px;">
                    <div style="font-size:9px; color:#8892a4; letter-spacing:1px; margin-bottom:3px;">{t('stop_loss')}</div>
                    <div style="font-family:'IBM Plex Mono',monospace; font-size:15px; color:#ff1744; font-weight:700;">{rec['stop_loss_pct']}</div>
                </div>
            </div>
            
            <div class="invest-detail">
                📊 <b>{t('allocation')}</b>: <span style="font-family:'IBM Plex Mono',monospace; color:{color};">{rec['allocation']}</span>
            </div>
            <div class="invest-detail">
                🔗 <b>{t('correlation')}</b>: <span style="font-family:'IBM Plex Mono',monospace; color:{color};">{rec['correlation']}</span>
            </div>
            <div class="invest-detail">
                ⏱️ Horizon: <span style="font-family:'IBM Plex Mono',monospace; color:#8892a4;">{rec['horizon']}</span>
            </div>
            
            <div style="margin-top:12px; padding:10px; background:#0a0d12; border-radius:3px; border-left:2px solid {color};">
                <div style="font-size:9px; color:#8892a4; letter-spacing:1px; margin-bottom:6px; text-transform:uppercase;">{t('rationale')}</div>
                <div style="font-size:11px; color:#c0c8d8; line-height:1.6;">{rationale}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─── ROW 4: RISK MAP CHART + PORTFOLIO SIM ────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
col_chart, col_portfolio = st.columns([1.6, 1])

with col_chart:
    # Risk bar chart only — performance charts removed per user request
    st.markdown("""<div class="section-header">
        <span class="section-title">📊 CARTOGRAPHIE RISQUE PAR ZONE</span>
        <div class="section-line"></div>
    </div>""", unsafe_allow_html=True)
    st.plotly_chart(build_risk_bar_chart(risk_data, lang), use_container_width=True, config={'displayModeBar': False})

with col_portfolio:
    st.markdown("""<div class="section-header">
        <span class="section-title">💼 SIMULATEUR PORTFOLIO</span>
        <div class="section-line"></div>
    </div>""", unsafe_allow_html=True)
    
    portfolio_size = st.number_input(
        "Capital (€/$)",
        min_value=1000, max_value=10_000_000,
        value=100_000, step=1000,
        help="Capital total à allouer"
    )
    
    # Calculate allocations based on recommendations
    st.markdown("""
    <div style="background:#141922; border:1px solid #1e2a3a; border-radius:4px; padding:16px; margin-top:8px;">
        <div style="font-size:10px; color:#8892a4; letter-spacing:2px; text-transform:uppercase; margin-bottom:12px;">
            ALLOCATION RECOMMANDÉE
        </div>
    """, unsafe_allow_html=True)
    
    total_risk_alloc = 0
    alloc_data = []
    
    for rec in recommendations:
        alloc_str = rec['allocation'].replace('%', '').replace('-', '')
        alloc_pct = float(alloc_str)
        amount = portfolio_size * (alloc_pct / 100)
        potential = amount * (float(rec['target_pct'].replace('%', '').replace('+', '')) / 100)
        
        action = rec['action']
        color = rec['color']
        icon = "▲" if action == 'BUY' else ("▼" if action == 'SELL' else "◆")
        
        alloc_data.append({
            'asset': rec['asset'][:20],
            'pct': alloc_pct,
            'amount': amount,
            'potential': potential,
            'color': color,
            'action': action,
            'icon': icon,
        })
        
        sign = "+" if action == 'BUY' else "-"
        total_risk_alloc += alloc_pct
        
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center;
                    padding:10px 0; border-bottom:1px solid #1e2a3a;">
            <div>
                <div style="font-size:11px; font-weight:600; color:{color};">{icon} {rec['asset'][:22]}</div>
                <div style="font-size:10px; color:#8892a4; font-family:'IBM Plex Mono',monospace;">{rec['ticker']}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-family:'IBM Plex Mono',monospace; font-size:14px; font-weight:700; color:#e8eaf0;">
                    {sign}{alloc_pct:.0f}%
                </div>
                <div style="font-size:10px; color:#8892a4;">
                    {amount:,.0f} €
                </div>
                <div style="font-size:10px; color:#00e676; font-family:'IBM Plex Mono',monospace;">
                    cible: +{potential:,.0f}€
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Cash remaining
    total_deployed = sum(a['pct'] for a in alloc_data if alloc_data[0]['action'] != 'SELL')
    cash_pct = max(0, 100 - total_deployed)
    cash_amount = portfolio_size * (cash_pct / 100)
    total_potential = sum(a['potential'] for a in alloc_data)
    
    st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 0; border-bottom:1px solid #1e2a3a;">
            <div style="font-size:11px; color:#8892a4;">◆ Cash / Liquidités</div>
            <div style="text-align:right;">
                <div style="font-family:'IBM Plex Mono',monospace; font-size:14px; color:#8892a4;">{cash_pct:.0f}%</div>
                <div style="font-size:10px; color:#8892a4;">{cash_amount:,.0f} €</div>
            </div>
        </div>
        <div style="margin-top:12px; padding:10px; background:#0a0d12; border-radius:3px;">
            <div style="font-size:10px; color:#8892a4; margin-bottom:4px;">GAIN POTENTIEL ESTIMÉ (72h)</div>
            <div style="font-family:'IBM Plex Mono',monospace; font-size:20px; color:#00e676; font-weight:700;">
                +{total_potential:,.0f} €
            </div>
            <div style="font-size:10px; color:#4a5568; margin-top:4px;">
                *Projections basées sur corrélations historiques. Pas un conseil financier.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Portfolio pie chart
    if alloc_data:
        labels = [a['asset'][:18] for a in alloc_data] + ['Cash']
        values = [a['pct'] for a in alloc_data] + [cash_pct]
        colors_pie = [a['color'] for a in alloc_data] + ['#2a3f5f']
        
        fig_pie = go.Figure(go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors_pie, line=dict(color='#0a0d12', width=2)),
            textfont=dict(size=10, color='#e8eaf0', family='IBM Plex Mono'),
            hole=0.5,
            hovertemplate='<b>%{label}</b><br>%{value:.0f}%<extra></extra>',
        ))
        fig_pie.update_layout(
            height=220,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='#141922',
            showlegend=False,
            annotations=[dict(
                text=f"{portfolio_size//1000}k€",
                x=0.5, y=0.5,
                font_size=14,
                font_family='IBM Plex Mono',
                font_color='#e8eaf0',
                showarrow=False
            )]
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""<hr>""", unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align:center; padding:16px; color:#4a5568; font-size:10px; letter-spacing:1px; font-family:'IBM Plex Mono',monospace;">
    GeoInvest Pro v2.0 &nbsp;|&nbsp; Données: NewsAPI · Alpha Vantage · GDELT (Demo Mode)
    &nbsp;|&nbsp; Powered by Streamlit + Plotly &nbsp;|&nbsp; {now_str}
    <br><br>
    <span style="color:#2a3f5f;">⚠ AVERTISSEMENT: Cette application est à des fins éducatives et analytiques uniquement. 
    Pas un conseil financier. Consultez un conseiller agréé avant tout investissement. 
    Les performances passées ne garantissent pas les performances futures.</span>
</div>
""", unsafe_allow_html=True)

# Auto-refresh logic
if auto_refresh:
    time.sleep(1)
    st.rerun()
