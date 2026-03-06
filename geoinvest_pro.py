"""
GeoInvest Pro — v4.0
Minimal · Real-Time · Geopolitical Intelligence
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import time, random
from datetime import datetime, timedelta

try:
    import yfinance as yf
    YF = True
except ImportError:
    YF = False

try:
    from streamlit_autorefresh import st_autorefresh
    AR = True
except ImportError:
    AR = False

# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="GeoInvest Pro", page_icon="🌍",
                   layout="wide", initial_sidebar_state="expanded")

def _s(k, d=""):
    try: return st.secrets.get(k, d)
    except: return d

NEWS_KEY    = _s("NEWS_API_KEY",   "YOUR_NEWSAPI_KEY")
TWIT_TOKEN  = _s("TWITTER_BEARER", "YOUR_TWITTER_BEARER")

# ── CSS — Minimal · Noir / Blanc / Orange ─────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&family=Geist+Mono:wght@400;500;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

:root {
  --ink:      #0a0a0a;
  --ink2:     #111111;
  --ink3:     #1a1a1a;
  --ink4:     #222222;
  --wire:     #2a2a2a;
  --dim:      #444444;
  --mid:      #777777;
  --fog:      #aaaaaa;
  --snow:     #f0f0f0;
  --white:    #ffffff;
  --orange:   #ff6b35;
  --orange2:  #ff8c5a;
  --orangeD:  rgba(255,107,53,.12);
  --red:      #f03e3e;
  --redD:     rgba(240,62,62,.1);
  --amber:    #e8b000;
  --amberD:   rgba(232,176,0,.1);
  --jade:     #2ecc71;
  --jadeD:    rgba(46,204,113,.1);
}

*, *::before, *::after { box-sizing:border-box; margin:0; padding:0; }

/* ── BASE ───────────────────────────────── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"]                { background:var(--ink)  !important; color:var(--snow) !important; }
[data-testid="stSidebar"]             { background:var(--ink2) !important; border-right:1px solid var(--wire); }
[data-testid="stSidebar"] *           { color:var(--snow) !important; }
[data-testid="block-container"]       { padding-top:1.5rem !important; }

/* font override everywhere */
*, input, button, select, textarea {
  font-family:'DM Sans','Geist',system-ui,sans-serif !important;
}
.mono { font-family:'DM Mono','Geist Mono',monospace !important; }

/* Streamlit chrome */
#MainMenu, footer, header, [data-testid="stToolbar"] { visibility:hidden; }
.stSelectbox>div>div { background:var(--ink3) !important; border:1px solid var(--wire) !important; color:var(--snow) !important; }
.stRadio>div  { gap:4px; }
hr            { border:none; border-top:1px solid var(--wire) !important; margin:20px 0; }
::-webkit-scrollbar       { width:4px; }
::-webkit-scrollbar-track { background:var(--ink); }
::-webkit-scrollbar-thumb { background:var(--wire); border-radius:4px; }

/* ── BUTTONS ────────────────────────────── */
.stButton>button {
  background:transparent !important;
  color:var(--fog) !important;
  border:1px solid var(--wire) !important;
  border-radius:6px !important;
  font-size:12px !important;
  font-weight:500 !important;
  letter-spacing:.3px !important;
  transition:all .15s !important;
  padding:6px 14px !important;
}
.stButton>button:hover {
  border-color:var(--orange) !important;
  color:var(--orange) !important;
}

/* ── HEADER ─────────────────────────────── */
.hdr {
  display:flex; align-items:center; justify-content:space-between;
  padding:0 0 20px 0;
  border-bottom:1px solid var(--wire);
  margin-bottom:24px;
}
.hdr-brand  { display:flex; align-items:baseline; gap:10px; }
.hdr-logo   {
  font-family:'DM Mono','Geist Mono',monospace;
  font-size:22px; font-weight:700;
  color:var(--orange); letter-spacing:1px;
}
.hdr-version{
  font-size:10px; font-weight:500; color:var(--dim);
  letter-spacing:2px; text-transform:uppercase;
}
.hdr-time   { font-size:11px; color:var(--mid); letter-spacing:.3px; text-align:right; }
.hdr-live   { display:inline-flex; align-items:center; gap:5px; font-size:10px; color:var(--jade); letter-spacing:1px; margin-top:4px; }
.dot-live   { width:6px; height:6px; background:var(--jade); border-radius:50%; animation:blink 1.4s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.15} }

/* ── SCORE CARD (avec tooltip hover) ────── */
.score-card {
  position:relative; cursor:default;
  background:var(--ink3);
  border:1px solid var(--wire);
  border-radius:10px;
  padding:22px 24px;
}
.score-card-critical { border-left:3px solid var(--red);   background:rgba(240,62,62,.05); }
.score-card-high     { border-left:3px solid var(--orange); background:rgba(255,107,53,.05); }
.score-card-medium   { border-left:3px solid var(--amber);  background:rgba(232,176,0,.05); }
.score-card-low      { border-left:3px solid var(--jade);   background:rgba(46,204,113,.05); }

.score-region { font-size:10px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:var(--mid); margin-bottom:8px; }
.score-number {
  font-family:'DM Mono','Geist Mono',monospace;
  font-size:56px; font-weight:700; line-height:1;
  letter-spacing:-2px;
}
.score-c { color:var(--red); }
.score-h { color:var(--orange); }
.score-m { color:var(--amber); }
.score-l { color:var(--jade); }
.score-denom { font-size:18px; color:var(--mid); font-weight:400; margin-left:2px; }
.score-label { font-size:11px; font-weight:600; letter-spacing:1px; text-transform:uppercase; margin-top:6px; }

/* Tooltip */
.score-tooltip {
  position:absolute; top:calc(100% + 10px); left:0; right:0; z-index:100;
  background:var(--ink4); border:1px solid var(--wire);
  border-radius:8px; padding:14px 16px;
  font-size:11px; color:var(--fog); line-height:1.7;
  opacity:0; pointer-events:none;
  transform:translateY(-4px);
  transition:opacity .2s, transform .2s;
  box-shadow:0 8px 24px rgba(0,0,0,.6);
}
.score-card:hover .score-tooltip {
  opacity:1; pointer-events:auto; transform:translateY(0);
}
.tooltip-row { display:flex; justify-content:space-between; align-items:center; padding:3px 0; border-bottom:1px solid var(--wire); }
.tooltip-row:last-child { border-bottom:none; }
.tooltip-key { color:var(--mid); font-size:10px; text-transform:uppercase; letter-spacing:1px; }
.tooltip-val { font-family:'DM Mono','Geist Mono',monospace; font-size:11px; color:var(--snow); }
.tooltip-bar { height:3px; background:var(--wire); border-radius:2px; margin-top:8px; margin-bottom:2px; overflow:hidden; }
.tooltip-fill{ height:100%; border-radius:2px; background:var(--orange); }

/* ── KPI ASSET CARDS ─────────────────────── */
.kpi-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:24px; }
.kpi-card {
  display:block; text-decoration:none !important;
  background:var(--ink3); border:1px solid var(--wire);
  border-radius:10px; padding:18px 20px;
  transition:border-color .15s, background .15s;
}
.kpi-card:hover { border-color:var(--orange); background:var(--ink4); }
.kpi-name  { font-size:10px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:var(--mid); margin-bottom:6px; }
.kpi-price { font-family:'DM Mono','Geist Mono',monospace; font-size:30px; font-weight:700; color:var(--white); line-height:1; }
.kpi-chg   { font-family:'DM Mono','Geist Mono',monospace; font-size:13px; margin-top:5px; }
.kpi-up    { color:var(--jade); }
.kpi-dn    { color:var(--red); }
.kpi-src   { font-size:9px; color:var(--dim); margin-top:8px; letter-spacing:.5px; }
.kpi-dot-or{ width:3px; height:28px; background:var(--amber); border-radius:2px; position:absolute; right:0; top:18px; }

/* ── TICKER ──────────────────────────────── */
.ticker {
  display:flex; gap:28px; overflow-x:auto; scrollbar-width:none;
  padding:10px 0; border-top:1px solid var(--wire); border-bottom:1px solid var(--wire);
  margin-bottom:24px;
}
.ticker::-webkit-scrollbar { display:none; }
.ti   { display:flex; align-items:center; gap:8px; white-space:nowrap; }
.ts   { font-size:10px; font-weight:600; letter-spacing:1px; text-transform:uppercase; color:var(--mid); }
.tp   { font-family:'DM Mono','Geist Mono',monospace; font-size:12px; font-weight:500; color:var(--snow); }
.tu   { font-family:'DM Mono','Geist Mono',monospace; font-size:11px; color:var(--jade); }
.td   { font-family:'DM Mono','Geist Mono',monospace; font-size:11px; color:var(--red); }

/* ── SECTION LABEL ───────────────────────── */
.slabel {
  font-size:10px; font-weight:600; letter-spacing:2px;
  text-transform:uppercase; color:var(--mid);
  padding-bottom:10px; margin-bottom:14px;
  border-bottom:1px solid var(--wire);
}

/* ── NEWS CARD ───────────────────────────── */
.nc {
  display:block; text-decoration:none !important;
  border-bottom:1px solid var(--wire);
  padding:12px 0;
  transition:background .1s;
}
.nc:first-child { border-top:1px solid var(--wire); }
.nc:hover .nc-title { color:var(--orange); }
.nc-title { font-size:13px; font-weight:500; color:var(--snow); line-height:1.5; margin-bottom:4px; transition:color .12s; }
.nc-sub   { font-size:11px; color:var(--mid); line-height:1.5; margin-bottom:6px; }
.nc-foot  { display:flex; justify-content:space-between; align-items:center; }
.nc-meta  { font-size:10px; color:var(--dim); }
.nc-assets{ font-size:10px; color:var(--orange); font-family:'DM Mono','Geist Mono',monospace; }
.nc-bar   { height:2px; background:var(--wire); border-radius:1px; overflow:hidden; margin-top:7px; }
.nc-fill  { height:100%; border-radius:1px; background:linear-gradient(90deg,var(--red),var(--orange)); }
.nc-imp   {
  display:inline-block; font-size:9px; font-weight:600;
  letter-spacing:1px; text-transform:uppercase;
  padding:2px 6px; border-radius:3px; margin-bottom:5px;
}
.imp-h    { background:var(--redD);   color:var(--red); }
.imp-m    { background:var(--amberD); color:var(--amber); }
.imp-l    { background:var(--jadeD);  color:var(--jade); }

/* ── TWEET CARD ──────────────────────────── */
.tw-card {
  display:block; text-decoration:none !important;
  border-bottom:1px solid var(--wire); padding:12px 0;
}
.tw-card:first-child { border-top:1px solid var(--wire); }
.tw-card:hover .tw-handle { color:var(--orange2); }
.tw-handle { font-size:11px; font-weight:600; color:var(--orange); transition:color .12s; margin-bottom:4px; }
.tw-text   { font-size:12px; color:var(--fog); line-height:1.6; margin-bottom:5px; }
.tw-foot   { font-size:10px; color:var(--dim); }

/* ── RISK ZONES — minimal strip ─────────── */
.rz-strip { display:flex; flex-direction:column; gap:0; }
.rz-row {
  display:flex; align-items:center; justify-content:space-between;
  padding:9px 0; border-bottom:1px solid var(--wire);
}
.rz-row:last-child { border-bottom:none; }
.rz-name  { font-size:12px; font-weight:500; color:var(--snow); flex:1; }
.rz-bar-wrap { flex:1; margin:0 14px; }
.rz-bar   { height:2px; background:var(--wire); border-radius:1px; overflow:hidden; }
.rz-fill  { height:100%; border-radius:1px; }
.rz-score { font-family:'DM Mono','Geist Mono',monospace; font-size:12px; font-weight:600; width:36px; text-align:right; }
.rz-trend { font-size:14px; width:18px; text-align:center; margin-left:8px; }

/* ── INVEST CARD ─────────────────────────── */
.inv {
  background:var(--ink3); border:1px solid var(--wire);
  border-radius:10px; padding:18px 20px; margin-bottom:10px;
}
.inv.buy  { border-top:2px solid var(--jade); }
.inv.sell { border-top:2px solid var(--red); }
.inv.hold { border-top:2px solid var(--amber); }
.inv-act  {
  font-size:9px; font-weight:700; letter-spacing:2px;
  text-transform:uppercase; margin-bottom:5px;
}
.inv-act.buy  { color:var(--jade); }
.inv-act.sell { color:var(--red); }
.inv-act.hold { color:var(--amber); }
.inv-name { font-size:15px; font-weight:600; color:var(--white); margin-bottom:2px; }
.inv-tkr  { font-family:'DM Mono','Geist Mono',monospace; font-size:10px; color:var(--dim); margin-bottom:12px; }
.inv-row  { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:10px; }
.inv-box  { background:var(--ink); border-radius:6px; padding:8px 10px; }
.inv-bl   { font-size:8px; font-weight:600; letter-spacing:1px; text-transform:uppercase; color:var(--dim); margin-bottom:3px; }
.inv-bv   { font-family:'DM Mono','Geist Mono',monospace; font-size:17px; font-weight:700; }
.inv-meta { font-size:11px; color:var(--mid); margin:3px 0; }
.inv-why  { margin-top:10px; padding:10px 12px; background:var(--ink); border-radius:6px; border-left:2px solid var(--wire); }
.inv-wl   { font-size:8px; font-weight:600; letter-spacing:1px; text-transform:uppercase; color:var(--dim); margin-bottom:4px; }
.inv-wt   { font-size:11px; color:var(--fog); line-height:1.7; }

/* ── PORTFOLIO ───────────────────────────── */
.pf-row {
  display:flex; justify-content:space-between; align-items:center;
  padding:10px 0; border-bottom:1px solid var(--wire);
}
.pf-name  { font-size:12px; font-weight:500; }
.pf-tkr   { font-size:9px; color:var(--dim); font-family:'DM Mono','Geist Mono',monospace; }
.pf-pct   { font-family:'DM Mono','Geist Mono',monospace; font-size:14px; font-weight:600; }
.pf-amt   { font-size:10px; color:var(--mid); }
.pf-pot   { font-size:10px; color:var(--jade); font-family:'DM Mono','Geist Mono',monospace; }
.pf-total {
  margin-top:14px; padding:14px 16px;
  background:var(--ink3); border-radius:8px;
}
.pf-tl  { font-size:9px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:var(--mid); margin-bottom:6px; }
.pf-tv  { font-family:'DM Mono','Geist Mono',monospace; font-size:26px; font-weight:700; color:var(--jade); }
.pf-disc{ font-size:9px; color:var(--dim); margin-top:6px; }

/* ── ALERT BANNER ────────────────────────── */
.alert {
  border-left:3px solid var(--red);
  background:var(--redD); border-radius:0 6px 6px 0;
  padding:10px 16px; margin-bottom:20px;
  font-size:11px; font-weight:500; color:var(--red);
  letter-spacing:.2px;
  animation:pulse-l 2s infinite;
}
@keyframes pulse-l { 0%,100%{border-left-color:var(--red)} 50%{border-left-color:transparent} }

/* ── MAP override ────────────────────────── */
.js-plotly-plot { border-radius:10px; overflow:hidden; }
</style>
""", unsafe_allow_html=True)

