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
    /* Sfondo globale e font */
    .main {
        background: radial-gradient(circle at top left, #0d1117, #010409) !important;
    }
    
    /* Titolo Cyberpunk */
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

    /* Carte percentuali 1X2 Neon */
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

    /* Carte Risultati Esatti */
    .score-badge {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 4px solid #00f2fe;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
        text-align: center;
    }
    
    /* Box xG */
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

# Headings Stilizzati
st.markdown('<div class="cyber-title">⚡ EUROPE FOOTBALL AI PREDICTOR</div>', unsafe_allow_html=True)
st.markdown('<div class="cyber-subtitle">MODELLO ALGORITMICO AVANZATO • SEASON 2026/2027</div>', unsafe_allow_html=True)

FOOTBALL_DATABASE = {
    "Serie A": {
        "Inter": {"att": 91, "def": 89, "strikers": ["Lautaro Martínez", "Marcus Thuram", "Mehdi Taremi"]},
        "Juventus": {"att": 87, "def": 88, "strikers": ["Dusan Vlahovic", "Kenan Yıldız", "Francisco Conceição"]},
        "Napoli": {"att": 88, "def": 85, "strikers": ["Romelu Lukaku", "Khvicha Kvaratskhelia", "Scott McTominay"]},
        "Milan": {"att": 85, "def": 82, "strikers": ["Álvaro Morata", "Christian Pulisic", "Rafael Leão"]},
        "Atalanta": {"att": 89, "def": 81, "strikers": ["Mateo Retegui", "Ademola Lookman", "Charles De Ketelaere"]},
        "Roma": {"att": 83, "def": 82, "strikers": ["Artem Dovbyk", "Paulo Dybala", "Matías Soulé"]},
        "Lazio": {"att": 81, "def": 80, "strikers": ["Taty Castellanos", "Mattia Zaccagni", "Boulaye Dia"]},
        "Bologna": {"att": 79, "def": 79, "strikers": ["Thijs Dallinga", "Riccardo Orsolini", "Santiago Castro"]},
        "Fiorentina": {"att": 80, "def": 78, "strikers": ["Moise Kean", "Albert Guðmundsson", "Andrea Colpani"]},
        "Torino": {"att": 75, "def": 77, "strikers": ["Duván Zapata", "Antonio Sanabria", "Nikola Vlašić"]},
        "Como": {"att": 76, "def": 74, "strikers": ["Nico Paz", "Patrick Cutrone", "Andrea Belotti"]},
        "Genoa": {"att": 73, "def": 74, "strikers": ["Andrea Pinamonti", "Vitinha", "Junior Messias"]},
        "Udinese": {"att": 74, "def": 73, "strikers": ["Lorenzo Lucca", "Florian Thauvin", "Keinan Davis"]},
        "Parma": {"att": 73, "def": 71, "strikers": ["Ange-Yoan Bonny", "Dennis Man", "Matteo Cancellieri"]},
        "Monza": {"att": 71, "def": 73, "strikers": ["Milan Djuric", "Dany Mota", "Gianluca Caprari"]},
        "Verona": {"att": 70, "def": 71, "strikers": ["Casper Tengstedt", "Daniel Mosquera", "Darko Lazović"]},
        "Cagliari": {"att": 70, "def": 70, "strikers": ["Roberto Piccoli", "Zito Luvumbo", "Gianluca Lapadula"]},
        "Lecce": {"att": 68, "def": 70, "strikers": ["Nikola Krstović", "Santiago Pierotti", "Lameck Banda"]},
        "Sassuolo": {"att": 72, "def": 70, "strikers": ["Andrea Pinamonti", "Armand Laurienté", "Domenico Berardi"]},
        "Pisa": {"att": 67, "def": 68, "strikers": ["Nicholas Bonfanti", "Stefano Moreo", "Matteo Tramoni"]}
    },
    "Premier League": {
        "Manchester City": {"att": 94, "def": 89, "strikers": ["Erling Haaland", "Phil Foden", "Savinho"]},
        "Arsenal": {"att": 91, "def": 90, "strikers": ["Bukayo Saka", "Kai Havertz", "Gabriel Martinelli"]},
        "Liverpool": {"att": 92, "def": 87, "strikers": ["Mohamed Salah", "Darwin Núñez", "Luis Díaz"]},
        "Chelsea": {"att": 86, "def": 81, "strikers": ["Cole Palmer", "Nicolas Jackson", "Noni Madueke"]},
        "Aston Villa": {"att": 85, "def": 81, "strikers": ["Ollie Watkins", "Leon Bailey", "Jhon Durán"]},
        "Tottenham": {"att": 86, "def": 80, "strikers": ["Dominic Solanke", "Son Heung-min", "Dejan Kulusevski"]},
        "Newcastle": {"att": 85, "def": 82, "strikers": ["Alexander Isak", "Anthony Gordon", "Harvey Barnes"]},
        "Manchester United": {"att": 83, "def": 80, "strikers": ["Joshua Zirkzee", "Rasmus Højlund", "Marcus Rashford"]},
        "Brighton": {"att": 81, "def": 77, "strikers": ["Danny Welbeck", "Kaoru Mitoma", "Evan Ferguson"]},
        "West Ham": {"att": 80, "def": 77, "strikers": ["Niclas Füllkrug", "Jarrod Bowen", "Mohammed Kudus"]},
        "Bournemouth": {"att": 78, "def": 75, "strikers": ["Evanilson", "Antoine Semenyo", "Justin Kluivert"]},
        "Brentford": {"att": 78, "def": 74, "strikers": ["Igor Thiago", "Bryan Mbeumo", "Yoane Wissa"]},
        "Crystal Palace": {"att": 78, "def": 78, "strikers": ["Jean-Philippe Mateta", "Eberechi Eze", "Ismaïla Sarr"]},
        "Fulham": {"att": 77, "def": 76, "strikers": ["Raúl Jiménez", "Adama Traoré", "Alex Iwobi"]},
        "Nottingham Forest": {"att": 76, "def": 76, "strikers": ["Chris Wood", "Taiwo Awoniyi", "Anthony Elanga"]},
        "Everton": {"att": 74, "def": 76, "strikers": ["Dominic Calvert-Lewin", "Beto", "Iliman Ndiaye"]},
        "Wolves": {"att": 75, "def": 74, "strikers": ["Jørgen Strand Larsen", "Matheus Cunha", "Hwang Hee-chan"]},
        "Leeds United": {"att": 73, "def": 72, "strikers": ["Joel Piroe", "Wilfried Gnonto", "Dan James"]},
        "Burnley": {"att": 71, "def": 71, "strikers": ["Lyle Foster", "Zian Flemming", "Mike Trésor"]},
        "Sunderland": {"att": 70, "def": 70, "strikers": ["Wilson Isidor", "Eliezer Mayenda", "Romaine Mundle"]}
    },
    "LaLiga": {
        "Real Madrid": {"att": 96, "def": 90, "strikers": ["Kylian Mbappé", "Vinícius Jr.", "Jude Bellingham"]},
        "Barcelona": {"att": 92, "def": 84, "strikers": ["Robert Lewandowski", "Lamine Yamal", "Raphinha"]},
        "Atlético Madrid": {"att": 88, "def": 88, "strikers": ["Julián Álvarez", "Antoine Griezmann", "Alexander Sørloth"]},
        "Athletic Bilbao": {"att": 83, "def": 84, "strikers": ["Iñaki Williams", "Nico Williams", "Oihan Sancet"]},
        "Real Sociedad": {"att": 80, "def": 81, "strikers": ["Mikel Oyarzabal", "Takefusa Kubo", "Orri Óskarsson"]},
        "Villarreal": {"att": 82, "def": 77, "strikers": ["Ayoze Pérez", "Thierno Barry", "Álex Baena"]},
        "Real Betis": {"att": 80, "def": 79, "strikers": ["Vitor Roque", "Giovani Lo Celso", "Ezequiel Ávila"]},
        "Girona": {"att": 81, "def": 77, "strikers": ["Bojan Miovski", "Viktor Tsygankov", "Yaser Asprilla"]},
        "Sevilla": {"att": 77, "def": 77, "strikers": ["Kelechi Iheanacho", "Isaac Romero", "Dodi Lukebakio"]},
        "Osasuna": {"att": 75, "def": 76, "strikers": ["Ante Budimir", "Bryan Zaragoza", "Moi Gómez"]},
        "Celta Vigo": {"att": 75, "def": 73, "strikers": ["Iago Aspas", "Borja Iglesias", "Jonathan Bamba"]},
        "Valencia": {"att": 74, "def": 75, "strikers": ["Hugo Duro", "Rafa Mir", "Diego López"]},
        "Rayo Vallecano": {"att": 72, "def": 74, "strikers": ["Sergio Camello", "Raúl de Tomás", "Isi Palazón"]},
        "Mallorca": {"att": 73, "def": 75, "strikers": ["Vedat Muriqi", "Cyle Larin", "Dani Rodríguez"]},
        "Getafe": {"att": 69, "def": 76, "strikers": ["Borja Mayoral", "Bertuğ Yıldırım", "Carles Pérez"]},
        "Alavés": {"att": 71, "def": 73, "strikers": ["Kike García", "Toni Martínez", "Carlos Vicente"]},
        "Las Palmas": {"att": 71, "def": 72, "strikers": ["Oli McBurnie", "Sandro Ramírez", "Alberto Moleiro"]},
        "Espanyol": {"att": 70, "def": 71, "strikers": ["Javi Puado", "Alejo Véliz", "Walid Cheddira"]},
        "Levante": {"att": 69, "def": 69, "strikers": ["José Morales", "Iván Romero", "Carlos Álvarez"]},
        "Elche": {"att": 68, "def": 68, "strikers": ["Sory Kaba", "Mourad El Ghezouani", "Nico Fernández"]}
    },
    "Bundesliga": {
        "Bayern Monaco": {"att": 93, "def": 86, "strikers": ["Harry Kane", "Jamal Musiala", "Michael Olise"]},
        "Bayer Leverkusen": {"att": 89, "def": 85, "strikers": ["Victor Boniface", "Florian Wirtz", "Patrik Schick"]},
        "RB Lipsia": {"att": 86, "def": 83, "strikers": ["Benjamin Šeško", "Loïs Openda", "Xavi Simons"]},
        "Borussia Dortmund": {"att": 87, "def": 81, "strikers": ["Serhou Guirassy", "Karim Adeyemi", "Julian Brandt"]},
        "Eintracht Francoforte": {"att": 84, "def": 78, "strikers": ["Hugo Ekitike", "Omar Marmoush", "Mario Götze"]},
        "Stoccarda": {"att": 83, "def": 79, "strikers": ["Ermedin Demirović", "Deniz Undav", "Chris Führich"]},
        "Friburgo": {"att": 77, "def": 78, "strikers": ["Junior Adamu", "Vincenzo Grifo", "Ritsu Doan"]},
        "Gladbach": {"att": 76, "def": 74, "strikers": ["Tim Kleindienst", "Alassane Pléa", "Robin Hack"]},
        "Wolfsburg": {"att": 76, "def": 75, "strikers": ["Mohamed Amoura", "Jonas Wind", "Lovro Majer"]},
        "Hoffenheim": {"att": 77, "def": 73, "strikers": ["Andrej Kramarić", "Adam Hložek", "Mergim Berisha"]},
        "Augsburg": {"att": 73, "def": 73, "strikers": ["Phillip Tietz", "Samuel Essende", "Alexis Claude-Maurice"]},
        "Werder Brema": {"att": 74, "def": 73, "strikers": ["Marvin Ducksch", "Keke Topp", "Mitchell Weiser"]},
        "Mainz": {"att": 73, "def": 74, "strikers": ["Jonathan Burkardt", "Nadiem Amiri", "Paul Nebel"]},
        "Union Berlino": {"att": 72, "def": 75, "strikers": ["Benedict Hollerbach", "Yorbe Vertessen", "Tom Rothe"]},
        "Heidenheim": {"att": 72, "def": 72, "strikers": ["Marvin Pieringer", "Leo Scienza", "Paul Wanner"]},
        "St. Pauli": {"att": 68, "def": 69, "strikers": ["Johannes Eggestein", "Morgan Guilavogui", "Elias Saad"]},
        "Köln": {"att": 71, "def": 70, "strikers": ["Tim Lemperle", "Damion Downs", "Linton Maina"]},
        "Hamburger SV": {"att": 70, "def": 69, "strikers": ["Robert Glatzel", "Davie Selke", "Jean-Luc Dompé"]}
    },
    "Ligue 1": {
        "PSG": {"att": 91, "def": 86, "strikers": ["Ousmane Dembélé", "Bradley Barcola", "Gonçalo Ramos"]},
        "Monaco": {"att": 84, "def": 80, "strikers": ["Folarin Balogun", "Breel Embolo", "Takumi Minamino"]},
        "Marsiglia": {"att": 85, "def": 79, "strikers": ["Mason Greenwood", "Elye Wahi", "Neal Maupay"]},
        "Lilla": {"att": 82, "def": 81, "strikers": ["Jonathan David", "Edon Zhegrova", "Rémy Cabella"]},
        "Lione": {"att": 81, "def": 77, "strikers": ["Alexandre Lacazette", "Georges Mikautadze", "Malick Fofana"]},
        "Nizza": {"att": 79, "def": 80, "strikers": ["Youssoufa Moukoko", "Gaëtan Laborde", "Jérémie Boga"]},
        "Lens": {"att": 77, "def": 78, "strikers": ["M'Bala Nzola", "Wesley Saïd", "Florian Sotoca"]},
        "Rennes": {"att": 78, "def": 76, "strikers": ["Arnaud Kalimuendo", "Ludovic Blas", "Albert Grønbæk"]},
        "Brest": {"att": 77, "def": 77, "strikers": ["Ludovic Ajorque", "Romain Del Castillo", "Pierre Lees-Melou"]},
        "Strasburgo": {"att": 75, "def": 72, "strikers": ["Emanuel Emegha", "Diego Moreira", "Sebastian Nanasi"]},
        "Reims": {"att": 74, "def": 74, "strikers": ["Keito Nakamura", "Junya Ito", "Oumar Diakité"]},
        "Tolosa": {"att": 72, "def": 72, "strikers": ["Zakaria Aboukhlal", "Frank Magri", "Yann Gboho"]},
        "Nantes": {"att": 71, "def": 72, "strikers": ["Mostafa Mohamed", "Moses Simon", "Matthis Abline"]},
        "Auxerre": {"att": 68, "def": 68, "strikers": ["Ado Onaiwu", "Lassine Sinayoko", "Gaëtan Perrin"]},
        "Saint-Étienne": {"att": 68, "def": 69, "strikers": ["Ibrahim Sissoko", "Zuriko Davitashvili", "Lucas Stassin"]},
        "Le Havre": {"att": 67, "def": 69, "strikers": ["Emmanuel Sabbi", "Antoine Joujou", "Yassine Kechta"]},
        "Lorient": {"att": 70, "def": 68, "strikers": ["Bamba Dieng", "Aiyegun Tosin", "Pablo Pagis"]},
        "Paris FC": {"att": 67, "def": 67, "strikers": ["Jean-Philippe Krasso", "Nouha Dicko", "Alimami Gory"]}
    }
}

# Selettori Squadre
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
        
        for h in range(max_goals):
            for a in range(max_goals):
                p = poisson.pmf(h, home_xg) * poisson.pmf(a, away_xg)
                prob_matrix[h, a] = p
                exact_scores.append((f"{h} - {a}", p * 100))

        home_win = float(np.sum(np.tril(prob_matrix, -1))) * 100
        draw = float(np.sum(np.diag(prob_matrix))) * 100
        away_win = float(np.sum(np.triu(prob_matrix, 1))) * 100

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Schede Neon 1X2
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

        # Expected Goals Box
        st.markdown(f"""
            <div class="xg-box">
                ⚽ Expected Goals (xG) Calcolati: 
                <strong style="color: #00f2fe;">{home_team} {round(home_xg, 2)}</strong> — 
                <strong style="color: #ff007f;">{round(away_xg, 2)} {away_team}</strong>
            </div>
        """, unsafe_allow_html=True)

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

        with st.expander("📋 Tabella Completa Risultati (Tutte le Combinazioni 0-0 fino a 5-5)"):
            st.dataframe(
                np.round(prob_matrix * 100, 1),
                column_config={i: f"Ospiti: {i} gol" for i in range(max_goals)},
                use_container_width=True
            )
