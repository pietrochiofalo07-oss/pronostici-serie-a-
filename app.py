import streamlit as st
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="Europe AI Predictor", page_icon="⚽", layout="wide")

st.title("⚽ Europe Football AI Predictor")
st.caption("Analisi predittiva per Serie A, Premier League e Champions League.")

# Database Campionati Europei
DATA = {
    "Serie A": {
        "Inter": {"att": 88, "def": 85, "strikers": [("Lautaro Martínez", 0.45), ("M. Thuram", 0.35)]},
        "Juventus": {"att": 82, "def": 86, "strikers": [("D. Vlahović", 0.45), ("K. Yıldız", 0.25)]},
        "Roma": {"att": 80, "def": 79, "strikers": [("A. Dovbyk", 0.42), ("P. Dybala", 0.38)]},
        "Lecce": {"att": 68, "def": 71, "strikers": [("N. Krstović", 0.35), ("L. Banda", 0.18)]}
    },
    "Champions League / Top Europe": {
        "Real Madrid": {"att": 92, "def": 88, "strikers": [("K. Mbappé", 0.50), ("Vini Jr.", 0.40)]},
        "Manchester City": {"att": 93, "def": 87, "strikers": [("E. Haaland", 0.55), ("Phil Foden", 0.30)]},
        "Bayern Monaco": {"att": 90, "def": 84, "strikers": [("Harry Kane", 0.52), ("Jamal Musiala", 0.30)]},
        "Barcelona": {"att": 89, "def": 82, "strikers": [("R. Lewandowski", 0.48), ("Lamine Yamal", 0.28)]},
        "PSG": {"att": 87, "def": 83, "strikers": [("O. Dembélé", 0.32), ("B. Barcola", 0.28)]}
    }
}

league = st.selectbox("🏆 Seleziona Competizione:", list(DATA.keys()))
teams = sorted(list(DATA[league].keys()))

col1, col2 = st.columns(2)
with col1:
    home_team = st.selectbox("Squadra Casa (1):", teams, index=0)
with col2:
    away_team = st.selectbox("Squadra Trasferta (2):", teams, index=1 if len(teams) > 1 else 0)

if home_team != away_team:
    if st.button("🚀 Calcola Pronostico Europeo", type="primary"):
        h_data = DATA[league][home_team]
        a_data = DATA[league][away_team]
        
        home_xg = 1.35 * (h_data["att"] / 75.0) * (75.0 / a_data["def"])
        away_xg = 1.05 * (a_data["att"] / 75.0) * (75.0 / h_data["def"])
        
        max_goals = 6
        prob_matrix = np.zeros((max_goals, max_goals))
        exact_scores = []
        
        for h in range(max_goals):
            for a in range(max_goals):
                p = poisson.pmf(h, home_xg) * poisson.pmf(a, away_xg)
                prob_matrix[h, a] = p
                exact_scores.append((f"{h} - {a}", p * 100))

        home_win = float(np.sum(np.tril(prob_matrix, -1))) * 100
        draw = float(np.sum(np.diag(prob_matrix))) * 100
        away_win = float(np.sum(np.triu(prob_matrix, 1))) * 100

        st.markdown("---")
        st.write(f"### 📊 Pronostico **{home_team} vs {away_team}**")
        
        m1, m2, m3 = st.columns(3)
        m1.metric(f"1 ({home_team})", f"{round(home_win, 1)}%")
        m2.metric("X (Pareggio)", f"{round(draw, 1)}%")
        m3.metric(f"2 ({away_team})", f"{round(away_win, 1)}%")
        
        st.info(f"⚽ **xG Stimati:** {home_team} **{round(home_xg, 2)}** - **{round(away_xg, 2)}** {away_team}")
        
        # Top 5 Risultati Esatti
        st.write("### 🎯 Risultati Esatti Più Probabili")
        exact_scores.sort(key=lambda x: x[1], reverse=True)
        cols = st.columns(5)
        for idx, (score, prob) in enumerate(exact_scores[:5]):
            cols[idx].metric(f"Risultato {score}", f"{round(prob, 1)}%")