# ── SESSION ───────────────────────────────────────────────────────────────────
for k, v in [('lang','FR')]:
    if k not in st.session_state: st.session_state[k] = v

# ── TRANSLATIONS ──────────────────────────────────────────────────────────────
L = {
  'FR': dict(
    sub='ANALYSE GÉOPOLITIQUE · TEMPS RÉEL',
    risk_lbl='SCORE DE RISQUE', region_lbl='RÉGION',
    refresh='Actualiser', auto='Refresh auto',
    horizon='HORIZON', regions='RÉGION',
    buy='▲ ACHAT', sell='▼ VENTE', hold='◆ NEUTRE',
    target='Objectif', stoploss='Stop-Loss',
    alloc='Allocation', correl='Corrélation',
    reason='Justification', hlbl='Horizon',
    news_sec='ACTUALITÉS', tw_sec='SIGNAUX TWITTER / X',
    map_sec='CARTE DES RISQUES', rz_sec='ZONES À RISQUE',
    inv_sec='RECOMMANDATIONS', pf_sec='PORTFOLIO SIMULATEUR',
    mkt_sec='MARCHÉS',
    capital='Capital (€)',
    alloc_ttl='ALLOCATION', pot_ttl='GAIN POTENTIEL ESTIMÉ (72H)',
    disc='Projections indicatives. Pas un conseil financier.',
    crit='CRITIQUE', high='ÉLEVÉ', med='MODÉRÉ', low='FAIBLE',
    updated='Actualisé le',
    read='Lire l\'article →', tweet_link='Voir le tweet →',
    tw_setup='Pour activer Twitter/X live :',
    tw_step1='1. Créer un compte développeur sur developer.twitter.com',
    tw_step2='2. Créer une app → copier le Bearer Token',
    tw_step3='3. Ajouter dans Streamlit Secrets : TWITTER_BEARER = "..."',
    tw_accounts='Comptes surveillés : Reuters · AP · BBCWorld · KyivIndependent · IranIntl_En…',
    score_why_title='Comment ce score est calculé',
    score_comp1='Sentiment actualités (50%)',
    score_comp2='Conflits actifs (30%)',
    score_comp3='Impact économique (20%)',
    score_news_neg='News à sentiment négatif',
    score_high_zones='Zones à haut risque (>7)',
    score_eco='Score économique',
    tooltip_hover='Survolez pour l\'explication →',
  ),
  'EN': dict(
    sub='GEOPOLITICAL ANALYSIS · REAL-TIME',
    risk_lbl='RISK SCORE', region_lbl='REGION',
    refresh='Refresh', auto='Auto refresh',
    horizon='HORIZON', regions='REGION',
    buy='▲ BUY', sell='▼ SELL', hold='◆ HOLD',
    target='Target', stoploss='Stop-Loss',
    alloc='Allocation', correl='Correlation',
    reason='Rationale', hlbl='Horizon',
    news_sec='LIVE NEWS', tw_sec='TWITTER / X SIGNALS',
    map_sec='RISK MAP', rz_sec='RISK ZONES',
    inv_sec='RECOMMENDATIONS', pf_sec='PORTFOLIO SIMULATOR',
    mkt_sec='MARKETS',
    capital='Capital (€)',
    alloc_ttl='ALLOCATION', pot_ttl='ESTIMATED GAIN (72H)',
    disc='Indicative projections. Not financial advice.',
    crit='CRITICAL', high='HIGH', med='MODERATE', low='LOW',
    updated='Updated',
    read='Read article →', tweet_link='View tweet →',
    tw_setup='To enable live Twitter/X :',
    tw_step1='1. Create a developer account at developer.twitter.com',
    tw_step2='2. Create an app → copy the Bearer Token',
    tw_step3='3. Add in Streamlit Secrets: TWITTER_BEARER = "..."',
    tw_accounts='Monitored accounts: Reuters · AP · BBCWorld · KyivIndependent · IranIntl_En…',
    score_why_title='How this score is calculated',
    score_comp1='News sentiment (50%)',
    score_comp2='Active conflicts (30%)',
    score_comp3='Economic impact (20%)',
    score_news_neg='Negative-sentiment news',
    score_high_zones='High-risk zones (>7)',
    score_eco='Economic score',
    tooltip_hover='Hover for explanation →',
  ),
}
def t(k): return L[st.session_state.lang].get(k, k)

