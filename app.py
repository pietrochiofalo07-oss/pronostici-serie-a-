import streamlit as st
import requests
import numpy as np
from scipy.stats import poisson

st.set_page_config(
    page_title="EUROPE AI PREDICTOR PRO", 
    page_icon="⚡", 
    layout="wide"
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
    except Exception:
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

# --- CUSTOM CSS & DESIGN SYSTEM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0f172a 50%, #020617 100%);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }

    /* Header Styling */
    .hero-container {
        padding: 2rem 1rem;
        text-align: center;
        background: linear-gradient(180deg, rgba(30, 27, 75, 0.4) 0%, rgba(15, 23, 42, 0) 100%);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 2rem;
        border-radius: 0 0 24px 24px;
    }
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.025em;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #94a3b8;
        font-size: 0.9rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 600;
    }

    /* Glassmorphic Cards */
    .card-box {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(16px);
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .card-box:hover {
        border-color: rgba(56, 189, 248, 0.3);
    }
    .card-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #38bdf8;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 8px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        padding-bottom: 10px;
    }

    /* Special AI Combo Box */
    .combo-box {
        background: linear-gradient(135deg, rgba(6, 95, 70, 0.4) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(52, 211, 153, 0.4);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 30px -10px rgba(5, 150, 105, 0.2);
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
    }
    .combo-box::before {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 4px; height: 100%;
        background: #34d399;
    }

    /* Metric Item Styling */
    .metric-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        font-size: 0.95rem;
    }
    .metric-row:last-child {
        border-bottom: none;
    }
    .highlight-green {
        color: #34d399;
        font-weight: 600;
    }
    .highlight-blue {
        color: #38bdf8;
        font-weight: 600;
    }
    
    /* Form Badge Styling */
    .form-badge {
        font-family: monospace;
        background: rgba(15, 23, 42, 0.6);
        padding: 4px 8px;
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #34d399;
        letter-spacing: 2px;
    }

    /* Hide Streamlit Branding elements for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- HERO HEADER ---
st.markdown("""
    <div class="hero-container">
        <div class="main-title">⚡ EUROPE AI PREDICTOR PRO</div>
        <div class="sub-title">Advanced Poisson Matrix & Smart Value Finder</div>
    </div>
""", unsafe_allow_html=True)

# Selection Controls inside a sleek container
with st.container():
    col_sel1, col_sel2, col_sel3 = st.columns(3)
    with col_sel1:
        league_name = st.selectbox("🏆 Campionato / Coppa", list(leagues_map.keys()))
        competition_code = leagues_map[league_name]

    FOOTBALL_DATABASE = get_advanced_database(competition_code)

    if not FOOTBALL_DATABASE:
        st.warning("⚠️ Impossibile caricare i dati per questa competizione (potrebbe essere tra una fase e l'altra o non disporre di classifica attiva al momento). Prova un campionato nazionale o verifica la connessione.")
    else:
        teams_list = sorted(list(FOOTBALL_DATABASE.keys()))

        with col_sel2:
            home_team = st.selectbox("🏠 Squadra di Casa", teams_list, index=0)
        with col_sel3:
            away_team = st.selectbox("✈️ Squadra Ospite", teams_list, index=1 if len(teams_list) > 1 else 0)

        st.markdown("<div style='margin: 15px 0;'></div>", unsafe_allow_html=True)

        if home_team == away_team:
            st.warning("⚠️ Seleziona due squadre diverse per procedere con l'analisi.")
        else:
            if st.button("🚀 ESEGUI ANALISI PREDITTIVA", type="primary", use_container_width=True):
                h_data = FOOTBALL_DATABASE.get(home_team, {"home_gf": 1.2, "home_ga": 1.0, "form_mult": 1.0, "win_rate": 50.0, "clean_sheets_prob": 30.0, "form_sequence": "N/D", "avg_corners": 4.5, "avg_cards": 2.0, "strikers": ["Attaccante 1"]})
                a_data = FOOTBALL_DATABASE.get(away_team, {"away_gf": 1.1, "away_ga": 1.1, "form_mult": 1.0, "win_rate": 40.0, "clean_sheets_prob": 25.0, "form_sequence": "N/D", "avg_corners": 4.0, "avg_cards": 2.2, "strikers": ["Attaccante 1"]})
                
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
                        
                        if h == 0 and a == 0:
                            p *= max(0.0, (1 - home_xg * away_xg * rho))
                        elif h == 0 and a == 1:
                            p *= max(0.0, (1 + home_xg * rho))
                        elif h == 1 and a == 0:
                            p *= max(0.0, (1 + away_xg * rho))
                        elif h == 1 and a == 1:
                            p *= max(0.0, (1 - rho))
                            
                        p = max(0.0, p)
                        prob_matrix[h, a] = p
                        
                        if (h + a) > 1.5: prob_over15 += p
                        if (h + a) > 2.5: prob_over25 += p
                        if (h + a) < 3.5: prob_under35 += p
                        if h > 0 and a > 0: prob_gg += p

                total_sum = np.sum(prob_matrix)
                if total_sum > 0:
                    prob_matrix /= total_sum

                home_win = float(np.sum(np.tril(prob_matrix, -1))) * 100
                draw = float(np.sum(np.diag(prob_matrix))) * 100
                away_win = float(np.sum(np.triu(prob_matrix, 1))) * 100
                h_or_draw = home_win + draw
                a_or_draw = away_win + draw

                prob_over15 *= 100
                prob_over25 *= 100
                prob_under35 *= 100
                prob_gg *= 100

                expected_corners = round((h_data["avg_corners"] + a_data["avg_corners"]) * 0.95, 1)
                expected_cards = round((h_data["avg_cards"] + a_data["avg_cards"]) * 0.9, 1)

                # --- MOTORE DI SCELTA SMART COMBO ---
                combos = []
                
                if abs(home_win - away_win) < 15.0 or (home_win < 45 and away_win < 40):
                    combos.append(("1X + Under 3.5", h_or_draw * (prob_under35/100), 1.45))
                    combos.append(("1X + Over 1.5", h_or_draw * (prob_over15/100), 1.50))
                    combos.append(("X2 + Over 1.5", a_or_draw * (prob_over15/100), 1.60))
                    if prob_gg > 50:
                        combos.append(("1X + Goal", h_or_draw * (prob_gg/100), 1.85))
                else:
                    if home_win > 45:
                        combos.append(("1 + Over 1.5", home_win * (prob_over15/100), 1.65))
                        combos.append(("1X + Under 3.5", h_or_draw * (prob_under35/100), 1.45))
                    elif away_win > 40:
                        combos.append(("2 + Over 1.5", away_win * (prob_over15/100), 1.85))
                        combos.append(("X2 + Over 1.5", a_or_draw * (prob_over15/100), 1.50))
                    else:
                        combos.append(("1X + Over 1.5", h_or_draw * (prob_over15/100), 1.40))
                        
                if prob_gg > 55 and not any("Goal" in c[0] for c in combos):
                    combos.append(("Goal + Over 2.5", prob_gg * (prob_over25/100), 2.10))
                
                best_combo = max(combos, key=lambda x: x[1]) if combos else ("1X + Over 1.5", 70.0, 1.45)

                st.markdown("<br>", unsafe_allow_html=True)
                
                # --- BOX SPECIALE: LA COMBO CONSIGLIATA ---
                st.markdown(f"""
                    <div class="combo-box">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 0.9rem; font-weight: 800; color: #34d399; letter-spacing: 1px;">🔥 TOP AI COMBO SELECTION</span>
                            <span style="background: rgba(52, 211, 153, 0.15); color: #34d399; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">Quota stimata: ~{best_combo[2]}</span>
                        </div>
                        <div style="font-size: 1.6rem; font-weight: 800; color: #ffffff; margin-bottom: 8px;">{best_combo[0]}</div>
                        <div style="font-size: 0.9rem; color: #cbd5e1;">
                            Affidabilità stimata dal modello di Poisson: <b style="color: #38bdf8;">{round(best_combo[1], 1)}%</b>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # --- BOX 1: Schedina & Esiti ---
                st.markdown(f"""
                    <div class="card-box">
                        <div class="card-title">📊 Analisi di Mercato & Quote Implicite: {home_team} vs {away_team}</div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
                            <div>
                                <div class="metric-row">
                                    <span>🎯 1X2 Probabilities</span>
                                    <span class="highlight-green">1: {round(home_win, 1)}% | X: {round(draw, 1)}% | 2: {round(away_win, 1)}%</span>
                                </div>
                                <div class="metric-row">
                                    <span>🥅 Entrambe a Segno (Goal)</span>
                                    <span class="highlight-blue">{round(prob_gg, 1)}%</span>
                                </div>
                            </div>
                            <div>
                                <div class="metric-row">
                                    <span>⚽ Expected Goals (xG)</span>
                                    <span class="highlight-blue">{round(home_xg, 2)} — {round(away_xg, 2)}</span>
                                </div>
                                <div class="metric-row">
                                    <span>📈 Linea Gol Consigliata</span>
                                    <span class="highlight-green">{'OVER 2.5' if prob_over25 > 50 else 'UNDER 2.5'} ({round(prob_over25, 1)}%)</span>
                                </div>
                            </div>
                        </div>
                        <div style="margin-top: 18px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.06); display: flex; justify-content: space-around; font-size: 0.9rem; color: #94a3b8;">
                            <span>🚩 <b>Angoli Stimati:</b> {expected_corners}</span>
                            <span>•</span>
                            <span>🟨 <b>Cartellini Stimati:</b> {expected_cards}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # --- SEZIONE RISULTATI ESATTI ---
                with st.expander("🎯 I 4 Risultati Esatti più Probabili"):
                    score_list = []
                    for h in range(max_goals):
                        for a in range(max_goals):
                            score_list.append((f"{h} - {a}", prob_matrix[h, a] * 100))
                    
                    score_list.sort(key=lambda x: x[1], reverse=True)
                    top_scores = score_list[:4]
                    
                    sc_cols = st.columns(4)
                    for idx, (sc_val, sc_prob) in enumerate(top_scores):
                        with sc_cols[idx]:
                            st.markdown(f"""
                                <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 12px; padding: 16px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                                    <div style="font-size: 1.3rem; font-weight: 800; color: #38bdf8;">{sc_val}</div>
                                    <div style="font-size: 0.9rem; color: #34d399; margin-top: 6px; font-weight: 600;">{round(sc_prob, 1)}%</div>
                                </div>
                            """, unsafe_allow_html=True)

                # --- BOX 2: Metriche di Squadra e Forma ---
                st.markdown(f"""
                    <div class="card-box">
                        <div class="card-title">📈 Trend & Metriche Avanzate a Confronto</div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
                            <div>
                                <div style="font-weight: 700; color: #38bdf8; margin-bottom: 12px; font-size: 1rem;">🏠 {home_team}</div>
                                <div class="metric-row"><span>Win Rate</span> <b>{h_data['win_rate']}%</b></div>
                                <div class="metric-row"><span>Clean Sheet Prob.</span> <b>{h_data['clean_sheets_prob']}%</b></div>
                                <div class="metric-row"><span>Ultime 5 Partite</span> <span class="form-badge">{h_data['form_sequence']}</span></div>
                            </div>
                            <div>
                                <div style="font-weight: 700; color: #c084fc; margin-bottom: 12px; font-size: 1rem;">✈️ {away_team}</div>
                                <div class="metric-row"><span>Win Rate</span> <b>{a_data['win_rate']}%</b></div>
                                <div class="metric-row"><span>Clean Sheet Prob.</span> <b>{a_data['clean_sheets_prob']}%</b></div>
                                <div class="metric-row"><span>Ultime 5 Partite</span> <span class="form-badge">{a_data['form_sequence']}</span></div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # --- SEZIONE MARCATORI ---
                with st.expander("⚽ Probabilità Goal Marcatori Chiave"):
                    m_col1, m_col2 = st.columns(2)
                    weights = [0.38, 0.28, 0.20, 0.14]
                    
                    with m_col1:
                        st.markdown(f"<p style='color: #38bdf8; font-weight: 700;'>{home_team}</p>", unsafe_allow_html=True)
                        for idx, player in enumerate(h_data["strikers"]):
                            p_score = min(round(weights[idx] * (home_xg / 1.35) * 100, 1), 85.0)
                            st.text(f"{player} ({p_score}%)")
                            st.progress(p_score / 100)
                            
                    with m_col2:
                        st.markdown(f"<p style='color: #c084fc; font-weight: 700;'>{away_team}</p>", unsafe_allow_html=True)
                        for idx, player in enumerate(a_data["strikers"]):
                            p_score = min(round(weights[idx] * (away_xg / 1.05) * 100, 1), 85.0)
                            st.text(f"{player} ({p_score}%)")
                            st.progress(p_score / 100)
