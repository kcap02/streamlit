import streamlit as st
import requests
import pandas as pd
import os
import io

# Titre Interface Streamlit
st.title("Outil de scraping")

# Champ de saisie pour l'URL
url = st.text_input('Entrez l\'URL à scraper :')


if st.button('Scraper et Enregistrer'):
    if url:
        link={"url": url}
        req=requests.post("https://fastapiimage-452158084207.europe-west9.run.app/scrape",json=link)
        if req.status_code == 200:
            st.success('Les données ont été scrapées avec succès')
            response_data = req.json()
            json_data = response_data['data']
            json_io = io.StringIO(json_data)
            # Convertir les données JSON en DataFrame
            df = pd.read_json(json_io, orient='records')
            st.write('Prévisualisation des données :')
            st.dataframe(df)
            if not df.empty:
                df.to_excel('scraped_data.xlsx', index=False)
                st.success('Les données ont été enregistrées dans scraped_data.xlsx')
                st.write('Prévisualisation des données :')
                st.dataframe(df)
            else:
                st.warning('Aucune donnée trouvée.')
        else:
            st.error(f'Erreur: {req.status_code}')
            st.write(req.text)
    else:
        st.warning('Veuillez entrer une URL valide.')
else:
    st.warning('Veuillez entrer une URL valide.')


if os.path.exists('scraped_data.xlsx'):
    with open('scraped_data.xlsx', 'rb') as f:
        bytes_data = f.read()
    st.download_button(label='Télécharger le fichier Excel', data=bytes_data, file_name='scraped_data.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
else:
    st.error('Le fichier scraped_data.xlsx n\'existe pas.')