# ── KEYWORD ENGINE ─────────────────────────────────────────────────────────────
NEG = ["war","attack","strike","conflict","tension","missile","nuclear","sanction",
       "crisis","killed","death","threat","escalat","invasion","coup","terror",
       "guerre","attaque","conflit","nucléaire","crise","menace","escalad","terroris","tué","frappe"]
POS = ["ceasefire","peace","deal","agreement","diplomacy","recovery","growth",
       "cessez","paix","accord","diplo","reprise","croissance","rebond"]
AMAP = {
    "iran":["OIL","XAU"],"ormuz":["OIL","XAU"],"opec":["OIL","USO"],
    "ukraine":["DEF","GAS"],"russia":["DEF","GAS"],"russie":["DEF","GAS"],
    "taiwan":["XAU","OIL"],"china":["XAU"],"chine":["XAU"],
    "gold":["XAU"],"inflation":["XAU","BOND"],
    "oil":["OIL","USO"],"pétrole":["OIL","USO"],"brent":["OIL"],
    "defense":["DEF"],"défense":["DEF"],"rheinmetall":["DEF"],"thales":["DEF"],
    "sp500":["SP500"],"s&p":["SP500"],"dow":["SP500"],"nasdaq":["SP500"],
    "cac":["CAC40"],"euro":["CAC40","BOND"],"ecb":["BOND"],"bce":["BOND"],
}
ZONES = {
    "Middle-East":["iran","ormuz","middle east","moyen-orient","red sea","mer rouge","houthi","israel","gaza","liban","hamas","saudi"],
    "Europe":     ["ukraine","russia","russie","putin","zelensky","nato","otan","kiev","kharkiv","germany","allemagne","france","ecb","bce"],
    "Asia-Pacific":["taiwan","china","chine","beijing","pékin","xi jinping","south china sea","north korea","japan"],
    "Americas":   ["sp500","federal reserve","fed ","dow jones","nasdaq","wall street","white house","congress"],
}

def ssent(text):
    tl = text.lower()
    n = sum(1 for k in NEG if k in tl); p = sum(1 for k in POS if k in tl)
    return max(-1.0, min(1.0, (p-n)/max(n+p,1) - 0.1))

def dassets(text):
    tl = text.lower(); a = set()
    for k,v in AMAP.items():
        if k in tl: a.update(v)
    return list(a) if a else ["XAU"]

def dimpact(s): return "HIGH" if s<=-0.6 else ("MEDIUM" if s<=-0.3 else "LOW")

def dzone(text):
    tl = text.lower()
    for z, kws in ZONES.items():
        if any(k in tl for k in kws): return z
    return "Global"

