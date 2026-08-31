import streamlit as st
import numpy as np
from scipy.stats import poisson

st.set_page_config(
    page_title="EUROPE AI PREDICTOR 2027", 
    page_icon="⚡", 
    layout="wide"
)

# --- CSS FUTURISTICO AVANZATO (NEON & GLASSMORPHISM) ---
st.markdown("""
    <style>
    .main {
        background: radial-gradient(circle at top left, #0d1117, #010409) !important;
    }
    
    .cyber-title {
        font-family: 'Segoe UI', Roboto, sans-serif;
        font-size: 2.6rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 50%, #00c6ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(0, 242, 254, 0.3);
        margin-bottom: 5px;
        letter-spacing: 1px;
    }
    
    .cyber-subtitle {
        text-align: center;
        color: #8b949e;
        font-size: 0.95rem;
        margin-bottom: 35px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .neon-card {
        background: rgba(22, 27, 34, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 24px 15px;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.3s ease;
    }
    .neon-card-1 { border: 1px solid #00f2fe; box-shadow: 0 0 15px rgba(0, 242, 254, 0.2); }
    .neon-card-x { border: 1px solid #ffb703; box-shadow: 0 0 15px rgba(255, 183, 3, 0.2); }
    .neon-card-2 { border: 1px solid #ff007f; box-shadow: 0 0 15px rgba(255, 0, 127, 0.2); }

    .neon-label {
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        color: #8b949e;
        margin-bottom: 8px;
    }
    
    .neon-val-1 { color: #00f2fe; font-size: 2.2rem; font-weight: 900; text-shadow: 0 0 10px rgba(0, 242, 254, 0.5); }
    .neon-val-x { color: #ffb703; font-size: 2.2rem; font-weight: 900; text-shadow: 0 0 10px rgba(255, 183, 3, 0.5); }
    .neon-val-2 { color: #ff007f; font-size: 2.2rem; font-weight: 900; text-shadow: 0 0 10px rgba(255, 0, 127, 0.5); }

    .score-badge {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 4px solid #00f2fe;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
        text-align: center;
    }

    .bet-card {
        background: rgba(22, 27, 34, 0.8);
        border: 1px solid rgba(0, 242, 254, 0.3);
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        margin-bottom: 10px;
    }
    
    .xg-box {
        background: linear-gradient(90deg, rgba(0,242,254,0.1) 0%, rgba(255,0,127,0.1) 100%);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        font-size: 1.1rem;
        color: #f0f6fc;
        margin-top: 25px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="cyber-title">⚡ EUROPE FOOTBALL AI PREDICTOR</div>', unsafe_allow_html=True)
st.markdown('<div class="cyber-subtitle">MODELLO ALGORITMICO AVANZATO • EUROPEAN LEAGUES 2026/2027</div>', unsafe_allow_html=True)

FOOTBALL_DATABASE = {
    "Serie A": {
        "Atalanta": {"att": 87, "def": 82, "strikers": ["De Ketelaere", "Scamacca", "Gaetano"]},
        "Bologna": {"att": 80, "def": 79, "strikers": ["Orsolini", "Ndoye", "Castro"]},
        "Cagliari": {"att": 70, "def": 70, "strikers": ["Luvumbo", "Piccoli", "Lapadula"]},
        "Como": {"att": 77, "def": 75, "strikers": ["Strefezza", "Belotti", "Cutrone"]},
        "Fiorentina": {"att": 80, "def": 78, "strikers": ["Gudmundsson", "Kean", "Mandragora"]},
        "Frosinone": {"att": 71, "def": 72, "strikers": ["Birligea", "Kvernadze", "Calò"]},
        "Genoa": {"att": 73, "def": 74, "strikers": ["Malinovskyi", "Messias", "Pinamonti"]},
        "Inter": {"att": 91, "def": 89, "strikers": ["Lautaro Martínez", "Thuram", "Calhanoglu"]},
        "Juventus": {"att": 88, "def": 87, "strikers": ["Yildiz", "Vlahović", "Koopmeiners"]},
        "Lazio": {"att": 81, "def": 80, "strikers": ["Zaccagni", "Noslin", "Dia"]},
        "Lecce": {"att": 69, "def": 70, "strikers": ["Rebic", "Krstovic", "Joel Monteiro"]},
        "Milan": {"att": 85, "def": 82, "strikers": ["Pulisic", "Leão", "Morata"]},
        "Monza": {"att": 72, "def": 73, "strikers": ["Maldini", "Mota", "Djuric"]},
        "Napoli": {"att": 89, "def": 85, "strikers": ["Kvaratskhelia", "Politano", "Lukaku"]},
        "Parma": {"att": 73, "def": 71, "strikers": ["Man", "Mihaila", "Bonny"]},
        "Roma": {"att": 84, "def": 83, "strikers": ["Soulé", "Dybala", "Dovbyk"]},
        "Sassuolo": {"att": 73, "def": 71, "strikers": ["Laurienté", "Moro", "Mulattieri"]},
        "Torino": {"att": 75, "def": 77, "strikers": ["Vlasic", "Adams", "Sanabria"]},
        "Udinese": {"att": 74, "def": 73, "strikers": ["Thauvin", "Brenner", "Lucca"]},
        "Venezia": {"att": 69, "def": 69, "strikers": ["Oristanio", "Pohjanpalo", "Duncan"]}
    },
    "Premier League": {
        "Arsenal": {"att": 92, "def": 91, "strikers": ["Bukayo Saka", "Kai Havertz", "Gabriel Martinelli"]},
        "Aston Villa": {"att": 83, "def": 80, "strikers": ["Ollie Watkins", "Leon Bailey", "Morgan Rogers"]},
        "Chelsea": {"att": 86, "def": 81, "strikers": ["Cole Palmer", "Nicolas Jackson", "Christopher Nkunku"]},
        "Liverpool": {"att": 91, "def": 88, "strikers": ["Mohamed Salah", "Darwin Núñez", "Luis Díaz"]},
        "Manchester City": {"att": 95, "def": 89, "strikers": ["Erling Haaland", "Phil Foden", "Savinho"]},
        "Manchester United": {"att": 83, "def": 82, "strikers": ["Joshua Zirkzee", "Rasmus Højlund", "Alejandro Garnacho"]},
        "Newcastle United": {"att": 84, "def": 82, "strikers": ["Alexander Isak", "Anthony Gordon", "Harvey Barnes"]},
        "Tottenham": {"att": 86, "def": 81, "strikers": ["Son Heung-min", "Dominic Solanke", "Dejan Kulusevski"]}
    },
    "La Liga": {
        "Atletico Madrid": {"att": 86, "def": 86, "strikers": ["Julián Álvarez", "Antoine Griezmann", "Alexander Sørloth"]},
        "Barcelona": {"att": 93, "def": 85, "strikers": ["Robert Lewandowski", "Lamine Yamal", "Raphinha"]},
        "Real Madrid": {"att": 96, "def": 90, "strikers": ["Kylian Mbappé", "Vinicius Junior", "Rodrygo"]}
    },
    "Bundesliga": {
        "Bayer Leverkusen": {"att": 90, "def": 85, "strikers": ["Victor Boniface", "Florian Wirtz", "Patrik Schick"]},
        "Bayern Munich": {"att": 94, "def": 86, "strikers": ["Harry Kane", "Jamal Musiala", "Michael Olise"]},
        "Borussia Dortmund": {"att": 86, "def": 82, "strikers": ["Serhou Guirassy", "Karim Adeyemi", "Donyell Malen"]}
    },
    "Ligue 1": {
        "Monaco": {"att": 83, "def": 80, "strikers": ["Folarin Balogun", "Breel Embolo", "Takumi Minamino"]},
        "Marseille": {"att": 84, "def": 79, "strikers": ["Mason Greenwood", "Elye Wahi", "Luis Henrique"]},
        "Paris Saint-Germain": {"att": 92, "def": 85, "strikers": ["Ousmane Dembélé", "Bradley Barcola", "Marco Asensio"]}
    }
}

# Selettori Campionato e Squadre
league = st.selectbox("🌐 Seleziona Campionato", list(FOOTBALL_DATABASE.keys()))
teams_list = sorted(list(FOOTBALL_DATABASE[league].keys()))

c1, c2 = st.columns(2)
with c1:
    home_team = st.selectbox("🏠 Squadra di Casa", teams_list, index=0)
with c2:
    away_team = st.selectbox("✈️ Squadra Ospite", teams_list, index=1 if len(teams_list) > 1 else 0)

if home_team == away_team:
    st.warning("⚠️ Seleziona due squadre diverse.")
else:
    if st.button("🚀 AVVIA SIMULAZIONE IA", type="primary", use_container_width=True):
        h_data = FOOTBALL_DATABASE[league][home_team]
        a_data = FOOTBALL_DATABASE[league][away_team]
        
        home_xg = 1.25 * ((h_data["att"] / a_data["def"]) ** 2.2)
        away_xg = 0.95 * ((a_data["att"] / h_data["def"]) ** 2.2)
        
        max_goals = 6
        prob_matrix = np.zeros((max_goals, max_goals))
        exact_scores = []
        
        prob_over15 = 0.0
        prob_over25 = 0.0
        prob_under25 = 0.0
        prob_gg = 0.0
        prob_ng = 0.0
        
        prob_0_1_gol = 0.0
        prob_2_3_gol = 0.0
        prob_4_plus_gol = 0.0

        for h in range(max_goals):
            for a in range(max_goals):
                p = poisson.pmf(h, home_xg) * poisson.pmf(a, away_xg)
                prob_matrix[h, a] = p
                exact_scores.append((f"{h} - {a}", p * 100))

                total_goals = h + a
                
                if total_goals > 1.5:
                    prob_over15 += p
                if total_goals > 2.5:
                    prob_over25 += p
                else:
                    prob_under25 += p
                
                if h > 0 and a > 0:
                    prob_gg += p
                else:
                    prob_ng += p

                if total_goals <= 1:
                    prob_0_1_gol += p
                elif 2 <= total_goals <= 3:
                    prob_2_3_gol += p
                else:
                    prob_4_plus_gol += p

        home_win = float(np.sum(np.tril(prob_matrix, -1))) * 100
        draw = float(np.sum(np.diag(prob_matrix))) * 100
        away_win = float(np.sum(np.triu(prob_matrix, 1))) * 100

        dc_1x = home_win + draw
        dc_x2 = away_win + draw
        dc_12 = home_win + away_win

        prob_over15 *= 100
        prob_over25 *= 100
        prob_under25 *= 100
        prob_gg *= 100
        prob_ng *= 100
        prob_0_1_gol *= 100
        prob_2_3_gol *= 100
        prob_4_plus_gol *= 100

        st.markdown("<br>", unsafe_allow_html=True)
        
        col_1, col_x, col_2 = st.columns(3)
        with col_1:
            st.markdown(f"""
                <div class="neon-card neon-card-1">
                    <div class="neon-label">VITTORIA CASA (1)</div>
                    <div class="neon-val-1">{round(home_win, 1)}%</div>
                    <div style="color: #00f2fe; font-size: 0.8rem; margin-top:5px;">{home_team}</div>
                </div>
            """, unsafe_allow_html=True)
        with col_x:
            st.markdown(f"""
                <div class="neon-card neon-card-x">
                    <div class="neon-label">PAREGGIO (X)</div>
                    <div class="neon-val-x">{round(draw, 1)}%</div>
                    <div style="color: #ffb703; font-size: 0.8rem; margin-top:5px;">EQ. MATEMATICA</div>
                </div>
            """, unsafe_allow_html=True)
        with col_2:
            st.markdown(f"""
                <div class="neon-card neon-card-2">
                    <div class="neon-label">VITTORIA TRASFERTA (2)</div>
                    <div class="neon-val-2">{round(away_win, 1)}%</div>
                    <div style="color: #ff007f; font-size: 0.8rem; margin-top:5px;">{away_team}</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="xg-box">
                ⚽ Expected Goals (xG) Calcolati: 
                <strong style="color: #00f2fe;">{home_team} {round(home_xg, 2)}</strong> — 
                <strong style="color: #ff007f;">{round(away_xg, 2)} {away_team}</strong>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📊 Statistiche & Pronostici Schedina")
        
        d1, d2, d3, d4, d5 = st.columns(5)
        with d1:
            st.markdown(f"""<div class="bet-card">
                <span style="color:#8b949e; font-size:0.8rem;">DOPPIA CHANCE 1X</span>
                <h3 style="color:#00f2fe; margin:5px 0;">{round(dc_1x, 1)}%</h3>
            </div>""", unsafe_allow_html=True)
        with d2:
            st.markdown(f"""<div class="bet-card">
                <span style="color:#8b949e; font-size:0.8rem;">DOPPIA CHANCE X2</span>
                <h3 style="color:#ff007f; margin:5px 0;">{round(dc_x2, 1)}%</h3>
            </div>""", unsafe_allow_html=True)
        with d3:
            st.markdown(f"""<div class="bet-card">
                <span style="color:#8b949e; font-size:0.8rem;">DOPPIA CHANCE 12</span>
                <h3 style="color:#ffb703; margin:5px 0;">{round(dc_12, 1)}%</h3>
            </div>""", unsafe_allow_html=True)
        with d4:
            st.markdown(f"""<div class="bet-card">
                <span style="color:#8b949e; font-size:0.8rem;">GOAL (GG)</span>
                <h3 style="color:#00c6ff; margin:5px 0;">{round(prob_gg, 1)}%</h3>
            </div>""", unsafe_allow_html=True)
        with d5:
            st.markdown(f"""<div class="bet-card">
                <span style="color:#8b949e; font-size:0.8rem;">NO GOAL (NG)</span>
                <h3 style="color:#8b949e; margin:5px 0;">{round(prob_ng, 1)}%</h3>
            </div>""", unsafe_allow_html=True)

        o1, o2, o3, o4, o5 = st.columns(5)
        with o1:
            st.markdown(f"""<div class="bet-card">
                <span style="color:#8b949e; font-size:0.8rem;">OVER 1.5 GOL</span>
                <h3 style="color:#00f2fe; margin:5px 0;">{round(prob_over15, 1)}%</h3>
            </div>""", unsafe_allow_html=True)
        with o2:
            st.markdown(f"""<div class="bet-card">
                <span style="color:#8b949e; font-size:0.8rem;">OVER 2.5 GOL</span>
                <h3 style="color:#00c6ff; margin:5px 0;">{round(prob_over25, 1)}%</h3>
            </div>""", unsafe_allow_html=True)
        with o3:
            st.markdown(f"""<div class="bet-card">
                <span style="color:#8b949e; font-size:0.8rem;">UNDER 2.5 GOL</span>
                <h3 style="color:#ffb703; margin:5px 0;">{round(prob_under25, 1)}%</h3>
            </div>""", unsafe_allow_html=True)
        with o4:
            st.markdown(f"""<div class="bet-card">
                <span style="color:#8b949e; font-size:0.8rem;">SOMMA GOL 2-3</span>
                <h3 style="color:#00f2fe; margin:5px 0;">{round(prob_2_3_gol, 1)}%</h3>
            </div>""", unsafe_allow_html=True)
        with o5:
            st.markdown(f"""<div class="bet-card">
                <span style="color:#8b949e; font-size:0.8rem;">SOMMA GOL 0-1</span>
                <h3 style="color:#8b949e; margin:5px 0;">{round(prob_0_1_gol, 1)}%</h3>
            </div>""", unsafe_allow_html=True)

        best_dc = "1X" if dc_1x > dc_x2 and dc_1x > dc_12 else ("X2" if dc_x2 > dc_1x and dc_x2 > dc_12 else "12")
        best_goals = "OVER 2.5" if prob_over25 > prob_under25 else "UNDER 2.5"
        best_gg_ng = "GOAL (GG)" if prob_gg > prob_ng else "NO GOAL (NG)"

        st.info(f"""
            💡 **CONSIGLI PER LA VINCITA DELLA SCHEDINA:**
            * 🛡️ **Doppia Chance Sicura:** `{best_dc}` (Probabilità: **{round(max(dc_1x, dc_x2, dc_12), 1)}%**)
            * ⚽ **Linea Gol Consigliata:** `{best_goals}` (Over 1.5 coperto al **{round(prob_over15, 1)}%**)
            * 🥅 **Entrambe a segno:** `{best_gg_ng}`
        """)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🎯 Risultati Esatti più Probabili")
        
        exact_scores.sort(key=lambda x: x[1], reverse=True)
        top5 = exact_scores[:5]
        
        res_cols = st.columns(5)
        for idx, (score, prob) in enumerate(top5):
            with res_cols[idx]:
                st.markdown(f"""
                    <div class="score-badge">
                        <span style="color: #8b949e; font-size: 0.75rem;">RANK #{idx+1}</span><br>
                        <strong style="color: #ffffff; font-size: 1.4rem;">{score}</strong><br>
                        <span style="color: #00f2fe; font-weight: bold;">{round(prob, 1)}%</span>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("⚽ Probabilità Marcatori IA")
        
        m_col1, m_col2 = st.columns(2)
        weights = [0.44, 0.32, 0.22]
        
        with m_col1:
            st.write(f"**Marcatori {home_team}:**")
            for idx, player in enumerate(h_data["strikers"]):
                prob_scorer = min(round(weights[idx] * (home_xg / 1.35) * 100, 1), 82.0)
                st.write(f"👤 **{player}** — `{prob_scorer}%`")
                st.progress(prob_scorer / 100)
                
        with m_col2:
            st.write(f"**Marcatori {away_team}:**")
            for idx, player in enumerate(a_data["strikers"]):
                prob_scorer = min(round(weights[idx] * (away_xg / 1.05) * 100, 1), 82.0)
                st.write(f"👤 **{player}** — `{prob_scorer}%`")
                st.progress(prob_scorer / 100)
