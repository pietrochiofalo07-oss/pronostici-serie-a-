import streamlit as st
import numpy as np
from scipy.stats import poisson

st.set_page_config(
    page_title="Europe Football AI Predictor", 
    page_icon="⚽", 
    layout="wide"
)

# --- CSS PERSONALIZZATO PER LA GRAFICA ---
st.markdown("""
    <style>
    /* Stile generale e sfondo carte */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-title {
        color: #94a3b8;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .metric-value {
        color: #38bdf8;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .score-card {
        background: #1e293b;
        border-left: 4px solid #38bdf8;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚽ Europe Football AI Predictor Pro")
st.caption("Modello di analisi predittiva avanzato | Stagione 2026/2027")

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

# --- SELEZIONE COMPETIZIONE E SQUADRE ---
league = st.selectbox("🌍 Campionato", list(FOOTBALL_DATABASE.keys()))
teams_list = sorted(list(FOOTBALL_DATABASE[league].keys()))

c1, c2 = st.columns(2)
with c1:
    home_team = st.selectbox("🏠 Squadra Casa (1)", teams_list, index=0)
with c2:
    away_team = st.selectbox("✈️ Squadra Trasferta (2)", teams_list, index=1 if len(teams_list) > 1 else 0)

if home_team == away_team:
    st.warning("⚠️ Seleziona due squadre diverse per procedere.")
else:
    if st.button("⚡ Genera Analisi & Pronostico", type="primary", use_container_width=True):
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
        st.subheader(f"📊 Probabilità 1X2 | {home_team} vs {away_team}")
        
        # Schede grafiche 1X2
        col_1, col_x, col_2 = st.columns(3)
        with col_1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">VITTORIA CASA (1)</div>
                    <div class="metric-value">{round(home_win, 1)}%</div>
                </div>
            """, unsafe_allow_html=True)
        with col_x:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">PAREGGIO (X)</div>
                    <div class="metric-value">{round(draw, 1)}%</div>
                </div>
            """, unsafe_allow_html=True)
        with col_2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">VITTORIA TRASFERTA (2)</div>
                    <div class="metric-value">{round(away_win, 1)}%</div>
                </div>
            """, unsafe_allow_html=True)

        st.info(f"⚽ **Expected Goals (xG Stimati):** {home_team} **{round(home_xg, 2)}** — **{round(away_xg, 2)}** {away_team}")

        st.markdown("---")
        
        # Risultati Esatti Top 5 Stilizzati
        st.subheader("🎯 Risultati Esatti Più Probabili")
        exact_scores.sort(key=lambda x: x[1], reverse=True)
        top5 = exact_scores[:5]
        
        res_cols = st.columns(5)
        for idx, (score, prob) in enumerate(top5):
            with res_cols[idx]:
                st.markdown(f"""
                    <div class="score-card">
                        <span style="color: #94a3b8; font-size: 0.8rem;"># {idx+1} Opzione</span><br>
                        <strong style="color: #f8fafc; font-size: 1.3rem;">{score}</strong><br>
                        <span style="color: #38bdf8; font-weight: bold;">{round(prob, 1)}%</span>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        
        # Marcatori con Barre di Progresso Visuali
        st.subheader("⚽ Probabilità Marcatori")
        m_col1, m_col2 = st.columns(2)
        weights = [0.44, 0.32, 0.22]
        
        with m_col1:
            st.write(f"**Marcatori {home_team}:**")
            for idx, player in enumerate(h_data["strikers"]):
                prob_scorer = min(round(weights[idx] * (home_xg / 1.35) * 100, 1), 82.0)
                st.write(f"👤 **{player}** ({prob_scorer}%)")
                st.progress(prob_scorer / 100)
                
        with m_col2:
            st.write(f"**Marcatori {away_team}:**")
            for idx, player in enumerate(a_data["strikers"]):
                prob_scorer = min(round(weights[idx] * (away_xg / 1.05) * 100, 1), 82.0)
                st.write(f"👤 **{player}** ({prob_scorer}%)")
                st.progress(prob_scorer / 100)

        # Tabella completa espandibile
        with st.expander("📋 Mostra Matrice Completa di Tutti i Punteggi Possibili"):
            st.dataframe(
                np.round(prob_matrix * 100, 1),
                column_config={i: f"Ospiti: {i} gol" for i in range(max_goals)},
                use_container_width=True
            )
