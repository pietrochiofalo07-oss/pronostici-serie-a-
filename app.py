import streamlit as st
import requests
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="Serie A Predictor AI", page_icon="⚽", layout="wide")

st.title("⚽ Serie A AI Predictor")
st.caption("Applicazione per l'analisi predittiva delle partite di Serie A.")

st.sidebar.header("⚙️ Configurazione API")
api_key = st.sidebar.text_input("Inserisci API-Football Key:", type="password")
season = st.sidebar.number_input("Anno Stagione (es. 2025 o 2024):", min_value=2020, max_value=2030, value=2025)

LEAGUE_ID = 135

def fetch_fixtures(key, season_year):
    # Prova prima le intestazioni API-Sports standard
    headers = {'x-apisports-key': key}
    url = f"https://v3.football.api-sports.io/fixtures?league={LEAGUE_ID}&season={season_year}&last=10"
    
    res = requests.get(url, headers=headers)
    data = res.json()
    
    # Se fallisce, prova l'intestazione RapidAPI
    if res.status_code != 200 or not data.get("response"):
        headers = {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': key}
        res = requests.get(url, headers=headers)
        data = res.json()
        
    return data.get("response", [])

def analyze_match(home_att, home_def, away_att, away_def):
    home_xg = 1.45 * (home_att / 50.0) * (50.0 / away_def)
    away_xg = 1.15 * (away_att / 50.0) * (50.0 / home_def)

    max_goals = 6
    prob_matrix = np.zeros((max_goals, max_goals))
    for h in range(max_goals):
        for a in range(max_goals):
            prob_matrix[h, a] = poisson.pmf(h, home_xg) * poisson.pmf(a, away_xg)

    home_win = float(np.sum(np.tril(prob_matrix, -1))) * 100
    draw = float(np.sum(np.diag(prob_matrix))) * 100
    away_win = float(np.sum(np.triu(prob_matrix, 1))) * 100

    return {
        "home_xg": round(home_xg, 2), 
        "away_xg": round(away_xg, 2),
        "prob_1": round(home_win, 1), 
        "prob_X": round(draw, 1), 
        "prob_2": round(away_win, 1)
    }

# Modalità manuale sempre attiva come backup
st.subheader("📊 Analisi Partita")

if api_key:
    fixtures = fetch_fixtures(api_key, season)
    if fixtures:
        options = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']} ({f['fixture']['date'][:10]})": f for f in fixtures}
        selected = st.selectbox("Seleziona una partita trovata via API:", list(options.keys()))
        
        if st.button("🚀 Analizza Partita API", type="primary"):
            res = analyze_match(75.0, 75.0, 70.0, 70.0)
            m1, m2, m3 = st.columns(3)
            m1.metric("Vittoria Casa (1)", f"{res['prob_1']}%")
            m2.metric("Pareggio (X)", f"{res['prob_X']}%")
            m3.metric("Vittoria Trasferta (2)", f"{res['prob_2']}%")
            st.write(f"**xG Stimati:** {res['home_xg']} - {res['away_xg']}")
    else:
        st.warning("⚠️ Impossibile recuperare partite automatiche (Chiave errata o quota API esaurita per oggi). Usa la modalità manuale qui sotto:")

st.markdown("---")
st.subheader("⚙️ Calcolatore Manuale Scontro")
col1, col2 = st.columns(2)
with col1:
    h_att = st.slider("Attacco Squadra Casa", 40, 99, 75)
    h_def = st.slider("Difesa Squadra Casa", 40, 99, 75)
with col2:
    a_att = st.slider("Attacco Squadra Trasferta", 40, 99, 70)
    a_def = st.slider("Difesa Squadra Trasferta", 40, 99, 70)

if st.button("🚀 Calcola Pronostico Manuale"):
    res = analyze_match(h_att, h_def, a_att, a_def)
    m1, m2, m3 = st.columns(3)
    m1.metric("Vittoria Casa (1)", f"{res['prob_1']}%")
    m2.metric("Pareggio (X)", f"{res['prob_X']}%")
    m3.metric("Vittoria Trasferta (2)", f"{res['prob_2']}%")
    st.write(f"**xG Stimati:** Casa {res['home_xg']} - {res['away_xg']} Trasferta")
