import streamlit as st
import requests
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="Serie A Predictor AI", page_icon="⚽", layout="wide")

st.title("⚽ Serie A AI Predictor")
st.caption("Applicazione privata per l'analisi predittiva delle partite di Serie A.")

st.sidebar.header("⚙️ Configurazione API")
api_key = st.sidebar.text_input("Inserisci API-Football Key:", type="password")

LEAGUE_ID = 135
SEASON = 2026

def get_api_headers(key):
    return {'x-rapidapi-host': "v3.football.api-sports.io", 'x-rapidapi-key': key}

def fetch_today_fixtures(key):
    url = f"https://v3.football.api-sports.io/fixtures?league={LEAGUE_ID}&season={SEASON}&next=10"
    response = requests.get(url, headers=get_api_headers(key))
    return response.json().get("response", []) if response.status_code == 200 else []

def fetch_lineups(key, fixture_id):
    url = f"https://v3.football.api-sports.io/fixtures/lineups?fixture={fixture_id}"
    response = requests.get(url, headers=get_api_headers(key))
    return response.json().get("response", []) if response.status_code == 200 else []

def analyze_match(home_players, away_players):
    home_att, home_def = 75.0, 75.0
    away_att, away_def = 70.0, 70.0
    
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
        "home_xg": round(home_xg, 2), "away_xg": round(away_xg, 2),
        "prob_1": round(home_win, 1), "prob_X": round(draw, 1), "prob_2": round(away_win, 1)
    }

if not api_key:
    st.warning("⚠️ Inserisci la tua API Key nella barra laterale a sinistra per iniziare.")
else:
    fixtures = fetch_today_fixtures(api_key)
    if not fixtures:
        st.info("Nessuna partita trovata o chiave API errata.")
    else:
        fixture_options = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']}": f for f in fixtures}
        selected_option = st.selectbox("Seleziona la partita da analizzare:", list(fixture_options.keys()))
        selected_fixture = fixture_options[selected_option]

        if st.button("🚀 Genera Pronostico IA", type="primary"):
            lineups = fetch_lineups(api_key, selected_fixture['fixture']['id'])
            res = analyze_match(lineups, lineups)
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Vittoria Casa (1)", f"{res['prob_1']}%")
            m2.metric("Pareggio (X)", f"{res['prob_X']}%")
            m3.metric("Vittoria Trasferta (2)", f"{res['prob_2']}%")
            st.write(f"**xG Stimati:** {selected_fixture['teams']['home']['name']} {res['home_xg']} - {res['away_xg']} {selected_fixture['teams']['away']['name']}")
