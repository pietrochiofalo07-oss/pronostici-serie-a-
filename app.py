import streamlit as st
import requests
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="Serie A Predictor AI", page_icon="⚽", layout="wide")

st.title("⚽ Serie A AI Predictor")
st.caption("Applicazione per l'analisi predittiva delle partite di Serie A.")

st.sidebar.header("⚙️ Configurazione API")
api_key = st.sidebar.text_input("Inserisci API-Football Key:", type="password")

LEAGUE_ID = 135  # Serie A
SEASON = 2025    # Anno di inizio della stagione calcistica attuale

def fetch_fixtures(key):
    # Endpoint che recupera sia le ultime partite giocate sia le prossime
    url = f"https://v3.football.api-sports.io/fixtures?league={LEAGUE_ID}&season={SEASON}&last=10"
    headers = {'x-apisports-key': key.strip()}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        # Se la chiave è di RapidAPI invece che API-Sports direct
        if response.status_code != 200 or not data.get("response"):
            headers_rapid = {
                'x-rapidapi-host': "v3.football.api-sports.io",
                'x-rapidapi-key': key.strip()
            }
            response = requests.get(url, headers=headers_rapid, timeout=10)
            data = response.json()
            
        return data.get("response", [])
    except Exception:
        return []

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

if not api_key:
    st.warning("⚠️ Inserisci la tua API Key nella barra laterale a sinistra per iniziare.")
else:
    fixtures = fetch_fixtures(api_key)
    if not fixtures:
        st.error("❌ Impossibile recuperare i dati. Verifica che la chiave API sia corretta e attiva sul dashboard di API-Football.")
    else:
        st.success("✅ Connessione API riuscita! Seleziona una partita dal menu:")
        options = {f"{f['teams']['home']['name']} vs {f['teams']['away']['name']} ({f['fixture']['date'][:10]})": f for f in fixtures}
        selected_option = st.selectbox("Partite disponibili:", list(options.keys()))
        
        if st.button("🚀 Genera Pronostico IA", type="primary"):
            res = analyze_match(75.0, 75.0, 70.0, 70.0)
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Vittoria Casa (1)", f"{res['prob_1']}%")
            m2.metric("Pareggio (X)", f"{res['prob_X']}%")
            m3.metric("Vittoria Trasferta (2)", f"{res['prob_2']}%")
            st.write(f"**xG Stimati:** {res['home_xg']} - {res['away_xg']}")
