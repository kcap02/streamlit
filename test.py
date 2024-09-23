from fastapi import FastAPI,HTTPException
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
import re
from dotenv import load_dotenv
import os
import time
import pandas as pd


# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

app=FastAPI()

class ScrapeRequest(BaseModel):
    url: str

@app.get("/")
def greet():
    return {"message": "bonjour"}

    

@app.post("/scrape")
# Fonction de scraping
def scraping_data(request: ScrapeRequest):
    
    # Extraire l'URL de la requête

    
    url_website = request.url

    API_KEY = os.getenv('API_KEY')
    if url_website:
        url='https://proxy.scrapeops.io/v1/'
        params={
        'api_key': API_KEY,
        'url': url_website,
        }
        # Liste pour stocker tous les prix
        all_products = []
        try:
            response = requests.get(url,params=params)
            response.raise_for_status()
            # Parsing du HTML avec BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extraire le nombre total de pages
            last_page_element  = soup.select_one('span.listing-pagination__item.listing-pagination__item--last')
            
            if last_page_element:
                last_page_link  = last_page_element.get('data-link')
                if last_page_link:
                    # Extraire le numéro de la page à partir de l'URL
                    match = re.search(r'page=(\d+)', last_page_link)
                    if match:
                        total_pages = int(match.group(1))
                    else:
                        total_pages = 1  # Si le numéro de page n'est pas trouvé, on suppose qu'il n'y a qu'une seule page
                else:
                    total_pages = 1  # Si l'attribut 'data-link' n'est pas trouvé, on suppose qu'il n'y a qu'une seule page
            else:
                total_pages = 1  # Si l'élément de pagination n'est pas trouvé, on suppose qu'il n'y a qu'une seule page

            # Boucle pour parcourir toutes les pages
            for page in range(1, total_pages + 1):
                # Mettre à jour les paramètres pour la page courante
                params['url'] = f'{url_website}?page={page}'
                if page==1:
                    params['url'] = f'{url_website}'
                # Envoi de la requête
                response = requests.get(url, params=params)
                response.raise_for_status()  # Vérifie si la requête a réussi

                # Parsing du HTML avec BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')

                # Sélection de tous les éléments de produit
                product_elements = soup.select('div.listing-item')


            

                if product_elements:
                    for product_element in product_elements:
                        # Extraire le nom du produit
                        product_name_elements = product_element.select_one('a.listing-item__name')
                        product_name = product_name_elements.get_text(strip=True) if product_name_elements else product_element.select_one('span.listing-item__name').get_text(strip=True)

                        
                        print(product_name)
                        product_name_detail = product_element.select_one('span.listing-item__name-span').get_text(strip=True)
                        
                        product_price  = product_element.select_one('div.listing-item__price-new').get_text(strip=True)
                        #print(f'Prix trouvé: {price}')

                        # Ajouter les informations du produit à la liste
                        all_products.append({
                            'name': product_name,
                            'name_detail': product_name_detail,
                            'price': product_price
                            
                        })
                        print(f'Produit trouvé: {product_name}, Details: {product_name_detail}, Prix: {product_price}')
                else:
                    print(f'Aucun prix trouvé sur la page {page}')

                # Ajouter un délai de 5 secondes entre les requêtes
                time.sleep(5)

        except requests.RequestException as e:
            print(f"Erreur lors de la requête: {e}")

        # Créer un DataFrame à partir de la liste de produits
        df = pd.DataFrame(all_products)

        # Convertir le DataFrame en JSON
        df_json = df.to_json(orient='records')

        # Renvoyer la réponse JSON
        response_data = {
            'status': 'Données scrapées avec succès',
            'message': f'Données scrapées depuis {url}',
            'data': df_json
        }
        return response_data

    else:
        raise HTTPException(status_code=400, detail="URL manquante dans la requête")