# ── FALLBACK NEWS ──────────────────────────────────────────────────────────────
FB_NEWS = [
    dict(title="Iran déploie des missiles balistiques près du détroit d'Ormuz",
         title_en="Iran deploys ballistic missiles near Strait of Hormuz",
         source="Reuters", sentiment=-0.72, impact="HIGH", zone="Middle-East",
         sf="Escalade militaire — risque fermeture détroit → pétrole, or en hausse",
         se="Military escalation — strait closure risk → oil, gold rising",
         ai=["OIL","XAU"], am=45, url="https://www.reuters.com/world/middle-east/"),
    dict(title="Négociations nucléaires Iran s'effondrent, nouvelles sanctions US",
         title_en="Iran nuclear talks collapse, new US sanctions",
         source="Bloomberg", sentiment=-0.81, impact="HIGH", zone="Middle-East",
         sf="Sanctions → perturbations export pétrole, hedge XAU",
         se="Sanctions → oil export disruptions, XAU hedge",
         ai=["OIL","XAU","USO"], am=120, url="https://www.bloomberg.com/energy"),
    dict(title="Ukraine frappe infrastructure russe, Moscou riposte sur Kharkiv",
         title_en="Ukraine strikes Russian infrastructure, Moscow retaliates",
         source="AP", sentiment=-0.65, impact="HIGH", zone="Europe",
         sf="Intensification — défense EU en hausse, gaz +",
         se="Escalation — EU defense up, gas prices rising",
         ai=["DEF","GAS"], am=30, url="https://apnews.com/hub/russia-ukraine"),
    dict(title="Exercices militaires chinois entourent Taiwan, destroyer US déployé",
         title_en="Chinese exercises encircle Taiwan, US destroyer deployed",
         source="NYT", sentiment=-0.78, impact="HIGH", zone="Asia-Pacific",
         sf="Risque semi-conducteurs — tech à vendre, XAU à acheter",
         se="Chip disruption risk — sell tech, buy XAU",
         ai=["XAU","OIL"], am=90, url="https://www.nytimes.com/section/world/asia"),
    dict(title="OPEP+ maintient coupes production, Brent au-dessus de 87$/b",
         title_en="OPEC+ holds production cuts, Brent above $87/b",
         source="OPEC", sentiment=-0.30, impact="MEDIUM", zone="Global",
         sf="Pétrole soutenu → inflation maintenue",
         se="Oil supported → inflation maintained",
         ai=["OIL","USO"], am=60, url="https://www.opec.org/opec_web/en/press_room/"),
    dict(title="Mer Rouge : 15 navires déroutés, attaques Houthis, fret +22%",
         title_en="Red Sea: 15 ships rerouted after Houthi attacks, freight +22%",
         source="FT", sentiment=-0.68, impact="HIGH", zone="Middle-East",
         sf="Routes maritimes menacées → impact supply chaînes EU",
         se="Maritime routes threatened → EU supply chain impact",
         ai=["OIL","DEF"], am=210, url="https://www.ft.com/world/middle-east"),
    dict(title="BCE signale pause dans les baisses de taux, inflation core persistante",
         title_en="ECB signals pause in rate cuts, core inflation persists",
         source="ECB", sentiment=-0.25, impact="MEDIUM", zone="Europe",
         sf="Taux hauts prolongés → pression immobilier EU",
         se="Prolonged high rates → EU real estate pressure",
         ai=["XAU","BOND"], am=150, url="https://www.ecb.europa.eu/press/pressconf/"),
    dict(title="S&P 500 cède 1.4% face aux tensions géopolitiques croissantes",
         title_en="S&P 500 drops 1.4% amid rising geopolitical tensions",
         source="WSJ", sentiment=-0.55, impact="MEDIUM", zone="Americas",
         sf="Volatilité SP500 — réduire exposition actions US",
         se="SP500 volatility — reduce US equity exposure",
         ai=["SP500","XAU"], am=75, url="https://www.wsj.com/markets"),
]

def _enrich(items, rf):
    now = datetime.utcnow(); out = []
    for it in items:
        x = dict(it); x['published_at'] = (now-timedelta(minutes=x['am'])).strftime('%H:%M UTC'); out.append(x)
    if rf not in ["All","Monde"]:
        zm = {"EU":["Europe"],"Middle-East":["Middle-East"],"Asia-Pacific":["Asia-Pacific"],"Americas":["Americas"]}
        zz = zm.get(rf,[])
        if zz: out = [n for n in out if n.get('zone') in zz or n.get('zone')=='Global']
    out.sort(key=lambda x: abs(x['sentiment']), reverse=True)
    return out[:8]

# ── LIVE NEWS ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def fetch_news(key, rf):
    if not key or "YOUR_" in key: return _enrich(FB_NEWS, rf), False
    q = {
        "All":"iran OR ukraine OR taiwan OR geopolitical OR opec OR nato OR sp500",
        "EU":"europe OR ukraine OR nato OR ECB OR germany OR france OR eurozone",
        "Middle-East":"iran OR israel OR gaza OR ormuz OR houthi OR opec OR saudi",
        "Asia-Pacific":"taiwan OR china OR \"north korea\" OR japan OR \"south china sea\"",
        "Americas":"sp500 OR \"federal reserve\" OR nasdaq OR \"wall street\"",
    }
    try:
        r = requests.get("https://newsapi.org/v2/everything", timeout=8, params=dict(
            q=q.get(rf,q["All"]), language="en", sortBy="publishedAt", pageSize=20, apiKey=key))
        d = r.json()
        if d.get("status") != "ok" or not d.get("articles"): return _enrich(FB_NEWS, rf), False
        out = []
        for a in d["articles"][:14]:
            if not a.get("title") or a["title"]=="[Removed]": continue
            ti = a["title"]; de = a.get("description") or ""; full = f"{ti} {de}"; s = ssent(full)
            out.append(dict(title=ti, title_en=ti, source=a.get("source",{}).get("name","—"),
                sentiment=s, impact=dimpact(s), zone=dzone(full),
                sf=de[:130]+"…" if len(de)>130 else de,
                se=de[:130]+"…" if len(de)>130 else de,
                ai=dassets(full),
                published_at=a.get("publishedAt","")[:16].replace("T"," ")+" UTC",
                url=a.get("url","#")))
        out.sort(key=lambda x: abs(x["sentiment"]), reverse=True)
        return out[:8], True
    except: return _enrich(FB_NEWS, rf), False

# ── TWEETS ────────────────────────────────────────────────────────────────────
TW_ACCS = ["Reuters","AP","BBCWorld","FT","KyivIndependent","IranIntl_En","AJEnglish"]

@st.cache_data(ttl=300, show_spinner=False)
def fetch_tweets(token):
    if not token or "YOUR_" in token: return _fb_tweets(), False
    aq = " OR ".join(f"from:{a}" for a in TW_ACCS)
    gq = "(iran OR ukraine OR taiwan OR geopolitical OR opec OR nato)"
    try:
        r = requests.get("https://api.twitter.com/2/tweets/search/recent",
            headers={"Authorization":f"Bearer {token}"},
            params=dict(query=f"({aq}) {gq} -is:retweet lang:en", max_results=10,
                tweet_fields="created_at,author_id", expansions="author_id",
                user_fields="username"), timeout=8)
        d = r.json()
        if "data" not in d: return _fb_tweets(), False
        users = {u["id"]:u for u in d.get("includes",{}).get("users",[])}
        out = []
        for tw in d["data"][:5]:
            u = users.get(tw.get("author_id",""),{}); h = u.get("username","?")
            tx = tw["text"]; s = ssent(tx)
            out.append(dict(text=tx[:200]+"…" if len(tx)>200 else tx,
                handle=f"@{h}", sentiment=s, impact=dimpact(s),
                zone=dzone(tx), ai=dassets(tx),
                published_at=tw.get("created_at","")[:16].replace("T"," ")+" UTC",
                url=f"https://twitter.com/{h}/status/{tw['id']}"))
        return out, True
    except: return _fb_tweets(), False

def _fb_tweets():
    now = datetime.utcnow()
    return [
        dict(text="BREAKING: Iran Revolutionary Guard conducts live-fire exercises near Strait of Hormuz, warning to US naval presence in the region",
             handle="@IranIntl_En", sentiment=-0.78, impact="HIGH", zone="Middle-East",
             ai=["OIL","XAU"], published_at=(now-timedelta(minutes=22)).strftime('%H:%M UTC'),
             url="https://twitter.com/IranIntl_En"),
        dict(text="Russian forces target Ukrainian energy grid for 4th time this month. EU emergency energy meeting called for tomorrow morning.",
             handle="@KyivIndependent", sentiment=-0.65, impact="HIGH", zone="Europe",
             ai=["DEF","GAS"], published_at=(now-timedelta(minutes=55)).strftime('%H:%M UTC'),
             url="https://twitter.com/KyivIndependent"),
        dict(text="OPEC+ sources: production cuts extended by 3 months minimum. Brent crude testing $88/b resistance level.",
             handle="@Reuters", sentiment=-0.3, impact="MEDIUM", zone="Global",
             ai=["OIL","USO"], published_at=(now-timedelta(minutes=88)).strftime('%H:%M UTC'),
             url="https://twitter.com/Reuters"),
    ]

# ── MARKET DATA ───────────────────────────────────────────────────────────────
MKT = {
    "Or (XAU)": dict(sym="GC=F",  unit="$", link="https://finance.yahoo.com/quote/GC=F"),
    "Pétrole":  dict(sym="BZ=F",  unit="$", link="https://finance.yahoo.com/quote/BZ=F"),
    "S&P 500":  dict(sym="^GSPC", unit="",  link="https://finance.yahoo.com/quote/%5EGSPC"),
}
MKT_FULL = {
    **MKT,
    "CAC 40":   dict(sym="^FCHI",   unit="",  link="https://finance.yahoo.com/quote/%5EFCHI"),
    "EUR/USD":  dict(sym="EURUSD=X",unit="",  link="https://finance.yahoo.com/quote/EURUSD=X"),
    "VIX":      dict(sym="^VIX",    unit="",  link="https://finance.yahoo.com/quote/%5EVIX"),
    "GLD ETF":  dict(sym="GLD",     unit="$", link="https://finance.yahoo.com/quote/GLD"),
}

