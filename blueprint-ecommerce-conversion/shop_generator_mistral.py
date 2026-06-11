import asyncio
import os
import json
import requests

# 🔑 TA CLÉ API MISTRAL AI (Gratuite et sans CB)
MISTRAL_API_KEY = "lz1MXg4YkGe2jzd1wdHeFoXMYWJmexYn"

def appeler_mistral_api(prompt: str) -> str:
    """Parle à Mistral AI via requêtes HTTP directes"""
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MISTRAL_API_KEY}"
    }
    payload = {
        "model": "mistral-small-latest",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"\n❌ Erreur Mistral (Status {response.status_code}) : {response.text}")
            raise Exception("Erreur API")
        
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        raise Exception(f"Connexion impossible à Mistral : {e}")


class CopywriterAgent:
    def __init__(self):
        self.name = "Agent-Alpha (Copywriter)"

    async def generate_branding(self, theme: str):
        print(f"✍️ [{self.name}] Demande à l'IA de créer le branding pour : {theme}...")
        prompt = f"""
        Tu es un expert en marketing e-commerce. Crée une marque pour une boutique sur le thème : '{theme}'.
        Réponds UNIQUEMENT sous la forme d'un objet JSON strict avec cette structure exacte, sans texte avant ni après, pas de blabla :
        {{
            "brand": "NOM DE LA MARQUE EN MAJUSCULES",
            "hero": "Slogan principal accrocheur de 4-5 mots",
            "sub": "Une phrase de description élégante pour la sous-section."
        }}
        """
        res = await asyncio.to_thread(appeler_mistral_api, prompt)
        clean = res.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)


class ProductAgent:
    def __init__(self):
        self.name = "Agent-Beta (Product-Specialist)"

    async def generate_products(self, theme: str):
        print(f"📦 [{self.name}] Demande à l'IA de concevoir le catalogue produit...")
        prompt = f"""
        Génère une liste de 4 produits uniques, haut de gamme et réalistes pour une boutique sur le thème : '{theme}'.
        Pour chaque produit, fournis une URL d'image libre de droit provenant d'Unsplash en rapport DIRECT avec le produit.
        Réponds UNIQUEMENT sous la forme d'un tableau JSON strict avec cette structure exacte, sans blabla autour :
        [
            {{"name": "Nom du produit 1", "price": "89,00 €", "img": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?q=80&w=600&auto=format&fit=crop"}},
            {{"name": "Nom du produit 2", "price": "120,00 €", "img": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600&auto=format&fit=crop"}},
            {{"name": "Nom du produit 3", "price": "45,00 €", "img": "https://images.unsplash.com/photo-105740420928-5e560c06d30e?q=80&w=600&auto=format&fit=crop"}},
            {{"name": "Nom du produit 4", "price": "150,00 €", "img": "https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?q=80&w=600&auto=format&fit=crop"}}
        ]
        """
        res = await asyncio.to_thread(appeler_mistral_api, prompt)
        clean = res.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)


