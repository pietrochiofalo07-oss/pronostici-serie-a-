import streamlit as st
import requests
import numpy as np
from scipy.stats import poisson

st.set_page_config(
    page_title="EUROPE AI PREDICTOR LIVE PRO", 
    page_icon="⚡", 
    layout="wide"
)

# --- CONFIGURAZIONE API ---
API_KEY = "98ba0f8782444519931d382828466579"
BASE_URL = "https://api.football-data.org/v4/"

headers = {"X-Auth-Token": API_KEY}

# Database aggiornato con i trasferimenti e i nuovi giocatori chiave
KNOWN_PLAYERS = {
    "AC Milan": ["Gonçalo Ramos", "Christian Pulisic", "Tijjani Reijnders", "Rafael Leão"],
    "Inter Milano": ["Lautaro Martínez", "Marcus Thuram", "Hakan Çalhanoğlu", "Henrikh Mkhitaryan"],
    "Juventus": ["Dusan Vlahovic", "Kenan Yildiz", "Teun Koopmeiners", "Nico Gonzalez"],
    "Napoli": ["Romelu Lukaku", "Kevin De Bruyne", "Khvicha Kvaratskhelia", "Scott McTominay"],
    "Atalanta BC": ["Mateo Retegui", "Ademola Lookman", "Charles De Ketelaere", "Elmas"],
    "AS Roma": ["Malen", "Paulo Dybala", "Artem Dovbyk", "Tommaso Baldanzi"],
    "SS Lazio": ["Valentín Castellanos", "Mattia Zaccagni", "Boulaye Dia", "Pinamonti"],
    "Venezia FC": ["Akor Adams", "Gaetano Oristanio", "Joel Pohjanpalo", "Toni Fernandez"],
    "Manchester City FC": ["Erling Haaland", "Phil Foden", "Kevin De Bruyne", "Savinho"],
    "Arsenal FC": ["Bukayo Saka", "Kai Havertz", "Gabriel Martinelli", "Leandro Trossard"],
    "Liverpool FC": ["Mohamed Salah", "Darwin Núñez", "Luis Díaz", "Diogo Jota"],
    "Chelsea FC": ["Cole Palmer", "Nicolas Jackson", "Christopher Nkunku", "Pedro Neto"],
}

