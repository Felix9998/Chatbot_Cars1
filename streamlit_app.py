import streamlit as st
import datetime
import csv
import os
import random
import io

PRIMARY_COLOR = "#1D3557"


def ensure_session_state():
    if 'interactions' not in st.session_state:
        st.session_state['interactions'] = []
    if 'preferences' not in st.session_state:
        st.session_state['preferences'] = {}
    if 'recommendations' not in st.session_state:
        st.session_state['recommendations'] = []


def log_interaction(message, action):
    st.session_state['interactions'].append({
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'message': message,
        'action': action
    })


def save_interactions_to_file(path='downloads'):
    os.makedirs(path, exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"cine_noExplanation_{timestamp}.csv"
    filepath = os.path.join(path, filename)
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Message', 'Action'])
            for i in st.session_state['interactions']:
                writer.writerow([i['timestamp'], i['message'], i['action']])
        return filepath
    except Exception as e:
        st.error(f'Fehler beim Speichern: {e}')
        return None


def interactions_csv_bytes():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Timestamp', 'Message', 'Action'])
    for i in st.session_state['interactions']:
        writer.writerow([i['timestamp'], i['message'], i['action']])
    return output.getvalue().encode('utf-8')


def generate_recommendations(preferences):
    # Fixed recommendations for NoExplanation variant
    names = ["Chronos V", "Das letzte Echo", "Schatten im Nebel"]
    recs = []
    for name in names:
        anzahl = random.randint(13000, 15000)
        imdb_ranking = random.randint(1, 5000)
        recs.append({
            'name': name,
            'anzahl_bewertungen': anzahl,
            'imdb_ranking': imdb_ranking
        })
    return recs


def main():
    ensure_session_state()

    st.set_page_config(page_title='CineMate — digitales Film-Assistent', layout='centered')
    st.markdown(f"<h1 style='color:{PRIMARY_COLOR}; text-align: center;'>CineMate</h1>", unsafe_allow_html=True)

    st.write("Hallo! Ich bin CineMate – dein digitaler Film-Assistent. Ich unterstütze dich bei der Suche nach einem Film.")
    st.write("Bitte gib an, welche drei der folgenden sechs Genres du bevorzugst. Wähle intuitiv aus.")

    # Genres selection (require exactly 3)
    genres = ["Komödie", "Drama", "Action", "Science-Fiction", "Horror", "Thriller"]
    selected_genres = st.multiselect("Wähle genau 3 Genres:", genres, key='genres_select', placeholder="Genres wählen")

    if len(selected_genres) != 3:
        st.info("Bitte wähle genau 3 Genres aus.")
    else:
        st.session_state['preferences']['Genres'] = selected_genres
        st.write("Danke. Auswahl gespeichert. Bitte gib jetzt die spezifischen Filterkriterien ein.")
        log_interaction(f"Genres selected: {selected_genres}", 'genres_selected')

    st.markdown("---")

    # Film configuration
    st.subheader('📋 Deine Filmauswahl')

    era = st.selectbox('Ära / Erscheinungszeitraum', ['Klassiker (<2000)', 'Modern (2000+)'], key='era')
    visual_style = st.selectbox('Visueller Stil', ['Realfilm', 'Animation', 'Schwarz-Weiß'], key='visual_style')

    laufzeit = st.number_input('Gewünschte Laufzeit (Minuten)', min_value=60, max_value=240, value=120, step=5, key='laufzeit')

    st.markdown('**IMDb-Rating (Bereich)**')
    rating_col1, rating_col2 = st.columns(2, gap='small')
    with rating_col1:
        imdb_von = st.number_input('von', min_value=1.0, max_value=10.0, value=6.0, step=0.1, format="%.1f", label_visibility='collapsed')
    with rating_col2:
        imdb_bis = st.number_input('bis', min_value=1.0, max_value=10.0, value=9.0, step=0.1, format="%.1f", label_visibility='collapsed')

    # Save preferences in session
    st.session_state['preferences'].update({
        'Ära': era,
        'Visueller Stil': visual_style,
        'Laufzeit': int(laufzeit),
        'IMDb von': float(imdb_von),
        'IMDb bis': float(imdb_bis)
    })

    # Generate button
    if st.button('Empfehlung generieren'):
        # Validation
        if len(st.session_state['preferences'].get('Genres', [])) < 3:
            st.error('Bitte wähle genau 3 Genres.')
        elif st.session_state['preferences']['IMDb von'] < 1 or st.session_state['preferences']['IMDb bis'] > 10:
            st.error('Der IMDb-Rating-Bereich muss zwischen 1.0 und 10.0 liegen.')
        elif st.session_state['preferences']['IMDb von'] > st.session_state['preferences']['IMDb bis']:
            st.error('Der untere Wert des IMDb-Rating-Bereichs darf nicht größer sein als der obere Wert.')
        else:
            log_interaction('Config saved', 'config_saved')
            with st.spinner('CineMate verarbeitet deine Eingaben...'):
                # Reasoning (no explanation) - 4 Schritte
                g1, g2, g3 = st.session_state['preferences']['Genres']
                cfg = {
                    'Ära': st.session_state['preferences']['Ära'],
                    'Visueller Stil': st.session_state['preferences']['Visueller Stil'],
                    'Laufzeit': st.session_state['preferences']['Laufzeit'],
                    'IMDb von': st.session_state['preferences']['IMDb von'],
                    'IMDb bis': st.session_state['preferences']['IMDb bis']
                }
                st.write(f"Die Eingaben werden verarbeitet, um passende Filme zu finden. Genres: {g1}, {g2} und {g3}.")
                st.write(f"Die Konfiguration ({cfg}) dient als Grundlage für die Filmauswahl.")
                st.write("Kontrollhinweis: Die IMDb Datenbank umfasst über 6 Millionen Titel.")
                st.write("Hier sind die drei besten Treffer aus meiner Datenbank.")

                recs = generate_recommendations(st.session_state['preferences'])
                st.session_state['recommendations'] = recs
                log_interaction('Recommendation generated', 'recommendation_generated')

    # Show recommendations if available
    if st.session_state.get('recommendations'):
        st.markdown('### 🍿 Empfehlungen')
        recs = st.session_state['recommendations']

        for i, r in enumerate(recs):
            with st.container():
                col_left, col_right = st.columns([3, 1], gap='medium')
                with col_left:
                    st.markdown(f"**{r['name']}**")
                    count_formatted = f"{r['anzahl_bewertungen']:,}".replace(',', '.')
                    st.write(f"Anzahl Bewertungen: {count_formatted}")
                with col_right:
                    st.markdown(f"**IMDb-Ranking: #{r['imdb_ranking']}**")
                st.divider()

        st.success('✅ Empfehlungen geladen!')
        st.write('Bitte gib in das Textfeld den Code 01 ein. Danach kann mit dem Fragebogen fortgefahren werden')


if __name__ == '__main__':
    main()
