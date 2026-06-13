import os
import json
import httpx
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client

app = FastAPI()

# SÉCURITÉ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        "temperature": 0.15  # Rigueur technique maximale
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(MISTRAL_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']


@app.get("/", response_class=HTMLResponse)
async def read_index():
    if not os.path.exists("index.html"):
        return HTMLResponse(content="<h1>Erreur : index.html introuvable !</h1>", status_code=404)
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/generate")
async def generate_store(theme: str = Form(...)):
    try:
        # 1. AGENT ALPHA : Marketing
        prompt_alpha = f"Donne un nom de marque, un slogan et un paragraphe d'accueil captivant pour une boutique sur le thème : {theme}. Réponds en JSON pur avec les clés 'nom', 'slogan', 'accueil'."
        system_alpha = "Tu es l'Agent Alpha, expert en marketing e-commerce. Tu réponds UNIQUEMENT en JSON pur sans balises Markdown."
        res_alpha_raw = await call_mistral_agent_async(prompt_alpha, system_alpha)
        
        # 2. AGENT BETA : Merchandising
        prompt_beta = f"Génère une liste de 3 produits parfaits pour le thème : {theme}. Donne un nom, un prix et une courte description. Réponds en JSON pur (une liste d'objets) sans balises Markdown."
        system_beta = "Tu es l'Agent Beta, expert en merchandising. Tu réponds UNIQUEMENT en JSON pur sans balises Markdown."
        res_beta_raw = await call_mistral_agent_async(prompt_beta, system_beta)

        clean_alpha = res_alpha_raw.replace("```json", "").replace("```", "").strip()
        clean_beta = res_beta_raw.replace("```json", "").replace("```", "").strip()

        brand_data = json.loads(clean_alpha)
        products_data = json.loads(clean_beta)
        
    except Exception as e:
        return JSONResponse(content={"error": "Échec lors du parsing IA des données de base", "details": str(e)}, status_code=500)

    # 3. AGENT GAMMA : Développeur Front-End (Version Sans Images Cassées et avec Panier Blindé)
    prompt_gamma = f"""
    Tu es un ingénieur Creative Front-End Senior. Tu dois concevoir un site e-commerce complet, ultra-moderne, premium et entièrement codé dans un seul fichier (index.html) pour la boutique "{brand_data.get('nom')}" basée sur la thématique spécifique : "{theme}".
    
    Données à inclure obligatoirement :
    - Slogan : {brand_data.get('slogan')}
    - Message d'accueil : {brand_data.get('accueil')}
    - Les produits suivants : {json.dumps(products_data)}
    
    CONSIGNES CRITIQUES SÉCURITÉ & LOGIQUE :
    1. Inclus Tailwind CSS : <script src="https://cdn.tailwindcss.com"></script>
    
    2. INTERDICTION DES IMAGES EXTERNES : N'utilise AUCUN lien d'image externe (pas de balise img pointant vers des placeholders qui provoquent des erreurs ERR_CONNECTION_CLOSED). À la place, représente chaque produit visuellement par un grand EMOJI très stylisé et centré au milieu d'un carré de couleur moderne en Tailwind CSS.
    
    3. LE PANIER D'ACHAT INTERACTIF :
       - Dans la Navbar, ajoute un bouton avec l'id exact "cart-btn" (ex: 🛒 Panier (<span id="cart-count">0</span>)).
       - Crée un volet latéral pour le panier avec l'id exact "cart-sidebar" (ajoute la classe Tailwind "hidden" par défaut pour le masquer). Il doit contenir une div interne avec l'id exact "cart-items-container".
       - Chaque bouton de produit doit posséder exactement cet attribut : onclick="addToCart('NOM_DU_PRODUIT', PRIX)" (remplace dynamiquement par le vrai nom du produit nettoyé et son prix numérique).
       - Inclus ce script JavaScript exact à la fin de ton code pour faire fonctionner le panier :
         <script>
         let cart = [];
         function addToCart(name, price) {{
             cart.push({{ name, price }});
             document.getElementById('cart-count').innerText = cart.length;
             updateCartUI();
         }}
         function updateCartUI() {{
             const container = document.getElementById('cart-items-container');
             let html = '<h3 class="text-xl font-bold mb-4">Votre Panier</h3>';
             let total = 0;
             if (cart.length === 0) {{
                 html += '<p class="text-gray-500 text-sm">Votre panier est vide.</p>';
             }} else {{
                 cart.forEach(item => {{
                     html += '<div class="flex justify-between border-b py-2 text-sm"><span>' + item.name + '</span><span class="font-bold">' + item.price + '€</span></div>';
                     total += item.price;
                 }});
             }}
             html += '<div class="mt-4 font-bold text-lg">Total: ' + total.toFixed(2) + '€</div>';
             html += '<button class="w-full mt-4 bg-black text-white py-2 rounded text-sm font-medium">Valider la commande</button>';
             html += '<button onclick="toggleCart()" class="w-full mt-2 text-xs text-gray-400 hover:text-black">Fermer le panier</button>';
             container.innerHTML = html;
         }}
         function toggleCart() {{
             const sidebar = document.getElementById('cart-sidebar');
             sidebar.classList.toggle('hidden');
         }}
         document.getElementById('cart-btn')?.addEventListener('click', toggleCart);
         </script>

    4. Dans la Navbar, ajoute un bouton avec l'id exact "download-site-btn" pour télécharger le site.
    5. Ajoute ce script juste avant la fermeture du body pour activer le téléchargement :
       <script>
       document.getElementById('download-site-btn')?.addEventListener('click', function(e) {{
           e.preventDefault();
           const blob = new Blob([document.documentElement.outerHTML], {{ type: 'text/html' }});
           const url = URL.createObjectURL(blob);
           const a = document.createElement('a');
           a.href = url;
           a.download = 'ma_boutique.html';
           document.body.appendChild(a);
           a.click();
           document.body.removeChild(a);
       }});
       </script>
    6. Rends le design magnifique, immersif et épuré.

    Renvoie UNIQUEMENT le code HTML complet commençant par <!DOCTYPE html>. Pas de balises markdown ```html.
    """
    system_gamma = "Tu es un ingénieur Creative Front-End de génie, spécialisé dans les interfaces UI/UX minimalistes et le JavaScript fonctionnel sans images cassées."
    
    try:
        final_html = await call_mistral_agent_async(prompt_gamma, system_gamma)
        final_html = final_html.replace("```html", "").replace("```", "").strip()

        # --- 4. AGENT DELTA : Super-Débugueur Polyglotte ---
        print("🔧 Activation de l'Agent Delta : Analyse et sécurisation multi-langages (HTML, CSS, JS, PHP, Python)...")
        
        prompt_delta = f"""
        Tu es l'Agent Delta, un ingénieur QA et débugueur Senior d'élite. Ton rôle est d'analyser, de réparer et d'optimiser le code fourni.
        Tu maîtrises à la perfection le HTML5, le CSS (Tailwind), le JavaScript (ES6+), le PHP 8+ et Python 3.
        
        CRITIQUE POUR LE DESIGN ET LE PANIER :
        Tu DOIS impérativement vérifier que la ligne du CDN Tailwind est présente dans le <head> : <script src="[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)"></script>.
        Assure-toi qu'aucune image cassée provoquant un plantage réseau n'est présente.
        Vérifie que chaque bouton possède 'onclick="addToCart(...)"' et que la fonction correspondante 'function addToCart(name, price)' est présente et fonctionnelle.
        
        Inspecte le code ci-dessous et effectue les corrections nécessaires :
        1. Répare les balises HTML mal fermées ou manquantes.
        2. Assure-toi que les classes Tailwind CSS sont bien orthographiées.
        3. Corrige les erreurs de syntaxe JavaScript (promesses, fonctions mal fermées, accolades manquantes).
        4. Si des structures logiques ressemblant à du PHP ou du Python s'y trouvent, assure-toi qu'elles respectent scrupuleusement leur syntaxe.
        5. Interdiction absolue de supprimer ou casser le mécanisme du panier d'achat ou du bouton de téléchargement ('download-site-btn').
        
        Voici le code source à analyser et réparer :
        {final_html}
        
        Renvoie UNIQUEMENT le code corrigé final, sans fioritures, sans explications et sans bloc de code Markdown (pas de ```).
        """
        system_delta = "Tu es un compilateur humain et un expert en refactoring de code. Tu répares le HTML, CSS, JS, PHP et Python sans jamais altérer les fonctionnalités interactives demandées."
        
        final_html = await call_mistral_agent_async(prompt_delta, system_delta)
        final_html = final_html.replace("```html", "").replace("```", "").strip()

        return HTMLResponse(content=final_html, status_code=200)
        
    except Exception as e:
        return JSONResponse(content={"error": f"Erreur critique lors de la réparation. Détails : {str(e)}"}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