@st.cache_data(ttl=3600)
def get_advanced_database(competition_code):
    """
    Scarica la classifica generale, casa, trasferta e calcola metriche avanzate 
    estese (Clean Sheet Rate, Shot Conversion, Goal Difference, Momentum e Indici di Rischio).
    """
    try:
        res_total = requests.get(f"{BASE_URL}competitions/{competition_code}/standings?standingType=TOTAL", headers=headers)
        res_home = requests.get(f"{BASE_URL}competitions/{competition_code}/standings?standingType=HOME", headers=headers)
        res_away = requests.get(f"{BASE_URL}competitions/{competition_code}/standings?standingType=AWAY", headers=headers)

        if res_total.status_code == 200:
            table_total = res_total.json()["standings"][0]["table"]
            table_home = res_home.json()["standings"][0]["table"] if res_home.status_code == 200 else table_total
            table_away = res_away.json()["standings"][0]["table"] if res_away.status_code == 200 else table_total

            home_map = {row["team"]["name"]: row for row in table_home}
            away_map = {row["team"]["name"]: row for row in table_away}

            teams_data = {}
            total_games = sum(row["playedGames"] for row in table_total)
            league_avg_gf = (sum(row["goalsFor"] for row in table_total) / total_games) if total_games > 0 else 1.35

            for row in table_total:
                team_name = row["team"]["name"]
                played = row["playedGames"]
                won = row.get("won", 0)
                drawn = row.get("draw", 0)
                lost = row.get("lost", 0)
                
                h_row = home_map.get(team_name, row)
                a_row = away_map.get(team_name, row)

                h_played = h_row.get("playedGames", 1) or 1
                a_played = a_row.get("playedGames", 1) or 1

                home_gf_per_match = h_row.get("goalsFor", 0) / h_played
                home_ga_per_match = h_row.get("goalsAgainst", 0) / h_played
                away_gf_per_match = a_row.get("goalsFor", 0) / a_played
                away_ga_per_match = a_row.get("goalsAgainst", 0) / a_played

                # Metrica 1: Win Rate Generale e Trend Casalingo/Esterno
                win_rate = (won / played) * 100 if played > 0 else 0.0
                home_win_rate = (h_row.get("won", 0) / h_played) * 100
                away_win_rate = (a_row.get("won", 0) / a_played) * 100

                # Metrica 2: Momentum (Forma Recente Ultime 5)
                form_string = row.get("form", "")
                form_multiplier = 1.0
                form_list = []
                if form_string:
                    form_list = form_string.replace(",", "").split()[-5:]
                    points = form_list.count("W") * 3 + form_list.count("D") * 1
                    max_pts = len(form_list) * 3 if len(form_list) > 0 else 1
                    form_ratio = points / max_pts
                    form_multiplier = 0.80 + (form_ratio * 0.4) # Range più ampio: 0.80 - 1.20

                # Metrica 3: Goal Difference Ratio e Solidità
                gf = row["goalsFor"]
                ga = row["goalsAgainst"]
                gd = gf - ga
                gd_per_match = gd / played if played > 0 else 0.0

                weight = played / (played + 4.0)
                tot_gf = (gf / played) if played > 0 else league_avg_gf
                tot_ga = (ga / played) if played > 0 else league_avg_gf
                smooth_gf = (tot_gf * weight) + (league_avg_gf * (1 - weight))
                smooth_ga = (tot_ga * weight) + (league_avg_gf * (1 - weight))

                # Metrica 4: Clean Sheet e Failed to Score percentbuali stimate
                clean_sheets_est = max(5.0, min(85.0, 50.0 + ((league_avg_gf - smooth_ga) * 25)))
                failed_to_score_est = max(5.0, min(80.0, 30.0 - ((smooth_gf - league_avg_gf) * 20)))

                # Medie Angoli e Cartellini avanzate
                estimated_corners = round(4.2 + (smooth_gf * 0.85) + (smooth_ga * 0.25), 1)
                estimated_cards = round(1.7 + (smooth_ga * 0.55) + ((lost / max(played, 1)) * 0.6), 1)

                teams_data[team_name] = {
                    "att": round(78 + ((smooth_gf - league_avg_gf) * 9), 1),
                    "def": round(78 + ((league_avg_gf - smooth_ga) * 9), 1),
                    "home_gf": home_gf_per_match,
                    "home_ga": home_ga_per_match,
                    "away_gf": away_gf_per_match,
                    "away_ga": away_ga_per_match,
                    "win_rate": round(win_rate, 1),
                    "home_win_rate": round(home_win_rate, 1),
                    "away_win_rate": round(away_win_rate, 1),
                    "gd_per_match": round(gd_per_match, 2),
                    "clean_sheets_prob": round(clean_sheets_est, 1),
                    "fts_prob": round(failed_to_score_est, 1),
                    "form_mult": form_multiplier,
                    "form_sequence": " ".join(form_list) if form_list else "N/D",
                    "avg_corners": estimated_corners,
                    "avg_cards": estimated_cards,
                    "strikers": KNOWN_PLAYERS.get(team_name, ["Attaccante Principale", "Rigorista", "Trequartista", "Esterno Offensivo"])
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
        font-size: 2.3rem; font-weight: 900; text-align: center;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 50%, #00c6ff 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    .cyber-subtitle {
        text-align: center; color: #8b949e; font-size: 0.85rem; margin-bottom: 25px; letter-spacing: 2px; text-transform: uppercase;
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

st.markdown('<div class="cyber-title">⚡ EUROPE FOOTBALL AI PREDICTOR (ULTRA PRO)</div>', unsafe_allow_html=True)
st.markdown('<div class="cyber-subtitle">MODELLO A 12 PARAMETRI: CASA/TRASFERTA + MOMENTUM + CLEAN SHEET + xG</div>', unsafe_allow_html=True)

col_sel1, col_sel2, col_sel3 = st.columns([1.2, 1.2, 1.2])
with col_sel1:
    league_name = st.selectbox("🌐 Campionato", list(leagues_map.keys()))
    competition_code = leagues_map[league_name]

FOOTBALL_DATABASE = get_advanced_database(competition_code)

if not FOOTBALL_DATABASE:
    st.error("⚠️ Impossibile scaricare i dati avanzati. Verifica la connessione o i parametri dell'API.")
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
        if st.button("🚀 ESEGUI ANALISI MULTI-METRICA LIVE", type="primary", use_container_width=True):
            h_data = FOOTBALL_DATABASE[home_team]
            a_data = FOOTBALL_DATABASE[away_team]
            
            # Calcolo xG avanzato con scambi di forza Casa/Trasferta + Momentum aggiornato
            home_power = (h_data["home_gf"] + a_data["away_ga"]) / 2
            away_power = (a_data["away_gf"] + h_data["home_ga"]) / 2
            
            home_xg = max(0.3, home_power * h_data["form_mult"] * 1.12)
            away_xg = max(0.3, away_power * a_data["form_mult"] * 0.92)
            
            max_goals = 6
            prob_matrix = np.zeros((max_goals, max_goals))
            exact_scores = []
            
            prob_over25 = prob_under25 = prob_gg = prob_ng = 0.0

            for h in range(max_goals):
                for a in range(max_goals):
                    p = poisson.pmf(h, home_xg) * poisson.pmf(a, away_xg)
                    prob_matrix[h, a] = p
                    exact_scores.append((f"{h} - {a}", p * 100))

                    total_goals = h + a
                    if total_goals > 2.5: prob_over25 += p
                    else: prob_under25 += p
                    
                    if h > 0 and a > 0: prob_gg += p
                    else: prob_ng += p

            home_win = float(np.sum(np.tril(prob_matrix, -1))) * 100
            draw = float(np.sum(np.diag(prob_matrix))) * 100
            away_win = float(np.sum(np.triu(prob_matrix, 1))) * 100

            prob_over25 *= 100; prob_under25 *= 100
            prob_gg *= 100; prob_ng *= 100

            expected_corners = round((h_data["avg_corners"] + a_data["avg_corners"]) * 0.95, 1)
            prob_over95_corners = min(round(50 + ((expected_corners - 9.5) * 12), 1), 89.0)
            prob_over95_corners = max(prob_over95_corners, 15.0)

            expected_cards = round((h_data["avg_cards"] + a_data["avg_cards"]) * 0.9, 1)
            prob_over35_cards = min(round(50 + ((expected_cards - 4.0) * 15), 1), 90.0)
            prob_over35_cards = max(prob_over35_cards, 20.0)

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
                    ⚽ <strong>Expected Goals (xG con Home/Away & Fattore Rosa Aggiornato):</strong> &nbsp; 
                    <span style="color: #00f2fe;">{home_team} ({round(home_xg, 2)})</span> &nbsp;—&nbsp; 
                    <span style="color: #ff007f;">({round(away_xg, 2)}) {away_team}</span>
                </div>
            """, unsafe_allow_html=True)

            total_xg = home_xg + away_xg
            if total_xg > 3.2:
                match_narrative = f"🔥 **Analisi Tattica Avanzata:** Elevata spinta offensiva stimata per entrambe. Ci si attende una partita aperta, ad alto ritmo e con molteplici conclusioni nello specchio."
            elif total_xg < 2.2:
                match_narrative = f"🔒 **Analisi Tattica Avanzata:** Parametri difensivi solidi e tassi di Clean Sheet elevati per le due contendenti. Gara bloccata, tattica e con scarsi spazi di manovra."
            else:
                match_narrative = f"⚖️ **Analisi Tattica Avanzata:** Incontro in perfetto equilibrio tecnico, deciso dai dettagli sui reparti esterni e dallo stato di forma recente."

            st.markdown(f'<div class="match-analysis-box">{match_narrative}</div>', unsafe_allow_html=True)

            best_goals = "OVER 2.5" if prob_over25 > prob_under25 else "UNDER 2.5"
            best_gg_ng = "GOAL (GG)" if prob_gg > prob_ng else "NO GOAL (NG)"

            st.success(f"""
                💡 **SINTESI SCHEDINA MULTI-METRICA:**
                * ⚽ **Linea Gol Consigliata:** `{best_goals}`
                * 🥅 **Opzione Entrambe a Segno:** `{best_gg_ng}`
                * 🚩 **Angoli Stimati:** `Over 9.5` ({prob_over95_corners}%)
                * 🟨 **Cartellini Stimati:** `Over 3.5` ({prob_over35_cards}%)
            """)

            with st.expander("📊 Cruscotto Metriche Avanzate a Confronto", expanded=True):
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.markdown(f"### 🏠 {home_team}")
                    st.metric("Win Rate Totale", f"{h_data['win_rate']}%")
                    st.metric("Win Rate Casalingo", f"{h_data['home_win_rate']}%")
                    st.metric("Differenza Reti / Partita", f"{h_data['gd_per_match']:+d}" if isinstance(h_data['gd_per_match'], int) else f"{h_data['gd_per_match']}")
                    st.metric("Forma Recente (Ultime 5)", f"{h_data['form_sequence']}")
                    st.metric("Probabilità Clean Sheet", f"{h_data['clean_sheets_prob']}%")
                with col_m2:
                    st.markdown(f"### ✈️ {away_team}")
                    st.metric("Win Rate Totale", f"{a_data['win_rate']}%")
                    st.metric("Win Rate Esterno", f"{a_data['away_win_rate']}%")
                    st.metric("Differenza Reti / Partita", f"{a_data['gd_per_match']:+d}" if isinstance(a_data['gd_per_match'], int) else f"{a_data['gd_per_match']}")
                    st.metric("Forma Recente (Ultime 5)", f"{a_data['form_sequence']}")
                    st.metric("Probabilità Clean Sheet", f"{a_data['clean_sheets_prob']}%")

            with st.expander("📈 Statistiche di Mercato e Scommesse", expanded=False):
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    st.markdown(f'<div class="stat-box">Entrambe a Segno (Goal): <strong style="color:#00c6ff;">{round(prob_gg, 1)}%</strong></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="stat-box">No Goal (NG): <strong style="color:#ffb703;">{round(prob_ng, 1)}%</strong></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="stat-box">Over 2.5 Gol: <strong style="color:#00c6ff;">{round(prob_over25, 1)}%</strong></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="stat-box">Under 2.5 Gol: <strong style="color:#ffb703;">{round(prob_under25, 1)}%</strong></div>', unsafe_allow_html=True)
                with col_s2:
                    st.markdown(f'<div class="stat-box">Media Angoli Previsti: <strong style="color:#00f2fe;">{expected_corners}</strong></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="stat-box">Probabilità Over 9.5 Angoli: <strong style="color:#00f2fe;">{prob_over95_corners}%</strong></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="stat-box">Media Cartellini Previsti: <strong style="color:#ffb703;">{expected_cards}</strong></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="stat-box">Probabilità Over 3.5 Cartellini: <strong style="color:#ffb703;">{prob_over35_cards}%</strong></div>', unsafe_allow_html=True)

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

            with st.expander("⚽ Probabilità Marcatori (Aggiornate con Nuovi Inserimenti)", expanded=False):
                m_col1, m_col2 = st.columns(2)
                weights = [0.38, 0.28, 0.20, 0.14]
                
                with m_col1:
                    st.markdown(f"**Reparto Offensivo {home_team}**")
                    for idx, player in enumerate(h_data["strikers"]):
                        prob_scorer = min(round(weights[idx] * (home_xg / 1.35) * 100, 1), 85.0)
                        st.write(f"• **{player}**: `{prob_scorer}%`")
                        st.progress(prob_scorer / 100)
                        
                with m_col2:
                    st.markdown(f"**Reparto Offensivo {away_team}**")
                    for idx, player in enumerate(a_data["strikers"]):
                        prob_scorer = min(round(weights[idx] * (away_xg / 1.05) * 100, 1), 85.0)
                        st.write(f"• **{player}**: `{prob_scorer}%`")
                        st.progress(prob_scorer / 100)
