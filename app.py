import streamlit as st
import numpy as np
from scipy.stats import poisson

st.set_page_config(page_title="Europe Football AI Predictor", page_icon="⚽", layout="wide")

st.title("⚽ Europe Football AI Predictor (Stagione 2026-2027)")
st.caption("Modello predittivo avanzato: 1X2, Risultati Esatti e Marcatori per i campionati europei.")

FOOTBALL_DATABASE = {
    "Serie A": {
        "Inter": {"att": 88, "def": 85, "strikers": ["Lautaro Martínez", "Marcus Thuram", "Hakan Çalhanoğlu"]},
        "Juventus": {"att": 83, "def": 86, "strikers": ["Dušan Vlahović", "Kenan Yıldız", "Teun Koopmeiners"]},
        "Milan": {"att": 84, "def": 80, "strikers": ["Álvaro Morata", "Rafael Leão", "Christian Pulisic"]},
        "Atalanta": {"att": 86, "def": 78, "strikers": ["Mateo Retegui", "Ademola Lookman", "Charles De Ketelaere"]},
        "Napoli": {"att": 83, "def": 82, "strikers": ["Romelu Lukaku", "Giacomo Raspadori", "Scott McTominay"]},
        "Roma": {"att": 80, "def": 79, "strikers": ["Santiago Castro", "Paulo Dybala", "Matías Soulé"]},
        "Bologna": {"att": 77, "def": 77, "strikers": ["Artem Dovbyk", "Thijs Dallinga", "Riccardo Orsolini"]},
        "Lazio": {"att": 79, "def": 78, "strikers": ["Taty Castellanos", "Mattia Zaccagni", "Boulaye Dia"]},
        "Fiorentina": {"att": 78, "def": 76, "strikers": ["Moise Kean", "Albert Guðmundsson", "Andrea Colpani"]},
        "Torino": {"att": 72, "def": 76, "strikers": ["Duván Zapata", "Antonio Sanabria", "Nikola Vlašić"]},
        "Lecce": {"att": 68, "def": 71, "strikers": ["Nikola Krstović", "Lameck Banda", "Santiago Pierotti"]},
        "Genoa": {"att": 71, "def": 73, "strikers": ["Andrea Pinamonti", "Vitinha", "Junior Messias"]},
        "Monza": {"att": 70, "def": 72, "strikers": ["Dany Mota", "Milan Đurić", "Gianluca Caprari"]},
        "Udinese": {"att": 71, "def": 72, "strikers": ["Lorenzo Lucca", "Florian Thauvin", "Brenner"]},
        "Verona": {"att": 69, "def": 70, "strikers": ["Casper Tengstedt", "Daniel Mosquera", "Darko Lazović"]},
        "Cagliari": {"att": 69, "def": 69, "strikers": ["Roberto Piccoli", "Zito Luvumbo", "Gianluca Lapadula"]},
        "Empoli": {"att": 67, "def": 70, "strikers": ["Lorenzo Colombo", "Sebastiano Esposito", "Emmanuel Gyasi"]},
        "Parma": {"att": 70, "def": 68, "strikers": ["Ange-Yoan Bonny", "Dennis Man", "Matteo Cancellieri"]},
        "Como": {"att": 71, "def": 69, "strikers": ["Patrick Cutrone", "Andrea Belotti", "Nico Paz"]},
        "Venezia": {"att": 67, "def": 67, "strikers": ["Joel Pohjanpalo", "Gaetano Oristanio", "Christian Gytkjær"]}
    },
    "Premier League": {
        "Manchester City": {"att": 93, "def": 87, "strikers": ["Erling Haaland", "Phil Foden", "Kevin De Bruyne"]},
        "Arsenal": {"att": 89, "def": 88, "strikers": ["Kai Havertz", "Bukayo Saka", "Gabriel Martinelli"]},
        "Liverpool": {"att": 90, "def": 84, "strikers": ["Mohamed Salah", "Darwin Núñez", "Luis Díaz"]},
        "Aston Villa": {"att": 83, "def": 79, "strikers": ["Ollie Watkins", "Leon Bailey", "Jhon Durán"]},
        "Tottenham": {"att": 84, "def": 78, "strikers": ["Son Heung-min", "Dominic Solanke", "Sandro Tonali"]},
        "Chelsea": {"att": 83, "def": 77, "strikers": ["Nicolas Jackson", "Cole Palmer", "Morgan Rogers"]},
        "Manchester United": {"att": 80, "def": 78, "strikers": ["Rasmus Højlund", "Marcus Rashford", "Bruno Fernandes"]},
        "Newcastle": {"att": 82, "def": 79, "strikers": ["Alexander Isak", "Harvey Barnes", "Jacob Murphy"]},
        "West Ham": {"att": 78, "def": 76, "strikers": ["Michail Antonio", "Jarrod Bowen", "Lucas Paquetá"]},
        "Brighton": {"att": 80, "def": 75, "strikers": ["Danny Welbeck", "Kaoru Mitoma", "Evan Ferguson"]}
    },
    "LaLiga": {
        "Real Madrid": {"att": 94, "def": 88, "strikers": ["Kylian Mbappé", "Vinícius Jr.", "Jude Bellingham"]},
        "Barcelona": {"att": 90, "def": 82, "strikers": ["Robert Lewandowski", "Lamine Yamal", "Raphinha"]},
        "Atlético Madrid": {"att": 85, "def": 86, "strikers": ["Julian Alvarez", "Antoine Griezmann", "Alexander Sørloth"]},
        "Athletic Bilbao": {"att": 80, "def": 82, "strikers": ["Iñaki Williams", "Nico Williams", "Oihan Sancet"]},
        "Real Sociedad": {"att": 78, "def": 80, "strikers": ["Mikel Oyarzabal", "Takefusa Kubo", "Umar Sadiq"]},
        "Girona": {"att": 81, "def": 76, "strikers": ["Bojan Miovski", "Viktor Tsygankov", "Yaser Asprilla"]},
        "Villarreal": {"att": 81, "def": 75, "strikers": ["Ayoze Pérez", "Thierno Barry", "Álex Baena"]},
        "Real Betis": {"att": 77, "def": 78, "strikers": ["Vitor Roque", "Giovani Lo Celso", "Ezequiel Ávila"]}
    },
    "Bundesliga": {
        "Bayern Monaco": {"att": 91, "def": 84, "strikers": ["Harry Kane", "Jamal Musiala", "Michael Olise"]},
        "Bayer Leverkusen": {"att": 89, "def": 83, "strikers": ["Victor Boniface", "Florian Wirtz", "Patrik Schick"]},
        "RB Lipsia": {"att": 84, "def": 81, "strikers": ["Benjamin Šeško", "Loïs Openda", "Xavi Simons"]},
        "Borussia Dortmund": {"att": 85, "def": 79, "strikers": ["Serhou Guirassy", "Donyell Malen", "Julian Brandt"]},
        "Eintracht Francoforte": {"att": 82, "def": 76, "strikers": ["Omar Marmoush", "Hugo Ekitike", "Mario Götze"]}
    },
    "Ligue 1": {
        "PSG": {"att": 90, "def": 84, "strikers": ["Khvicha Kvaratskhelia", "Bradley Barcola", "Ousmane Dembélé"]},
        "Monaco": {"att": 82, "def": 78, "strikers": ["Folarin Balogun", "Breel Embolo", "Takumi Minamino"]},
        "Lilla": {"att": 80, "def": 79, "strikers": ["Jonathan David", "Edon Zhegrova", "Rémy Cabella"]},
        "Marsiglia": {"att": 83, "def": 77, "strikers": ["Elye Wahi", "Mason Greenwood", "Amine Harit"]},
        "Lione": {"att": 79, "def": 75, "strikers": ["Alexandre Lacazette", "Georges Mikautadze", "Said Benrahma"]}
    },
    "Champions League / Coppe Europee": {
        "Real Madrid": {"att": 94, "def": 88, "strikers": ["Kylian Mbappé", "Vinícius Jr.", "Jude Bellingham"]},
        "Manchester City": {"att": 93, "def": 87, "strikers": ["Erling Haaland", "Phil Foden", "Kevin De Bruyne"]},
        "Bayern Monaco": {"att": 91, "def": 84, "strikers": ["Harry Kane", "Jamal Musiala", "Michael Olise"]},
        "PSG": {"att": 90, "def": 84, "strikers": ["Khvicha Kvaratskhelia", "Bradley Barcola", "Ousmane Dembélé"]},
        "Inter": {"att": 88, "def": 85, "strikers": ["Lautaro Martínez", "Marcus Thuram", "Hakan Çalhanoğlu"]},
        "Barcelona": {"att": 90, "def": 82, "strikers": ["Robert Lewandowski", "Lamine Yamal", "Raphinha"]},
        "Arsenal": {"att": 89, "def": 88, "strikers": ["Kai Havertz", "Bukayo Saka", "Gabriel Martinelli"]},
        "Liverpool": {"att": 90, "def": 84, "strikers": ["Mohamed Salah", "Darwin Núñez", "Luis Díaz"]},
        "Bayer Leverkusen": {"att": 89, "def": 83, "strikers": ["Victor Boniface", "Florian Wirtz", "Patrik Schick"]},
        "Juventus": {"att": 83, "def": 86, "strikers": ["Dušan Vlahović", "Kenan Yıldız", "Teun Koopmeiners"]},
        "Benfica": {"att": 80, "def": 79, "strikers": ["Vangelis Pavlidis", "Angel Di María", "Orkun Kökçü"]},
        "Sporting CP": {"att": 83, "def": 80, "strikers": ["Viktor Gyökeres", "Francisco Trincão", "Pedro Gonçalves"]}
    }
}