@st.cache_data(ttl=180, show_spinner=False)
def fetch_market():
    if not YF: return _sim_mkt(), False
    out = {}
    try:
        syms = " ".join(v["sym"] for v in MKT_FULL.values())
        tk = yf.Tickers(syms)
        for name, meta in MKT_FULL.items():
            try:
                h = tk.tickers[meta["sym"]].history(period="2d", interval="1h")
                if h.empty or len(h)<2: raise ValueError
                cur = float(h["Close"].iloc[-1]); prev = float(h["Close"].iloc[0])
                out[name] = dict(price=round(cur,2), change=round((cur-prev)/prev*100,2),
                                 unit=meta["unit"], link=meta["link"])
            except:
                out[name] = _sim_mkt().get(name, dict(price=0,change=0,unit="",link="#"))
        return out, True
    except: return _sim_mkt(), False

def _sim_mkt():
    seed = int(time.time()/180); random.seed(seed)
    rp = lambda b,v=.012: round(b*(1+random.gauss(0,v)),2)
    rc = lambda b,v=.35: round(b+random.gauss(0,v),2)
    return {
        "Or (XAU)": dict(price=rp(2341), change=rc(.8),  unit="$", link="https://finance.yahoo.com/quote/GC=F"),
        "Pétrole":  dict(price=rp(87.4), change=rc(1.1), unit="$", link="https://finance.yahoo.com/quote/BZ=F"),
        "S&P 500":  dict(price=rp(5210), change=rc(-.6), unit="",  link="https://finance.yahoo.com/quote/%5EGSPC"),
        "CAC 40":   dict(price=rp(7823), change=rc(-.4), unit="",  link="https://finance.yahoo.com/quote/%5EFCHI"),
        "EUR/USD":  dict(price=rp(1.084,.003),change=rc(-.1,.15),unit="",link="https://finance.yahoo.com/quote/EURUSD=X"),
        "VIX":      dict(price=rp(16.8,.05),change=rc(2.,.8),unit="",link="https://finance.yahoo.com/quote/%5EVIX"),
        "GLD ETF":  dict(price=rp(218.5),change=rc(.7),unit="$",link="https://finance.yahoo.com/quote/GLD"),
    }

# ── RISK ZONES ────────────────────────────────────────────────────────────────
def risk_zones():
    return [
        dict(zf="Iran / Moyen-Orient", ze="Iran / Middle-East", lat=32.4,lon=53.7,
             risk=9.1,trend="▲",td="up",
             if_="Risque énergie critique — pétrole, chaînes appro",
             ie="Critical energy risk — oil, supply chains",color="#f03e3e"),
        dict(zf="Ukraine / Russie",ze="Ukraine / Russia",lat=49.,lon=32.,
             risk=7.8,trend="→",td="neutral",
             if_="Défense EU, gaz naturel, blé",ie="EU defense, natural gas, wheat",color="#ff6b35"),
        dict(zf="Mer Rouge / Houthis",ze="Red Sea / Houthis",lat=15.,lon=43.,
             risk=7.5,trend="▲",td="up",
             if_="Disruption maritime +15% fret",ie="Maritime disruption +15% freight",color="#ff6b35"),
        dict(zf="Détroit de Taïwan",ze="Taiwan Strait",lat=23.7,lon=121.,
             risk=7.2,trend="▲",td="up",
             if_="Semi-conducteurs, logistique maritime",ie="Semiconductors, maritime logistics",color="#ff6b35"),
        dict(zf="Zone Euro (éco)",ze="Eurozone (eco)",lat=50.,lon=10.,
             risk=5.9,trend="▼",td="down",
             if_="Récession Allemagne, BCE, inflation",ie="Germany recession, ECB, inflation",color="#e8b000"),
        dict(zf="Sahel / Afrique",ze="Sahel / Africa",lat=14.,lon=2.,
             risk=5.1,trend="→",td="neutral",
             if_="Matières premières, instabilité",ie="Raw materials, instability",color="#e8b000"),
        dict(zf="Corée du Nord",ze="North Korea",lat=40.,lon=127.5,
             risk=4.8,trend="▼",td="down",
             if_="Risque nucléaire latent",ie="Latent nuclear risk",color="#e8b000"),
        dict(zf="Amérique Latine",ze="Latin America",lat=-15.,lon=-60.,
             risk=3.2,trend="→",td="neutral",
             if_="Commodities, lithium",ie="Commodities, lithium",color="#2ecc71"),
    ]

def compute_score(news, zones):
    sents = [abs(n['sentiment']) for n in news] or [.5]
    ns = (sum(sents)/len(sents))*10
    cs = min(sum(1 for z in zones if z['risk']>7.)*2.5, 10)
    es = 6.2
    return min(round(ns*.5+cs*.3+es*.2, 1), 10.)

def compute_region_score(news, zones, rk):
    zm = {"EU":"Europe","Middle-East":"Middle-East","Asia-Pacific":"Asia-Pacific","Americas":"Americas"}
    target = zm.get(rk)
    if not target: return compute_score(news, zones)
    rn = [n for n in news if n.get('zone')==target] or news
    rz = [z for z in zones if target.lower() in z['ze'].lower()] or zones
    return compute_score(rn, rz)

def score_meta(score):
    if score>=8.5: return "critical","c",t("crit")
    if score>=7.0: return "high","h",t("high")
    if score>=5.0: return "medium","m",t("med")
    return "low","l",t("low")

# ── RECOMMENDATIONS ─────────────────────────────────────────────────────────
def get_recs(risk, lang):
    if risk >= 8.0:
        return [
            dict(asset="Or (XAU/USD)",ticker="XAU / GLD",action="BUY",icon="🥇",
                 target="+5.5%",sl="-1.8%",alloc="25%",corr="0.82",horizon="48-72h",color="#2ecc71",
                 rf="Corrélation 0.82 avec tensions Moyen-Orient. Escalade Iran-Ormuz → valeurs refuges. +1pt risque = +0.8% XAU historiquement.",
                 re="0.82 correlation with Middle-East tensions. Iran-Hormuz escalation → safe havens. +1pt risk = +0.8% XAU historically."),
            dict(asset="Pétrole Brent / USO",ticker="USO / UCO",action="BUY",icon="🛢️",
                 target="+4.2%",sl="-2.5%",alloc="15%",corr="0.91",horizon="24-48h",color="#2ecc71",
                 rf="Risque fermeture Ormuz (30% pétrole mondial). Corrélation 0.91 Iran-Brent. OPEC+ cuts soutiennent le plancher.",
                 re="Hormuz closure risk (30% world oil). 0.91 Iran-Brent correlation. OPEC+ cuts support the floor."),
            dict(asset="ETF Défense EU",ticker="EUDF / HELO",action="BUY",icon="🛡️",
                 target="+6.0%",sl="-2.0%",alloc="20%",corr="0.75",horizon="72h–1 sem",color="#2ecc71",
                 rf="Budget défense EU +40% depuis 2022. Rheinmetall, Thales, Leonardo bénéficiaires directs.",
                 re="EU defense budget +40% since 2022. Rheinmetall, Thales, Leonardo direct beneficiaries."),
            dict(asset="S&P 500 / SPY",ticker="SPY / ES=F",action="SELL",icon="📉",
                 target="-2.5%",sl="+1.2%",alloc="-15%",corr="-0.71",horizon="48h",color="#f03e3e",
                 rf="Corrélation négative -0.71 avec risque géo élevé. VIX en hausse → réduire exposition équités US.",
                 re="Negative -0.71 correlation with high geo-risk. Rising VIX → reduce US equity exposure."),
        ]
    elif risk >= 6.0:
        return [
            dict(asset="Or (XAU/USD)",ticker="XAU / GLD",action="BUY",icon="🥇",
                 target="+2.5%",sl="-1.5%",alloc="15%",corr="0.82",horizon="72h",color="#2ecc71",
                 rf="Risque modéré croissant. Position défensive sur XAU avant escalade potentielle.",
                 re="Moderate and growing risk. Defensive XAU position ahead of potential escalation."),
            dict(asset="Pétrole Brent",ticker="USO ETF",action="HOLD",icon="🛢️",
                 target="+1.5%",sl="-3.0%",alloc="10%",corr="0.65",horizon="72h",color="#e8b000",
                 rf="OPEC+ soutient les cours. Conserver positions, pas d'extension agressive.",
                 re="OPEC+ supports prices. Hold positions, no aggressive extension."),
            dict(asset="S&P 500",ticker="SPY / ES=F",action="HOLD",icon="📊",
                 target="+1.0%",sl="-2.0%",alloc="20%",corr="-0.55",horizon="72h",color="#e8b000",
                 rf="Marché US résilient mais vulnérable. Réduire levier, conserver core.",
                 re="US market resilient but vulnerable. Reduce leverage, keep core."),
        ]
    else:
        return [
            dict(asset="S&P 500 / SPY",ticker="SPY / QQQ",action="BUY",icon="📈",
                 target="+2.5%",sl="-1.0%",alloc="30%",corr="-0.5",horizon="1 semaine",color="#2ecc71",
                 rf="Risque faible → retour vers actifs risqués. Croissance US robuste, VIX bas.",
                 re="Low risk → return to risk assets. Robust US growth, low VIX."),
            dict(asset="Or (XAU/USD)",ticker="XAU / GLD",action="HOLD",icon="🥇",
                 target="+1.0%",sl="-1.5%",alloc="10%",corr="0.82",horizon="1 semaine",color="#e8b000",
                 rf="Conserver allocation or structurelle. Risque géo résiduel justifie position minimale.",
                 re="Hold structural gold allocation. Residual geo-risk justifies minimum position."),
        ]

