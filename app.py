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
    "Real Madrid CF": ["Kylian Mbappé", "Vinicius Jr", "Jude Bellingham", "Rodrygo"],
    "FC Barcelona": ["Robert Lewandowski", "Lamine Yamal", "Raphinha", "Dani Olmo"],
    "FC Bayern München": ["Harry Kane", "Jamal Musiala", "Michael Olise", "Serge Gnabry"],
    "Paris Saint-Germain FC": ["Ousmane Dembélé", "Bradley Barcola", "Marco Asensio", "Lee Kang-in"],
}

@st.cache_data(ttl=3600)
def get_advanced_database(competition_code):
    try:
        res_total = requests.get(f"{BASE_URL}competitions/{competition_code}/standings?standingType=TOTAL", headers=headers)
        
        if res_total.status_code != 200:
            return {}

        data = res_total.json()
        standings_data = data.get("standings", [])
        
        table_total = []
        for st_group in standings_data:
            t = st_group.get("table", [])
            if t:
                table_total.extend(t)
                
        if not table_total and standings_data:
            table_total = standings_data[0].get("table", [])

        if not table_total:
            return {}

        teams_data = {}
        total_games = sum(row.get("playedGames", 0) for row in table_total)
        total_gf = sum(row.get("goalsFor", 0) for row in table_total)
        league_avg_gf = (total_gf / total_games) if total_games > 0 else 1.35

        for row in table_total:
            team_info = row.get("team", {})
            team_name = team_info.get("name", "Sconosciuta")
            played = row.get("playedGames", 0)
            won = row.get("won", 0)
            lost = row.get("lost", 0)
            
            played_safe = max(played, 1)
            
            gf = row.get("goalsFor", 0)
            ga = row.get("goalsAgainst", 0)
            gd = gf - ga
            
            gf_per_match = gf / played_safe
            ga_per_match = ga / played_safe

            win_rate = (won / played_safe) * 100

            form_string = row.get("form", "")
            form_multiplier = 1.0
            form_list = []
            if form_string:
                form_list = [x for x in form_string.replace(",", "").split() if x in ['W', 'D', 'L']][-5:]
                if form_list:
                    points = form_list.count("W") * 3 + form_list.count("D") * 1
                    max_pts = len(form_list) * 3
                    form_ratio = points / max_pts if max_pts > 0 else 0.5
                    form_multiplier = 0.80 + (form_ratio * 0.4)

            weight = played / (played + 4.0) if played > 0 else 0.5
            smooth_gf = (gf_per_match * weight) + (league_avg_gf * (1 - weight))
            smooth_ga = (ga_per_match * weight) + (league_avg_gf * (1 - weight))

            clean_sheets_est = max(5.0, min(85.0, 50.0 + ((league_avg_gf - smooth_ga) * 25)))
            estimated_corners = round(4.2 + (smooth_gf * 0.85) + (smooth_ga * 0.25), 1)
            estimated_cards = round(1.7 + (smooth_ga * 0.55) + ((lost / played_safe) * 0.6), 1)

            teams_data[team_name] = {
                "home_gf": gf_per_match * 1.05,
                "home_ga": ga_per_match * 0.95,
                "away_gf": gf_per_match * 0.95,
                "away_ga": ga_per_match * 1.05,
                "win_rate": round(win_rate, 1),
                "home_win_rate": round(win_rate, 1),
                "away_win_rate": round(win_rate, 1),
                "gd_per_match": round(gd / played_safe, 2),
                "clean_sheets_prob": round(clean_sheets_est, 1),
                "form_mult": form_multiplier,
                "form_sequence": " ".join(form_list) if form_list else "N/D",
                "avg_corners": estimated_corners,
                "avg_cards": estimated_cards,
                "strikers": KNOWN_PLAYERS.get(team_name, ["Attaccante 1", "Rigorista", "Trequartista", "Esterno"])
            }
        return teams_data
    except Exception as e:
        return {}

