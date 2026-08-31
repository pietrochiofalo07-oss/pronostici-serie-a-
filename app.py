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
        "Inter": {"att": 90, "def": 88, "strikers": ["Lautaro Martínez", "Marcus Thuram", "Hakan Çalhanoğlu"]},
        "Juventus": {"att": 86, "def": 87, "strikers": ["Jonathan David", "Loïs Openda", "Kenan Yıldız"]},
        "Milan": {"att": 84, "def": 81, "strikers": ["Álvaro Morata", "Christian Pulisic", "Omari Hutchinson"]},
        "Atalanta": {"att": 88, "def": 80, "strikers": ["Mateo Retegui", "Ademola Lookman", "Charles De Ketelaere"]},
        "Napoli": {"att": 87, "def": 83, "strikers": ["Rasmus Højlund", "Romelu Lukaku", "Scott McTominay"]},
        "Roma": {"att": 86, "def": 84, "strikers": ["Donyell Malen", "Rodrigo Mora", "Matías Soulé"]},
        "Bologna": {"att": 80, "def": 78, "strikers": ["Artem Dovbyk", "Riccardo Orsolini", "Thijs Dallinga"]},
        "Lazio": {"att": 79, "def": 78, "strikers": ["Taty Castellanos", "Mattia Zaccagni", "Boulaye Dia"]},
        "Fiorentina": {"att": 79, "def": 77, "strikers": ["Moise Kean", "Albert Guðmundsson", "Andrea Colpani"]},
        "Torino": {"att": 73, "def": 76, "strikers": ["Duván Zapata", "Antonio Sanabria", "Nikola Vlašić"]},
        "Genoa": {"att": 71, "def": 73, "strikers": ["Andrea Pinamonti", "Vitinha", "Junior Messias"]},
        "Udinese": {"att": 72, "def": 72, "strikers": ["Lorenzo Lucca", "Florian Thauvin", "Brenner"]},
        "Parma": {"att": 71, "def": 69, "strikers": ["Ange-Yoan Bonny", "Dennis Man", "Matteo Cancellieri"]},
        "Como": {"att": 74, "def": 71, "strikers": ["Samuele Ricci", "Patrick Cutrone", "Nico Paz"]},
        "Monza": {"att": 70, "def": 72, "strikers": ["Cyril Ngonge", "Dany Mota", "Gianluca Caprari"]},
        "Verona": {"att": 69, "def": 70, "strikers": ["Casper Tengstedt", "Daniel Mosquera", "Darko Lazović"]},
        "Lecce": {"att": 66, "def": 68, "strikers": ["Nikola Krstović", "Santiago Pierotti", "Willem Geubbels"]},
        "Cagliari": {"att": 68, "def": 68, "strikers": ["Roberto Piccoli", "Zito Luvumbo", "Gianluca Lapadula"]},
        "Empoli": {"att": 67, "def": 70, "strikers": ["Lorenzo Colombo", "Sebastiano Esposito", "Emmanuel Gyasi"]},
        "Venezia": {"att": 66, "def": 66, "strikers": ["Joel Pohjanpalo", "Gaetano Oristanio", "Christian Gytkjær"]}
    },
    "Premier League": {
        "Arsenal": {"att": 90, "def": 89, "strikers": ["Bukayo Saka", "Kai Havertz", "Gabriel Martinelli"]},
        "Aston Villa": {"att": 84, "def": 80, "strikers": ["Ollie Watkins", "Leon Bailey", "Jhon Durán"]},
        "Bournemouth": {"att": 76, "def": 74, "strikers": ["Evanilson", "Antoine Semenyo", "Justin Kluivert"]},
        "Brentford": {"att": 77, "def": 73, "strikers": ["Igor Thiago", "Bryan Mbeumo", "Yoane Wissa"]},
        "Brighton": {"att": 80, "def": 76, "strikers": ["Danny Welbeck", "Kaoru Mitoma", "Evan Ferguson"]},
        "Chelsea": {"att": 85, "def": 79, "strikers": ["Cole Palmer", "Nicolas Jackson", "Noni Madueke"]},
        "Crystal Palace": {"att": 76, "def": 77, "strikers": ["Jean-Philippe Mateta", "Eberechi Eze", "Ismaïla Sarr"]},
        "Everton": {"att": 73, "def": 75, "strikers": ["Dominic Calvert-Lewin", "Beto", "Iliman Ndiaye"]},
        "Fulham": {"att": 76, "def": 75, "strikers": ["Raúl Jiménez", "Adama Traoré", "Alex Iwobi"]},
        "Ipswich Town": {"att": 68, "def": 67, "strikers": ["Liam Delap", "Omari Hutchinson", "Sammie Szmodics"]},
        "Leicester City": {"att": 72, "def": 70, "strikers": ["Jamie Vardy", "Stephy Mavididi", "Abdul Fatawu"]},
        "Liverpool": {"att": 91, "def": 85, "strikers": ["Mohamed Salah", "Darwin Núñez", "Luis Díaz"]},
        "Manchester City": {"att": 93, "def": 88, "strikers": ["Erling Haaland", "Phil Foden", "Kevin De Bruyne"]},
        "Manchester United": {"att": 82, "def": 78, "strikers": ["Joshua Zirkzee", "Marcus Rashford", "Bruno Fernandes"]},
        "Newcastle": {"att": 84, "def": 80, "strikers": ["Alexander Isak", "Nick Woltemade", "Anthony Gordon"]},
        "Nottingham Forest": {"att": 74, "def": 74, "strikers": ["Chris Wood", "Taiwo Awoniyi", "Anthony Elanga"]},
        "Southampton": {"att": 69, "def": 68, "strikers": ["Cameron Archer", "Adam Armstrong", "Ben Brereton Díaz"]},
        "Tottenham": {"att": 85, "def": 79, "strikers": ["Dejan Kulusevski", "Dominic Solanke", "Son Heung-min"]},
        "West Ham": {"att": 78, "def": 76, "strikers": ["Niclas Füllkrug", "Jarrod Bowen", "Lucas Paquetá"]},
        "Wolves": {"att": 74, "def": 73, "strikers": ["Jørgen Strand Larsen", "Matheus Cunha", "Hwang Hee-chan"]}
    },
    "LaLiga": {
        "Alavés": {"att": 70, "def": 72, "strikers": ["Kike García", "Toni Martínez", "Carlos Vicente"]},
        "Athletic Bilbao": {"att": 82, "def": 83, "strikers": ["Iñaki Williams", "Nico Williams", "Oihan Sancet"]},
        "Atlético Madrid": {"att": 87, "def": 87, "strikers": ["Julián Álvarez", "Antoine Griezmann", "Alexander Sørloth"]},
        "Barcelona": {"att": 91, "def": 83, "strikers": ["Robert Lewandowski", "Lamine Yamal", "Raphinha"]},
        "Celta Vigo": {"att": 74, "def": 72, "strikers": ["Iago Aspas", "Borja Iglesias", "Jonathan Bamba"]},
        "Espanyol": {"att": 69, "def": 70, "strikers": ["Javi Puado", "Alejo Véliz", "Walid Cheddira"]},
        "Getafe": {"att": 68, "def": 75, "strikers": ["Borja Mayoral", "Bertuğ Yıldırım", "Carles Pérez"]},
        "Girona": {"att": 80, "def": 76, "strikers": ["Bojan Miovski", "Viktor Tsygankov", "Yaser Asprilla"]},
        "Las Palmas": {"att": 70, "def": 71, "strikers": ["Oli McBurnie", "Sandro Ramírez", "Alberto Moleiro"]},
        "Leganés": {"att": 67, "def": 70, "strikers": ["Sébastien Haller", "Miguel de la Fuente", "Juan Cruz"]},
        "Mallorca": {"att": 72, "def": 74, "strikers": ["Vedat Muriqi", "Cyle Larin", "Dani Rodríguez"]},
        "Osasuna": {"att": 74, "def": 75, "strikers": ["Ante Budimir", "Bryan Zaragoza", "Moi Gómez"]},
        "Rayo Vallecano": {"att": 71, "def": 73, "strikers": ["Sergio Camello", "Raúl de Tomás", "Isi Palazón"]},
        "Real Betis": {"att": 78, "def": 78, "strikers": ["Vitor Roque", "Giovani Lo Celso", "Ezequiel Ávila"]},
        "Real Madrid": {"att": 95, "def": 89, "strikers": ["Kylian Mbappé", "Vinícius Jr.", "Jude Bellingham"]},
        "Real Sociedad": {"att": 79, "def": 80, "strikers": ["Mikel Oyarzabal", "Takefusa Kubo", "Orri Óskarsson"]},
        "Sevilla": {"att": 76, "def": 76, "strikers": ["Kelechi Iheanacho", "Isaac Romero", "Dodi Lukebakio"]},
        "Valencia": {"att": 73, "def": 74, "strikers": ["Hugo Duro", "Rafa Mir", "Diego López"]},
        "Valladolid": {"att": 67, "def": 68, "strikers": ["Mamadou Sylla", "Raúl Moro", "Kike Pérez"]},
        "Villarreal": {"att": 81, "def": 76, "strikers": ["Ayoze Pérez", "Thierno Barry", "Álex Baena"]}
    },
    "Bundesliga": {
        "Augsburg": {"att": 72, "def": 72, "strikers": ["Phillip Tietz", "Samuel Essende", "Alexis Claude-Maurice"]},
        "Bayer Leverkusen": {"att": 89, "def": 84, "strikers": ["Florian Wirtz", "Giovanni Simeone", "Patrik Schick"]},
        "Bayern Monaco": {"att": 92, "def": 85, "strikers": ["Harry Kane", "Jamal Musiala", "Michael Olise"]},
        "Bochum": {"att": 67, "def": 67, "strikers": ["Philipp Hofmann", "Myron Boadu", "Dani de Wit"]},
        "Borussia Dortmund": {"att": 86, "def": 80, "strikers": ["Serhou Guirassy", "Karim Adeyemi", "Julian Brandt"]},
        "Gladbach": {"att": 75, "def": 73, "strikers": ["Tim Kleindienst", "Alassane Pléa", "Robin Hack"]},
        "Eintracht Francoforte": {"att": 83, "def": 77, "strikers": ["Omar Marmoush", "Hugo Ekitike", "Mario Götze"]},
        "Friburgo": {"att": 76, "def": 77, "strikers": ["Junior Adamu", "Vincenzo Grifo", "Ritsu Doan"]},
        "Heidenheim": {"att": 71, "def": 71, "strikers": ["Marvin Pieringer", "Leo Scienza", "Paul Wanner"]},
        "Hoffenheim": {"att": 76, "def": 72, "strikers": ["Andrej Kramarić", "Adam Hložek", "Mergim Berisha"]},
        "Holstein Kiel": {"att": 66, "def": 65, "strikers": ["Shuto Machino", "Steven Skrzybski", "Fiete Arp"]},
        "Mainz": {"att": 72, "def": 73, "strikers": ["Jonathan Burkardt", "Nadiem Amiri", "Paul Nebel"]},
        "RB Lipsia": {"att": 85, "def": 82, "strikers": ["Benjamin Šeško", "Loïs Openda", "Xavi Simons"]},
        "St. Pauli": {"att": 67, "def": 68, "strikers": ["Johannes Eggestein", "Morgan Guilavogui", "Elias Saad"]},
        "Stoccarda": {"att": 82, "def": 78, "strikers": ["Ermedin Demirović", "Deniz Undav", "Chris Führich"]},
        "Union Berlino": {"att": 71, "def": 74, "strikers": ["Benedict Hollerbach", "Yorbe Vertessen", "Tom Rothe"]},
        "Werder Brema": {"att": 73, "def": 72, "strikers": ["Marvin Ducksch", "Keke Topp", "Mitchell Weiser"]},
        "Wolfsburg": {"att": 75, "def": 74, "strikers": ["Mohamed Amoura", "Jonas Wind", "Lovro Majer"]}
    },
    "Ligue 1": {
        "Angers": {"att": 65, "def": 66, "strikers": ["Lois Diony", "Farid El Melali", "Jim Allevinah"]},
        "Auxerre": {"att": 67, "def": 67, "strikers": ["Ado Onaiwu", "Lassine Sinayoko", "Gaëtan Perrin"]},
        "Brest": {"att": 76, "def": 76, "strikers": ["Ludovic Ajorque", "Romain Del Castillo", "Pierre Lees-Melou"]},
        "Le Havre": {"att": 66, "def": 68, "strikers": ["Emmanuel Sabbi", "Antoine Joujou", "Yassine Kechta"]},
        "Lilla": {"att": 81, "def": 80, "strikers": ["Jonathan David", "Edon Zhegrova", "Rémy Cabella"]},
        "Lione": {"att": 80, "def": 76, "strikers": ["Alexandre Lacazette", "Georges Mikautadze", "Said Benrahma"]},
        "Lens": {"att": 76, "def": 77, "strikers": ["M'Bala Nzola", "Wesley Saïd", "Florian Sotoca"]},
        "Marsiglia": {"att": 84, "def": 78, "strikers": ["Timothy Weah", "Mason Greenwood", "Elye Wahi"]},
        "Monaco": {"att": 83, "def": 79, "strikers": ["Folarin Balogun", "Breel Embolo", "Takumi Minamino"]},
        "Montpellier": {"att": 70, "def": 69, "strikers": ["Akor Adams", "Teco Savanier", "Arnaud Nordin"]},
        "Nantes": {"att": 70, "def": 71, "strikers": ["Mostafa Mohamed", "Moses Simon", "Matthis Abline"]},
        "Nizza": {"att": 78, "def": 79, "strikers": ["Youssoufa Moukoko", "Gaëtan Laborde", "Jérémie Boga"]},
        "PSG": {"att": 92, "def": 85, "strikers": ["Khvicha Kvaratskhelia", "Ousmane Dembélé", "Gonçalo Ramos"]},
        "Reims": {"att": 73, "def": 73, "strikers": ["Keito Nakamura", "Junya Ito", "Oumar Diakité"]},
        "Rennes": {"att": 77, "def": 75, "strikers": ["Arnaud Kalimuendo", "Ludovic Blas", "Albert Grønbæk"]},
        "Saint-Étienne": {"att": 67, "def": 68, "strikers": ["Ibrahim Sissoko", "Zuriko Davitashvili", "Lucas Stassin"]},
        "Strasburgo": {"att": 73, "def": 71, "strikers": ["Emanuel Emegha", "Diego Moreira", "Sebastian Nanasi"]},
        "Tolosa": {"att": 71, "def": 71, "strikers": ["Zakaria Aboukhlal", "Thijs Dallinga", "Yann Gboho"]}
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
