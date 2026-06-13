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
        "temperature": 0.15
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
        prompt_beta = f"Génère une liste de 4 produits parfaits et pertinents pour le thème : {theme}. Donne un nom, un prix (ex: '95,00 €') et une courte description. Réponds en JSON pur (une liste d'objets) sans balises Markdown."
        system_beta = "Tu es l'Agent Beta, expert en merchandising. Tu réponds UNIQUEMENT en JSON pur sans balises Markdown."
        res_beta_raw = await call_mistral_agent_async(prompt_beta, system_beta)

        clean_alpha = res_alpha_raw.replace("```json", "").replace("```", "").strip()
        clean_beta = res_beta_raw.replace("```json", "").replace("```", "").strip()

        brand_data = json.loads(clean_alpha)
        products_data = json.loads(clean_beta)
        
    except Exception as e:
        return JSONResponse(content={"error": "Échec lors du parsing IA des données de base", "details": str(e)}, status_code=500)

    # 3. AGENT GAMMA : Développeur Front-End
    prompt_gamma = f"""
    Tu es un ingénieur Creative Front-End Senior. Tu dois concevoir un site e-commerce complet, premium, minimaliste et entièrement codé dans un seul fichier (index.html) pour la boutique "{brand_data.get('nom')}" basée sur la thématique spécifique : "{theme}".
    
    Données à inclure obligatoirement :
    - Slogan : {brand_data.get('slogan')}
    - Message d'accueil : {brand_data.get('accueil')}
    - Les produits suivants : {json.dumps(products_data)}
    
    CONSIGNES CRITIQUES DE STRUCTURE ET DE SÉCURITÉ JAVASCRIPT :
    1. Inclus Tailwind CSS : <script src="https://cdn.tailwindcss.com"></script>
    
    2. IMAGES DES PRODUITS : Utilise de vraies belles images d'illustration issues d'Unsplash adaptées au thème "{theme}" via l'URL `https://images.unsplash.com/...`.
    
    3. STRUCTURE STRICTE DE LA NAVBAR :
       Dans l'en-tête de la page (`header`), tout à droite, crée un conteneur flex aligné : `flex items-center space-x-6`. À l'intérieur, place obligatoirement :
       - Le bouton de téléchargement : `<button id="download-site-btn" class="px-3 py-1.5 bg-black hover:bg-gray-800 text-white text-xs rounded font-medium transition">📥 Télécharger</button>`
       - Le bouton panier icône : Un bouton avec `onclick="toggleCart()"` contenant un SVG de panier et le badge `<span id="cart-count" class="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full hidden">0</span>`.

    4. LE PANIER D'ACHAT INTERACTIF (DRAWER LATÉRAL) :
       - Ajoute la div du panier latéral : `<div id="cart-drawer" class="fixed inset-y-0 right-0 w-full max-w-md bg-white shadow-2xl z-50 transform translate-x-full transition-transform duration-300 flex flex-col border-l border-gray-200">`.
       - À l'intérieur, inclus la zone des éléments : `<div id="cart-items" class="flex-1 overflow-y-auto p-6 space-y-4">`.
       - Inclus la zone du total avec le bouton valider : `<p id="cart-total">0,00 €</p>` et le bouton `<button onclick="checkout()" class="w-full bg-black text-white text-center py-3 rounded-md font-medium hover:bg-gray-800 transition">Passer la commande</button>`.
       
    5. STRUCTURE OBLIGATOIRE DE CHAQUE CARTE PRODUIT :
       Chaque produit généré doit posséder uniquement et obligatoirement un bouton écrit "Ajouter au panier". Les boutons écrits "Voir details" ou "Voir" sont formellement interdits.
       Encapsule chaque produit dans une div avec la classe exacte `product-card group relative flex flex-col bg-white border border-gray-200 rounded-lg overflow-hidden shadow-sm p-4`.
       À l'intérieur, place obligatoirement :
       - La balise image avec la classe : `class="product-img ..."`
       - Le titre du produit avec la classe : `class="product-name ..."`
       - Le prix écrit avec la classe : `class="product-price ..."`
       - Le bouton d'ajout exact : `<button onclick="addToCart(this)" class="mt-4 w-full bg-gray-900 text-white text-xs py-2.5 rounded font-medium hover:bg-black transition">Ajouter au panier</button>`

    6. LOGIQUE JAVASCRIPT ULTRA-SÉCURISÉE (SANS REDÉCLARATION NI COMPOSANT BRISÉ) :
       N'utilise aucun template string contenant le symbole dollar pour éviter les conflits de génération. Utilise la concaténation de chaînes standard.

    7. LOGIQUE JAVASCRIPT EXACTE DU PANIER ET DU TÉLÉCHARGEMENT :
       Inclus scrupuleusement ces fonctions de script avant la fermeture du body :
       <script>
       var cart = [];
       function toggleCart() {{
           var drawer = document.getElementById('cart-drawer');
           if(drawer) {{ drawer.classList.toggle('translate-x-full'); }}
       }}
       function addToCart(button) {{
           var card = button.closest('.product-card');
           var name = card.querySelector('.product-name').innerText;
           var priceText = card.querySelector('.product-price').innerText;
           var img = card.querySelector('.product-img').src;
           var existingItem = null;
           for (var i = 0; i < cart.length; i++) {{
               if (cart[i].name === name) {{
                   existingItem = cart[i];
                   break;
               }}
           }}
           if (existingItem) {{
               existingItem.quantity += 1;
           }} else {{
               cart.push({{ name: name, price: priceText, img: img, quantity: 1 }});
           }}
           updateCartUI();
           var drawer = document.getElementById('cart-drawer');
           if(drawer) {{ drawer.classList.remove('translate-x-full'); }}
       }}
       function changeQuantity(index, delta) {{
           cart[index].quantity += delta;
           if (cart[index].quantity <= 0) {{ cart.splice(index, 1); }}
           updateCartUI();
       }}
       function removeItem(index) {{
           cart.splice(index, 1);
           updateCartUI();
       }}
       function parsePrice(priceStr) {{
           var clean = priceStr.replace(/[^0-9.,]/g, '');
           if (clean.includes(',') && clean.includes('.')) {{ clean = clean.replace(/,/g, ''); }}
           else if (clean.includes(',')) {{ clean = clean.replace(',', '.'); }}
           return parseFloat(clean) || 0;
       }}
       function updateCartUI() {{
           var itemsContainer = document.getElementById('cart-items');
           var countBadge = document.getElementById('cart-count');
           var totalContainer = document.getElementById('cart-total');
           if(!itemsContainer || !countBadge || !totalContainer) return;
           itemsContainer.innerHTML = '';
           var totalPrice = 0;
           var totalItems = 0;
           
           for (var i = 0; i < cart.length; i++) {{
               var item = cart[i];
               var numericPrice = parsePrice(item.price);
               totalPrice += numericPrice * item.quantity;
               totalItems += item.quantity;
               
               var itemHtml = '<div class="flex items-center justify-between border-b border-gray-100 pb-4">' +
                   '<div class="flex items-center space-x-4">' +
                       '<img src="' + item.img + '" class="w-16 h-16 object-cover rounded-md bg-gray-100">' +
                       '<div>' +
                           '<h5 class="text-sm font-semibold text-gray-900">' + item.name + '</h5>' +
                           '<p class="text-xs text-gray-500">' + item.price + '</p>' +
                           '<div class="flex items-center space-x-2 mt-2">' +
                               '<button onclick="changeQuantity(' + i + ', -1)" class="bg-gray-100 text-gray-800 px-2 py-0.5 rounded text-xs font-bold hover:bg-gray-200">-</button>' +
                               '<span class="text-xs font-medium">' + item.quantity + '</span>' +
                               '<button onclick="changeQuantity(' + i + ', 1)" class="bg-gray-100 text-gray-800 px-2 py-0.5 rounded text-xs font-bold hover:bg-gray-200">+</button>' +
                           '</div>' +
                       '</div>' +
                   '</div>' +
                   '<button onclick="removeItem(' + i + ')" class="text-xs text-red-500 hover:text-red-700 underline">Enlever</button>' +
               '</div>';
               itemsContainer.innerHTML += itemHtml;
           }}
           
           if (totalItems > 0) {{
               countBadge.innerText = totalItems;
               countBadge.classList.remove('hidden');
           }} else {{
               countBadge.classList.add('hidden');
               itemsContainer.innerHTML = '<p class="text-gray-500 text-center py-8">Votre panier est vide.</p>';
           }}
           var currency = '€';
           if (cart.length > 0 && cart[0].price.includes('$')) currency = '$';
           totalContainer.innerText = totalPrice.toFixed(2).replace('.', ',') + ' ' + currency;
       }}
       function checkout() {{
           if (cart.length === 0) {{ alert("Votre panier est vide !"); return; }}
           fetch('/.netlify/functions/create-checkout', {{
               method: 'POST',
               headers: {{ 'Content-Type': 'application/json' }},
               body: JSON.stringify({{ items: cart }}),
           }})
           .then(function(res) {{ return res.ok ? res.json() : res.json().then(function(json) {{ return Promise.reject(json); }}); }})
           .then(function(data) {{ window.location = data.url; }})
           .catch(function(e) {{ console.error(e); alert("Une erreur est survenue lors de la connexion avec Stripe."); }});
       }}
       
       document.getElementById('download-site-btn')?.addEventListener('click', function(e) {{
           e.preventDefault();
           var blob = new Blob([document.documentElement.outerHTML], {{ type: 'text/html' }});
           var url = URL.createObjectURL(blob);
           var a = document.createElement('a');
           a.href = url;
           a.download = 'ma_boutique.html';
           document.body.appendChild(a);
           a.click();
           document.body.removeChild(a);
       }});
       </script>
    """
    system_gamma = "Tu es un ingénieur Creative Front-End de génie. Tu n'utilises JAMAIS de template literals backticks ni de signe dollar dans tes fonctions JS d'insertion HTML."
    
    try:
        final_html = await call_mistral_agent_async(prompt_gamma, system_gamma)
        final_html = final_html.replace("```html", "").replace("```", "").strip()

        # --- 4. AGENT DELTA : Super-Débugueur Polyglotte ---
        print("🔧 Activation de l'Agent Delta...")
        
        prompt_delta = f"""
        Tu es l'Agent Delta, un ingénieur QA d'élite. Tu dois valider le code HTML fourni.
        Tu as l'interdiction de laisser un bouton écrit 'Voir' ou 'Voir détails'. Modifie son texte pour qu'il soit écrit 'Ajouter au panier' avec l'attribut onclick="addToCart(this)".
        Conserve le système complet de panier en chaînes concaténées et le bouton download-site-btn.
        
        Voici le code source à valider :
        {final_html}
        
        Renvoie uniquement le code HTML final corrigé, sans bloc markdown (pas de ```).
        """
        system_delta = "Tu es un débugueur intransigeant. Tu appliques les corrections de boutons de panier à la lettre."
        
        final_html = await call_mistral_agent_async(prompt_delta, system_delta)
        final_html = final_html.replace("```html", "").replace("```", "").strip()

        return HTMLResponse(content=final_html, status_code=200)
        
    except Exception as e:
        return JSONResponse(content={"error": f"Erreur critique lors de la réparation. Détails : {str(e)}"}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