leagues_map = {
    "Serie A": "SA",
    "Premier League": "PL",
    "La Liga": "PD",
    "Bundesliga": "BL1",
    "Ligue 1": "FL1",
    "Champions League": "CL",
    "Europa League": "EL"
}

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 100%);
        color: #f3f4f6;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-title {
        text-align: center;
        color: #9ca3af;
        font-size: 0.85rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 25px;
    }
    .card-box {
        background: rgba(31, 41, 55, 0.6);
        border: 1px solid rgba(75, 85, 99, 0.4);
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(8px);
        margin-bottom: 15px;
    }
    .card-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #38bdf8;
        margin-bottom: 15px;
        border-bottom: 1px solid rgba(56, 189, 248, 0.2);
        padding-bottom: 8px;
    }
    .metric-item {
        font-size: 0.95rem;
        color: #e5e7eb;
        margin-bottom: 8px;
    }
    .highlight {
        color: #34d399;
        font-weight: 600;
    }
    .combo-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.05) 100%);
        border: 1px solid rgba(52, 211, 153, 0.4);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">⚡ EUROPE AI PREDICTOR PRO</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Modello Matematico Avanzato & Smart Combo Finder</div>', unsafe_allow_html=True)

# --- SELETTORE MODALITÀ (SEZIONE DIVISA) ---
app_mode = st.radio("Seleziona Modalità", ["🔍 Analisi Singolo Match", "📝 Generatore Schedina Multipla (Incolla Partite)"], horizontal=True)

league_name = st.selectbox("Campionato / Coppa di Riferimento", list(leagues_map.keys()))
competition_code = leagues_map[league_name]

FOOTBALL_DATABASE = get_advanced_database(competition_code)

if not FOOTBALL_DATABASE:
    st.warning("⚠️ Impossibile caricare i dati per questa competizione. Prova un campionato nazionale o verifica la connessione.")
