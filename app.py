import os
import json
import httpx
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from supabase import create_client, Client

app = FastAPI()

# Configuration du dossier pour stocker la boutique finale
os.makedirs("theme", exist_ok=True)
app.mount("/static", StaticFiles(directory="theme"), name="static")

# CONFIGURATION SUPABASE
SUPABASE_URL = "https://spwrqwjhxjmnzszcstpm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNwd3Jxd2poeGptbnpzemNzdHBtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODAzMzA5NzksImV4cCI6MjA5NTkwNjk3OX0.PZKgsNZ0u0fPeSI_S5xd_AScoCKHfBQtceNZkXTTFtY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuration de l'API Mistral
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "lz1MXg4YkGe2jzd1wdHeFoXMYWJmexYn")
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
MODEL_NAME = "mistral-small-latest"
THEME_PATH = os.path.join("theme", "index.html")

# Utilisation de HTTPX Async pour ne JAMAIS bloquer le serveur
async def call_mistral_agent_async(prompt: str, system_instruction: str) -> str:
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.85
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(MISTRAL_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']


# --- SERVIR LE FORMULAIRE DE DÉPART (index.html) ---
@app.get("/", response_class=HTMLResponse)
async def read_index():
    if not os.path.exists("index.html"):
        return HTMLResponse(content="<h1>Erreur : index.html introuvable !</h1>", status_code=404)
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


# --- SERVIR LA PAGE D'INSCRIPTION SEULE (register.html) ---
@app.get("/register", response_class=HTMLResponse)
async def get_register_page():
    if not os.path.exists("register.html"):
        return HTMLResponse(content="<h1>Erreur : register.html introuvable !</h1>", status_code=404)
    with open("register.html", "r", encoding="utf-8") as f:
        return f.read()


# --- CORPS DE LA GÉNÉRATION IA ---
@app.post("/generate")
async def generate_store(theme: str = Form(...)):
    try:
        prompt_alpha = f"Donne un nom de marque, un slogan et un paragraphe d'accueil captivant pour une boutique sur le thème : {theme}. Réponds en JSON pur avec les clés 'nom', 'slogan', 'accueil'."
        system_alpha = "Tu es l'Agent Alpha, expert en marketing e-commerce. Tu réponds UNIQUEMENT en JSON pur sans balises Markdown."
        res_alpha_raw = await call_mistral_agent_async(prompt_alpha, system_alpha)
        
        prompt_beta = f"Génère une liste de 3 produits parfaits pour le thème : {theme}. Donne un nom, un prix et une courte description. Réponds en JSON pur (une liste d'objets) sans balises Markdown."
        system_beta = "Tu es l'Agent Beta, expert en merchandising. Tu réponds UNIQUEMENT en JSON pur sans balises Markdown."
        res_beta_raw = await call_mistral_agent_async(prompt_beta, system_beta)

        clean_alpha = res_alpha_raw.replace("```json", "").replace("```", "").strip()
        clean_beta = res_beta_raw.replace("```json", "").replace("```", "").strip()

        brand_data = json.loads(clean_alpha)
        products_data = json.loads(clean_beta)
        
    except Exception as e:
        return JSONResponse(content={"error": "Échec lors du parsing IA", "details": str(e)}, status_code=500)

    prompt_gamma = f"""
    Tu es un ingénieur Creative Front-End Senior. Tu dois concevoir un site e-commerce complet, ultra-moderne, premium et entièrement codé dans un seul fichier (index.html) pour la boutique "{brand_data.get('nom')}" basée sur la thématique spécifique : "{theme}".
    
    Données à inclure obligatoirement :
    - Slogan : {brand_data.get('slogan')}
    - Message d'accueil : {brand_data.get('accueil')}
    - Les produits suivants : {json.dumps(products_data)}
    
    CONSIGNES D'ARCHITECTURE HTML ET DE DESIGN :
    1. Inclus Tailwind CSS : <script src="https://cdn.tailwindcss.com"></script>
    2. Inclus la balise <script src="https://js.stripe.com/v3/"></script> dans le <head>.
    3. FONCTIONNALITÉ COMPTE CONNECTÉ (OBLIGATOIRE) :
       - Inclus Supabase dans le <head> : <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
       - Dans le menu de navigation (Navbar) du site généré, crée une zone visible avec l'id "user-profile-zone".
       - Ajoute un script en bas de page pour initialiser Supabase avec ces coordonnées EXACTES :
         URL : "{SUPABASE_URL}"
         KEY : "{SUPABASE_KEY}"
       - Ce script doit vérifier la session avec `supabase.auth.getUser()`. Si un utilisateur est connecté, remplace immédiatement le contenu de "user-profile-zone" par un badge stylisé affichant son adresse e-mail (ex: "👤 email@domaine.com") parfaitement intégré dans le thème graphique de la boutique.
    4. Ne fais JAMAIS une structure classique en blocs empilés basiques. Crée une mise en page asymétrique et immersive adaptée à la thématique "{theme}".
    5. Choisis une palette de couleurs digne d'un grand studio : des dégradés subtils, des effets de flou et de transparence haut de gamme (backdrop-blur-md), et des typographies soignées.
    6. Pas d'images vides brutes : remplace les visuels des produits par des conteneurs <div> artistiques avec des dégradés abstraits ou des icônes minimalistes.
    7. Inclus un système de panier d'achat interactif codé proprement en JavaScript (panneau coulissant ou modal).

    Renvoie UNIQUEMENT le code HTML complet commençant par <!DOCTYPE html>. Pas de balises markdown ```html.
    """
    system_gamma = "Tu es un ingénieur Creative Front-End de génie, spécialisé dans les interfaces UI/UX minimalistes, fluides et ultra-modernes."
    
    try:
        final_html = await call_mistral_agent_async(prompt_gamma, system_gamma)
        final_html = final_html.replace("```html", "").replace("```", "").strip()

        with open(THEME_PATH, "w", encoding="utf-8") as f:
            f.write(final_html)
            
        # Génération d'une clé de version aléatoire pour éviter le cache du navigateur
        anti_cache_version = os.urandom(4).hex()
        # Formatage propre du nom de fichier pour le téléchargement
        safe_filename = theme.replace(' ', '_').lower()

        return HTMLResponse(content=f"""
            <div style="font-family: -apple-system, sans-serif; max-width: 460px; margin: 80px auto; text-align: center; background: #ffffff; padding: 40px; border-radius: 12px; border: 1px solid #e0e0e0; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                <h2 style="color: #111; font-size: 22px; font-weight: 600; margin-bottom: 12px; letter-spacing: -0.5px;">🎉 Version Pro Max Générée !</h2>
                <p style="color: #666; font-size: 14px; margin-bottom: 24px; line-height: 1.5;">L'Agent Gamma a appliqué les standards UI/UX pour le thème : <strong>{theme}</strong>.</p>
                
                <p style="margin-bottom: 12px;">
                    <a href="/static/index.html?v={anti_cache_version}" target="_blank" style="display: block; background: #000; color: #fff; padding: 12px; text-decoration: none; border-radius: 8px; font-weight: 500; font-size: 14px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        Voir ma boutique sur-mesure
                    </a>
                </p>

                <p style="margin-bottom: 24px;">
                    <a href="/static/index.html" download="ma_boutique_{safe_filename}.html" style="display: block; background: #f3f4f6; color: #1f2937; padding: 12px; text-decoration: none; border-radius: 8px; font-weight: 500; font-size: 14px; border: 1px solid #e5e7eb; transition: background 0.2s;">
                        📥 Télécharger le fichier HTML
                    </a>
                </p>

                <a href="/" style="color: #666; font-size: 13px; text-decoration: none; font-weight: 500;">Créer un autre style</a>
            </div>
        """)
    except Exception as e:
        return JSONResponse(content={"error": f"Erreur lors de la génération par Gamma : {str(e)}"}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)