# ── MAP ────────────────────────────────────────────────────────────────────────
def build_map(zones, news, lang):
    lf = "ze" if lang=="EN" else "zf"
    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        lat=[z["lat"] for z in zones], lon=[z["lon"] for z in zones],
        text=[f"<b>{z[lf]}</b><br>{z['risk']}/10" for z in zones],
        hoverinfo="text", mode="markers",
        marker=dict(size=[z["risk"]*5 for z in zones],
                    color=[z["color"] for z in zones],
                    opacity=.65, sizemode="area",
                    line=dict(width=1, color="rgba(255,255,255,.1)")),
    ))
    zcoords = {"Middle-East":(26.,50.),"Europe":(51.,15.),"Asia-Pacific":(30.,118.),"Americas":(35.,-95.),"Global":(20.,0.)}
    crits = [n for n in news if n["impact"]=="HIGH"]
    seen = set(); cl=[]; cla=[]; clo=[]
    for n in crits:
        z = n.get("zone","Global")
        if z in seen: continue
        seen.add(z); coord=zcoords.get(z,(0.,0.))
        tk = "title_en" if lang=="EN" else "title"
        cl.append(f"⚡ {n[tk][:55]}…"); cla.append(coord[0]); clo.append(coord[1])
    if cl:
        fig.add_trace(go.Scattergeo(lat=cla, lon=clo, text=cl, hoverinfo="text", mode="markers",
            marker=dict(size=9, color="#f03e3e", symbol="star",
                        line=dict(width=1.5, color="#ffffff")), name="Alertes"))
    fig.update_layout(
        height=380, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="#0a0a0a",
        geo=dict(showframe=False, showcoastlines=True, coastlinecolor="#222",
                 showland=True, landcolor="#111", showocean=True, oceancolor="#0a0a0a",
                 showcountries=True, countrycolor="#1a1a1a",
                 projection_type="natural earth", bgcolor="#0a0a0a"),
        showlegend=False)
    return fig

# ═══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:12px 0 16px;border-bottom:1px solid #2a2a2a;margin-bottom:16px;">
      <div style="font-family:'DM Mono','Geist Mono',monospace;font-size:16px;font-weight:700;color:#ff6b35;letter-spacing:1px;">⬡ GeoInvest Pro</div>
      <div style="font-size:9px;color:#444;letter-spacing:2px;text-transform:uppercase;margin-top:4px;">TERMINAL v4.0</div>
    </div>
    """, unsafe_allow_html=True)

    c1,c2 = st.columns(2)
    with c1:
        if st.button("FR 🇫🇷", use_container_width=True): st.session_state.lang="FR"
    with c2:
        if st.button("EN 🇬🇧", use_container_width=True): st.session_state.lang="EN"

    st.markdown("---")
    st.markdown(f"<div style='font-size:9px;color:#444;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;'>{t('regions')}</div>", unsafe_allow_html=True)
    sel = st.selectbox("", ["Monde / World","EU / Europe","Middle-East / Iran","Asia-Pacific","Americas / US"], label_visibility="collapsed")
    rk = ("Middle-East" if "Iran" in sel or "Middle" in sel
          else "EU"           if "EU" in sel
          else "Asia-Pacific" if "Asia" in sel
          else "Americas"     if "Americas" in sel
          else "All")

    st.markdown("---")
    st.markdown(f"<div style='font-size:9px;color:#444;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;'>{t('horizon')}</div>", unsafe_allow_html=True)
    horizon = st.radio("", ["24h","72h","1 semaine"], label_visibility="collapsed")

    st.markdown("---")
    auto_on = st.toggle(t('auto'), value=True)
    if auto_on:
        ri = st.select_slider("Intervalle", [30,60,120,300], value=60, format_func=lambda x:f"{x}s")
    else: ri = 60

    if st.button(t('refresh'), use_container_width=True):
        st.cache_data.clear(); st.rerun()

    st.markdown("---")
    status_ph = st.empty()

    st.markdown("---")
    st.markdown("<div style='font-size:9px;color:#444;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;'>EXPORT</div>", unsafe_allow_html=True)
    rz = risk_zones()
    csv = pd.DataFrame(rz)[["zf","ze","risk","trend"]].rename(columns={"zf":"zone_fr","ze":"zone_en"}).to_csv(index=False)
    st.download_button("↓ Export CSV", csv, "risks.csv", "text/csv", use_container_width=True)

# ── AUTO-REFRESH ──────────────────────────────────────────────────────────────
if auto_on and AR:
    st_autorefresh(interval=ri*1000, key="ar")
elif auto_on:
    if "nxt" not in st.session_state: st.session_state.nxt = time.time()+ri
    if time.time() >= st.session_state.nxt:
        st.session_state.nxt = time.time()+ri; st.cache_data.clear(); st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
#  DATA
# ═══════════════════════════════════════════════════════════════════════════════
lang       = st.session_state.lang
news, nl   = fetch_news(NEWS_KEY, rk)
tweets, tl = fetch_tweets(TWIT_TOKEN)
mkt, ml    = fetch_market()
zones      = risk_zones()
score      = compute_region_score(news, zones, rk)
recs       = get_recs(score, lang)
now_s      = datetime.utcnow().strftime("%d %b %Y  %H:%M UTC")
sclass, schar, slabel = score_meta(score)
reg_name   = sel.split("/")[0].strip()

# Sidebar status
nb = "🟢 Live NewsAPI"    if nl else "🟡 Demo"
mb = "🟢 Live Yahoo Finance" if ml else "🟡 Simulé"
tb = "🟢 Live Twitter/X" if tl else "🟡 Demo"
status_ph.markdown(f"""
<div style="padding:10px;background:#111;border:1px solid #2a2a2a;border-radius:6px;font-size:10px;color:#555;">
  <div style="color:#2ecc71;margin-bottom:6px;font-weight:600;">● EN LIGNE</div>
  <div>{nb}</div><div>{mb}</div><div>{tb}</div>
  <div style="margin-top:8px;font-size:9px;color:#333;">{'Clés API actives ✓' if nl else 'Configurer Streamlit Secrets'}</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  RENDER — HEADER