league = st.selectbox("🌍 Seleziona Competizione / Campionato:", list(FOOTBALL_DATABASE.keys()))
teams_list = sorted(list(FOOTBALL_DATABASE[league].keys()))

st.subheader("⚔️ Seleziona le Squadre")
col1, col2 = st.columns(2)

with col1:
    home_team = st.selectbox("Squadra Casa (1):", teams_list, index=0)

with col2:
    away_team = st.selectbox("Squadra Trasferta (2):", teams_list, index=1 if len(teams_list) > 1 else 0)

if home_team == away_team:
    st.warning("⚠️ Seleziona due squadre diverse per calcolare il pronostico.")
else:
    if st.button("🚀 Calcola Pronostico IA Completo", type="primary"):
        h_data = FOOTBALL_DATABASE[league][home_team]
        a_data = FOOTBALL_DATABASE[league][away_team]
        
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
        st.write(f"### 📊 Esito 1X2 & xG per **{home_team} vs {away_team}**")
        m1, m2, m3 = st.columns(3)
        m1.metric(f"Vittoria {home_team} (1)", f"{round(home_win, 1)}%")
        m2.metric("Pareggio (X)", f"{round(draw, 1)}%")
        m3.metric(f"Vittoria {away_team} (2)", f"{round(away_win, 1)}%")
        st.info(f"⚽ **Expected Goals (xG):** {home_team} **{round(home_xg, 2)}** - **{round(away_xg, 2)}** {away_team}")

        st.markdown("---")
        st.write("### 🎯 Risultati Esatti Più Probabili")
        exact_scores.sort(key=lambda x: x[1], reverse=True)
        top5_scores = exact_scores[:5]
        
        cols = st.columns(5)
        for idx, (score, prob) in enumerate(top5_scores):
            cols[idx].metric(f"Risultato {score}", f"{round(prob, 1)}%")

        st.markdown("---")
        st.write("### ⚽ Probabilità Marcatori Calcolate dall'IA")
        
        c_home, c_away = st.columns(2)
        weights = [0.42, 0.30, 0.20]
        
        with c_home:
            st.write(f"**Marcatori {home_team}:**")
            for idx, player in enumerate(h_data["strikers"]):
                prob_scorer = min(round(weights[idx] * (home_xg / 1.35) * 100, 1), 78.0)
                st.write(f"• **{player}**: ~{prob_scorer}%")
                
        with c_away:
            st.write(f"**Marcatori {away_team}:**")
            for idx, player in enumerate(a_data["strikers"]):
                prob_scorer = min(round(weights[idx] * (away_xg / 1.05) * 100, 1), 78.0)
                st.write(f"• **{player}**: ~{prob_scorer}%")
