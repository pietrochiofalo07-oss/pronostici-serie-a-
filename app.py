import streamlit as st
import requests
import numpy as np
from scipy.stats import poisson

st.set_page_config(
    page_title="EUROPE AI PREDICTOR LIVE", 
    page_icon="⚡", 
    layout="wide"
)

# --- CONFIGURAZIONE API ---
API_KEY = "98ba0f8782444519931d382828466579"
BASE_URL = "https://api.football-data.org/v4/"

headers = {"X-Auth-Token": API_KEY}

@st.cache_data(ttl=3600)
def get_dynamic_database(competition_code):
    url = f"{BASE_URL}competitions/{competition_code}/standings"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            table = data["standings"][0]["table"]
            teams_data = {}
            for row in table:
                team_name = row["team"]["name"]
                played = row["playedGames"]
                if played > 0:
                    gf_per_match = row["goalsFor"] / played
                    ga_per_match = row["goalsAgainst"] / played
                else:
                    gf_per_match, ga_per_match = 1.0, 1.0
                
                # Valutazioni dinamiche basate sui gol reali in classifica
                teams_data[team_name] = {
                    "att": round(75 + (gf_per_match * 6), 1),
                    "def": round(75 + (ga_per_match * 6), 1),
                    "strikers": [f"Capocannoniere {team_name}", "Rigorista", "Jolly d'attacco", "Esterno offensivo"]
                }
            return teams_data
    except Exception:
        pass
    return {}

leagues_map = {
    "Serie A": "SA",
    "Premier League": "PL",
    "La Liga": "PD",
    "Bundesliga": "BL1",
    "Ligue 1": "FL1"
}