class CoderAgent:
    def __init__(self):
        self.name = "Agent-Gamma (Coder/Designer)"

    async def rewrite_html(self, theme: str, branding: dict, products: list):
        print(f"🛠️ [{self.name}] Intégration du Slider et restructuration complète du CSS/HTML...")
        html_path = os.path.join("theme", "index.html")
        if not os.path.exists(html_path):
            print(f"❌ Erreur : Le fichier {html_path} est introuvable.")
            return

        with open(html_path, "r", encoding="utf-8") as file:
            content = file.read()

        if not os.path.exists(html_path + ".bak"):
            with open(html_path + ".bak", "w", encoding="utf-8") as bak:
                bak.write(content)

        with open(html_path + ".bak", "r", encoding="utf-8") as bak:
            template_content = bak.read()

        # --- NOUVEAU PROMPT AVEC INSTRUCTION SLIDER IMAGE ---
        prompt_gamma = f"""
        Tu es Agent-Gamma, un Directeur Artistique Mondial et Développeur Frontend d'élite.
        Ton but est de réécrire le code HTML fourni pour injecter un Slider d'images et un design unique basé STRICTEMENT sur le thème '{theme}'.
        
        Voici le code HTML de base actuel :
        \"\"\"{template_content}\"\"\"

        Tu dois appliquer les règles de l'UI/UX pour métamorphoser le site :

        1. AJOUT D'UN SLIDER D'IMAGES (CAROUSEL) :
           - Juste en dessous de la barre de navigation (Navbar) et AU-DESSUS du titre principal, tu dois obligatoirement intégrer un magnifique Slider/Carrousel d'images fluide.
           - Ce slider doit utiliser les images des produits fournis : {json.dumps(products, ensure_ascii=False)}.
           - Chaque diapositive du slider doit afficher l'image du produit en grand (hauteur fixe élégante, ex: 450px ou 500px, avec un effet d'assombrissement léger pour la lisibilité) et afficher en surimpression le Nom du produit et un bouton "Découvrir".
           - Si le template utilise Bootstrap, utilise le composant 'carousel' de Bootstrap. Sinon, écris un système de slider ultra-propre en HTML/CSS/JS.

        2. ANALYSE ET AMBIANCE VISUELLE DU THÈME :
           - Si Nourriture/Tradition -> Ambiance chaleureuse, lumineuse. Couleurs gourmandes (miel, crème, terracotta, touches d'or).
           - Si Tech/Vitesse/Gaming -> Ambiance sombre (Dark Mode), contrastes électriques/néons, lignes acérées.
           - Si Luxe/Mode/Bien-être -> Design minimaliste, beaucoup d'espaces blancs, écriture fine, touches dorées ou noires profondes.

        3. LOI DES COULEURS PRO (60-30-10) :
           Génère une palette de couleurs sur-mesure dans la balise <style> :
           - 60% (Fond du site) : Clair pour la nourriture/luxe, sombre pour la tech/gaming.
           - 30% (Cartes produits, menus, blocs de texte) : Harmonie et lisibilité maximale.
           - 10% (Boutons "Ajouter au panier", boutons du Slider) : Une couleur vibrante qui appelle au clic.

        4. TYPOGRAPHIE, FORMES ET FORCE STYLISTIQUE :
           - Adapte la police de caractères (font-family) selon le thème ('Georgia'/'Playfair' pour traditionnel/luxe, 'Poppins'/'Inter' pour moderne).
           - Formes (border-radius) : Donne du style ! Arrondis très doux (ex: 20px !important) pour de la nourriture, très angulaires et carrés (0px) pour de la tech.

        5. LOGIQUE D'INTÉGRATION DES DONNÉES :
           - Injecte le Branding : Nom = {branding['brand']}, Titre Principal = {branding['hero']}, Sous-titre = {branding['sub']}.
           - Injecte les 4 produits du Catalogue dans la grille des produits : {json.dumps(products, ensure_ascii=False)}.
           - ACCENT CRITIQUE : Conserve impérativement la logique JavaScript du panier d'achat, les événements onclick et les ID des boutons pour que le système de paiement Stripe continue de fonctionner sans aucun bug.

        Renvoie-moi UNIQUEMENT le code HTML complet mis à jour. Ne mets aucune explication avant ou après, commence directement par <!DOCTYPE html> et finis par </html>.
        """

        res = await asyncio.to_thread(appeler_mistral_api, prompt_gamma)
        clean_html = res.replace("```html", "").replace("```", "").strip()

        with open(html_path, "w", encoding="utf-8") as file:
            file.write(clean_html)
            
        print(f"✅ [{self.name}] Le slider a été intégré et le site a été relooké avec succès !")


async def main():
    print("👑 [Jarvis-Manager] Usine IA connectée via l'API Mistral AI.")
    theme_choisi = input("👉 Entrez un thème TOTALEMENT LIBRE pour votre boutique : ")

    alpha = CopywriterAgent()
    beta = ProductAgent()
    gamma = CoderAgent()

    print(f"\n🚨 [Jarvis-Manager] Consultation en temps réel de l'IA...")
    try:
        branding = await alpha.generate_branding(theme_choisi)
        
        print("⏳ [Jarvis-Manager] Petite pause de sécurité de 2 secondes...")
        await asyncio.sleep(2)
        
        products = await beta.generate_products(theme_choisi)
        
        print(f"\n🚨 [Jarvis-Manager] L'IA a répondu avec succès. Passage à l'intégration graphique.")
        await gamma.rewrite_html(theme_choisi, branding, products)
        
        print("\n✨ PROCESSUS TERMINÉ ! Glisse ton dossier sur Netlify, puis rafraîchis ton navigateur (Ctrl + F5) pour admirer ton magnifique Slider !")
    except Exception as e:
        print(f"\n❌ Le processus a échoué : {e}")

if __name__ == "__main__":
    asyncio.run(main())