import streamlit as st
import datetime
import random

PRIMARY_COLOR = "#1D3557"

st.set_page_config(
    page_title="CineMate — digitaler Film-Assistent",
    layout="centered",
)

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
# Dummy-Filmempfehlungen (inkl. Kurzbeschreibungen)
# ----------------------------------------------------------

def generate_recommendations(preferences):
    films = [
        {
            "name": "Chronos V",
            "short_desc": "Ein Science-Fiction-Drama über ein experimentelles Zeitsystem, das unerwartete Auswirkungen auf Vergangenheit und Gegenwart hat."
        },
        {
            "name": "Das letzte Echo",
            "short_desc": "Ein Mystery-Thriller über rätselhafte Tonaufnahmen, die in einer abgelegenen Kleinstadt alte Konflikte wieder aufleben lassen."
        },
        {
            "name": "Schatten im Nebel",
            "short_desc": "Ein stilisierter Neo-Noir über einen Ermittler, der in einem scheinbar harmlosen Fall immer tiefer in ein Netz aus Täuschung gerät."
        }
    ]

    recs = []

    imdb_min = float(preferences["IMDb von"])
    imdb_max = float(preferences["IMDb bis"])

    lmin = int(preferences.get("Laufzeit von", 90))
    lmax = int(preferences.get("Laufzeit bis", 140))

    offsets = [0.0, -0.3, 0.2]

    for i, film in enumerate(films):
        rating = round(
            min(imdb_max, max(imdb_min, random.uniform(imdb_min, imdb_max) + offsets[i])),
            1
        )
        runtime = random.randint(lmin, lmax)

        if str(preferences["Ära"]).startswith("Klassiker"):
            year = random.randint(1970, 1999)
        else:
            year = random.randint(2000, 2024)

        recs.append({
            "name": film["name"],
            "year": year,
            "runtime": runtime,
            "visual_style": preferences["Visueller Stil"],
            "genres": preferences["Genres"],
            "imdb_rating": rating,
            "votes": random.randint(5_000, 250_000),
            "short_desc": film["short_desc"],
        })

    return recs


# ----------------------------------------------------------
# Helfer: Kriterien-Block
# ----------------------------------------------------------

def render_user_criteria(prefs: dict):
    st.markdown("#### 🔎 Deine Kriterien (aus deinen Eingaben)")
    st.write(f"**Genres:** {', '.join(prefs.get('Genres', []))}")
    st.write(f"**Ära:** {prefs.get('Ära', '–')}")
    st.write(f"**Visueller Stil:** {prefs.get('Visueller Stil', '–')}")
    st.write(
        f"**Laufzeit:** {prefs.get('Laufzeit von', '–')}–{prefs.get('Laufzeit bis', '–')} Minuten"
    )
    st.write(
        f"**IMDb-Rating:** {prefs.get('IMDb von', 0):.1f}–{prefs.get('IMDb bis', 0):.1f}"
    )


# ----------------------------------------------------------
# Hauptfunktion
# ----------------------------------------------------------

def main():
    ensure_session_state()

    st.markdown(
        f"<h1 style='color:{PRIMARY_COLOR}; text-align: center;'>CineMate</h1>",
        unsafe_allow_html=True,
    )

    st.write("Hallo! Ich bin CineMate – dein digitaler Film-Assistent.")
    st.write("Bitte wähle spontan drei Genres, die dir gerade gefallen.")

    genres = ["Komödie", "Drama", "Action", "Science-Fiction", "Horror", "Thriller"]
    selected_genres = st.multiselect(
        "Wähle genau 3 Genres:",
        genres,
        key="genres_select",
        placeholder="Genres wählen",
    )

    if len(selected_genres) != 3:
        st.info("Bitte wähle genau 3 Genres aus.")
        return

    st.session_state["preferences"]["Genres"] = selected_genres
    log_interaction(f"Genres selected: {selected_genres}", "genres_selected")

    st.markdown("---")
    st.subheader("📋 Deine Filmauswahl")

    era = st.selectbox("Ära / Erscheinungszeitraum", ["Klassiker (<2000)", "Modern (2000+)"])
    visual_style = st.selectbox("Visueller Stil", ["Realfilm", "Animation", "Schwarz-Weiß"])

    laufzeit_range = st.slider(
        "Gewünschte Laufzeit (Minuten, Bereich)",
        min_value=60,
        max_value=240,
        value=(90, 140),
        step=5,
    )

    st.markdown("**IMDb-Rating (Bereich)**")
    st.caption("IMDb = Filmdatenbank. Das Rating (1–10) ist ein Durchschnitt aus Nutzerbewertungen.")
    c1, c2 = st.columns(2)
    with c1:
        imdb_von = st.number_input("von", 1.0, 10.0, 6.0, 0.1, format="%.1f")
    with c2:
        imdb_bis = st.number_input("bis", 1.0, 10.0, 9.0, 0.1, format="%.1f")

    st.session_state["preferences"].update(
        {
            "Ära": era,
            "Visueller Stil": visual_style,
            "Laufzeit von": laufzeit_range[0],
            "Laufzeit bis": laufzeit_range[1],
            "IMDb von": imdb_von,
            "IMDb bis": imdb_bis,
        }
    )

    if st.button("Empfehlung generieren"):
        with st.spinner("CineMate verarbeitet deine Eingaben..."):
            st.session_state["recommendations"] = generate_recommendations(
                st.session_state["preferences"]
            )
            log_interaction("Recommendation generated", "recommendation_generated")

    if st.session_state["recommendations"]:
        st.markdown("### 🍿 Empfehlungen")

        render_user_criteria(st.session_state["preferences"])
        st.markdown("---")

        for r in st.session_state["recommendations"]:
            left, right = st.columns([3, 1])

            with left:
                st.markdown(f"**{r['name']}** ({r['year']})")
                st.write(r["short_desc"])
                st.write(f"Genre: {', '.join(r['genres'])}")
                st.write(f"Stil: {r['visual_style']} • Laufzeit: {r['runtime']} Min")

            with right:
                st.markdown(f"**IMDb: {r['imdb_rating']:.1f}/10**")
                st.caption(f"{r['votes']:,} Bewertungen".replace(",", "."))

            st.divider()

        st.success("✅ Empfehlungen geladen!")
        st.write(
            "Bitte gib den Code *01* in das Textfeld unter dem Chatbot ein – danach kann mit dem Fragebogen fortgefahren werden."
        )

        st.caption(
            "Hinweis: Die angezeigten Filmtitel und Inhalte sind fiktiv und dienen ausschließlich als Platzhalter für das Experiment."
        )


if __name__ == "__main__":
    main()





