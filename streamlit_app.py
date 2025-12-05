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
    filename = f"cara_ohneExplanation_{timestamp}.csv"
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
    names = ["Zirell Avantis", "Velvra Monaro", "Tirora Qyra"]
    ratings = ["4,2/5 Sterne (155 Bewertungen)", "4,3/5 Sterne (152 Bewertungen)", "4,25/5 Sterne (150 Bewertungen)"]
    von = preferences.get('Preis von', 5000)
    bis = preferences.get('Preis bis', 100000)
    base_price = int(round(((von + bis) / 2) / 5.0) * 5)
    price_values = [base_price - 50, base_price, base_price + 50]
    price_values = [max(von, min(bis, p)) for p in price_values]

    def format_price(p):
        s = f"{p:,.0f}".replace(',', '.')
        return f"{s} €"

    prices = [format_price(p) for p in price_values]
    random.shuffle(names)
    random.shuffle(ratings)
    random.shuffle(prices)
    recs = [{'name': names[i], 'rating': ratings[i], 'price': prices[i]} for i in range(3)]
    return recs


def main():
    ensure_session_state()

    st.set_page_config(page_title='Cara — digitales Autohaus', layout='centered')
    st.markdown(f"<h1 style='color:{PRIMARY_COLOR}; text-align: center;'>Cara</h1>", unsafe_allow_html=True)

    st.write("Hallo! 👋 Ich bin Cara von Carage — ich helfe dir, ein passendes Fahrzeug zu finden.\n\n")

    # Traits selection (require exactly 3)
    traits = ["Groß", "Klein", "Sportlich", "Luxuriös", "Leistungsstark", "Alltagstauglich"]
    selected_traits = st.multiselect("Wähle genau 3 Merkmale, die dir wichtig sind:", traits, key='traits_select', placeholder="Merkmale wählen")

    # Validation: Groß und Klein dürfen nicht zusammen gewählt werden
    if "Groß" in selected_traits and "Klein" in selected_traits:
        st.error("⚠️ 'Groß' und 'Klein' schließen sich aus — bitte wähle nur eines davon.")
    elif len(selected_traits) != 3:
        st.info("Bitte wähle genau 3 Merkmale aus.")
    else:
        st.session_state['preferences']['Persönlichkeitsmerkmale'] = selected_traits
        log_interaction(f"Traits selected: {selected_traits}", 'trait_selected')

    st.markdown("---")

    # Configuration (responsive for mobile)
    st.subheader('📋 Deine Fahrzeugwünsche')
    fahrzeugtyp = st.selectbox('Fahrzeugtyp', ['Gebrauchtwagen', 'Neuwagen'], key='fahrzeugtyp')
    kraftstoff = st.selectbox('Kraftstoff', ['Elektrisch', 'Benzin', 'Diesel'], key='kraftstoff')
    sitzplaetze = st.number_input('Sitzplätze', min_value=2, max_value=9, value=4, key='sitzplaetze')

    st.markdown('**Preisvorstellung (in €)**')
    price_col1, price_col2 = st.columns(2, gap='small')
    with price_col1:
        preis_von = st.number_input('von', min_value=0, max_value=1000000, value=5000, step=100, label_visibility='collapsed')
    with price_col2:
        preis_bis = st.number_input('bis', min_value=0, max_value=1000000, value=30000, step=100, label_visibility='collapsed')

    # Save preferences in session
    st.session_state['preferences'].update({
        'Fahrzeugtyp': fahrzeugtyp,
        'Kraftstoff': kraftstoff,
        'Sitzplätze': sitzplaetze,
        'Preis von': int(preis_von),
        'Preis bis': int(preis_bis)
    })

    # Generate button
    if st.button('Empfehlung generieren'):
        # Validation
        if len(st.session_state['preferences'].get('Persönlichkeitsmerkmale', [])) < 3:
            st.error('Bitte wähle genau 3 Merkmale.')
        elif st.session_state['preferences']['Preis von'] < 5000 or st.session_state['preferences']['Preis bis'] > 100000:
            st.error('Der angegebene Preis sollte zwischen 5.000 € und 100.000 € liegen.')
        else:
            log_interaction('Config saved', 'config_saved')
            with st.spinner('Cara verarbeitet deine Eingaben...'):
                # Short staged messages (keep UX responsive)
                st.info(f"Wichtige Merkmale: {', '.join(st.session_state['preferences']['Persönlichkeitsmerkmale'])}")
                st.write('Die Konfiguration dient als Grundlage für die Auswahl.')
                recs = generate_recommendations(st.session_state['preferences'])
                st.session_state['recommendations'] = recs
                log_interaction('Recommendation generated', 'recommendation_generated')

    # Show recommendations if available
    if st.session_state.get('recommendations'):
        st.markdown('### 🚗 Empfehlungen')
        recs = st.session_state['recommendations']
        
        # Display recommendations in mobile-friendly format
        for i, r in enumerate(recs):
            with st.container():
                col_left, col_right = st.columns([2, 1], gap='medium')
                with col_left:
                    st.markdown(f"**{r['name']}**")
                    st.write(f"⭐ {r['rating']}")
                with col_right:
                    st.markdown(f"**{r['price']}**")
                st.divider()
        
        st.success('✅ Empfehlungen geladen!')
        st.write("Bitte fahren Sie jetzt mit dem Fragebogen fort.")



if __name__ == '__main__':
    main()