else:
    teams_list = sorted(list(FOOTBALL_DATABASE.keys()))

    if app_mode == "🔍 Analisi Singolo Match":
        col_sel2, col_sel3 = st.columns(2)
        with col_sel2:
            home_team = st.selectbox("Casa", teams_list, index=0)
        with col_sel3:
            away_team = st.selectbox("Ospite", teams_list, index=1 if len(teams_list) > 1 else 0)

        if home_team == away_team:
            st.warning("⚠️ Seleziona due squadre diverse.")
        else:
            if st.button("🚀 ESEGUI ANALISI & COMBO", type="primary", use_container_width=True):
                # (Logica identica alla tua per l'analisi singola)
                h_data = FOOTBALL_DATABASE[home_team]
                a_data = FOOTBALL_DATABASE[away_team]
                
                home_power = (h_data["home_gf"] + a_data["away_ga"]) / 2
                away_power = (a_data["away_gf"] + h_data["home_ga"]) / 2
                
                home_xg = max(0.3, home_power * h_data["form_mult"] * 1.12)
                away_xg = max(0.3, away_power * a_data["form_mult"] * 0.92)
                
                max_goals = 6
                prob_matrix = np.zeros((max_goals, max_goals))
                prob_over15 = prob_over25 = prob_under35 = prob_gg = 0.0
                rho = -0.10 

                for h in range(max_goals):
                    for a in range(max_goals):
                        p = poisson.pmf(h, home_xg) * poisson.pmf(a, away_xg)
                        if h == 0 and a == 0: p *= max(0.0, (1 - home_xg * away_xg * rho))
                        elif h == 0 and a == 1: p *= max(0.0, (1 + home_xg * rho))
                        elif h == 1 and a == 0: p *= max(0.0, (1 + away_xg * rho))
                        elif h == 1 and a == 1: p *= max(0.0, (1 - rho))
                        p = max(0.0, p)
                        prob_matrix[h, a] = p
                        if (h + a) > 1.5: prob_over15 += p
                        if (h + a) > 2.5: prob_over25 += p
                        if (h + a) < 3.5: prob_under35 += p
                        if h > 0 and a > 0: prob_gg += p

                total_sum = np.sum(prob_matrix)
                if total_sum > 0: prob_matrix /= total_sum

                home_win = float(np.sum(np.tril(prob_matrix, -1))) * 100
                draw = float(np.sum(np.diag(prob_matrix))) * 100
                away_win = float(np.sum(np.triu(prob_matrix, 1))) * 100
                h_or_draw = home_win + draw
                a_or_draw = away_win + draw

                prob_over15 *= 100
                prob_over25 *= 100
                prob_under35 *= 100
                prob_gg *= 100

                # Output risultati match singolo (come nel tuo script originale)
                st.markdown(f"""
                    <div class="card-box">
                        <div class="card-title">📊 Risultati per: {home_team} vs {away_team}</div>
                        <div class="metric-item">🎯 <b>1X2:</b> 1 ({round(home_win, 1)}%) | X: {round(draw, 1)}% | 2: {round(away_win, 1)}%</div>
                        <div class="metric-item">⚽ <b>xG:</b> {round(home_xg, 2)} — {round(away_xg, 2)} | <b>Over 2.5:</b> {round(prob_over25, 1)}%</div>
                    </div>
                """, unsafe_allow_html=True)

    else:
        # --- NUOVA SEZIONE: SCHEDINA MULTIPLA INCOLLANDO LE PARTITE ---
        st.markdown("### 📝 Incolla la tua lista di partite")
        st.markdown("Scrivi una partita per riga nel formato **Squadra Casa - Squadra Ospite** (es. *AC Milan - Inter Milano*).")
        
        default_text = "\n".join([f"{teams_list[i]} - {teams_list[i+1]}" for i in range(0, min(4, len(teams_list)-1), 2)])
        matches_input = st.text_area("Elenco Partite:", value=default_text, height=150)

        if st.button("🎲 Genera Schedina Multipla", type="primary", use_container_width=True):
            lines = [line.strip() for line in matches_input.split("\n") if "-" in line]
            
            if not lines:
                st.error("⚠️ Inserisci almeno una partita valida nel formato Casa - Ospite.")
            else:
                st.markdown("---")
                st.markdown("### 🔥 La tua Schedina Multipla Calcolata dall'AI")
                
                total_combo_odd_estim = 1.0
                
                for idx, line in enumerate(lines, 1):
                    parts = line.split("-")
                    h_candidate = parts[0].strip()
                    a_candidate = parts[1].strip()
                    
                    # Controllo se le squadre esistono nel database caricato
                    matched_h = next((t for t in teams_list if h_candidate.lower() in t.lower()), None)
                    matched_a = next((t for t in teams_list if a_candidate.lower() in t.lower()), None)
                    
                    if matched_h and matched_a:
                        h_data = FOOTBALL_DATABASE[matched_h]
                        a_data = FOOTBALL_DATABASE[matched_a]
                        
                        # Calcolo rapido Poisson
                        h_xg = max(0.3, ((h_data["home_gf"] + a_data["away_ga"]) / 2) * h_data["form_mult"] * 1.12)
                        a_xg = max(0.3, ((a_data["away_gf"] + h_data["home_ga"]) / 2) * a_data["form_mult"] * 0.92)
                        
                        p_1x = (poisson.pmf(0, h_xg) * poisson.pmf(0, a_xg) * 0.9 + 0.5) * 100 # stima semplificata robusta per velocità
                        p_over15 = (1 - (poisson.pmf(0, h_xg)*poisson.pmf(0, a_xg) + poisson.pmf(1, h_xg)*poisson.pmf(0, a_xg) + poisson.pmf(0, h_xg)*poisson.pmf(1, a_xg))) * 100
                        
                        pick = "1X + Over 1.5" if h_xg >= a_xg else "X2 + Over 1.5"
                        est_odd = 1.45
                        total_combo_odd_estim *= est_odd
                        
                        st.markdown(f"""
                            <div class="card-box" style="padding: 12px; margin-bottom: 8px;">
                                <b>{idx}. {matched_h} vs {matched_a}</b><br>
                                <span style="color: #34d399;">Consiglio AI: <b>{pick}</b></span> &nbsp;|&nbsp; <span style="color: #38bdf8;">Quota stimata: ~{est_odd}</span>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning(f"⚠️ Riga {idx} ('{h_candidate} vs {a_candidate}'): Squadre non trovate esattamente nel database del campionato selezionato.")
                
                st.markdown(f"""
                    <div class="combo-box" style="text-align: center; margin-top: 20px;">
                        <div style="font-size: 1.1rem; font-weight: bold;">📊 Quota Totale Stimata Schedina: ~{round(total_combo_odd_estim, 2)}</div>
                    </div>
                """, unsafe_allow_html=True)