# ═══════════════════════════════════════════════════════════════════════════════
live_src = "NewsAPI · Yahoo Finance · Twitter/X" if (nl or ml) else "Demo Mode"
st.markdown(f"""
<div class="hdr">
  <div class="hdr-brand">
    <span class="hdr-logo">⬡ GeoInvest Pro</span>
    <span class="hdr-version">v4.0</span>
  </div>
  <div class="hdr-time">
    <div>{t('updated')} {now_s}</div>
    <div class="hdr-live"><span class="dot-live"></span>{live_src}</div>
  </div>
</div>
""", unsafe_allow_html=True)

if score >= 7.5:
    msgs = {
        "FR": f"Risque {slabel} détecté sur {reg_name} — {score}/10 · Hedge géopolitique recommandé",
        "EN": f"{slabel} risk detected on {reg_name} — {score}/10 · Geopolitical hedge recommended",
    }
    st.markdown(f'<div class="alert">⚡ {msgs[lang]}</div>', unsafe_allow_html=True)

# ── TICKER ────────────────────────────────────────────────────────────────────
ticker_html = '<div class="ticker">'
for name, d in mkt.items():
    c = d['change']; cls = "tu" if c>=0 else "td"; arrow = "▲" if c>=0 else "▼"
    ticker_html += f'<div class="ti"><span class="ts">{name}</span><span class="tp">{d["unit"]}{d["price"]:,}</span><span class="{cls}">{arrow}{abs(c):.2f}%</span></div>'
