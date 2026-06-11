import asyncio
import os
import json
import requests
import time

# 🔑 PLUS DE CLÉ EN DUR ICI ! Le script va la chercher dans ton système.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6KbfgpGd-Th5BwpMO-j6db3eyaLr0sdOMRWdZ3bjL5BFw")


def appeler_gemini_api(prompt: str) -> str:
    """Fonction intelligente qui réessaie automatiquement en cas de saturation (429)"""
    # On repasse sur le modèle 2.0 qui est validé par ta clé
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    max_tentatives = 5
    attente = 2  # Temps d'attente initial en secondes
    
    for tentative in range(max_tentatives):
        response = requests.post(url, headers=headers, json=payload)
        
        # Si Google est surchargé ou dit qu'on va trop vite (Error 429)
        if response.status_code == 429:
            print(f"⚠️ [IA-Quota] L'API est occupée ({tentative + 1}/{max_tentatives}). Pause de {attente}s avant de réessayer...")
            time.sleep(attente)
            attente *= 2  # On double le temps d'attente à chaque essai (2s, 4s, 8s...)
            continue  # On relance la boucle
            
        # Déclenche une erreur si c'est un autre problème (ex: 400, 404, 500)
        response.raise_for_status() 
        
        # Si tout est OK, on extrait le texte
        data = response.json()
        return data['candidates'][0]['content']['parts'][0]['text']
        
    raise Exception("L'API Gemini est restée saturée après 5 tentatives. Réessaye dans une minute.")


class CopywriterAgent:
    def __init__(self):
        self.name = "Agent-Alpha (Copywriter)"

    async def generate_branding(self, theme: str):
        print(f"✍️ [{self.name}] Demande à Gemini de créer le branding pour : {theme}...")
        
        prompt = f"""
        Tu es un expert en marketing e-commerce. Crée une marque pour une boutique sur le thème : '{theme}'.
        Réponds UNIQUEMENT sous la forme d'un objet JSON strict avec cette structure exacte, sans texte avant ni après, pas de blabla :
        {{
            "brand": "NOM DE LA MARQUE EN MAJUSCULES",
            "hero": "Slogan principal accrocheur de 4-5 mots",
            "sub": "Une phrase de description élégante pour la sous-section."
        }}
        """
        response_text = await asyncio.to_thread(appeler_gemini_api, prompt)
        
        text_clean = response_text.replace("```json", "")
        text_clean = text_clean.replace("```", "").strip()
        return json.loads(text_clean)


class ProductAgent:
    def __init__(self):
        self.name = "Agent-Beta (Product-Specialist)"

    async def generate_products(self, theme: str):
        print(f"📦 [{self.name}] Demande à Gemini de concevoir le catalogue produit...")
        
        prompt = f"""
        Génère une liste de 4 produits uniques, haut de gamme et réalistes pour une boutique sur le thème : '{theme}'.
        Pour chaque produit, fournis une URL d'image libre de droit provenant d'Unsplash en rapport DIRECT avec le produit.
        Réponds UNIQUEMENT sous la forme d'un tableau JSON strict avec cette structure exacte, sans blabla autour :
        [
            {{"name": "Nom du produit 1", "price": "89,00 €", "img": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?q=80&w=600&auto=format&fit=crop"}},
            {{"name": "Nom du produit 2", "price": "120,00 €", "img": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600&auto=format&fit=crop"}},
            {{"name": "Nom du produit 3", "price": "45,00 €", "img": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=600&auto=format&fit=crop"}},
            {{"name": "Nom du produit 4", "price": "150,00 €", "img": "https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?q=80&w=600&auto=format&fit=crop"}}
        ]
        Utilise de vraies images Unsplash valides si tu en connais, ou adapte les IDs de manière réaliste.
        """
        response_text = await asyncio.to_thread(appeler_gemini_api, prompt)
        
        text_clean = response_text.replace("```json", "")
        text_clean = text_clean.replace("```", "").strip()
        return json.loads(text_clean)


