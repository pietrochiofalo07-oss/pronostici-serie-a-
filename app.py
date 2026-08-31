import streamlit as st
import numpy as np
from scipy.stats import poisson

st.set_page_config(
    page_title="EUROPE AI PREDICTOR 2027", 
    page_icon="⚡", 
    layout="wide"
)

# --- CSS ORDINATO & PULITO ---
st.markdown("""
    <style>
    .main {
        background: radial-gradient(circle at top left, #0d1117, #010409) !important;
    }
    
    .cyber-title {
        font-family: 'Segoe UI', Roboto, sans-serif;
        font-size: 2.4rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 50%, #00c6ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(0, 242, 254, 0.3);
        margin-bottom: 5px;
    }
    
    .cyber-subtitle {
        text-align: center;
        color: #8b949e;
        font-size: 0.9rem;
        margin-bottom: 25px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .neon-card {
        background: rgba(22, 27, 34, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 14px;
        padding: 18px 10px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .neon-card-1 { border: 1px solid #00f2fe; }
    .neon-card-x { border: 1px solid #ffb703; }
    .neon-card-2 { border: 1px solid #ff007f; }

    .neon-label {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1px;
        color: #8b949e;
        margin-bottom: 6px;
    }
    
    .neon-val-1 { color: #00f2fe; font-size: 1.8rem; font-weight: 900; }
    .neon-val-x { color: #ffb703; font-size: 1.8rem; font-weight: 900; }
    .neon-val-2 { color: #ff007f; font-size: 1.8rem; font-weight: 900; }

    .stat-box {
        background: rgba(22, 27, 34, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        margin-bottom: 8px;
    }
    
    .xg-box {
        background: linear-gradient(90deg, rgba(0,242,254,0.08) 0%, rgba(255,0,127,0.08) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        font-size: 1rem;
        color: #f0f6fc;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="cyber-title">⚡ EUROPE FOOTBALL AI PREDICTOR</div>', unsafe_allow_html=True)
st.markdown('<div class="cyber-subtitle">MODELLO POTENZIATO TOP ROSE • EUROPEAN LEAGUES 2026/2027</div>', unsafe_allow_html=True)

FOOTBALL_DATABASE = {
    "Serie A": {
        "Atalanta": {"att": 91, "def": 86, "strikers": ["De Ketelaere", "Scamacca", "Retegui", "Lookman"]},
        "Bologna": {"att": 84, "def": 83, "strikers": ["Orsolini", "Ndoye", "Castro", "Dallinga"]},
        "Cagliari": {"att": 76, "def": 75, "strikers": ["Luvumbo", "Piccoli", "Lapadula", "Viola"]},
        "Como": {"att": 81, "def": 79, "strikers": ["Strefezza", "Belotti", "Cutrone", "Nico Paz"]},
        "Fiorentina": {"att": 85, "def": 82, "strikers": ["Gudmundsson", "Kean", "Colpani", "Beltrán"]},
        "Frosinone": {"att": 75, "def": 75, "strikers": ["Birligea", "Kvernadze", "Ambrosino"]},
        "Genoa": {"att": 78, "def": 78, "strikers": ["Malinovskyi", "Messias", "Pinamonti", "Vitinha"]},
        "Inter": {"att": 95, "def": 93, "strikers": ["Lautaro Martínez", "Thuram", "Taremi", "Calhanoglu"]},
        "Juventus": {"att": 92, "def": 91, "strikers": ["Yildiz", "Vlahović", "Koopmeiners", "Conceição"]},
        "Lazio": {"att": 86, "def": 84, "strikers": ["Zaccagni", "Noslin", "Dia", "Castellanos"]},
        "Lecce": {"att": 74, "def": 75, "strikers": ["Rebic", "Krstovic", "Banda"]},
        "Milan": {"att": 90, "def": 86, "strikers": ["Pulisic", "Leão", "Morata", "Abraham"]},
        "Monza": {"att": 77, "def": 77, "strikers": ["Maldini", "Mota", "Djuric", "Caprari"]},
        "Napoli": {"att": 93, "def": 89, "strikers": ["Kvaratskhelia", "Politano", "Lukaku", "Neres"]},
        "Parma": {"att": 78, "def": 75, "strikers": ["Man", "Mihaila", "Bonny", "Charpentier"]},
        "Roma": {"att": 89, "def": 87, "strikers": ["Soulé", "Dybala", "Dovbyk", "El Shaarawy"]},
        "Sassuolo": {"att": 77, "def": 75, "strikers": ["Laurienté", "Moro", "Mulattieri", "Berardi"]},
        "Torino": {"att": 80, "def": 81, "strikers": ["Vlasic", "Adams", "Sanabria", "Zapata"]},
        "Udinese": {"att": 79, "def": 77, "strikers": ["Thauvin", "Brenner", "Lucca", "Davis"]},
        "Venezia": {"att": 74, "def": 73, "strikers": ["Oristanio", "Pohjanpalo", "Ellertsson"]}
    },
    "Premier League": {
        "Arsenal": {"att": 95, "def": 94, "strikers": ["Bukayo Saka", "Kai Havertz", "Gabriel Martinelli", "Gabriel Jesus"]},
        "Aston Villa": {"att": 88, "def": 85, "strikers": ["Ollie Watkins", "Leon Bailey", "Morgan Rogers", "Jhon Durán"]},
        "Bournemouth": {"att": 81, "def": 80, "strikers": ["Evanilson", "Antoine Semenyo", "Justin Kluivert"]},
        "Brentford": {"att": 82, "def": 79, "strikers": ["Igor Thiago", "Bryan Mbeumo", "Yoane Wissa"]},
        "Brighton": {"att": 85, "def": 82, "strikers": ["Danny Welbeck", "Kaoru Mitoma", "Evan Ferguson", "João Pedro"]},
        "Chelsea": {"att": 91, "def": 86, "strikers": ["Cole Palmer", "Nicolas Jackson", "Christopher Nkunku", "Pedro Neto"]},
        "Crystal Palace": {"att": 82, "def": 82, "strikers": ["Jean-Philippe Mateta", "Eberechi Eze", "Ismaïla Sarr"]},
        "Everton": {"att": 79, "def": 80, "strikers": ["Dominic Calvert-Lewin", "Beto", "Iliman Ndiaye"]},
        "Fulham": {"att": 81, "def": 80, "strikers": ["Raúl Jiménez", "Adama Traoré", "Alex Iwobi", "Emile Smith Rowe"]},
        "Ipswich Town": {"att": 75, "def": 74, "strikers": ["Liam Delap", "Omari Hutchinson", "Sammie Szmodics"]},
        "Leeds United": {"att": 78, "def": 77, "strikers": ["Joel Piroe", "Wilfried Gnonto", "Dan James"]},
        "Liverpool": {"att": 94, "def": 92, "strikers": ["Mohamed Salah", "Darwin Núñez", "Luis Díaz", "Diogo Jota"]},
        "Manchester City": {"att": 98, "def": 93, "strikers": ["Erling Haaland", "Phil Foden", "Savinho", "Kevin De Bruyne"]},
        "Manchester United": {"att": 88, "def": 86, "strikers": ["Joshua Zirkzee", "Rasmus Højlund", "Alejandro Garnacho", "Marcus Rashford"]},
        "Newcastle United": {"att": 89, "def": 87, "strikers": ["Alexander Isak", "Anthony Gordon", "Harvey Barnes", "Callum Wilson"]},
        "Nottingham Forest": {"att": 81, "def": 81, "strikers": ["Chris Wood", "Taiwo Awoniyi", "Anthony Elanga", "Morgan Gibbs-White"]},
        "Sunderland": {"att": 75, "def": 75, "strikers": ["Wilson Isidor", "Eliezer Mayenda", "Romaine Mundle"]},
        "Tottenham": {"att": 90, "def": 85, "strikers": ["Son Heung-min", "Dominic Solanke", "Dejan Kulusevski", "James Maddison"]},
        "West Ham": {"att": 85, "def": 81, "strikers": ["Jarrod Bowen", "Mohammed Kudus", "Niclas Füllkrug", "Lucas Paquetá"]},
        "Wolves": {"att": 80, "def": 79, "strikers": ["Matheus Cunha", "Jørgen Strand Larsen", "Hwang Hee-chan"]}
    },
    "La Liga": {
        "Alavés": {"att": 76, "def": 78, "strikers": ["Kike García", "Toni Martínez", "Carlos Vicente"]},
        "Athletic Club": {"att": 87, "def": 88, "strikers": ["Nico Williams", "Iñaki Williams", "Oihan Sancet", "Gorka Guruzeta"]},
        "Atlético Madrid": {"att": 91, "def": 91, "strikers": ["Julián Álvarez", "Antoine Griezmann", "Alexander Sørloth", "Ángel Correa"]},
        "Barcelona": {"att": 96, "def": 89, "strikers": ["Robert Lewandowski", "Lamine Yamal", "Raphinha", "Dani Olmo"]},
        "Celta Vigo": {"att": 80, "def": 78, "strikers": ["Iago Aspas", "Borja Iglesias", "Jonathan Bamba"]},
        "Elche": {"att": 73, "def": 73, "strikers": ["Sory Kaba", "Mourad", "Nico Fernández"]},
        "Espanyol": {"att": 75, "def": 76, "strikers": ["Javi Puado", "Alejo Véliz", "Walid Cheddira"]},
        "Getafe": {"att": 74, "def": 80, "strikers": ["Borja Mayoral", "Bertuğ Yıldırım", "Carles Pérez"]},
        "Girona": {"att": 85, "def": 81, "strikers": ["Bojan Miovski", "Viktor Tsygankov", "Yaser Asprilla", "Abel Ruiz"]},
        "Las Palmas": {"att": 76, "def": 77, "strikers": ["Oli McBurnie", "Sandro Ramírez", "Alberto Moleiro"]},
        "Leganés": {"att": 72, "def": 75, "strikers": ["Sébastien Haller", "Miguel de la Fuente", "Juan Cruz"]},
        "Levante": {"att": 74, "def": 74, "strikers": ["José Morales", "Iván Romero", "Carlos Álvarez"]},
        "Mallorca": {"att": 78, "def": 80, "strikers": ["Vedat Muriqi", "Cyle Larin", "Dani Rodríguez"]},
        "Osasuna": {"att": 80, "def": 81, "strikers": ["Ante Budimir", "Bryan Zaragoza", "Moi Gómez"]},
        "Rayo Vallecano": {"att": 77, "def": 79, "strikers": ["Sergio Camello", "Raúl de Tomás", "Isi Palazón"]},
        "Real Betis": {"att": 85, "def": 83, "strikers": ["Vitor Roque", "Giovani Lo Celso", "Ezequiel Ávila", "Isco"]},
        "Real Madrid": {"att": 99, "def": 94, "strikers": ["Kylian Mbappé", "Vinicius Junior", "Rodrygo", "Jude Bellingham"]},
        "Real Sociedad": {"att": 85, "def": 85, "strikers": ["Mikel Oyarzabal", "Takefusa Kubo", "Orri Óskarsson", "Brais Méndez"]},
        "Sevilla": {"att": 82, "def": 82, "strikers": ["Kelechi Iheanacho", "Isaac Romero", "Dodi Lukebakio", "Lucas Ocampos"]},
        "Valencia": {"att": 79, "def": 80, "strikers": ["Hugo Duro", "Rafa Mir", "Diego López", "Javi Guerra"]},
        "Villarreal": {"att": 86, "def": 81, "strikers": ["Ayoze Pérez", "Thierno Barry", "Álex Baena", "Gerard Moreno"]}
    },
    "Bundesliga": {
        "Augsburg": {"att": 78, "def": 78, "strikers": ["Phillip Tietz", "Samuel Essende", "Alexis Claude-Maurice"]},
        "Bayer Leverkusen": {"att": 94, "def": 89, "strikers": ["Victor Boniface", "Florian Wirtz", "Patrik Schick", "Jeremie Frimpong"]},
        "Bayern Munich": {"att": 97, "def": 90, "strikers": ["Harry Kane", "Jamal Musiala", "Michael Olise", "Serge Gnabry"]},
        "Borussia Dortmund": {"att": 90, "def": 86, "strikers": ["Serhou Guirassy", "Karim Adeyemi", "Donyell Malen", "Julian Brandt"]},
        "Eintracht Frankfurt": {"att": 88, "def": 83, "strikers": ["Hugo Ekitike", "Omar Marmoush", "Mario Götze", "Ansgar Knauff"]},
        "Freiburg": {"att": 82, "def": 83, "strikers": ["Junior Adamu", "Vincenzo Grifo", "Ritsu Doan"]},
        "Gladbach": {"att": 81, "def": 79, "strikers": ["Tim Kleindienst", "Alassane Pléa", "Robin Hack"]},
        "Hamburger SV": {"att": 75, "def": 74, "strikers": ["Robert Glatzel", "Davie Selke", "Jean-Luc Dompé"]},
        "Hoffenheim": {"att": 82, "def": 78, "strikers": ["Andrej Kramarić", "Adam Hložek", "Mergim Berisha"]},
        "Köln": {"att": 76, "def": 75, "strikers": ["Tim Lemperle", "Damion Downs", "Linton Maina"]},
        "Mainz": {"att": 78, "def": 79, "strikers": ["Jonathan Burkardt", "Nadiem Amiri", "Paul Nebel"]},
        "RB Leipzig": {"att": 90, "def": 87, "strikers": ["Benjamin Šeško", "Loïs Openda", "Xavi Simons", "Yussuf Poulsen"]},
        "St. Pauli": {"att": 73, "def": 74, "strikers": ["Johannes Eggestein", "Morgan Guilavogui", "Elias Saad"]},
        "Stuttgart": {"att": 87, "def": 83, "strikers": ["Ermedin Demirović", "Deniz Undav", "Chris Führich", "Enzo Millot"]},
        "Union Berlin": {"att": 77, "def": 80, "strikers": ["Benedict Hollerbach", "Yorbe Vertessen", "Tom Rothe"]},
        "Werder Bremen": {"att": 79, "def": 78, "strikers": ["Marvin Ducksch", "Keke Topp", "Mitchell Weiser"]},
        "Wolfsburg": {"att": 81, "def": 80, "strikers": ["Mohamed Amoura", "Jonas Wind", "Lovro Majer", "Tiago Tomás"]}
    },
    "Ligue 1": {
        "Angers": {"att": 73, "def": 74, "strikers": ["Farid El Melali", "Lois Diony", "Jim Allevinah"]},
        "Auxerre": {"att": 73, "def": 73, "strikers": ["Ado Onaiwu", "Lassine Sinayoko", "Gaëtan Perrin"]},
        "Brest": {"att": 82, "def": 82, "strikers": ["Ludovic Ajorque", "Romain Del Castillo", "Pierre Lees-Melou"]},
        "Le Havre": {"att": 72, "def": 74, "strikers": ["Emmanuel Sabbi", "Antoine Joujou", "Yassine Kechta"]},
        "Lens": {"att": 82, "def": 83, "strikers": ["M'Bala Nzola", "Wesley Saïd", "Florian Sotoca", "Angelo Fulgini"]},
        "Lille": {"att": 87, "def": 86, "strikers": ["Jonathan David", "Edon Zhegrova", "Rémy Cabella", "Hakon Haraldsson"]},
        "Lyon": {"att": 86, "def": 82, "strikers": ["Alexandre Lacazette", "Georges Mikautadze", "Malick Fofana", "Rayan Cherki"]},
        "Marseille": {"att": 89, "def": 84, "strikers": ["Mason Greenwood", "Elye Wahi", "Luis Henrique", "Pierre-Emerick Aubameyang"]},
        "Monaco": {"att": 88, "def": 85, "strikers": ["Folarin Balogun", "Breel Embolo", "Takumi Minamino", "Aleksandr Golovin"]},
        "Nantes": {"att": 76, "def": 77, "strikers": ["Mostafa Mohamed", "Moses Simon", "Matthis Abline"]},
        "Nice": {"att": 84, "def": 85, "strikers": ["Youssoufa Moukoko", "Gaëtan Laborde", "Jérémie Boga", "Terem Moffi"]},
        "Paris FC": {"att": 72, "def": 72, "strikers": ["Jean-Philippe Krasso", "Nouha Dicko", "Alimami Gory"]},
        "PSG": {"att": 96, "def": 90, "strikers": ["Ousmane Dembélé", "Bradley Barcola", "Marco Asensio", "Gonçalo Ramos"]},
        "Reims": {"att": 79, "def": 79, "strikers": ["Keito Nakamura", "Junya Ito", "Oumar Diakité"]},
        "Rennes": {"att": 83, "def": 81, "strikers": ["Arnaud Kalimuendo", "Ludovic Blas", "Albert Grønbæk", "Amine Gouiri"]},
        "Saint-Étienne": {"att": 73, "def": 74, "strikers": ["Ibrahim Sissoko", "Zuriko Davitashvili", "Lucas Stassin"]},
        "Strasbourg": {"att": 80, "def": 77, "strikers": ["Emanuel Emegha", "Diego Moreira", "Sebastian Nanasi", "Habib Diallo"]},
        "Toulouse": {"att": 77, "def": 77, "strikers": ["Zakaria Aboukhlal", "Frank Magri", "Yann Gboho"]}
    }
}

# Pannello di controllo superiore compatto
col_sel1, col_sel2, col_sel3 = st.columns([1.2, 1.2, 1.2])
with col_sel1:
    league = st.selectbox("🌐 Campionato", list(FOOTBALL_DATABASE.keys()))
teams_list = sorted(list(FOOTBALL_DATABASE[league].keys()))

with col_sel2:
    home_team = st.selectbox("🏠 Casa", teams_list, index=0)
with col_sel3:
    away_team = st.selectbox("✈️ Ospite", teams_list, index=1 if len(teams_list) > 1 else 0)

st.markdown("<br>", unsafe_allow_html=True)

if home_team == away_team:
    st.warning("⚠️ Seleziona due squadre diverse per procedere.")
else:
    if st.button("🚀 ESEGUI ANALISI ALGORITMICA", type="primary", use_container_width=True):
        h_data = FOOTBALL_DATABASE[league][home_team]
        a_data = FOOTBALL_DATABASE[league][away_team]
        
        home_xg = 1.25 * ((h_data["att"] / a_data["def"]) ** 2.2)
        away_xg = 0.95 * ((a_data["att"] / h_data["def"]) ** 2.2)
        
        max_goals = 6
        prob_matrix = np.zeros((max_goals, max_goals))
        exact_scores = []
        
        prob_over15 = prob_over25 = prob_under25 = prob_gg = prob_ng = 0.0
        prob_0_1_gol = prob_2_3_gol = prob_4_plus_gol = 0.0

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

                if total_goals <= 1: prob_0_1_gol += p
                elif 2 <= total_goals <= 3: prob_2_3_gol += p
                else: prob_4_plus_gol += p

        home_win = float(np.sum(np.tril(prob_matrix, -1))) * 100
        draw = float(np.sum(np.diag(prob_matrix))) * 100
        away_win = float(np.sum(np.triu(prob_matrix, 1))) * 100

        dc_1x, dc_x2, dc_12 = home_win + draw, away_win + draw, home_win + away_win

        prob_over15 *= 100; prob_over25 *= 100; prob_under25 *= 100
        prob_gg *= 100; prob_ng *= 100
        prob_0_1_gol *= 100; prob_2_3_gol *= 100; prob_4_plus_gol *= 100

        # --- 1. ESITO 1X2 PRINCIPALE ---
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
                ⚽ <strong>Expected Goals (xG):</strong> &nbsp; 
                <span style="color: #00f2fe;">{home_team} ({round(home_xg, 2)})</span> &nbsp;—&nbsp; 
                <span style="color: #ff007f;">({round(away_xg, 2)}) {away_team}</span>
            </div>
        """, unsafe_allow_html=True)

        # --- 2. SEZIONE CONSIGLI & DRITTE SCHEDINA ---
        best_dc = "1X" if dc_1x > dc_x2 and dc_1x > dc_12 else ("X2" if dc_x2 > dc_1x and dc_x2 > dc_12 else "12")
        best_goals = "OVER 2.5" if prob_over25 > prob_under25 else "UNDER 2.5"
        best_gg_ng = "GOAL (GG)" if prob_gg > prob_ng else "NO GOAL (NG)"

        st.success(f"""
            💡 **SINTESI SCHEDINA CONSIGLIATA:**
            * 🛡️ **Miglior Doppia Chance:** `{best_dc}` ({round(max(dc_1x, dc_x2, dc_12), 1)}%)
            * ⚽ **Linea Gol Consigliata:** `{best_goals}` (Over 1.5 al {round(prob_over15, 1)}%)
            * 🥅 **Opzione Entrambe a Segno:** `{best_gg_ng}`
        """)

        # --- 3. DETTAGLI STATISTICI TRAMITE EXPANDERS ---
        with st.expander("📊 Visualizza statistiche dettagliate mercati (Doppia Chance, Over/Under, Somma Gol)", expanded=True):
            col_s1, col_s2 = st.columns(2)
            
            with col_s1:
                st.markdown("**🔹 Mercati Esito & Doppia Chance**")
                st.markdown(f'<div class="stat-box">Doppia Chance 1X: <strong style="color:#00f2fe;">{round(dc_1x, 1)}%</strong></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="stat-box">Doppia Chance X2: <strong style="color:#ff007f;">{round(dc_x2, 1)}%</strong></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="stat-box">Doppia Chance 12: <strong style="color:#ffb703;">{round(dc_12, 1)}%</strong></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="stat-box">Entrambe a Segno (Goal): <strong style="color:#00c6ff;">{round(prob_gg, 1)}%</strong></div>', unsafe_allow_html=True)
            
            with col_s2:
                st.markdown("**🔹 Mercati Goal & Somma Reti**")
                st.markdown(f'<div class="stat-box">Over 1.5 Gol: <strong style="color:#00f2fe;">{round(prob_over15, 1)}%</strong></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="stat-box">Over 2.5 Gol: <strong style="color:#00c6ff;">{round(prob_over25, 1)}%</strong></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="stat-box">Under 2.5 Gol: <strong style="color:#ffb703;">{round(prob_under25, 1)}%</strong></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="stat-box">Somma Gol 2-3: <strong style="color:#00f2fe;">{round(prob_2_3_gol, 1)}%</strong></div>', unsafe_allow_html=True)

        with st.expander("🎯 Visualizza i 5 Risultati Esatti più probabili", expanded=True):
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

        with st.expander("⚽ Analisi Probabilità Marcatori delle Squadre", expanded=False):
            m_col1, m_col2 = st.columns(2)
            weights = [0.38, 0.28, 0.20, 0.14]
            
            with m_col1:
                st.markdown(f"**Marcatori {home_team}**")
                for idx, player in enumerate(h_data["strikers"]):
                    prob_scorer = min(round(weights[idx] * (home_xg / 1.35) * 100, 1), 85.0)
                    st.write(f"• **{player}**: `{prob_scorer}%`")
                    st.progress(prob_scorer / 100)
                    
            with m_col2:
                st.markdown(f"**Marcatori {away_team}**")
                for idx, player in enumerate(a_data["strikers"]):
                    prob_scorer = min(round(weights[idx] * (away_xg / 1.05) * 100, 1), 85.0)
                    st.write(f"• **{player}**: `{prob_scorer}%`")
                    st.progress(prob_scorer / 100)
