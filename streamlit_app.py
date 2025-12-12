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


# ----------------------------------------------------------
# Dummy-Filmempfehlungen (Beispieldaten)
# ----------------------------------------------------------

def generate_recommendations(preferences):
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


# ----------------------------------------------------------
# Hauptfunktion der Streamlit-App
# ----------------------------------------------------------

def main():
    ensure_session_state()

    # Seiteneinstellungen & Titel
   st.set_page_config(page_title='CineMate — digitaler Film-Assistent', layout='centered')
   st.markdown(f"<h1 style='color:{PRIMARY_COLOR}; text-align: center;'>CineMate</h1>", unsafe_allow_html=True)

   st.write("Hallo! Ich bin CineMate – dein digitaler Film-Assistent.")
   st.write("Bitte gib an, welche drei der folgenden sechs Genres du bevorzugst. Wähle intuitiv aus.")

   # Genre-Auswahl (genau 3 erforderlich)
   genres=["Komödie","Drama","Action","Science-Fiction","Horror","Thriller"]
   selected_genres=_st.multiselect("Wähle genau 3 Genres:",genres,key="genres_select",placeholder="Genres wählen")

   if len(selected_genres)!=3:
       st.info("Bitte wähle genau 3 Genres aus.")
   else:
       st.session_state["preferences"]["Genres"]=selected_genres
       st.write("Danke. Auswahl gespeichert. Bitte gib jetzt die spezifischen Filterkriterien ein.")
       log_interaction(f"Genres selected: {selected_genres}","genres_selected")

       # Automatisch zur Filmauswahl scrollen (mit ID)
       markdown("""
           <script>
               setTimeout(function() {
                   var element=document.getElementById('filmauswahl');
                   if(element){
                       element.scrollIntoView({behavior:'smooth',block:'start'});
                   }
               },500);
           </script>
       """,unsafe_allow_html=True)

   _st.markdown("---")

   # Abschnitt mit ID für Scrollziel „Filmauswahl“
   st.markdown("<div id='filmauswahl'></div>",unsafe_allow_html=True)
   st.subheader('📋 Deine Filmauswahl')

   era=_st.selectbox('Ära / Erscheinungszeitraum',['Klassiker (<2000)','Modern (2000+)'],key='era')
   visual_style=_st.selectbox('Visueller Stil',['Realfilm','Animation','Schwarz-Weiß'],key='visual_style')

   laufzeit=_st.number_input('Gewünschte Laufzeit (Minuten)',min_value=60,max_value=240,value=120,step=5,key='laufzeit')

   st.markdown('**IMDb-Rating (Bereich)**')
   
   rating_col1,rating_col2=columns(2,gap="small")
   
   with rating_col1:
       imdb_von=number_input('von',min_value=1.0,max_value=10.0,value=6.0,step=0.1,format="%.1f")
   
   with rating_col2:
       imdb_bis=number_input('bis',min_value=1.0,max_value=10.0,value=9.0,step=0.1,format="%.1f")

   session state['preferences'].update({
       "Ära":era,
       "Visueller Stil":visual_style,
       "Laufzeit":int(laufzeit),
       "IMDb von":float(imdb_von),
       "IMDb bis":float(imdb_bis)
  })

  ## Button zum Generieren der Empfehlungen 
  if button("Empfehlung generieren"):
      prefs_okay=len(session state['_preferences'].get("Genres",[]))==3
      
      if not prefs_okay:
          error("Bitte wähle genau drei Genres.")
          return
      
      log_interaction("Config saved","config_saved")
      
      with spinner("CineMate verarbeitet deine Eingaben..."):
          g1,g2,g3=session state['_preferences']['Genres']
          cfg={
              "Ära":session state['_preferences']['Ära'],
              "Visueller Stil":session state['_preferences']['Visueller Stil'],
              "Laufzeit":session state['_preferences']['Laufzeit'],
              "IMDb von":session state['_preferences']['IMDb von'],
              "IMDb bis":session state['_preferences']['IMDb bis']
          }

         markdown("<div id='erklaerung'></div>",unsafe_allow_html=True)

         write(f"Die Eingaben werden verarbeitet, um passende Filme zu finden. Genres: {g1}, {g2} und {g3}.")
         write(f"Die Konfiguration ({cfg}) dient als Grundlage für die Filmauswahl.")
         write("Kontrollhinweis: Die IMDb Datenbank umfasst über 6 Millionen Titel.")
         write("Hier sind die drei besten Treffer aus meiner Datenbank.")

         recs=generate_recommendations(cfg)
         session state["_recommendations"]=recs

         log_interaction("Recommendation generated","recommendation_generated")

      ## Nach Generierung automatisch scrollen 
      markdown("""
          <script>
              setTimeout(function(){
                  var explanation=document.getElementById('erklaerung');
                  if(explanation){
                      explanation.scrollIntoView({behavior:'smooth',block:'center'});
                  }
              },800);

              setTimeout(function(){
                  var recommendations=document.getElementById('empfehlungen');
                  if(recommendations){
                      recommendations.scrollIntoView({behavior:'smooth',block:'start'});
                  }
              },1800);
          </script>
      """,unsafe_allow_html=True)

     ## Anzeige der Empfehlungen falls vorhanden 
     if "recommendations" in session state and session state["recommendations"]:
         
         markdown("<div id='empfehlungen'></div>",unsafe_allow_html=True)
         
         markdown("### 🍿 Empfehlungen")
         
         for r in session state["_recommendations"]:
             container()
             col_left,col_right=_columns_([3,1],gap="medium")
             
             with col_left:
                 markdown(f"**{r[name]}**")
                 count_formatted=f"{r[anzahl_bewertungen]:,.}".replace(",",".")
                 write(f"Anzahl Bewertungen: {count_formatted}")
             
             with col_right:
                 markdown(f"**IMDb-Ranking: #{r[imdb_ranking]}**")

             divider()
         
         success("✅ Empfehlungen geladen!")
         write("Bitte gib den Code *01* ein – danach kann mit dem Fragebogen fortgefahren werden.")


if name=="main":
     main()
