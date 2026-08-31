import streamlit as st
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="Serie A AI Predictor", page_icon="⚽", layout="wide")

st.title("⚽ Serie A AI Predictor")
st.caption("Modello predittivo avanzato per l'analisi delle partite di Serie A.")

# Valutazioni di forza delle squadre di Serie A (Attacco / Difesa)
TEAMS_DATA = {
    "Inter": {"att": 88, "def": 85},
    "Juventus": {"att": 82, "def": 86},
    "Milan": {"att": 84, "def": 80},
    "Atalanta": {"att": 86, "def": 78},
    "Napoli": {"att": 83, "def": 82},
    "Roma": {"att": 80, "def": 79},
    "Lazio": {"att": 79, "def": 78},
    "Fiorentina": {"att": 78, "def": 76},
    "Bologna": {"att": 76, "def": 77},
    "Torino": {"att": 72, "def": 76},
    "Genoa": {"att": 71, "def": 73},
    "Monza": {"att": 70, "def": 72},
    "Udinese": {"att": 71, "def": 72},
    "Verona": {"att": 69, "def": 70},
    "Lecce": {"att": 68, "def": 71},
    "Cagliari": {"att": 69, "def": 69},
    "Empoli": {"att": 67, "def": 70},
    "Parma": {"att": 70, "def": 68},
    "Como": {"att": 71, "def": 69},
    "Venezia": {"att": 67, "def": 67}
}

teams = sorted(list(TEAMS_DATA.keys()))

st.subheader("⚔️ Seleziona la Partita")

col1, col2 = st.columns(2)

with col1:
    home_team = st.selectbox("Squadra in Casa (1):", teams, index=teams.index("Roma") if "Roma" in teams else 0)

with col2:
    away_team = st.selectbox("Squadra in Trasferta (2):", teams, index=teams.index("Lecce") if "Lecce" in teams else 1)

if home_team == away_team:
    st.warning("⚠️ Seleziona due squadre diverse per calcolare il pronostico.")
else:
    if st.button("🚀 Calcola Pronostico IA", type="primary"):
        h_data = TEAMS_DATA[home_team]
        a_data = TEAMS_DATA[away_team]
        
        # Calcolo Expected Goals (xG) con fattore campo
        home_xg = 1.35 * (h_data["att"] / 75.0) * (75.0 / a_data["def"])
        away_xg = 1.05 * (a_data["att"] / 75.0) * (75.0 / h_data["def"])
        
        # Matrice di Poisson per probabilità 1X2
        max_goals = 6
        prob_matrix = np.zeros((max_goals, max_goals))
        for h in range(max_goals):
            for a in range(max_goals):
                prob_matrix[h, a] = poisson.pmf(h, home_xg) * poisson.pmf(a, away_xg)

        home_win = float(np.sum(np.tril(prob_matrix, -1))) * 100
        draw = float(np.sum(np.diag(prob_matrix))) * 100
        away_win = float(np.sum(np.triu(prob_matrix, 1))) * 100

        st.markdown("---")
        st.write(f"### 📊 Pronostico per **{home_team} - {away_team}**")
        
        m1, m2, m3 = st.columns(3)
        m1.metric(f"Vittoria {home_team} (1)", f"{round(home_win, 1)}%")
        m2.metric("Pareggio (X)", f"{round(draw, 1)}%")
        m3.metric(f"Vittoria {away_team} (2)", f"{round(away_win, 1)}%")
        
        st.info(f"⚽ **Expected Goals (xG) stimati:** {home_team} **{round(home_xg, 2)}** - **{round(away_xg, 2)}** {away_team}")
