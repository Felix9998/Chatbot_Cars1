import streamlit as st
import datetime
import csv
import os
import random
import io

PRIMARY_COLOR = "#1D3557"


# ----------------------------------------------------------
# Sitzungsverwaltung & Logging
# ----------------------------------------------------------

def ensure_session_state():
    if "interactions" not in st.session_state:
        st.session_state["interactions"] = []
    if "preferences" not in st.session_state:
        st.session_state["preferences"] = {}
    if "recommendations" not in st.session_state:
        st.session_state["recommendations"] = []


def log_interaction(message, action):
    st.session_state["interactions"].append(
        {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": message,
            "action": action,
        }
    )


# ----------------------------------------------------------
# Dummy-Filmempfehlungen
# ----------------------------------------------------------

def generate_recommendations(preferences):
    names = ["Chronos V", "Das letzte Echo", "Schatten im Nebel"]
    recs = []

    for name in names:
        recs.append(
            {
                "name": name,
                "anzahl_bewertungen": random.randint(13000, 15000),
                "imdb_ranking": random.randint(1, 5000),
            }
        )
    return recs


# ----------------------------------------------------------
# Hauptfunktion
# ----------------------------------------------------------

def main():
    ensure_session_state()

    st.set_page_config(
        page_title="CineMate — digitaler Film-Assistent",
        layout="centered",
    )

    st.markdown(
        f"<h1 style='color:{PRIMARY_COLOR}; text-align: center;'>CineMate</h1>",
        unsafe_allow_html=True,
    )

    st.write("Hallo! Ich bin CineMate – dein digitaler Film-Assistent.")
    st.write(
        "Bitte gib an, welche drei der folgenden sechs Genres du bevorzugst. "
        "Wähle intuitiv aus."
    )

    # --------------------------------------------------
    # Genre-Auswahl
    # --------------------------------------------------

    genres = ["Komödie", "Drama", "Action", "Science-Fiction", "Horror", "Thriller"]
    selected_genres = st.multiselect(
        "Wähle genau 3 Genres:",
        genres,
        key="genres_select",
        placeholder="Genres wählen",
    )

    if len(selected_genres) != 3:
        st.info("Bitte wähle genau 3 Genres aus.")
    else:
        st.session_state["preferences"]["Genres"] = selected_genres
        log_interaction(f"Genres selected: {selected_genres}", "genres_selected")

        st.write(
            "Danke. Auswahl gespeichert. Bitte gib jetzt die spezifischen Filterkriterien ein."
        )

        # 👉 Scroll zur Filmauswahl
        st.markdown(
            """
            <script>
                setTimeout(function() {
                    const el = document.getElementById("filmauswahl");
                    if (el) {
                        el.scrollIntoView({behavior: "smooth", block: "start"});
                    }
                }, 500);
            </script>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # --------------------------------------------------
    # Filmauswahl
    # --------------------------------------------------

    st.markdown("<div id='filmauswahl'></div>", unsafe_allow_html=True)
    st.subheader("📋 Deine Filmauswahl")

    era = st.selectbox(
        "Ära / Erscheinungszeitraum",
        ["Klassiker (<2000)", "Modern (2000+)"],
        key="era",
    )

    visual_style = st.selectbox(
        "Visueller Stil",
        ["Realfilm", "Animation", "Schwarz-Weiß"],
        key="visual_style",
    )

    laufzeit = st.number_input(
        "Gewünschte Laufzeit (Minuten)",
        min_value=60,
        max_value=240,
        value=120,
        step=5,
        key="laufzeit",
    )

    st.markdown("**IMDb-Rating (Bereich)**")
    c1, c2 = st.columns(2, gap="small")

    with c1:
        imdb_von = st.number_input(
            "von", 1.0, 10.0, value=6.0, step=0.1, format="%.1f"
        )
    with c2:
        imdb_bis = st.number_input(
            "bis", 1.0, 10.0, value=9.0, step=0.1, format="%.1f"
        )

    st.session_state["preferences"].update(
        {
            "Ära": era,
            "Visueller Stil": visual_style,
            "Laufzeit": int(laufzeit),
            "IMDb von": float(imdb_von),
            "IMDb bis": float(imdb_bis),
        }
    )

    # --------------------------------------------------
    # Empfehlung generieren
    # --------------------------------------------------

    if st.button("Empfehlung generieren"):
        if len(st.session_state["preferences"].get("Genres", [])) != 3:
            st.error("Bitte wähle genau drei Genres.")
            return

        log_interaction("Config saved", "config_saved")

        with st.spinner("CineMate verarbeitet deine Eingaben..."):
            g1, g2, g3 = st