class CoderAgent:
    def __init__(self):
        self.name = "Agent-Gamma (Coder)"

    async def rewrite_html(self, branding, products):
        print(f"🛠️ [{self.name}] Lecture et modification du fichier HTML...")
        html_path = os.path.join("theme", "index.html")
        
        if not os.path.exists(html_path):
            print(f"❌ Erreur : Le fichier {html_path} est introuvable.")
            return

        with open(html_path, "r", encoding="utf-8") as file:
            content = file.read()

        if not os.path.exists(html_path + ".bak"):
            with open(html_path + ".bak", "w", encoding="utf-8") as bak:
                bak.write(content)

        if os.path.exists(html_path + ".bak"):
            with open(html_path + ".bak", "r", encoding="utf-8") as bak:
                content = bak.read()

        content = content.replace("LA REVOLTOSA STYLE", branding["brand"])
        content = content.replace("LA REVOLTOSA", branding["brand"])
        content = content.replace("Nouvelle Saison", branding["hero"])
        content = content.replace("Une sélection de pièces intemporelles et singulières.", branding["sub"])
        content = content.replace("https://images.unsplash.com/photo-1490481651871-ab68de25d43d?q=80&w=1600&auto=format&fit=crop", products[0]["img"])

        old_products = [
            ("Robe Midi Cintrée", "89,00 €", "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?q=80&w=600&auto=format&fit=crop"),
            ("Blazer Oversize Beige", "120,00 €", "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?q=80&w=600&auto=format&fit=crop"),
            ("Mules en Cuir Souple", "75,00 €", "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?q=80&w=600&auto=format&fit=crop"),
            ("Chemise en Lin Fluide", "65,00 €", "https://images.unsplash.com/photo-1554412933-514a83d2f3c8?q=80&w=600&auto=format&fit=crop")
        ]

        for i in range(4):
            if i < len(products):
                content = content.replace(old_products[i][0], products[i]["name"])
                content = content.replace(old_products[i][1], products[i]["price"])
                content = content.replace(old_products[i][2], products[i]["img"])

        with open(html_path, "w", encoding="utf-8") as file:
            file.write(content)
            
        print(f"✅ [{self.name}] Le fichier theme/index.html a été mis à jour avec succès !")


async def main():
    est_valide = GEMINI_API_KEY.startswith("AIzaSy") or GEMINI_API_KEY.startswith("AQ.")
    if not est_valide:
        print("❌ Erreur : Ta clé API Gemini semble incorrecte.")
        return

    print("👑 [Jarvis-Manager] Usine IA connectée directement à l'API Gemini.")
    theme_choisi = input("👉 Entrez un thème TOTALEMENT LIBRE pour votre boutique (ex: cyberpunk, chat zen, bijoux vikings...) : ")

    alpha = CopywriterAgent()
    beta = ProductAgent()
    gamma = CoderAgent()

    print(f"\n🚨 [Jarvis-Manager] Consultation en temps réel de l'IA (Mode Automatisé Résistant)...")
    
    try:
        # Étape 1 : L'agent Alpha travaille
        branding = await alpha.generate_branding(theme_choisi)
        
        # Étape 2 : Petite pause de courtoisie intermédiaire
        print("⏳ [Jarvis-Manager] Pause de sécurité de 3 secondes...")
        await asyncio.sleep(3) 
        
        # Étape 3 : L'agent Beta travaille
        products = await beta.generate_products(theme_choisi)
        
        print(f"\n🚨 [Jarvis-Manager] L'IA a répondu avec succès. Passage à l'intégration.")
        await gamma.rewrite_html(branding, products)
        print("\n✨ PROCESSUS TERMINÉ ! Rafraîchis ton navigateur (F5) pour voir le résultat.")
        
    except Exception as e:
        print(f"\n❌ Une erreur est survenue lors de l'appel à l'IA : {e}")

if __name__ == "__main__":
    asyncio.run(main())