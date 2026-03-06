"""
╔══════════════════════════════════════════════════════════════╗
║        GeoInvest Pro — v3.0  |  Real-Time Edition           ║
║        Score live · SP500 · Twitter · Map news              ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import time
import random
from datetime import datetime, timedelta

try:
    import yfinance as yf
    YFINANCE_OK = True
except ImportError:
    YFINANCE_OK = False

try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_OK = True
except ImportError:
    AUTOREFRESH_OK = False

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GeoInvest Pro",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── API KEYS — via Streamlit Secrets ou variables directes ──────────────────
def _secret(key, default=""):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default

NEWS_API_KEY     = _secret("NEWS_API_KEY",     "YOUR_NEWSAPI_KEY")
TWITTER_BEARER   = _secret("TWITTER_BEARER",   "YOUR_TWITTER_BEARER_TOKEN")

# ─── CSS — Bloomberg Dark Terminal ────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

:root {
    --bg:        #07090f;
    --bg2:       #0d1117;
    --bg3:       #111720;
    --bg4:       #161e2e;
    --bgho:      #1a2236;
    --orange:    #ff6b35;
    --cyan:      #00d4ff;
    --green:     #00e676;
    --red:       #ff1744;
    --yellow:    #ffd600;
    --gold:      #ffc107;
    --white:     #e8eaf0;
    --grey:      #8892a4;
    --muted:     #3d4f6b;
    --border:    #1a2436;
    --borderhi:  #243554;
}
*                            { font-family:'IBM Plex Sans',sans-serif; box-sizing:border-box; }
html,body,[data-testid="stAppViewContainer"]
                             { background:var(--bg) !important; color:var(--white) !important; }
[data-testid="stSidebar"]    { background:var(--bg2) !important; border-right:1px solid var(--borderhi); }
[data-testid="stSidebar"] *  { color:var(--white) !important; }
.stSelectbox>div>div,.stMultiSelect>div>div
                             { background:var(--bg3) !important; border:1px solid var(--borderhi) !important; color:var(--white) !important; }
.stRadio>div                 { gap:6px; }
#MainMenu,footer,header      { visibility:hidden; }
::-webkit-scrollbar          { width:5px; }
::-webkit-scrollbar-track    { background:var(--bg); }
::-webkit-scrollbar-thumb    { background:var(--borderhi); border-radius:3px; }
hr                           { border-color:var(--border) !important; }

/* ── KPI ASSET CARD ─────────────────────── */
.kpi-card {
    background:var(--bg3);
    border:1px solid var(--border);
    border-radius:6px;
    padding:18px 22px;
    transition:border-color .15s,background .15s;
    text-decoration:none !important;
    display:block;
}
.kpi-card:hover { border-color:var(--cyan); background:var(--bgho); }
.kpi-label  { font-size:10px; letter-spacing:2px; text-transform:uppercase; color:var(--grey); margin-bottom:4px; }
.kpi-price  { font-family:'IBM Plex Mono',monospace; font-size:28px; font-weight:700; color:var(--white); line-height:1; }
.kpi-change { font-family:'IBM Plex Mono',monospace; font-size:13px; margin-top:5px; }
.kpi-up     { color:var(--green); }
.kpi-down   { color:var(--red); }
.kpi-link   { font-size:10px; color:var(--cyan); margin-top:8px; letter-spacing:1px; }

/* ── SCORE BADGES ───────────────────────── */
.score-wrap { display:flex; flex-direction:column; gap:10px; }
.score-badge {
    display:flex; align-items:center; justify-content:space-between;
    padding:14px 20px; border-radius:6px;
    font-family:'IBM Plex Mono',monospace; font-weight:700;
}
.s-critical { background:rgba(255,23,68,.12); border:2px solid var(--red);    color:var(--red);    box-shadow:0 0 18px rgba(255,23,68,.25); }
.s-high     { background:rgba(255,107,53,.12); border:2px solid var(--orange); color:var(--orange); box-shadow:0 0 18px rgba(255,107,53,.25); }
.s-medium   { background:rgba(255,214,0,.08);  border:2px solid var(--yellow); color:var(--yellow); }
.s-low      { background:rgba(0,230,118,.08);  border:2px solid var(--green);  color:var(--green);  }
.score-num  { font-size:32px; }
.score-info { text-align:right; }
.score-label{ font-size:9px; letter-spacing:2px; text-transform:uppercase; opacity:.7; }
.score-zone { font-size:12px; margin-top:2px; }

/* ── ALERT BANNER ───────────────────────── */
.alert {
    background:rgba(255,23,68,.08); border:1px solid rgba(255,23,68,.4);
    border-left:4px solid var(--red); border-radius:4px;
    padding:11px 16px; margin-bottom:14px; font-size:12px; color:var(--red);
    animation:pulse 2s infinite;
}
@keyframes pulse { 0%,100%{border-left-color:var(--red)} 50%{border-left-color:transparent} }

/* ── SECTION HEADER ─────────────────────── */
.sec {
    display:flex; align-items:center; gap:10px;
    padding:8px 0; margin:18px 0 12px; border-bottom:1px solid var(--borderhi);
}
.sec-title { font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:3px; text-transform:uppercase; color:var(--cyan); }
.sec-line  { flex:1; height:1px; background:var(--border); }

/* ── NEWS CARD ──────────────────────────── */
.news-card {
    background:var(--bg3); border:1px solid var(--border); border-radius:4px;
    padding:12px 16px; margin-bottom:8px; display:block; text-decoration:none !important;
    transition:border-color .12s,background .12s;
}
.news-card:hover { border-color:var(--orange); background:var(--bgho); }
.news-title { font-size:12px; font-weight:600; color:var(--white); line-height:1.5; margin-bottom:5px; }
.news-sub   { font-size:11px; color:var(--grey); font-style:italic; margin-bottom:6px; line-height:1.4; }
.news-foot  { display:flex; justify-content:space-between; align-items:center; }
.news-meta  { font-size:9px; color:var(--muted); letter-spacing:1px; text-transform:uppercase; }
.news-assets{ font-size:10px; color:var(--orange); font-family:'IBM Plex Mono',monospace; }
.news-read  { font-size:10px; color:var(--cyan); font-family:'IBM Plex Mono',monospace; }
.tag {
    display:inline-block; padding:2px 7px; border-radius:3px;
    font-size:10px; font-family:'IBM Plex Mono',monospace; margin-bottom:5px;
}
.tag-high   { background:rgba(255,23,68,.15); color:var(--red);    border:1px solid rgba(255,23,68,.3); }
.tag-medium { background:rgba(255,214,0,.08);  color:var(--yellow); border:1px solid rgba(255,214,0,.25); }
.tag-low    { background:rgba(0,230,118,.08);  color:var(--green);  border:1px solid rgba(0,230,118,.25); }
.tag-twitter{ background:rgba(0,212,255,.08);  color:var(--cyan);   border:1px solid rgba(0,212,255,.25); }

/* ── SENTIMENT BAR ──────────────────────── */
.sent-bar { height:4px; background:var(--border); border-radius:2px; overflow:hidden; margin-top:7px; }
.sent-fill { height:100%; border-radius:2px; background:linear-gradient(90deg,#ff1744,#ff6b35); }

/* ── INVEST CARD ────────────────────────── */
.inv-card {
    background:var(--bg3); border:1px solid var(--border); border-radius:6px;
    padding:16px 18px; margin-bottom:10px;
}
.inv-card.buy  { border-top:3px solid var(--green); }
.inv-card.sell { border-top:3px solid var(--red); }
.inv-card.hold { border-top:3px solid var(--yellow); }
.inv-action    { font-family:'IBM Plex Mono',monospace; font-size:9px; letter-spacing:2px; text-transform:uppercase; margin-bottom:4px; }
.inv-asset     { font-size:16px; font-weight:700; margin-bottom:4px; }
.inv-ticker    { font-family:'IBM Plex Mono',monospace; font-size:10px; color:var(--grey); margin-bottom:10px; }
.inv-grid      { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:10px; }
.inv-box       { background:var(--bg); padding:7px 10px; border-radius:3px; }
.inv-box-label { font-size:8px; color:var(--grey); letter-spacing:1px; text-transform:uppercase; }
.inv-box-val   { font-family:'IBM Plex Mono',monospace; font-size:16px; font-weight:700; margin-top:2px; }
.inv-detail    { font-size:11px; color:var(--grey); margin:3px 0; }
.inv-reason    { margin-top:10px; padding:9px 12px; background:var(--bg); border-radius:3px; }
.inv-reason-label { font-size:8px; color:var(--grey); letter-spacing:1px; text-transform:uppercase; margin-bottom:4px; }
.inv-reason-text  { font-size:11px; color:#b0bcd0; line-height:1.6; }

/* ── RISK TABLE ─────────────────────────── */
.rtable { background:var(--bg3); border:1px solid var(--border); border-radius:4px; overflow:hidden; }
.rrow   { display:grid; grid-template-columns:2fr .8fr 1.8fr .6fr; gap:8px; padding:10px 14px; border-bottom:1px solid var(--border); align-items:center; font-size:12px; }
.rrow:hover { background:var(--bgho); }
.rhead  { font-size:9px; color:var(--grey); letter-spacing:2px; text-transform:uppercase; font-weight:600; background:var(--bg2) !important; }
.pill   { display:inline-block; padding:2px 8px; border-radius:3px; font-family:'IBM Plex Mono',monospace; font-size:10px; font-weight:600; }
.p9,.p10{ background:rgba(255,23,68,.2); color:var(--red);    border:1px solid rgba(255,23,68,.4); }
.p7,.p8 { background:rgba(255,107,53,.2);color:var(--orange); border:1px solid rgba(255,107,53,.4); }
.p5,.p6 { background:rgba(255,214,0,.1); color:var(--yellow); border:1px solid rgba(255,214,0,.3); }
.p1,.p2,.p3,.p4 { background:rgba(0,230,118,.1); color:var(--green); border:1px solid rgba(0,230,118,.3); }

/* ── TICKER STRIP ───────────────────────── */
.ticker { background:var(--bg2); border:1px solid var(--border); border-radius:4px; padding:9px 14px; margin-bottom:14px; }
.ti { display:inline-block; font-family:'IBM Plex Mono',monospace; font-size:11px; margin-right:28px; white-space:nowrap; }
.ts { color:var(--cyan); font-weight:600; }
.tp { color:var(--white); margin:0 5px; }
.tu { color:var(--green); }
.td { color:var(--red); }

/* ── BUTTONS ────────────────────────────── */
.stButton>button {
    background:var(--bg3) !important; color:var(--cyan) !important;
    border:1px solid var(--borderhi) !important; border-radius:4px !important;
    font-family:'IBM Plex Mono',monospace !important; font-size:11px !important;
    letter-spacing:1px !important;
}
.stButton>button:hover { border-color:var(--cyan) !important; box-shadow:0 0 8px rgba(0,212,255,.2) !important; }

/* ── HEADER ─────────────────────────────── */
.hdr {
    background:linear-gradient(135deg,#07090f 0%,#0d1e38 60%,#070d1a 100%);
    border:1px solid var(--borderhi); border-top:3px solid var(--orange);
    border-radius:6px; padding:18px 24px; margin-bottom:16px;
    display:flex; align-items:center; justify-content:space-between;
    position:relative; overflow:hidden;
}
.hdr::before {
    content:''; position:absolute; inset:0;
    background:repeating-linear-gradient(90deg,transparent,transparent 50px,rgba(0,212,255,.02) 50px,rgba(0,212,255,.02) 51px);
}
.hdr-logo  { font-family:'IBM Plex Mono',monospace; font-size:26px; font-weight:700; color:var(--orange); letter-spacing:2px; text-shadow:0 0 18px rgba(255,107,53,.45); }
.hdr-sub   { font-size:10px; color:var(--grey); letter-spacing:3px; text-transform:uppercase; margin-top:2px; }
.hdr-right { text-align:right; font-family:'IBM Plex Mono',monospace; font-size:12px; color:var(--cyan); }
.live-dot  { display:inline-block; width:7px; height:7px; background:var(--green); border-radius:50%; margin-right:5px; animation:blink 1.2s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.2} }

/* ── PORTFOLIO SIM ──────────────────────── */
.alloc-row { display:flex; justify-content:space-between; align-items:center; padding:9px 0; border-bottom:1px solid var(--border); }
.alloc-name { font-size:11px; font-weight:600; }
.alloc-ticker{ font-size:9px; color:var(--grey); font-family:'IBM Plex Mono',monospace; }
.alloc-pct  { font-family:'IBM Plex Mono',monospace; font-size:14px; font-weight:700; }
.alloc-amt  { font-size:10px; color:var(--grey); text-align:right; }
.alloc-target{ font-size:10px; color:var(--green); font-family:'IBM Plex Mono',monospace; }
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
for k, v in [('lang','FR'), ('refresh_count', 0)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─── TRANSLATIONS ──────────────────────────────────────────────────────────────
L = {
    'FR': dict(
        subtitle='ANALYSE GÉOPOLITIQUE & INVESTISSEMENT EN TEMPS RÉEL',
        global_risk='RISQUE MONDIAL', region_risk='RISQUE RÉGION',
        refresh='⟳ ACTUALISER', auto='Refresh auto',
        news_sec='ACTUALITÉS EN DIRECT', map_sec='CARTE MONDIALE DES RISQUES',
        risk_sec='RISQUES PAR ZONE', invest_sec='RECOMMANDATIONS',
        portfolio_sec='SIMULATEUR PORTFOLIO',
        assets_sec='MARCHÉS CLÉS', twitter_sec='SIGNAUX TWITTER/X',
        regions='RÉGION', horizon='HORIZON', assets='ACTIFS',
        buy='▲ ACHAT', sell='▼ VENTE', hold='◆ NEUTRE',
        target='Objectif', stoploss='Stop-Loss',
        alloc='Allocation', correl='Corrélation géo',
        reason='Justification', horizon_lbl='Horizon',
        country='ZONE', score='SCORE', impact='IMPACT ÉCO', trend='TEND.',
        updated='MàJ', live_news='Live NewsAPI', live_mkt='Live Yahoo Finance',
        demo_news='Demo News', demo_mkt='Données simulées',
        twitter_live='Live Twitter/X', twitter_demo='Twitter non configuré',
        read_more='Lire →', tweet_src='@tweet',
        capital='Capital (€/$)', alloc_title='ALLOCATION RECOMMANDÉE',
        potential='Gain potentiel estimé (72h)',
        disclaimer='Projections indicatives. Pas un conseil financier.',
        critical='CRITIQUE', high='ÉLEVÉ', medium='MODÉRÉ', low='FAIBLE',
    ),
    'EN': dict(
        subtitle='REAL-TIME GEOPOLITICAL ANALYSIS & INVESTMENT',
        global_risk='GLOBAL RISK', region_risk='REGION RISK',
        refresh='⟳ REFRESH', auto='Auto Refresh',
        news_sec='LIVE NEWS', map_sec='GLOBAL RISK MAP',
        risk_sec='RISK BY ZONE', invest_sec='RECOMMENDATIONS',
        portfolio_sec='PORTFOLIO SIMULATOR',
        assets_sec='KEY MARKETS', twitter_sec='TWITTER/X SIGNALS',
        regions='REGION', horizon='HORIZON', assets='ASSETS',
        buy='▲ BUY', sell='▼ SELL', hold='◆ HOLD',
        target='Target', stoploss='Stop-Loss',
        alloc='Allocation', correl='Geo correlation',
        reason='Rationale', horizon_lbl='Horizon',
        country='ZONE', score='SCORE', impact='ECO IMPACT', trend='TREND',
        updated='Updated', live_news='Live NewsAPI', live_mkt='Live Yahoo Finance',
        demo_news='Demo News', demo_mkt='Simulated data',
        twitter_live='Live Twitter/X', twitter_demo='Twitter not configured',
        read_more='Read →', tweet_src='@tweet',
        capital='Capital (€/$)', alloc_title='RECOMMENDED ALLOCATION',
        potential='Estimated gain (72h)',
        disclaimer='Indicative projections. Not financial advice.',
        critical='CRITICAL', high='HIGH', medium='MODERATE', low='LOW',
    ),
}
def t(k): return L[st.session_state.lang].get(k, k)

# ─── KEYWORD HELPERS ───────────────────────────────────────────────────────────
NEG_KW = ["war","attack","strike","conflict","tension","missile","nuclear","sanction",
           "crisis","killed","death","threat","escalat","invasion","coup","terror",
           "guerre","attaque","conflit","nucléaire","crise","menace","escalad","terroris","tué","frappe"]
POS_KW = ["ceasefire","peace","deal","agreement","diplomacy","recovery","growth",
           "cessez","paix","accord","diplo","reprise","croissance","rebond"]
ASSET_MAP = {
    "iran":["OIL","XAU"],"ormuz":["OIL","XAU"],"opec":["OIL","USO"],
    "ukraine":["DEF","GAS"],"russia":["DEF","GAS"],"russie":["DEF","GAS"],
    "taiwan":["XAU","OIL"],"china":["XAU"],"chine":["XAU"],
    "gold":["XAU"],"inflation":["XAU","BOND"],
    "oil":["OIL","USO"],"pétrole":["OIL","USO"],"brent":["OIL"],
    "defense":["DEF"],"défense":["DEF"],"rheinmetall":["DEF"],"thales":["DEF"],
    "sp500":["SP500"],"s&p":["SP500"],"dow":["SP500"],
    "cac":["CAC40"],"euro":["CAC40","BOND"],"ecb":["BOND"],"bce":["BOND"],
}
ZONE_MAP = {
    "Middle-East": ["iran","ormuz","middle east","moyen-orient","red sea","mer rouge","houthi","israel","gaza","liban","hamas","riyadh","saudi"],
    "Europe":      ["ukraine","russia","russie","putin","zelensky","nato","otan","kiev","kharkiv","berlin","paris","ecb","bce","germany","allemagne","france"],
    "Asia-Pacific":["taiwan","china","chine","beijing","pékin","xi jinping","south china sea","north korea","japan","japon"],
    "Americas":    ["sp500","federal reserve","fed ","dow jones","nasdaq","wall street","white house","congress","venezuela","brazil"],
}

def score_sentiment(text):
    tl = text.lower()
    neg = sum(1 for kw in NEG_KW if kw in tl)
    pos = sum(1 for kw in POS_KW if kw in tl)
    raw = (pos - neg) / max(neg + pos, 1)
    return max(-1.0, min(1.0, raw - 0.1))

def detect_assets(text):
    tl = text.lower()
    assets = set()
    for kw, al in ASSET_MAP.items():
        if kw in tl: assets.update(al)
    return list(assets) if assets else ["XAU"]

def detect_impact(s): return "HIGH" if s <= -0.6 else ("MEDIUM" if s <= -0.3 else "LOW")

def detect_zone(text):
    tl = text.lower()
    for zone, keywords in ZONE_MAP.items():
        if any(k in tl for k in keywords): return zone
    return "Global"

# ─── FALLBACK NEWS ─────────────────────────────────────────────────────────────
FALLBACK_NEWS = [
    dict(title="Iran déploie des missiles balistiques près du détroit d'Ormuz",
         title_en="Iran deploys ballistic missiles near Strait of Hormuz",
         source="Reuters", sentiment=-0.72, impact="HIGH", zone="Middle-East",
         summary_fr="Escalade militaire : risque fermeture détroit → +pétrole, +or",
         summary_en="Military escalation: strait closure risk → +oil, +gold",
         asset_impact=["OIL","XAU"], age_min=45, url="https://www.reuters.com/world/middle-east/"),
    dict(title="Négociations nucléaires Iran s'effondrent, nouvelles sanctions US",
         title_en="Iran nuclear talks collapse, new US sanctions",
         source="Bloomberg", sentiment=-0.81, impact="HIGH", zone="Middle-East",
         summary_fr="Sanctions → perturbations export pétrole, hedge XAU",
         summary_en="Sanctions → oil export disruptions, XAU hedge",
         asset_impact=["OIL","XAU","USO"], age_min=120, url="https://www.bloomberg.com/energy"),
    dict(title="Ukraine frappe infrastructure russe, Moscou riposte sur Kharkiv",
         title_en="Ukraine strikes Russian infrastructure, Moscow retaliates",
         source="AP", sentiment=-0.65, impact="HIGH", zone="Europe",
         summary_fr="Intensification → défense EU en hausse, gaz +",
         summary_en="Escalation → EU defense up, gas prices rising",
         asset_impact=["DEF","GAS"], age_min=30, url="https://apnews.com/hub/russia-ukraine"),
    dict(title="Exercices militaires chinois entourent Taiwan, destroyer US déployé",
         title_en="Chinese exercises encircle Taiwan, US destroyer deployed",
         source="NYT", sentiment=-0.78, impact="HIGH", zone="Asia-Pacific",
         summary_fr="Risque semi-conducteurs → tech à vendre, XAU à acheter",
         summary_en="Chip disruption risk → sell tech, buy XAU",
         asset_impact=["XAU","OIL"], age_min=90, url="https://www.nytimes.com/section/world/asia"),
    dict(title="OPEP+ maintient coupes production, Brent au-dessus de 87$/b",
         title_en="OPEC+ holds production cuts, Brent above $87/b",
         source="OPEC", sentiment=-0.30, impact="MEDIUM", zone="Global",
         summary_fr="Pétrole soutenu → USO avantageux, inflation maintenue",
         summary_en="Oil supported → USO advantageous, inflation sustained",
         asset_impact=["OIL","USO"], age_min=60, url="https://www.opec.org/opec_web/en/press_room/"),
    dict(title="BCE signale pause dans les baisses de taux, inflation core persistante",
         title_en="ECB signals pause in rate cuts, core inflation persists",
         source="ECB", sentiment=-0.25, impact="MEDIUM", zone="Europe",
         summary_fr="Taux hauts prolongés → pression immobilier EU",
         summary_en="Prolonged high rates → EU real estate pressure",
         asset_impact=["XAU","BOND"], age_min=150, url="https://www.ecb.europa.eu/press/pressconf/"),
    dict(title="Mer Rouge : 15 navires déroutés suite aux attaques Houthis, fret +22%",
         title_en="Red Sea: 15 ships rerouted after Houthi attacks, freight +22%",
         source="FT", sentiment=-0.68, impact="HIGH", zone="Middle-East",
         summary_fr="Routes maritimes menacées → impact supply chaînes EU",
         summary_en="Maritime routes threatened → EU supply chain impact",
         asset_impact=["OIL","DEF"], age_min=210, url="https://www.ft.com/world/middle-east"),
    dict(title="S&P 500 chute de 1.4% face aux tensions géopolitiques croissantes",
         title_en="S&P 500 drops 1.4% amid rising geopolitical tensions",
         source="WSJ", sentiment=-0.55, impact="MEDIUM", zone="Americas",
         summary_fr="Volatilité SP500 → réduire exposition actions US court terme",
         summary_en="SP500 volatility → reduce US equity exposure short term",
         asset_impact=["SP500","XAU"], age_min=75, url="https://www.wsj.com/markets"),
]

def _enrich_fallback(items, region_filter):
    now = datetime.utcnow()
    out = []
    for item in items:
        it = dict(item)
        it['published_at'] = (now - timedelta(minutes=it['age_min'])).strftime('%H:%M UTC')
        out.append(it)
    if region_filter not in ["All","Monde"]:
        rm = {"EU":["Europe"],"Middle-East":["Middle-East"],"Asia-Pacific":["Asia-Pacific"],"Americas":["Americas"]}
        zones = rm.get(region_filter,[])
        if zones:
            out = [n for n in out if n.get('zone') in zones or n.get('zone')=='Global']
    out.sort(key=lambda x: abs(x['sentiment']), reverse=True)
    return out[:8]

# ─── LIVE NEWS — NEWSAPI ───────────────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def fetch_news(api_key, region_filter):
    if not api_key or "YOUR_" in api_key:
        return _enrich_fallback(FALLBACK_NEWS, region_filter), False

    queries = {
        "All":         "iran OR ukraine OR taiwan OR \"middle east\" OR geopolitical OR opec OR nato OR sp500",
        "Monde":       "iran OR ukraine OR taiwan OR \"middle east\" OR geopolitical OR opec OR nato",
        "EU":          "europe OR ukraine OR nato OR ECB OR germany OR france OR eurozone",
        "Middle-East": "iran OR israel OR gaza OR ormuz OR houthi OR opec OR saudi",
        "Asia-Pacific":"taiwan OR china OR \"north korea\" OR japan OR \"south china sea\"",
        "Americas":    "sp500 OR \"federal reserve\" OR nasdaq OR \"wall street\" OR \"white house\"",
    }
    try:
        r = requests.get("https://newsapi.org/v2/everything", timeout=8, params=dict(
            q=queries.get(region_filter, queries["All"]),
            language="en", sortBy="publishedAt", pageSize=20, apiKey=api_key,
        ))
        data = r.json()
        if data.get("status") != "ok" or not data.get("articles"):
            return _enrich_fallback(FALLBACK_NEWS, region_filter), False

        out = []
        for art in data["articles"][:14]:
            if not art.get("title") or art["title"] == "[Removed]": continue
            title = art["title"]
            desc  = art.get("description") or ""
            full  = f"{title} {desc}"
            sent  = score_sentiment(full)
            out.append(dict(
                title=title, title_en=title, source=art.get("source",{}).get("name","—"),
                sentiment=sent, impact=detect_impact(sent), zone=detect_zone(full),
                summary_fr=desc[:130]+"…" if len(desc)>130 else desc,
                summary_en=desc[:130]+"…" if len(desc)>130 else desc,
                asset_impact=detect_assets(full),
                published_at=art.get("publishedAt","")[:16].replace("T"," ")+" UTC",
                url=art.get("url","#"),
            ))
        out.sort(key=lambda x: abs(x["sentiment"]), reverse=True)
        return out[:8], True
    except Exception:
        return _enrich_fallback(FALLBACK_NEWS, region_filter), False

# ─── LIVE TWEETS — TWITTER API v2 ─────────────────────────────────────────────
# Key geopolitical signal accounts to monitor
TWITTER_ACCOUNTS = [
    "Reuters","AP","BBCWorld","FT","KyivIndependent",
    "IranIntl_En","AJEnglish","LippemannReport","RALee85",
]

@st.cache_data(ttl=300, show_spinner=False)
def fetch_tweets(bearer_token):
    if not bearer_token or "YOUR_" in bearer_token:
        return _fallback_tweets(), False
    accounts_query = " OR ".join(f"from:{acc}" for acc in TWITTER_ACCOUNTS)
    geo_query = "(iran OR ukraine OR taiwan OR geopolitical OR opec OR nato OR \"middle east\")"
    query = f"({accounts_query}) {geo_query} -is:retweet lang:en"
    try:
        r = requests.get(
            "https://api.twitter.com/2/tweets/search/recent",
            headers={"Authorization": f"Bearer {bearer_token}"},
            params=dict(query=query, max_results=10,
                        tweet_fields="created_at,author_id,entities",
                        expansions="author_id",
                        user_fields="username,name"),
            timeout=8,
        )
        data = r.json()
        if "data" not in data: return _fallback_tweets(), False

        users = {u["id"]: u for u in data.get("includes",{}).get("users",[])}
        tweets = []
        for tw in data["data"][:6]:
            uid    = tw.get("author_id","")
            user   = users.get(uid, {})
            handle = user.get("username","unknown")
            text   = tw["text"]
            sent   = score_sentiment(text)
            tweets.append(dict(
                text=text[:200]+"…" if len(text)>200 else text,
                handle=f"@{handle}",
                sentiment=sent,
                impact=detect_impact(sent),
                zone=detect_zone(text),
                asset_impact=detect_assets(text),
                published_at=tw.get("created_at","")[:16].replace("T"," ")+" UTC",
                url=f"https://twitter.com/{handle}/status/{tw['id']}",
            ))
        return tweets, True
    except Exception:
        return _fallback_tweets(), False

def _fallback_tweets():
    now = datetime.utcnow()
    return [
        dict(text="⚠️ BREAKING: Iran Revolutionary Guard conducts live-fire exercises near Strait of Hormuz, warning to US naval presence",
             handle="@IranIntl_En", sentiment=-0.78, impact="HIGH", zone="Middle-East",
             asset_impact=["OIL","XAU"],
             published_at=(now-timedelta(minutes=22)).strftime('%H:%M UTC'),
             url="https://twitter.com/IranIntl_En"),
        dict(text="Russian forces target Ukrainian energy grid for the 4th time this month. EU emergency energy meeting called for tomorrow.",
             handle="@KyivIndependent", sentiment=-0.65, impact="HIGH", zone="Europe",
             asset_impact=["DEF","GAS"],
             published_at=(now-timedelta(minutes=55)).strftime('%H:%M UTC'),
             url="https://twitter.com/KyivIndependent"),
        dict(text="OPEC+ sources: production cuts extended by 3 months minimum. Brent crude reacts immediately, now testing $88/b resistance.",
             handle="@Reuters", sentiment=-0.3, impact="MEDIUM", zone="Global",
             asset_impact=["OIL","USO"],
             published_at=(now-timedelta(minutes=88)).strftime('%H:%M UTC'),
             url="https://twitter.com/Reuters"),
        dict(text="Taiwan Strait tensions at 6-month high. PLA conducts unannounced drills. TSMC supply chain concerns resurface.",
             handle="@AP", sentiment=-0.72, impact="HIGH", zone="Asia-Pacific",
             asset_impact=["XAU","SP500"],
             published_at=(now-timedelta(minutes=140)).strftime('%H:%M UTC'),
             url="https://twitter.com/AP"),
    ]

# ─── LIVE MARKET DATA — YFINANCE ───────────────────────────────────────────────
MARKET_SYMBOLS = {
    "Or (XAU)":  dict(sym="GC=F",   unit="$",   link="https://finance.yahoo.com/quote/GC=F"),
    "Pétrole":   dict(sym="BZ=F",   unit="$",   link="https://finance.yahoo.com/quote/BZ=F"),
    "S&P 500":   dict(sym="^GSPC",  unit="",    link="https://finance.yahoo.com/quote/%5EGSPC"),
    "CAC 40":    dict(sym="^FCHI",  unit="",    link="https://finance.yahoo.com/quote/%5EFCHI"),
    "EUR/USD":   dict(sym="EURUSD=X",unit="",   link="https://finance.yahoo.com/quote/EURUSD=X"),
    "VIX":       dict(sym="^VIX",   unit="",    link="https://finance.yahoo.com/quote/%5EVIX"),
    "GLD ETF":   dict(sym="GLD",    unit="$",   link="https://finance.yahoo.com/quote/GLD"),
    "USO ETF":   dict(sym="USO",    unit="$",   link="https://finance.yahoo.com/quote/USO"),
}

@st.cache_data(ttl=180, show_spinner=False)   # refresh every 3 minutes
def fetch_market_data():
    if not YFINANCE_OK:
        return _sim_market(), False
    result = {}
    try:
        syms = " ".join(v["sym"] for v in MARKET_SYMBOLS.values())
        tickers = yf.Tickers(syms)
        for name, meta in MARKET_SYMBOLS.items():
            try:
                hist = tickers.tickers[meta["sym"]].history(period="2d", interval="1h")
                if hist.empty or len(hist) < 2: raise ValueError
                cur  = float(hist["Close"].iloc[-1])
                prev = float(hist["Close"].iloc[0])
                chg  = round((cur - prev) / prev * 100, 2)
                result[name] = dict(price=round(cur,2), change=chg,
                                    unit=meta["unit"], link=meta["link"])
            except Exception:
                sim = _sim_market()
                result[name] = sim.get(name, dict(price=0, change=0, unit="", link="#"))
        return result, True
    except Exception:
        return _sim_market(), False

def _sim_market():
    seed = int(time.time() / 180)
    random.seed(seed)
    rp = lambda b, v=0.012: round(b*(1+random.gauss(0,v)), 2)
    rc = lambda b, v=0.4:   round(b+random.gauss(0,v), 2)
    return {
        "Or (XAU)": dict(price=rp(2341),    change=rc(+0.8), unit="$",  link="https://finance.yahoo.com/quote/GC=F"),
        "Pétrole":  dict(price=rp(87.40),   change=rc(+1.1), unit="$",  link="https://finance.yahoo.com/quote/BZ=F"),
        "S&P 500":  dict(price=rp(5210),    change=rc(-0.6), unit="",   link="https://finance.yahoo.com/quote/%5EGSPC"),
        "CAC 40":   dict(price=rp(7823),    change=rc(-0.4), unit="",   link="https://finance.yahoo.com/quote/%5EFCHI"),
        "EUR/USD":  dict(price=rp(1.0842,0.003), change=rc(-0.1,0.15), unit="", link="https://finance.yahoo.com/quote/EURUSD=X"),
        "VIX":      dict(price=rp(16.8,0.05), change=rc(+2.0,0.8), unit="", link="https://finance.yahoo.com/quote/%5EVIX"),
        "GLD ETF":  dict(price=rp(218.5),   change=rc(+0.7), unit="$",  link="https://finance.yahoo.com/quote/GLD"),
        "USO ETF":  dict(price=rp(79.8),    change=rc(+1.0), unit="$",  link="https://finance.yahoo.com/quote/USO"),
    }

# ─── RISK ZONES ────────────────────────────────────────────────────────────────
def get_risk_zones():
    return [
        dict(zone_fr="Iran / Moyen-Orient", zone_en="Iran / Middle-East",
             lat=32.4, lon=53.7, risk=9.1, trend="▲", trend_dir="up",
             impact_fr="Risque énergie critique — pétrole, chaînes appro",
             impact_en="Critical energy risk — oil, supply chains", color="#ff1744"),
        dict(zone_fr="Ukraine / Russie", zone_en="Ukraine / Russia",
             lat=49.0, lon=32.0, risk=7.8, trend="→", trend_dir="neutral",
             impact_fr="Défense EU, gaz naturel, blé",
             impact_en="EU defense, natural gas, wheat", color="#ff6b35"),
        dict(zone_fr="Détroit de Taïwan", zone_en="Taiwan Strait",
             lat=23.7, lon=121.0, risk=7.2, trend="▲", trend_dir="up",
             impact_fr="Semi-conducteurs, logistique maritime",
             impact_en="Semiconductors, maritime logistics", color="#ff6b35"),
        dict(zone_fr="Mer Rouge / Houthis", zone_en="Red Sea / Houthis",
             lat=15.0, lon=43.0, risk=7.5, trend="▲", trend_dir="up",
             impact_fr="Disruption maritime, +15% coûts fret",
             impact_en="Maritime disruption, +15% freight costs", color="#ff6b35"),
        dict(zone_fr="Zone Euro (éco)", zone_en="Eurozone (eco)",
             lat=50.0, lon=10.0, risk=5.9, trend="▼", trend_dir="down",
             impact_fr="Récession Allemagne, BCE, inflation",
             impact_en="Germany recession, ECB, inflation", color="#ffd600"),
        dict(zone_fr="Sahel / Afrique", zone_en="Sahel / Africa",
             lat=14.0, lon=2.0, risk=5.1, trend="→", trend_dir="neutral",
             impact_fr="Matières premières, instabilité politique",
             impact_en="Raw materials, political instability", color="#ffd600"),
        dict(zone_fr="Corée du Nord", zone_en="North Korea",
             lat=40.0, lon=127.5, risk=4.8, trend="▼", trend_dir="down",
             impact_fr="Risque nucléaire latent, Seoul stable",
             impact_en="Latent nuclear risk, Seoul stable", color="#ffd600"),
        dict(zone_fr="Amérique Latine", zone_en="Latin America",
             lat=-15.0, lon=-60.0, risk=3.2, trend="→", trend_dir="neutral",
             impact_fr="Commodities, lithium, instabilité modérée",
             impact_en="Commodities, lithium, moderate instability", color="#00e676"),
    ]

def compute_risk_score(news_items, zones):
    sentiments = [abs(n['sentiment']) for n in news_items] or [0.5]
    news_s  = (sum(sentiments) / len(sentiments)) * 10
    conf_s  = min(sum(1 for z in zones if z['risk'] > 7.0) * 2.5, 10)
    eco_s   = 6.2
    return min(round(news_s*.5 + conf_s*.3 + eco_s*.2, 1), 10.0)

def compute_region_risk(news_items, zones, region):
    """Region-specific risk score from filtered news + matching zones."""
    zone_map = {
        "EU":          "Europe",
        "Middle-East": "Middle-East",
        "Asia-Pacific":"Asia-Pacific",
        "Americas":    "Americas",
    }
    target = zone_map.get(region)
    if not target:
        return compute_risk_score(news_items, zones)
    reg_news  = [n for n in news_items if n.get('zone') == target] or news_items
    reg_zones = [z for z in zones if target.lower() in z['zone_en'].lower()]
    if not reg_zones: reg_zones = zones
    return compute_risk_score(reg_news, reg_zones)

def risk_css(score):
    if score >= 8.5: return "s-critical", t('critical')
    if score >= 7.0: return "s-high",     t('high')
    if score >= 5.0: return "s-medium",   t('medium')
    return "s-low", t('low')

# ─── INVESTMENT RECS ───────────────────────────────────────────────────────────
def get_recommendations(global_risk, lang):
    if global_risk >= 8.0:
        return [
            dict(asset="Or (XAU/USD)", ticker="XAU / GLD", action="BUY", icon="🥇",
                 target="+5.5%", stoploss="-1.8%", alloc="25%", correl="0.82", horizon="48-72h",
                 color="#ffc107",
                 reason_fr="Corrélation 0.82 avec tensions Moyen-Orient. Escalade Iran-Ormuz → valeurs refuges. Chaque +1pt de risque = +0.8% XAU historiquement.",
                 reason_en="0.82 correlation with Middle-East tensions. Iran-Hormuz escalation → safe havens. Each +1pt risk = +0.8% XAU historically."),
            dict(asset="Pétrole Brent / USO", ticker="USO / UCO", action="BUY", icon="🛢️",
                 target="+4.2%", stoploss="-2.5%", alloc="15%", correl="0.91", horizon="24-48h",
                 color="#ff6b35",
                 reason_fr="Risque fermeture détroit d'Ormuz (30% pétrole mondial). Corrélation 0.91 Iran-Brent. OPEC+ cuts soutiennent le plancher.",
                 reason_en="Hormuz closure risk (30% world oil). 0.91 Iran-Brent correlation. OPEC+ cuts support the floor."),
            dict(asset="ETF Défense EU", ticker="EUDF / HELO", action="BUY", icon="🛡️",
                 target="+6.0%", stoploss="-2.0%", alloc="20%", correl="0.75", horizon="72h-1sem",
                 color="#00b0ff",
                 reason_fr="Budget défense EU +40% depuis 2022. Rheinmetall, Thales, Leonardo bénéficiaires directs.",
                 reason_en="EU defense budget +40% since 2022. Rheinmetall, Thales, Leonardo direct beneficiaries."),
            dict(asset="S&P 500 / SPY", ticker="SPY / ES=F", action="SELL", icon="📉",
                 target="-2.5%", stoploss="+1.2%", alloc="-15%", correl="-0.71", horizon="48h",
                 color="#ff1744",
                 reason_fr="Corrélation négative -0.71 avec risque géo élevé. Volatilité VIX en hausse → réduire exposition équités US.",
                 reason_en="Negative -0.71 correlation with high geo-risk. Rising VIX → reduce US equity exposure."),
        ]
    elif global_risk >= 6.0:
        return [
            dict(asset="Or (XAU/USD)", ticker="XAU / GLD", action="BUY", icon="🥇",
                 target="+2.5%", stoploss="-1.5%", alloc="15%", correl="0.82", horizon="72h",
                 color="#ffc107",
                 reason_fr="Risque modéré croissant. Position défensive sur XAU avant escalade potentielle.",
                 reason_en="Moderate and growing risk. Defensive XAU position ahead of potential escalation."),
            dict(asset="Pétrole Brent", ticker="USO ETF", action="HOLD", icon="🛢️",
                 target="+1.5%", stoploss="-3.0%", alloc="10%", correl="0.65", horizon="72h",
                 color="#ffd600",
                 reason_fr="OPEC+ soutient les cours. Conserver positions, pas d'extension agressive.",
                 reason_en="OPEC+ supports prices. Hold positions, no aggressive extension."),
            dict(asset="S&P 500", ticker="SPY / ES=F", action="HOLD", icon="📊",
                 target="+1.0%", stoploss="-2.0%", alloc="20%", correl="-0.55", horizon="72h",
                 color="#ffd600",
                 reason_fr="Marché US résilient mais vulnérable. Réduire levier, conserver positions core.",
                 reason_en="US market resilient but vulnerable. Reduce leverage, keep core positions."),
        ]
    else:
        return [
            dict(asset="S&P 500 / SPY", ticker="SPY / QQQ", action="BUY", icon="📈",
                 target="+2.5%", stoploss="-1.0%", alloc="30%", correl="-0.5", horizon="1 semaine",
                 color="#00e676",
                 reason_fr="Risque faible → retour vers actifs risqués. Croissance US robuste, VIX bas.",
                 reason_en="Low risk → return to risk assets. Robust US growth, low VIX."),
            dict(asset="Or (XAU/USD)", ticker="XAU / GLD", action="HOLD", icon="🥇",
                 target="+1.0%", stoploss="-1.5%", alloc="10%", correl="0.82", horizon="1 semaine",
                 color="#ffc107",
                 reason_fr="Conserver allocation or structurelle. Risque géo résiduel justifie une position minimale.",
                 reason_en="Hold structural gold allocation. Residual geo-risk justifies a minimum position."),
        ]

# ─── CHART: RISK MAP (Globe) ───────────────────────────────────────────────────
def build_risk_map(zones, news_items, lang):
    """World map with zone bubbles + critical news pins."""
    lats, lons, sizes, colors, labels = [], [], [], [], []
    lang_key = "zone_en" if lang == "EN" else "zone_fr"
    impact_key = "impact_en" if lang == "EN" else "impact_fr"

    for z in zones:
        lats.append(z["lat"]); lons.append(z["lon"])
        sizes.append(z["risk"] * 6)
        colors.append(z["color"])
        labels.append(f"<b>{z[lang_key]}</b><br>Risque: {z['risk']}/10<br>{z[impact_key]}")

    fig = go.Figure()

    # Zone bubbles
    fig.add_trace(go.Scattergeo(
        lat=lats, lon=lons, text=labels, hoverinfo="text",
        mode="markers",
        marker=dict(size=sizes, color=colors, opacity=0.70,
                    line=dict(width=1, color="rgba(255,255,255,0.2)"),
                    sizemode="area"),
        name="Zones",
    ))

    # Critical news pins (HIGH impact only)
    zone_coords = {
        "Middle-East": (26.0, 50.0), "Europe": (51.0, 15.0),
        "Asia-Pacific": (30.0, 118.0), "Americas": (35.0, -95.0), "Global": (20.0, 0.0),
    }
    critical_news = [n for n in news_items if n["impact"] == "HIGH"]
    seen_zones = set()
    n_lats, n_lons, n_text = [], [], []
    for n in critical_news:
        zone = n.get("zone","Global")
        if zone in seen_zones: continue
        seen_zones.add(zone)
        coord = zone_coords.get(zone, (0.0, 0.0))
        title_key = "title_en" if lang == "EN" else "title"
        n_lats.append(coord[0]); n_lons.append(coord[1])
        n_text.append(f"⚡ {n[title_key][:60]}…")

    if n_lats:
        fig.add_trace(go.Scattergeo(
            lat=n_lats, lon=n_lons, text=n_text, hoverinfo="text",
            mode="markers+text",
            marker=dict(size=10, color="#ff1744", symbol="star",
                        line=dict(width=1, color="#ffffff")),
            textfont=dict(size=8, color="#ff1744"),
            textposition="top center",
            name="Alertes",
        ))

    fig.update_layout(
        height=420, margin=dict(l=0,r=0,t=0,b=0),
        paper_bgcolor="#07090f",
        geo=dict(
            showframe=False, showcoastlines=True, coastlinecolor="#1e3050",
            showland=True, landcolor="#0d1520",
            showocean=True, oceancolor="#070c14",
            showcountries=True, countrycolor="#1a2a3a",
            showlakes=False,
            projection_type="natural earth",
            bgcolor="#07090f",
        ),
        showlegend=False,
    )
    return fig

# ─── CHART: RISK BAR ───────────────────────────────────────────────────────────
def build_risk_bar(zones, lang):
    key = "zone_en" if lang=="EN" else "zone_fr"
    zones_sorted = sorted(zones, key=lambda z: z["risk"], reverse=True)
    fig = go.Figure(go.Bar(
        x=[z["risk"] for z in zones_sorted],
        y=[z[key] for z in zones_sorted],
        orientation="h",
        marker=dict(color=[z["color"] for z in zones_sorted], opacity=0.80, line=dict(width=0)),
        text=[f"  {z['risk']}/10" for z in zones_sorted],
        textposition="outside",
        textfont=dict(family="IBM Plex Mono", size=10, color="#e8eaf0"),
    ))
    for x, label, col in [(7.0,"ÉLEVÉ","#ff6b35"),(8.5,"CRITIQUE","#ff1744")]:
        fig.add_vline(x=x, line_dash="dot", line_color=col, line_width=1,
                      annotation_text=label, annotation_font_color=col, annotation_font_size=9)
    fig.update_layout(
        height=300, margin=dict(l=10,r=60,t=10,b=10),
        paper_bgcolor="#07090f", plot_bgcolor="#07090f",
        xaxis=dict(range=[0,11], gridcolor="#1e2a3a", tickfont=dict(color="#8892a4",size=10), zeroline=False),
        yaxis=dict(tickfont=dict(color="#e8eaf0",size=11), gridcolor="#1e2a3a"),
        showlegend=False,
    )
    return fig

# ─── GAUGE ─────────────────────────────────────────────────────────────────────
def build_gauge(score, title=""):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number=dict(font=dict(size=44, color="#e8eaf0", family="IBM Plex Mono"), suffix="/10"),
        gauge=dict(
            axis=dict(range=[0,10], tickwidth=1, tickcolor="#4a5568", tickfont=dict(color="#8892a4",size=10)),
            bar=dict(color="#ff6b35", thickness=0.28),
            bgcolor="#141922", borderwidth=0,
            steps=[
                dict(range=[0,3],  color="rgba(0,230,118,0.10)"),
                dict(range=[3,6],  color="rgba(255,214,0,0.10)"),
                dict(range=[6,8],  color="rgba(255,107,53,0.10)"),
                dict(range=[8,10], color="rgba(255,23,68,0.13)"),
            ],
            threshold=dict(line=dict(color="#ff1744",width=2), thickness=0.75, value=score),
        )
    ))
    fig.update_layout(
        height=200, margin=dict(l=20,r=20,t=30,b=5),
        paper_bgcolor="#07090f", font=dict(family="IBM Plex Mono"),
        title=dict(text=title, font=dict(size=10, color="#8892a4"), x=0.5),
    )
    return fig

# ═══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:14px 0 12px;border-bottom:1px solid #1a2436;margin-bottom:14px;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:17px;color:#ff6b35;font-weight:700;letter-spacing:2px;">🌍 GeoInvest Pro</div>
        <div style="font-size:9px;color:#8892a4;letter-spacing:3px;margin-top:3px;">TERMINAL v3.0</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🇫🇷 FR", use_container_width=True): st.session_state.lang = "FR"
    with c2:
        if st.button("🇬🇧 EN", use_container_width=True): st.session_state.lang = "EN"

    st.markdown("---")

    lang = st.session_state.lang

    st.markdown(f"<div style='font-size:9px;color:#8892a4;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;'>{t('regions')}</div>", unsafe_allow_html=True)
    region_options = ["Monde / World","EU / Europe","Middle-East / Iran","Asia-Pacific","Americas / US"]
    sel_region = st.selectbox("", region_options, label_visibility="collapsed")
    region_key = (
        "Middle-East" if "Iran" in sel_region or "Middle" in sel_region
        else "EU"          if "EU" in sel_region
        else "Asia-Pacific"if "Asia" in sel_region
        else "Americas"    if "Americas" in sel_region
        else "All"
    )

    st.markdown("---")
    st.markdown(f"<div style='font-size:9px;color:#8892a4;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;'>{t('horizon')}</div>", unsafe_allow_html=True)
    horizon = st.radio("", ["24h","72h","1 semaine"], label_visibility="collapsed")

    st.markdown("---")
    st.markdown(f"<div style='font-size:9px;color:#8892a4;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;'>{t('assets')}</div>", unsafe_allow_html=True)
    assets_filter = st.multiselect("",
        ["Or (XAU)","Pétrole / Oil","S&P 500","ETF Défense","ETF Énergie","Forex EUR/USD","Indices EU"],
        default=["Or (XAU)","Pétrole / Oil","S&P 500","ETF Défense"],
        label_visibility="collapsed")

    st.markdown("---")

    # Auto-refresh toggle + interval
    auto_on = st.toggle(t('auto'), value=True)
    if auto_on:
        refresh_sec = st.select_slider("Intervalle", options=[30,60,120,300], value=60, format_func=lambda x: f"{x}s")
    else:
        refresh_sec = 60

    if st.button(t('refresh'), use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")

    # API status (will update after data is loaded — placeholder text)
    status_placeholder = st.empty()

    st.markdown("---")
    st.markdown("<div style='font-size:9px;color:#8892a4;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;'>EXPORT</div>", unsafe_allow_html=True)
    risk_zones = get_risk_zones()
    csv_data = pd.DataFrame(risk_zones)[["zone_fr","zone_en","risk","trend"]].to_csv(index=False)
    st.download_button("📥 Export CSV Risques", csv_data, "risks.csv", "text/csv", use_container_width=True)

# ─── AUTO-REFRESH (streamlit-autorefresh) ─────────────────────────────────────
if auto_on and AUTOREFRESH_OK:
    count = st_autorefresh(interval=refresh_sec * 1000, key="main_refresh")
elif auto_on:
    # Fallback: manual rerun via session state timer
    if "next_refresh" not in st.session_state:
        st.session_state.next_refresh = time.time() + refresh_sec
    if time.time() >= st.session_state.next_refresh:
        st.session_state.next_refresh = time.time() + refresh_sec
        st.cache_data.clear()
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
#  DATA LOAD
# ═══════════════════════════════════════════════════════════════════════════════
now_str   = datetime.utcnow().strftime("%Y-%m-%d  %H:%M UTC")
lang      = st.session_state.lang

news_items, news_live   = fetch_news(NEWS_API_KEY, region_key)
tweets, twitter_live    = fetch_tweets(TWITTER_BEARER)
market_data, mkt_live   = fetch_market_data()
risk_zones              = get_risk_zones()
global_risk             = compute_risk_score(news_items, risk_zones)
region_risk             = compute_region_risk(news_items, risk_zones, region_key)
recommendations         = get_recommendations(global_risk, lang)

gc, gl = risk_css(global_risk)
rc_cls, rl = risk_css(region_risk)

# Update sidebar status
news_badge   = (f"🟢 {t('live_news')}"    if news_live    else f"🟡 {t('demo_news')}")
mkt_badge    = (f"🟢 {t('live_mkt')}"     if mkt_live     else f"🟡 {t('demo_mkt')}")
twit_badge   = (f"🟢 {t('twitter_live')}" if twitter_live else f"🟡 {t('twitter_demo')}")

status_placeholder.markdown(f"""
<div style="padding:10px;background:#0d1117;border:1px solid #1a2436;border-radius:4px;font-size:10px;color:#8892a4;">
    <div style="color:#00e676;margin-bottom:5px;">● SYSTÈME EN LIGNE</div>
    <div>{news_badge}</div>
    <div>{mkt_badge}</div>
    <div>{twit_badge}</div>
    <div style="margin-top:6px;color:#3d4f6b;font-size:9px;">{'Clés actives ✓' if news_live else 'Configurer Streamlit Secrets'}</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  RENDER — HEADER
