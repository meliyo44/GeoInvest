# 🌍 GeoInvest Pro — Terminal v2.0
### Analyse Géopolitique & Recommandations Investissement en Temps Réel

---

## 🚀 Lancement rapide (< 2 minutes)

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer l'application
streamlit run geoinvest_pro.py
```

L'app s'ouvre automatiquement sur `http://localhost:8501`

---

## 🔑 Configuration des APIs (optionnel — données simulées par défaut)

Ouvrir `geoinvest_pro.py` et remplacer en haut du fichier :

```python
NEWS_API_KEY = "YOUR_NEWSAPI_KEY"          # → https://newsapi.org/register (gratuit)
ALPHA_VANTAGE_KEY = "YOUR_ALPHA_VANTAGE"  # → https://alphavantage.co/support/#api-key (gratuit)
```

### APIs gratuites supportées :
| API | Données | Limite gratuite |
|-----|---------|-----------------|
| **NewsAPI** | Actualités monde, sentiment | 100 req/jour |
| **Alpha Vantage** | Or, pétrole, ETFs, indices | 25 req/jour |
| **GDELT** | Événements géopolitiques | Illimité |
| **ACLED** | Incidents armés | Sur inscription |

---

## ☁️ Hébergement Cloud

### Option 1 — Streamlit Cloud (recommandé, gratuit)
1. Push sur GitHub
2. Connecter sur https://share.streamlit.io
3. Déployer en 1 clic

### Option 2 — Replit
1. Créer un projet Python sur https://replit.com
2. Uploader `geoinvest_pro.py` + `requirements.txt`
3. Configurer les secrets API dans l'onglet Secrets
4. Lancer

### Option 3 — Heroku / Railway
```bash
# Procfile (créer à la racine)
web: streamlit run geoinvest_pro.py --server.port=$PORT --server.address=0.0.0.0
```

---

## 📊 Fonctionnalités

### Section 1 — Score Risque & Sentiment
- 🎯 Score risque global pondéré (0-10) en temps réel
- 📈 Timeline sentiment 24h (VADER/NewsAPI)
- 💹 Ticker marchés (XAU, Brent, CAC40, VIX...)

### Section 2 — Synthèse Actualités
- 📡 Top 8 headlines géopolitiques avec impact
- 🗺️ Carte interactive des risques mondiaux (Plotly)
- 📋 Tableau risques par zone (score + tendance)

### Section 3 — Recommandations Investissement
- 💼 Cards actifs cliquables (Or, Pétrole, ETF Défense...)
- 🎯 Objectifs de prix + stop-loss automatiques
- 📊 Simulateur portfolio avec P&L estimé

### Sidebar — Filtres & Contrôles
- 🌍 Filtre régional (Monde/EU/Moyen-Orient/Asie)
- ⏱️ Horizon temporel (24h/72h/1 semaine)
- 🔄 Refresh manuel + auto toutes 30 minutes
- 📥 Export CSV des données de risque

---

## 🧮 Méthodologie Score Risque

```
Score Global = 50% × Sentiment News
             + 30% × Conflits Actifs (zones > 7/10)
             + 20% × Impact Économique

Seuils :
• < 5.0  → Risque FAIBLE  → Retour actifs risqués
• 5-7.0  → Risque MODÉRÉ → Hedge partiel XAU
• 7-8.5  → Risque ÉLEVÉ  → Achat or/pétrole/défense
• > 8.5  → CRITIQUE      → Alerte maximale, rotation défensive
```

---

## ⚠️ Avertissement
Cette application est à des fins éducatives et analytiques uniquement.
Elle ne constitue pas un conseil financier. Consultez un conseiller agréé avant tout investissement.

---

*GeoInvest Pro v2.0 | Built with ❤️ using Streamlit + Plotly*