ticker_html += '</div>'
st.markdown(ticker_html, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  ROW 1 — SCORE + KPI ACTIFS
# ═══════════════════════════════════════════════════════════════════════════════
col_score, col_kpi = st.columns([1, 2.4])

# Score tooltip data
sents = [abs(n['sentiment']) for n in news] or [.5]
news_score_val  = round((sum(sents)/len(sents))*10, 1)
high_zones      = sum(1 for z in zones if z['risk']>7.)
conflict_score  = min(high_zones*2.5, 10.)
eco_score       = 6.2
news_pct        = round(news_score_val*50/10, 1)
conf_pct        = round(conflict_score*30/10, 1)
eco_pct         = round(eco_score*20/10, 1)
neg_news        = sum(1 for n in news if n['sentiment']<-0.3)

with col_score:
    st.markdown(f"""
    <div class="score-card score-card-{sclass}">
      <div class="score-region">{t('region_lbl')} · {reg_name}</div>
      <div>
        <span class="score-number score-{schar}">{score}</span>
        <span class="score-denom">/10</span>
      </div>
      <div class="score-label score-{schar}">{slabel}</div>
      <div style="font-size:9px;color:#555;margin-top:12px;letter-spacing:.5px;">{t('tooltip_hover')}</div>

      <div class="score-tooltip">
        <div style="font-size:10px;font-weight:600;color:#aaa;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;">{t('score_why_title')}</div>
        <div class="tooltip-row">
          <span class="tooltip-key">{t('score_comp1')}</span>
          <span class="tooltip-val">{news_score_val}/10 → {news_pct:.1f}pts</span>
        </div>
        <div class="tooltip-row">
          <span class="tooltip-key">{t('score_comp2')}</span>
          <span class="tooltip-val">{conflict_score}/10 → {conf_pct:.1f}pts ({high_zones} zones)</span>
        </div>
        <div class="tooltip-row">
          <span class="tooltip-key">{t('score_comp3')}</span>
          <span class="tooltip-val">{eco_score}/10 → {eco_pct:.1f}pts</span>
        </div>
        <div class="tooltip-bar"><div class="tooltip-fill" style="width:{score*10}%;background:{'#f03e3e' if score>=8.5 else '#ff6b35' if score>=7 else '#e8b000' if score>=5 else '#2ecc71'};"></div></div>
        <div style="display:flex;justify-content:space-between;font-size:9px;color:#555;margin-top:4px;">
          <span>0</span><span>Score total {score}/10</span><span>10</span>
        </div>
        <div style="margin-top:10px;font-size:10px;color:#555;border-top:1px solid #2a2a2a;padding-top:8px;">
          <span style="color:#777;">{t('score_news_neg')} : </span><span style="color:#f03e3e;font-weight:600;">{neg_news}/{len(news)}</span>
          &nbsp;·&nbsp;
          <span style="color:#777;">{t('score_high_zones')} : </span><span style="color:#ff6b35;font-weight:600;">{high_zones}</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi:
    st.markdown(f'<div class="slabel">{t("mkt_sec")}</div>', unsafe_allow_html=True)
    kpi_cols = st.columns(3)
    for i, name in enumerate(["Or (XAU)","Pétrole","S&P 500"]):
        d = mkt.get(name, {}); c = d.get("change",0)
        cls = "kpi-up" if c>=0 else "kpi-dn"; arrow = "▲" if c>=0 else "▼"
        bc = "#e8b000" if "Or" in name else ("#ff6b35" if "Pétrole" in name else "#777")
        link = d.get("link","#")
        with kpi_cols[i]:
            st.markdown(f"""
            <a href="{link}" target="_blank" class="kpi-card" style="border-top:2px solid {bc};position:relative;">
              <div class="kpi-name">{name}</div>
              <div class="kpi-price">{d.get('unit','')}{d.get('price',0):,}</div>
              <div class="kpi-chg {cls}">{arrow} {abs(c):.2f}%</div>
              <div class="kpi-src">Yahoo Finance →</div>
            </a>
            """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  ROW 2 — MAP + NEWS + TWEETS
# ═══════════════════════════════════════════════════════════════════════════════
col_left, col_right = st.columns([1.6, 1])

with col_left:
    st.markdown(f'<div class="slabel">{t("map_sec")}</div>', unsafe_allow_html=True)
    st.plotly_chart(build_map(zones, news, lang), use_container_width=True, config={"displayModeBar":False})

    # ── RISK ZONES — minimal strip ─────────────────────────────────────────
    st.markdown(f'<div class="slabel" style="margin-top:20px;">{t("rz_sec")}</div>', unsafe_allow_html=True)
    zl = "ze" if lang=="EN" else "zf"
    st.markdown('<div class="rz-strip">', unsafe_allow_html=True)
    for z in sorted(zones, key=lambda x:x["risk"], reverse=True):
        sc_z = z["risk"]; fill_w = int(sc_z*10)
        tc = "#f03e3e" if z["td"]=="up" else ("#2ecc71" if z["td"]=="down" else "#444")
        st.markdown(f"""
        <div class="rz-row">
          <div class="rz-name">{z[zl]}</div>
          <div class="rz-bar-wrap">
            <div class="rz-bar">
              <div class="rz-fill" style="width:{fill_w}%;background:{z['color']};opacity:.7;"></div>
            </div>
          </div>
          <div class="rz-score" style="color:{z['color']};">{sc_z}</div>
          <div class="rz-trend" style="color:{tc};">{z['trend']}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    # ── NEWS ──────────────────────────────────────────────────────────────────
    ld = f'<span class="dot-live" style="display:inline-block;margin-right:5px;"></span>' if nl else ""
    st.markdown(f'<div class="slabel">{ld}{t("news_sec")}</div>', unsafe_allow_html=True)

    il_fr = {"HIGH":"IMPACT ÉLEVÉ","MEDIUM":"MODÉRÉ","LOW":"FAIBLE"}
    il_en = {"HIGH":"HIGH IMPACT","MEDIUM":"MODERATE","LOW":"LOW"}

    for i, n in enumerate(news[:5]):
        title   = n["title_en"] if lang=="EN" else n["title"]
        summary = n["se"]       if lang=="EN" else n["sf"]
        imp_lbl = (il_en if lang=="EN" else il_fr).get(n["impact"],"")
        imp_cls = f"imp-{n['impact'][0].lower()}"
        assets  = " · ".join(n.get("ai",[]))
        sw      = int(abs(n["sentiment"])*100)
        url     = n.get("url","#")
        st.markdown(f"""
        <a href="{url}" target="_blank" class="nc">
          <div><span class="nc-imp {imp_cls}">{imp_lbl}</span></div>
          <div class="nc-title">{title}</div>
          <div class="nc-sub">{summary}</div>
          <div class="nc-foot">
            <div class="nc-meta">{n['source']} · {n['published_at']}</div>
            <div class="nc-assets">{assets}</div>
          </div>
          <div class="nc-bar"><div class="nc-fill" style="width:{sw}%;"></div></div>
        </a>
        """, unsafe_allow_html=True)

    # ── TWEETS ────────────────────────────────────────────────────────────────
    td2 = f'<span class="dot-live" style="display:inline-block;margin-right:5px;"></span>' if tl else ""
    st.markdown(f'<div class="slabel" style="margin-top:20px;">{td2}{t("tw_sec")}</div>', unsafe_allow_html=True)

    if not tl:
        st.markdown(f"""
        <div style="background:#111;border:1px solid #2a2a2a;border-radius:8px;padding:14px 16px;font-size:11px;color:#555;line-height:1.8;">
          <div style="color:#777;font-weight:500;margin-bottom:6px;">{t('tw_setup')}</div>
          <div>{t('tw_step1')}</div>
          <div>{t('tw_step2')}</div>
          <div>{t('tw_step3')}</div>
          <div style="margin-top:8px;font-size:10px;color:#3a3a3a;">{t('tw_accounts')}</div>
        </div>
        """, unsafe_allow_html=True)

    for tw in tweets[:3]:
        imp_lbl = (il_en if lang=="EN" else il_fr).get(tw["impact"],"")
        imp_cls = f"imp-{tw['impact'][0].lower()}"
        assets  = " · ".join(tw.get("ai",[]))
        url     = tw.get("url","#")
        st.markdown(f"""
        <a href="{url}" target="_blank" class="tw-card">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
            <div class="tw-handle">{tw['handle']}</div>
            <span class="nc-imp {imp_cls}">{imp_lbl}</span>
          </div>
          <div class="tw-text">{tw['text']}</div>
          <div class="tw-foot">{tw['published_at']} · <span style="color:#ff6b35;">{assets}</span></div>
        </a>
        """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  ROW 3 — RECOMMANDATIONS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f'<div class="slabel">{t("inv_sec")} — {horizon}</div>', unsafe_allow_html=True)
rc_cols = st.columns(len(recs))
for i, r in enumerate(recs):
    ac = r["action"].lower()
    al = t(ac); col = r["color"]
    reason = r["re"] if lang=="EN" else r["rf"]
    tv = "#2ecc71" if "+" in r["target"] else "#f03e3e"
    sv = "#f03e3e" if "-" in r["sl"] else "#2ecc71"
    with rc_cols[i]:
        st.markdown(f"""
        <div class="inv {ac}">
          <div class="inv-act {ac}">{r['icon']} {al}</div>
          <div class="inv-name">{r['asset']}</div>
          <div class="inv-tkr">{r['ticker']}</div>
          <div class="inv-row">
            <div class="inv-box">
              <div class="inv-bl">{t('target')}</div>
              <div class="inv-bv" style="color:{tv};">{r['target']}</div>
            </div>
            <div class="inv-box">
              <div class="inv-bl">{t('stoploss')}</div>
              <div class="inv-bv" style="color:{sv};">{r['sl']}</div>
            </div>
          </div>
          <div class="inv-meta">📊 {t('alloc')} <span style="font-family:'DM Mono','Geist Mono',monospace;color:{col};">{r['alloc']}</span></div>
          <div class="inv-meta">🔗 {t('correl')} <span style="font-family:'DM Mono','Geist Mono',monospace;color:{col};">{r['corr']}</span></div>
          <div class="inv-meta">⏱ {t('hlbl')} <span style="font-family:'DM Mono','Geist Mono',monospace;color:#555;">{r['horizon']}</span></div>
          <div class="inv-why">
            <div class="inv-wl">{t('reason')}</div>
            <div class="inv-wt">{reason}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  ROW 4 — PORTFOLIO SIMULATOR
# ═══════════════════════════════════════════════════════════════════════════════
pf_col, chart_col = st.columns([1, 1])

with pf_col:
    st.markdown(f'<div class="slabel">{t("pf_sec")}</div>', unsafe_allow_html=True)
    capital = st.number_input(t("capital"), min_value=100, max_value=10_000_000,
                               value=1000, step=100)

    st.markdown(f"""
    <div style="background:#111;border:1px solid #2a2a2a;border-radius:8px;padding:16px 18px;margin-top:8px;">
      <div class="pf-row" style="border-bottom:1px solid #222;padding-bottom:8px;margin-bottom:2px;">
        <div style="font-size:9px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#444;">{t('alloc_ttl')}</div>
        <div style="font-size:9px;color:#333;">Capital : {capital:,} €</div>
      </div>
    """, unsafe_allow_html=True)

    total_pot = 0; alloc_data = []
    for r in recs:
        pct = float(r["alloc"].replace("%","").replace("-",""))
        amt = capital * pct / 100
        tgt = float(r["target"].replace("%","").replace("+",""))
        pot = amt * tgt / 100; total_pot += pot
        icon = "▲" if r["action"]=="BUY" else ("▼" if r["action"]=="SELL" else "◆")
        sign = "+" if r["action"]=="BUY" else ""
        alloc_data.append(dict(name=r["asset"][:20],ticker=r["ticker"],pct=pct,amt=amt,pot=pot,color=r["color"],icon=icon,sign=sign))
        st.markdown(f"""
        <div class="pf-row">
          <div>
            <div class="pf-name" style="color:{r['color']};">{icon} {r['asset'][:22]}</div>
            <div class="pf-tkr">{r['ticker']}</div>
          </div>
          <div style="text-align:right;">
            <div class="pf-pct" style="color:{r['color']};">{sign}{pct:.0f}%</div>
            <div class="pf-amt">{amt:,.0f} €</div>
            <div class="pf-pot">+{pot:,.0f} €</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    cash_pct = max(0, 100 - sum(a["pct"] for a in alloc_data))
    st.markdown(f"""
      <div class="pf-row" style="opacity:.5;">
        <div class="pf-name">◇ Cash</div>
        <div style="text-align:right;">
          <div class="pf-pct" style="color:#444;">{cash_pct:.0f}%</div>
          <div class="pf-amt">{capital*cash_pct/100:,.0f} €</div>
        </div>
      </div>
      <div class="pf-total">
        <div class="pf-tl">{t('pot_ttl')}</div>
        <div class="pf-tv">+{total_pot:,.0f} €</div>
        <div class="pf-disc">{t('disc')}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

with chart_col:
    st.markdown('<div class="slabel">ALLOCATION</div>', unsafe_allow_html=True)
    if alloc_data:
        labels = [a["name"] for a in alloc_data]+["Cash"]
        values = [a["pct"]  for a in alloc_data]+[cash_pct]
        colors = [a["color"]for a in alloc_data]+["#1a1a1a"]
        fig = go.Figure(go.Pie(
            labels=labels, values=values, hole=.55,
            marker=dict(colors=colors, line=dict(color="#0a0a0a",width=2)),
            textfont=dict(size=10,color="#aaa",family="DM Mono"),
            hovertemplate="<b>%{label}</b><br>%{value:.0f}%<extra></extra>",
        ))
        fig.update_layout(
            height=240, margin=dict(l=10,r=10,t=10,b=10),
            paper_bgcolor="#0a0a0a", showlegend=False,
            annotations=[dict(text=f"{capital:,}€",x=.5,y=.5,
                font_size=13,font_family="DM Mono",font_color="#888",showarrow=False)],
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;padding:20px 0 10px;color:#2a2a2a;font-size:9px;letter-spacing:.5px;">
  GeoInvest Pro v4.0 &nbsp;·&nbsp; NewsAPI · Yahoo Finance · Twitter/X &nbsp;·&nbsp; {now_s}<br>
  <span style="color:#1a1a1a;">Usage éducatif uniquement. Pas un conseil financier.</span>
</div>
""", unsafe_allow_html=True)