# ═══════════════════════════════════════════════════════════════════════════════
auto_label = f"{'ON ●' if auto_on else 'OFF ○'} ({refresh_sec}s)" if auto_on else "OFF ○"
st.markdown(f"""
<div class="hdr">
  <div>
    <div class="hdr-logo">⬡ GeoInvest Pro</div>
    <div class="hdr-sub">{t('subtitle')}</div>
  </div>
  <div style="display:flex;gap:14px;align-items:center;">
    <div>
      <div style="font-size:9px;color:#8892a4;letter-spacing:2px;margin-bottom:5px;">{t('global_risk')}</div>
      <div class="risk-badge {gc}" style="padding:10px 18px;font-size:20px;">{global_risk}/10 — {gl}</div>
    </div>
    <div>
      <div style="font-size:9px;color:#8892a4;letter-spacing:2px;margin-bottom:5px;">{t('region_risk')} · {sel_region.split('/')[0].strip()}</div>
      <div class="risk-badge {rc_cls}" style="padding:10px 18px;font-size:20px;">{region_risk}/10 — {rl}</div>
    </div>
  </div>
  <div class="hdr-right">
    <div style="font-size:9px;color:#8892a4;margin-bottom:3px;">{t('updated')}</div>
    <div>{now_str}</div>
    <div style="margin-top:5px;font-size:10px;">{news_badge}</div>
    <div style="font-size:10px;">{mkt_badge}</div>
    <div style="font-size:9px;color:#3d4f6b;margin-top:4px;">AUTO: {auto_label}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Alert banner
if global_risk >= 7.5:
    msgs = {
        "FR": f"⚡ ALERTE — Score {global_risk}/10 · Tensions {sel_region} au niveau {gl} · Hedge géopolitique recommandé · Surveillance 24/7 active",
        "EN": f"⚡ ALERT — Score {global_risk}/10 · {sel_region} tensions at {gl} level · Geopolitical hedge recommended · 24/7 active monitoring",
    }
    st.markdown(f'<div class="alert">{msgs[lang]}</div>', unsafe_allow_html=True)

# ─── TICKER STRIP ──────────────────────────────────────────────────────────────
ticker_html = '<div class="ticker">'
for name, d in market_data.items():
    c = d['change']
    cls = "tu" if c >= 0 else "td"
    arrow = "▲" if c >= 0 else "▼"
    ticker_html += f'<span class="ti"><span class="ts">{name}</span><span class="tp">{d["unit"]}{d["price"]}</span><span class="{cls}">{arrow}{abs(c):.2f}%</span></span>'
ticker_html += "</div>"
st.markdown(ticker_html, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  ROW 1 — KPI ACTIFS + GAUGES
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f'<div class="sec"><span class="sec-title">📊 {t("assets_sec")}</span><div class="sec-line"></div></div>', unsafe_allow_html=True)

kpi_keys = ["Or (XAU)", "Pétrole", "S&P 500"]
kpi_cols = st.columns([1, 1, 1, 1.2, 1.2])

for i, name in enumerate(kpi_keys):
    d = market_data.get(name, {})
    if not d: continue
    c = d.get("change", 0)
    cls = "kpi-up" if c >= 0 else "kpi-down"
    arrow = "▲" if c >= 0 else "▼"
    border_col = "#00e676" if c >= 0 else "#ff1744"
    if "Or" in name or "XAU" in name: border_col = "#ffc107"
    link = d.get("link", "#")
    unit = d.get("unit", "")
    with kpi_cols[i]:
        st.markdown(f"""
        <a href="{link}" target="_blank" class="kpi-card" style="border-left:3px solid {border_col};">
            <div class="kpi-label">{name}</div>
            <div class="kpi-price">{unit}{d['price']:,}</div>
            <div class="kpi-change {cls}">{arrow} {abs(c):.2f}%</div>
            <div class="kpi-link">Yahoo Finance →</div>
        </a>
        """, unsafe_allow_html=True)

with kpi_cols[3]:
    st.markdown(f'<div style="font-size:9px;color:#8892a4;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">{t("global_risk")}</div>', unsafe_allow_html=True)
    st.plotly_chart(build_gauge(global_risk, t("global_risk")), use_container_width=True, config={"displayModeBar":False})

with kpi_cols[4]:
    r_label = f"{t('region_risk')} · {sel_region.split('/')[0].strip()}"
    st.markdown(f'<div style="font-size:9px;color:#8892a4;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;">{r_label}</div>', unsafe_allow_html=True)
    st.plotly_chart(build_gauge(region_risk, r_label), use_container_width=True, config={"displayModeBar":False})

st.markdown("<hr>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  ROW 2 — MAP + NEWS + TWEETS  (side by side)
# ═══════════════════════════════════════════════════════════════════════════════
col_map, col_right = st.columns([1.5, 1])

with col_map:
    st.markdown(f'<div class="sec"><span class="sec-title">🗺️ {t("map_sec")}</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
    st.plotly_chart(build_risk_map(risk_zones, news_items, lang), use_container_width=True, config={"displayModeBar":False})

    # Risk bar chart below map
    st.markdown(f'<div class="sec"><span class="sec-title">📊 {t("risk_sec")}</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
    st.plotly_chart(build_risk_bar(risk_zones, lang), use_container_width=True, config={"displayModeBar":False})

with col_right:
    # ── NEWS ──────────────────────────────────────────────────────────────────
    live_dot = '<span class="live-dot"></span>' if news_live else ""
    st.markdown(f'<div class="sec"><span class="sec-title">📡 {live_dot}{t("news_sec")}</span><div class="sec-line"></div></div>', unsafe_allow_html=True)

    impact_labels_fr = {"HIGH":"IMPACT ÉLEVÉ","MEDIUM":"IMPACT MODÉRÉ","LOW":"IMPACT FAIBLE"}
    impact_labels_en = {"HIGH":"HIGH IMPACT","MEDIUM":"MEDIUM IMPACT","LOW":"LOW IMPACT"}

    for i, n in enumerate(news_items[:5]):
        title   = n["title_en"] if lang=="EN" else n["title"]
        summary = n["summary_en"] if lang=="EN" else n["summary_fr"]
        imp_lbl = (impact_labels_en if lang=="EN" else impact_labels_fr).get(n["impact"],"")
        imp_cls = f"tag-{n['impact'].lower()}"
        assets  = " · ".join(n.get("asset_impact",[]))
        sent_w  = int(abs(n["sentiment"]) * 100)
        url     = n.get("url","#")
        st.markdown(f"""
        <a href="{url}" target="_blank" class="news-card">
            <div style="display:flex;justify-content:space-between;align-items:start;gap:6px;">
                <div class="news-title">{i+1}. {title}</div>
                <span class="tag {imp_cls}" style="white-space:nowrap;">{imp_lbl}</span>
            </div>
            <div class="news-sub">{summary}</div>
            <div class="news-foot">
                <div class="news-meta">{n['source']} · {n['published_at']} · {n.get('zone','')}</div>
                <div class="news-assets">{assets}</div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px;">
                <div class="sent-bar" style="flex:1;margin-right:10px;"><div class="sent-fill" style="width:{sent_w}%;"></div></div>
                <div class="news-read">{t('read_more')}</div>
            </div>
        </a>
        """, unsafe_allow_html=True)

    # ── TWITTER SIGNALS ────────────────────────────────────────────────────────
    twit_dot = '<span class="live-dot"></span>' if twitter_live else ""
    st.markdown(f'<div class="sec"><span class="sec-title">🐦 {twit_dot}{t("twitter_sec")}</span><div class="sec-line"></div></div>', unsafe_allow_html=True)

    if not twitter_live:
        st.markdown("""
        <div style="background:#0d1117;border:1px solid #1a2436;border-radius:4px;padding:12px 16px;font-size:11px;color:#8892a4;">
            <b style="color:#00d4ff;">Pour activer Twitter/X live :</b><br>
            1. Créer un compte développeur sur <a href="https://developer.twitter.com" target="_blank" style="color:#00d4ff;">developer.twitter.com</a><br>
            2. Créer une app → copier le <b>Bearer Token</b><br>
            3. Ajouter dans Streamlit Secrets : <code style="color:#ff6b35;">TWITTER_BEARER = "votre_token"</code><br>
            <br><i>Comptes surveillés : Reuters, AP, BBCWorld, FT, KyivIndependent, IranIntl_En, AJEnglish…</i>
        </div>
        """, unsafe_allow_html=True)

    for tw in tweets[:4]:
        imp_cls = f"tag-{tw['impact'].lower()}"
        imp_lbl = (impact_labels_en if lang=="EN" else impact_labels_fr).get(tw["impact"],"")
        assets  = " · ".join(tw.get("asset_impact",[]))
        sent_w  = int(abs(tw["sentiment"]) * 100)
        url     = tw.get("url","#")
        st.markdown(f"""
        <a href="{url}" target="_blank" class="news-card" style="border-left:3px solid #00d4ff;">
            <div style="display:flex;justify-content:space-between;align-items:start;gap:6px;">
                <div class="news-title" style="color:#00d4ff;">{tw['handle']}</div>
                <span class="tag {imp_cls}" style="white-space:nowrap;">{imp_lbl}</span>
            </div>
            <div class="news-sub" style="font-style:normal;color:#b0bcd0;">{tw['text']}</div>
            <div class="news-foot">
                <div class="news-meta">{tw['published_at']} · {tw.get('zone','')}</div>
                <div class="news-assets">{assets}</div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px;">
                <div class="sent-bar" style="flex:1;margin-right:10px;"><div class="sent-fill" style="width:{sent_w}%;"></div></div>
                <div class="news-read">Voir tweet →</div>
            </div>
        </a>
        """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  ROW 3 — RECOMMANDATIONS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f'<div class="sec"><span class="sec-title">💼 {t("invest_sec")} — {horizon}</span><div class="sec-line"></div></div>', unsafe_allow_html=True)

rec_cols = st.columns(len(recommendations))
for i, rec in enumerate(recommendations):
    action = rec["action"].lower()
    action_lbl = t(action)
    color = rec["color"]
    reason = rec["reason_en"] if lang=="EN" else rec["reason_fr"]
    tgt_color = "#00e676" if "+" in rec["target"] else "#ff1744"
    sl_color  = "#ff1744" if "-" in rec["stoploss"] else "#00e676"
    with rec_cols[i]:
        st.markdown(f"""
        <div class="inv-card {action}">
            <div class="inv-action" style="color:{color};">{rec['icon']} {action_lbl}</div>
            <div class="inv-asset">{rec['asset']}</div>
            <div class="inv-ticker">{rec['ticker']}</div>
            <div class="inv-grid">
                <div class="inv-box">
                    <div class="inv-box-label">{t('target')}</div>
                    <div class="inv-box-val" style="color:{tgt_color};">{rec['target']}</div>
                </div>
                <div class="inv-box">
                    <div class="inv-box-label">{t('stoploss')}</div>
                    <div class="inv-box-val" style="color:{sl_color};">{rec['stoploss']}</div>
                </div>
            </div>
            <div class="inv-detail">📊 <b>{t('alloc')}</b>: <span style="font-family:'IBM Plex Mono',monospace;color:{color};">{rec['alloc']}</span></div>
            <div class="inv-detail">🔗 <b>{t('correl')}</b>: <span style="font-family:'IBM Plex Mono',monospace;color:{color};">{rec['correl']}</span></div>
            <div class="inv-detail">⏱ <b>{t('horizon_lbl')}</b>: <span style="font-family:'IBM Plex Mono',monospace;color:#8892a4;">{rec['horizon']}</span></div>
            <div class="inv-reason">
                <div class="inv-reason-label">{t('reason')}</div>
                <div class="inv-reason-text">{reason}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  ROW 4 — RISK TABLE + PORTFOLIO SIM
# ═══════════════════════════════════════════════════════════════════════════════
col_rt, col_pf = st.columns([1.2, 1])

with col_rt:
    st.markdown(f'<div class="sec"><span class="sec-title">🌐 {t("risk_sec")}</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
    zk  = "zone_en" if lang=="EN" else "zone_fr"
    ik  = "impact_en" if lang=="EN" else "impact_fr"
    st.markdown(f"""
    <div class="rtable">
        <div class="rrow rhead">
            <div>{t('country')}</div><div>{t('score')}</div>
            <div>{t('impact')}</div><div>{t('trend')}</div>
        </div>
    """, unsafe_allow_html=True)
    for z in sorted(risk_zones, key=lambda x: x["risk"], reverse=True):
        sc = z["risk"]; pi = int(sc)
        tc = "#ff6b35" if z["trend_dir"]=="up" else ("#00e676" if z["trend_dir"]=="down" else "#8892a4")
        st.markdown(f"""
        <div class="rrow">
            <div style="font-size:12px;font-weight:500;">{z[zk]}</div>
            <div><span class="pill p{pi}">{sc}/10</span></div>
            <div style="font-size:10px;color:#8892a4;">{z[ik][:38]}…</div>
            <div style="color:{tc};font-size:16px;font-family:'IBM Plex Mono',monospace;">{z['trend']}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_pf:
    st.markdown(f'<div class="sec"><span class="sec-title">💼 {t("portfolio_sec")}</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
    capital = st.number_input(t("capital"), min_value=1000, max_value=10_000_000,
                               value=100_000, step=5000)

    st.markdown(f"""
    <div style="background:#0d1117;border:1px solid #1a2436;border-radius:4px;padding:14px;margin-top:6px;">
        <div style="font-size:9px;color:#8892a4;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;">{t('alloc_title')}</div>
    """, unsafe_allow_html=True)

    total_pot = 0
    alloc_data = []
    for rec in recommendations:
        pct_str = rec["alloc"].replace("%","").replace("-","")
        pct = float(pct_str)
        amt = capital * pct / 100
        target_pct = float(rec["target"].replace("%","").replace("+",""))
        pot = amt * target_pct / 100
        total_pot += pot
        icon = "▲" if rec["action"]=="BUY" else ("▼" if rec["action"]=="SELL" else "◆")
        sign = "+" if rec["action"]=="BUY" else "-"
        alloc_data.append(dict(name=rec["asset"][:22], ticker=rec["ticker"], pct=pct,
                               amt=amt, pot=pot, color=rec["color"], icon=icon, sign=sign))
        st.markdown(f"""
        <div class="alloc-row">
            <div>
                <div class="alloc-name" style="color:{rec['color']};">{icon} {rec['asset'][:22]}</div>
                <div class="alloc-ticker">{rec['ticker']}</div>
            </div>
            <div style="text-align:right;">
                <div class="alloc-pct" style="color:{rec['color']};">{sign}{pct:.0f}%</div>
                <div class="alloc-amt">{amt:,.0f} €</div>
                <div class="alloc-target">cible: +{pot:,.0f}€</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    cash_pct = max(0, 100 - sum(a["pct"] for a in alloc_data))
    st.markdown(f"""
        <div class="alloc-row">
            <div><div class="alloc-name" style="color:#8892a4;">◆ Cash / Liquidités</div></div>
            <div style="text-align:right;">
                <div class="alloc-pct" style="color:#8892a4;">{cash_pct:.0f}%</div>
                <div class="alloc-amt">{capital*cash_pct/100:,.0f} €</div>
            </div>
        </div>
        <div style="margin-top:12px;padding:10px;background:#07090f;border-radius:4px;">
            <div style="font-size:9px;color:#8892a4;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">{t('potential')}</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:22px;color:#00e676;font-weight:700;">+{total_pot:,.0f} €</div>
            <div style="font-size:9px;color:#3d4f6b;margin-top:4px;">{t('disclaimer')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Pie chart
    if alloc_data:
        labels = [a["name"] for a in alloc_data] + ["Cash"]
        values = [a["pct"]  for a in alloc_data] + [cash_pct]
        colors = [a["color"]for a in alloc_data] + ["#1a2436"]
        fig_pie = go.Figure(go.Pie(
            labels=labels, values=values,
            marker=dict(colors=colors, line=dict(color="#07090f",width=2)),
            textfont=dict(size=10, color="#e8eaf0", family="IBM Plex Mono"),
            hole=0.52,
            hovertemplate="<b>%{label}</b><br>%{value:.0f}%<extra></extra>",
        ))
        fig_pie.update_layout(
            height=200, margin=dict(l=10,r=10,t=10,b=10),
            paper_bgcolor="#07090f", showlegend=False,
            annotations=[dict(text=f"{capital//1000}k€", x=.5, y=.5,
                              font_size=13, font_family="IBM Plex Mono",
                              font_color="#e8eaf0", showarrow=False)],
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar":False})

# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""<hr>
<div style="text-align:center;padding:14px;color:#3d4f6b;font-size:9px;letter-spacing:1px;font-family:'IBM Plex Mono',monospace;">
GeoInvest Pro v3.0 &nbsp;|&nbsp; NewsAPI · Yahoo Finance · Twitter/X API · GDELT &nbsp;|&nbsp; {now_str}<br><br>
<span style="color:#243554;">⚠ À des fins éducatives uniquement. Pas un conseil financier.
Consultez un conseiller agréé avant tout investissement. Les performances passées ne garantissent pas les résultats futurs.</span>
</div>
""", unsafe_allow_html=True)
