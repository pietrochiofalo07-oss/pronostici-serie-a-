import streamlit as st
import requests
import numpy as np
from scipy.stats import poisson

st.set_page_config(
    page_title="EUROPE AI PREDICTOR PRO", 
    page_icon="⚡", 
    layout="centered"
)

# --- CONFIGURAZIONE API ---
API_KEY = "98ba0f8782444519931d382828466579"
BASE_URL = "https://api.football-data.org/v4/"

headers = {"X-Auth-Token": API_KEY}

# Database aggiornato con i trasferimenti e i giocatori chiave
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
    estese (Clean Sheet Rate, Goal Difference, Momentum e Indici di Rischio).
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
                lost = row.get("lost", 0)
                
                h_row = home_map.get(team_name, row)
                a_row = away_map.get(team_name, row)

                h_played = h_row.get("playedGames", 1) or 1
                a_played = a_row.get("playedGames", 1) or 1

                home_gf_per_match = h_row.get("goalsFor", 0) / h_played
                home_ga_per_match = h_row.get("goalsAgainst", 0) / h_played
                away_gf_per_match = a_row.get("goalsFor", 0) / a_played
                away_ga_per_match = a_row.get("goalsAgainst", 0) / a_played

                win_rate = (won / played) * 100 if played > 0 else 0.0
                home_win_rate = (h_row.get("won", 0) / h_played) * 100
                away_win_rate = (a_row.get("won", 0) / a_played) * 100

                form_string = row.get("form", "")
                form_multiplier = 1.0
                form_list = []
                if form_string:
                    form_list = form_string.replace(",", "").split()[-5:]
                    points = form_list.count("W") * 3 + form_list.count("D") * 1
                    max_pts = len(form_list) * 3 if len(form_list) > 0 else 1
                    form_ratio = points / max_pts
                    form_multiplier = 0.80 + (form_ratio * 0.4)

                gf = row["goalsFor"]
                ga = row["goalsAgainst"]
                gd = gf - ga
                gd_per_match = gd / played if played > 0 else 0.0

                weight = played / (played + 4.0)
                tot_gf = (gf / played) if played > 0 else league_avg_gf
                tot_ga = (ga / played) if played > 0 else league_avg_gf
                smooth_gf = (tot_gf * weight) + (league_avg_gf * (1 - weight))
                smooth_ga = (tot_ga * weight) + (league_avg_gf * (1 - weight))

                clean_sheets_est = max(5.0, min(85.0, 50.0 + ((league_avg_gf - smooth_ga) * 25)))

                estimated_corners = round(4.2 + (smooth_gf * 0.85) + (smooth_ga * 0.25), 1)
                estimated_cards = round(1.7 + (smooth_ga * 0.55) + ((lost / max(played, 1)) * 0.6), 1)

                teams_data[team_name] = {
                    "home_gf": home_gf_per_match,
                    "home_ga": home_ga_per_match,
                    "away_gf": away_gf_per_match,
                    "away_ga": away_ga_per_match,
                    "win_rate": round(win_rate, 1),
                    "home_win_rate": round(home_win_rate, 1),
                    "away_win_rate": round(away_win_rate, 1),
                    "gd_per_match": round(gd_per_match, 2),
                    "clean_sheets_prob": round(clean_sheets_est, 1),
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

st.markdown("<h2 style='text-align: center;'>⚡ EUROPE AI PREDICTOR PRO</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Modello Matematico Avanzato & Interfaccia Minimal</p>", unsafe_allow_html=True)

col_sel1, col_sel2, col_sel3 = st.columns(3)
with col_sel1:
    league_name = st.selectbox("Campionato", list(leagues_map.keys()))
    competition_code = leagues_map[league_name]

FOOTBALL_DATABASE = get_advanced_database(competition_code)

if not FOOTBALL_DATABASE:
    st.error("⚠️ Impossibile scaricare i dati.")
else:
    teams_list = sorted(list(FOOTBALL_DATABASE.keys()))

    with col_sel2:
        home_team = st.selectbox("Casa", teams_list, index=0)
    with col_sel3:
        away_team = st.selectbox("Ospite", teams_list, index=1 if len(teams_list) > 1 else 0)

    if home_team == away_team:
        st.warning("⚠️ Seleziona due squadre diverse.")
    else:
        if st.button("🚀 ESEGUI ANALISI", type="primary", use_container_width=True):
            h_data = FOOTBALL_DATABASE[home_team]
            a_data = FOOTBALL_DATABASE[away_team]
            
            # Calcolo xG con bilanciamento Casa/Trasferta e Momentum
            home_power = (h_data["home_gf"] + a_data["away_ga"]) / 2
            away_power = (a_data["away_gf"] + h_data["home_ga"]) / 2
            
            home_xg = max(0.3, home_power * h_data["form_mult"] * 1.12)
            away_xg = max(0.3, away_power * a_data["form_mult"] * 0.92)
            
            max_goals = 6
            prob_matrix = np.zeros((max_goals, max_goals))
            prob_over25 = prob_under25 = prob_gg = 0.0

            # Correzione di Dixon-Coles semplificata per calibrare lo 0-0 e l'1-1
            rho = -0.10 

            for h in range(max_goals):
                for a in range(max_goals):
                    p = poisson.pmf(h, home_xg) * poisson.pmf(a, away_xg)
                    
                    # Applicazione correzione punteggi bassi
                    if h == 0 and a == 0:
                        p *= (1 - home_xg * away_xg * rho)
                    elif h == 0 and a == 1:
                        p *= (1 + home_xg * rho)
                    elif h == 1 and a == 0:
                        p *= (1 + away_xg * rho)
                    elif h == 1 and a == 1:
                        p *= (1 - rho)
                        
                    p = max(0.0, p)
                    prob_matrix[h, a] = p
                    
                    if (h + a) > 2.5: prob_over25 += p
                    else: prob_under25 += p
                    if h > 0 and a > 0: prob_gg += p

            # Normalizzazione matrice
            total_sum = np.sum(prob_matrix)
            if total_sum > 0:
                prob_matrix /= total_sum

            home_win = float(np.sum(np.tril(prob_matrix, -1))) * 100
            draw = float(np.sum(np.diag(prob_matrix))) * 100
            away_win = float(np.sum(np.triu(prob_matrix, 1))) * 100

            prob_over25 *= 100
            prob_gg *= 100

            expected_corners = round((h_data["avg_corners"] + a_data["avg_corners"]) * 0.95, 1)
            expected_cards = round((h_data["avg_cards"] + a_data["avg_cards"]) * 0.9, 1)

            st.markdown("---")
            
            # --- BOX 1: Schedina & Esiti (Minimal & Clean) ---
            with st.container():
                st.markdown(f"#### 📊 1. Pronostici & Mercato: {home_team} vs {away_team}")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(label="Esito 1X2 Principale", value=f"1 ({round(home_win, 1)}%)", delta=f"X: {round(draw, 1)}% | 2: {round(away_win, 1)}%")
                    st.metric(label="Entrambe a Segno (Goal)", value=f"{round(prob_gg, 1)}%")
                with col2:
                    st.metric(label="Expected Goals (xG)", value=f"{round(home_xg, 2)} — {round(away_xg, 2)}")
                    st.metric(label="Linea Gol Consigliata", value="OVER 2.5" if prob_over25 > 50 else "UNDER 2.5", delta=f"{round(prob_over25, 1)}% Over")

                st.info(f"🚩 **Angoli stimati:** `{expected_corners}` &nbsp;|&nbsp; 🟨 **Cartellini stimati:** `{expected_cards}`")

            st.markdown("---")

            # --- BOX 2: Metriche di Squadra e Forma ---
            with st.container():
                st.markdown("#### 📈 2. Trend & Metriche Avanzate a Confronto")
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.markdown(f"**🏠 {home_team}**")
                    st.write(f"• Win Rate Totale: **{h_data['win_rate']}%**")
                    st.write(f"• Win Rate Casa: **{h_data['home_win_rate']}%**")
                    st.write(f"• Clean Sheet Prob: **{h_data['clean_sheets_prob']}%**")
                    st.write(f"• Forma Recente: `{h_data['form_sequence']}`")
                with col_m2:
                    st.markdown(f"**✈️ {away_team}**")
                    st.write(f"• Win Rate Totale: **{a_data['win_rate']}%**")
                    st.write(f"• Win Rate Trasferta: **{a_data['away_win_rate']}%**")
                    st.write(f"• Clean Sheet Prob: **{a_data['clean_sheets_prob']}%**")
                    st.write(f"• Forma Recente: `{a_data['form_sequence']}`")

            # --- SEZIONE EXTRA: Probabilità Marcatori con Barre ---
            with st.expander("⚽ Probabilità Goal Marcatori Chiave"):
                m_col1, m_col2 = st.columns(2)
                weights = [0.38, 0.28, 0.20, 0.14]
                
                with m_col1:
                    st.markdown(f"**{home_team}**")
                    for idx, player in enumerate(h_data["strikers"]):
                        p_score = min(round(weights[idx] * (home_xg / 1.35) * 100, 1), 85.0)
                        st.text(f"{player} ({p_score}%)")
                        st.progress(p_score / 100)
                        
                with m_col2:
                    st.markdown(f"**{away_team}**")
                    for idx, player in enumerate(a_data["strikers"]):
                        p_score = min(round(weights[idx] * (away_xg / 1.05) * 100, 1), 85.0)
                        st.text(f"{player} ({p_score}%)")
                        st.progress(p_score / 100)
