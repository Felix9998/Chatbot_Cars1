import streamlit as st
import datetime
import random

PRIMARY_COLOR = "#1D3557"

# ✅ Muss der erste Streamlit-Call sein:
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
# Dummy-Filmempfehlungen
# ----------------------------------------------------------

def generate_recommendations(preferences):
    names = ["Chronos V", "Das letzte Echo", "Schatten im Nebel"]
    recs = []

    imdb_min = float(preferences["IMDb von"])
    imdb_max = float(preferences["IMDb bis"])

    lmin = int(preferences.get("Laufzeit von", 90))
    lmax = int(preferences.get("Laufzeit bis", 140))

    offsets = [0.0, -0.3, 0.2]

    for i, name in enumerate(names):
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
            "name": name,
            "year": year,
            "runtime": runtime,
            "visual_style": preferences["Visueller Stil"],
            "genres": preferences["Genres"],
            "imdb_rating": rating,
            "votes": random.randint(5_000, 250_000),
            "short_desc": "Kurzbeschreibung: Ein fiktiver Film, der als Platzhalter für das Experiment dient."
        })
    return recs


# ----------------------------------------------------------
# Helfer: Kriterien-Block & Abgleich pro Film
# ----------------------------------------------------------

def render_user_criteria(prefs: dict):
    genres = prefs.get("Genres", [])
    era = prefs.get("Ära", "–")
    style = prefs.get("Visueller Stil", "–")
    lmin = prefs.get("Laufzeit von", "–")
    lmax = prefs.get("Laufzeit bis", "–")
    imdb_min = prefs.get("IMDb von", "–")
    imdb_max = prefs.get("IMDb bis", "–")

    st.markdown("#### 🔎 Deine Kriterien (aus deinen Eingaben)")
    st.write(f"**Genres:** {', '.join(genres) if genres else '–'}")
    st.write(f"**Ära:** {era}")
    st.write(f"**Visueller Stil:** {style}")
    st.write(f"**Laufzeit:** {lmin}–{lmax} Minuten")
    st.write(f"**IMDb-Rating:** {float(imdb_min):.1f}–{float(imdb_max):.1f}")