# --- CSS STYLING ---
st.markdown("""
    <style>
    .main { background: radial-gradient(circle at top left, #0d1117, #010409) !important; }
    .cyber-title {
        font-size: 2.4rem; font-weight: 900; text-align: center;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 50%, #00c6ff 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    .cyber-subtitle {
        text-align: center; color: #8b949e; font-size: 0.9rem; margin-bottom: 25px; letter-spacing: 2px; text-transform: uppercase;
    }
    .neon-card {
        background: rgba(22, 27, 34, 0.7); backdrop-filter: blur(10px); border-radius: 14px; padding: 18px 10px; text-align: center;
    }
    .neon-card-1 { border: 1px solid #00f2fe; }
    .neon-card-x { border: 1px solid #ffb703; }
    .neon-card-2 { border: 1px solid #ff007f; }
    .neon-label { font-size: 0.75rem; font-weight: 700; color: #8b949e; margin-bottom: 6px; }
    .neon-val-1 { color: #00f2fe; font-size: 1.8rem; font-weight: 900; }
    .neon-val-x { color: #ffb703; font-size: 1.8rem; font-weight: 900; }
    .neon-val-2 { color: #ff007f; font-size: 1.8rem; font-weight: 900; }
    .stat-box { background: rgba(22, 27, 34, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 12px; text-align: center; margin-bottom: 8px; }
    .xg-box { background: linear-gradient(90deg, rgba(0,242,254,0.08) 0%, rgba(255,0,127,0.08) 100%); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 12px; text-align: center; color: #f0f6fc; margin-bottom: 20px; }
    .match-analysis-box { background: rgba(22, 27, 34, 0.8); border-left: 4px solid #00f2fe; border-radius: 4px 10px 10px 4px; padding: 15px; margin-bottom: 20px; color: #e6edf3; font-size: 0.95rem; line-height: 1.5; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="cyber-title">⚡ EUROPE FOOTBALL AI PREDICTOR (LIVE)</div>', unsafe_allow_html=True)
st.markdown('<div class="cyber-subtitle">DATI AGGIORNATI IN TEMPO REALE DA CLASSIFICA REALE</div>', unsafe_allow_html=True)

col_sel1, col_sel2, col_sel3 = st.columns([1.2, 1.2, 1.2])
with col_sel1:
    league_name = st.selectbox("🌐 Campionato", list(leagues_map.keys()))
    competition_code = leagues_map[league_name]

# Caricamento dinamico dal web
FOOTBALL_DATABASE = get_dynamic_database(competition_code)

if not FOOTBALL_DATABASE:
    st.error("⚠️ Impossibile scaricare i dati. Verifica che la chiave API sia attiva o che il campionato sia attualmente coperto dal piano gratuito.")
else:
    teams_list = sorted(list(FOOTBALL_DATABASE.keys()))

    with col_sel2:
        home_team = st.selectbox("🏠 Casa", teams_list, index=0)
    with col_sel3:
        away_team = st.selectbox("✈️ Ospite", teams_list, index=1 if len(teams_list) > 1 else 0)

    st.markdown("<br>", unsafe_allow_html=True)

    if home_team == away_team:
        st.warning("⚠️ Seleziona due squadre diverse per procedere.")
    else:
        if st.button("🚀 ESEGUI ANALISI ALGORITMICA LIVE", type="primary", use_container_width=True):
            h_data = FOOTBALL_DATABASE[home_team]
            a_data = FOOTBALL_DATABASE[away_team]
            
            home_xg = 1.25 * ((h_data["att"] / a_data["def"]) ** 2.2)
            away_xg = 0.95 * ((a_data["att"] / h_data["def"]) ** 2.2)
            
            max_goals = 6
            prob_matrix = np.zeros((max_goals, max_goals))
            exact_scores = []
            
            prob_over15 = prob_over25 = prob_under25 = prob_gg = prob_ng = 0.0

            for h in range(max_goals):
                for a in range(max_goals):
                    p = poisson.pmf(h, home_xg) * poisson.pmf(a, away_xg)
                    prob_matrix[h, a] = p
                    exact_scores.append((f"{h} - {a}", p * 100))

                    total_goals = h + a
                    if total_goals > 1.5: prob_over15 += p
                    if total_goals > 2.5: prob_over25 += p
                    else: prob_under25 += p
                    
                    if h > 0 and a > 0: prob_gg += p
                    else: prob_ng += p

            home_win = float(np.sum(np.tril(prob_matrix, -1))) * 100
            draw = float(np.sum(np.diag(prob_matrix))) * 100
            away_win = float(np.sum(np.triu(prob_matrix, 1))) * 100

            prob_over15 *= 100; prob_over25 *= 100; prob_under25 *= 100
            prob_gg *= 100; prob_ng *= 100

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f'<div class="neon-card neon-card-1"><div class="neon-label">1 (CASA)</div><div class="neon-val-1">{round(home_win, 1)}%</div><div style="font-size:0.75rem; color:#8b949e;">{home_team}</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="neon-card neon-card-x"><div class="neon-label">X (PAREGGIO)</div><div class="neon-val-x">{round(draw, 1)}%</div><div style="font-size:0.75rem; color:#8b949e;">Equilibrio</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="neon-card neon-card-2"><div class="neon-label">2 (TRASFERTA)</div><div class="neon-val-2">{round(away_win, 1)}%</div><div style="font-size:0.75rem; color:#8b949e;">{away_team}</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
                <div class="xg-box">
                    ⚽ <strong>Expected Goals (xG) Calcolati in Base ai Dati Reali:</strong> &nbsp; 
                    <span style="color: #00f2fe;">{home_team} ({round(home_xg, 2)})</span> &nbsp;—&nbsp; 
                    <span style="color: #ff007f;">({round(away_xg, 2)}) {away_team}</span>
                </div>
            """, unsafe_allow_html=True)

            total_xg = home_xg + away_xg
            if total_xg > 3.2:
                match_narrative = f"🔥 **Analisi Tattica del Match:** Sarà una partita **estremamente aperta e ad alto potenziale offensivo**, visti i dati reali di gol realizzati dalle due squadre in campionato."
            elif total_xg < 2.2:
                match_narrative = f"🔒 **Analisi Tattica del Match:** Ci attende una sfida **molto chiusa e difensivamente accorta**, con reparti che concedono pochi spazi in base alle statistiche attuali."
            else:
                match_narrative = f"⚖️ **Analisi Tattica del Match:** Sarà una gara **equilibrata e incerta**, dove i dettagli e la gestione del possesso palla faranno la differenza."

            st.markdown(f'<div class="match-analysis-box">{match_narrative}</div>', unsafe_allow_html=True)

            best_goals = "OVER 2.5" if prob_over25 > prob_under25 else "UNDER 2.5"
            best_gg_ng = "GOAL (GG)" if prob_gg > prob_ng else "NO GOAL (NG)"

            st.success(f"""
                💡 **SINTESI SCHEDINA CONSIGLIATA:**
                * ⚽ **Linea Gol Consigliata:** `{best_goals}` (Over 1.5 al {round(prob_over15, 1)}%)
                * 🥅 **Opzione Entrambe a Segno:** `{best_gg_ng}`
            """)

            with st.expander("📊 Statistiche Dettagliate Mercati", expanded=True):
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    st.markdown(f'<div class="stat-box">Entrambe a Segno (Goal): <strong style="color:#00c6ff;">{round(prob_gg, 1)}%</strong></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="stat-box">No Goal (NG): <strong style="color:#ffb703;">{round(prob_ng, 1)}%</strong></div>', unsafe_allow_html=True)
                with col_s2:
                    st.markdown(f'<div class="stat-box">Over 2.5 Gol: <strong style="color:#00c6ff;">{round(prob_over25, 1)}%</strong></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="stat-box">Under 2.5 Gol: <strong style="color:#ffb703;">{round(prob_under25, 1)}%</strong></div>', unsafe_allow_html=True)

            with st.expander("🎯 I 5 Risultati Esatti più probabili", expanded=True):
                exact_scores.sort(key=lambda x: x[1], reverse=True)
                top5 = exact_scores[:5]
                res_cols = st.columns(5)
                for idx, (score, prob) in enumerate(top5):
                    with res_cols[idx]:
                        st.markdown(f"""
                            <div class="stat-box">
                                <span style="font-size:0.7rem; color:#8b949e;">#{idx+1}</span><br>
                                <strong style="font-size:1.2rem; color:#fff;">{score}</strong><br>
                                <span style="color:#00f2fe; font-size:0.9rem;">{round(prob, 1)}%</span>
                            </div>
                        """, unsafe_allow_html=True)