def render_match_block(prefs: dict, rec: dict):
    lmin = int(prefs.get("Laufzeit von", 0))
    lmax = int(prefs.get("Laufzeit bis", 10_000))
    imdb_min = float(prefs.get("IMDb von", 0.0))
    imdb_max = float(prefs.get("IMDb bis", 10.0))

    runtime_ok = lmin <= int(rec["runtime"]) <= lmax
    imdb_ok = imdb_min <= float(rec["imdb_rating"]) <= imdb_max
    style_ok = str(rec["visual_style"]) == str(prefs.get("Visueller Stil", ""))

    st.markdown("**Abgleich mit deiner Auswahl:**")
    st.write(f"• **Jahr:** {rec['year']} (Ära-Auswahl: {prefs.get('Ära','–')})")
    st.write(f"• **Genres:** {', '.join(rec['genres'])}")
    st.write(f"• **Stil:** {rec['visual_style']} ({'✓ passt' if style_ok else '△ abweichend'})")
    st.write(f"• **Laufzeit:** {rec['runtime']} Min ({'✓ im Bereich' if runtime_ok else '△ außerhalb'})")
    st.write(f"• **IMDb:** {rec['imdb_rating']:.1f}/10 ({'✓ im Bereich' if imdb_ok else '△ außerhalb'})")


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
    else:
        st.session_state["preferences"]["Genres"] = selected_genres
        log_interaction(f"Genres selected: {selected_genres}", "genres_selected")
        st.write("Danke. Auswahl übernommen (nur für diese Sitzung). Bitte gib jetzt die Filterkriterien ein.")

        st.markdown(
            """
            <script>
                setTimeout(function() {
                    const el = document.getElementById("filmauswahl");
                    if (el) el.scrollIntoView({behavior:"smooth", block:"start"});
                }, 400);
            </script>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    st.markdown("<div id='filmauswahl'></div>", unsafe_allow_html=True)
    st.subheader("📋 Deine Filmauswahl")

    era = st.selectbox("Ära / Erscheinungszeitraum", ["Klassiker (<2000)", "Modern (2000+)"], key="era")
    visual_style = st.selectbox("Visueller Stil", ["Realfilm", "Animation", "Schwarz-Weiß"], key="visual_style")

    laufzeit_range = st.slider(
        "Gewünschte Laufzeit (Minuten, Bereich)",
        min_value=60, max_value=240,
        value=(90, 140), step=5,
        key="laufzeit_range"
    )

    st.markdown("**IMDb-Rating (Bereich)**")
    st.caption("IMDb = Filmdatenbank. Das Rating (1–10) ist ein Durchschnitt aus Nutzerbewertungen.")
    c1, c2 = st.columns(2, gap="small")
    with c1:
        imdb_von = st.number_input("von", 1.0, 10.0, value=6.0, step=0.1, format="%.1f")
    with c2:
        imdb_bis = st.number_input("bis", 1.0, 10.0, value=9.0, step=0.1, format="%.1f")

    # Preferences speichern (✅ Bugfix: kein "laufzeit" mehr)
    st.session_state["preferences"].update(
        {
            "Ära": era,
            "Visueller Stil": visual_style,
            "Laufzeit von": int(laufzeit_range[0]),
            "Laufzeit bis": int(laufzeit_range[1]),
            "IMDb von": float(imdb_von),
            "IMDb bis": float(imdb_bis),
        }
    )

    if st.button("Empfehlung generieren"):
        if len(st.session_state["preferences"].get("Genres", [])) != 3:
            st.error("Bitte wähle genau drei Genres.")
            return

        log_interaction("Config saved", "config_saved")

        with st.spinner("CineMate verarbeitet deine Eingaben..."):
            st.markdown("<div id='erklaerung'></div>", unsafe_allow_html=True)

            prefs = st.session_state["preferences"]
            g1, g2, g3 = prefs["Genres"]

            st.markdown(
                f"""
                **Verarbeitung der Eingaben**

                Die Eingaben werden verarbeitet, um passende Filme zu finden.  
                **Genres:** {g1}, {g2} und {g3}

                *Kontrollhinweis:* Die IMDb-Datenbank umfasst über **6 Millionen Titel**.

                **Hier sind die drei besten Treffer aus meiner Datenbank.**
                """
            )

            st.session_state["recommendations"] = generate_recommendations(prefs)
            log_interaction("Recommendation generated", "recommendation_generated")

        st.markdown(
            """
            <script>
                setTimeout(function(){
                    const e = document.getElementById("erklaerung");
                    if (e) e.scrollIntoView({behavior:"smooth", block:"center"});
                }, 500);

                setTimeout(function(){
                    const r = document.getElementById("empfehlungen");
                    if (r) r.scrollIntoView({behavior:"smooth", block:"start"});
                }, 1400);
            </script>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state["recommendations"]:
        st.markdown("<div id='empfehlungen'></div>", unsafe_allow_html=True)
        st.markdown("### 🍿 Empfehlungen")

        # ✅ (10) Kriterien direkt mit anzeigen
        render_user_criteria(st.session_state["preferences"])
        st.markdown("---")

        for r in st.session_state["recommendations"]:
            left, right = st.columns([3, 1], gap="medium")

            with left:
                st.markdown(f"**{r['name']}** ({r['year']})")
                st.write(f"Genre: {', '.join(r['genres'])}")
                st.write(f"Stil: {r['visual_style']} • Laufzeit: {r['runtime']} Min")
                st.write(r["short_desc"])
                st.markdown("")  # kleine Luft
                render_match_block(st.session_state["preferences"], r)

            with right:
                st.markdown(f"**IMDb: {r['imdb_rating']:.1f}/10**")
                st.caption(f"{r['votes']:,} Bewertungen".replace(",", "."))

            st.divider()

        st.success("✅ Empfehlungen geladen!")
        st.write("Bitte gib den Code *01* in das Textfeld unter dem Chatbot ein – danach kann mit dem Fragebogen fortgefahren werden.")


if __name__ == "__main__":
    main()



