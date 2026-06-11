const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

exports.handler = async (event) => {
  // Sécurité : On accepte uniquement les requêtes POST
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Méthode non autorisée' };
  }

  try {
    const { items } = JSON.parse(event.body);

    // Nettoie le prix de l'IA (ex: "89,00 €" -> 8900 centimes pour Stripe)
    const parsePriceToCentimes = (priceStr) => {
      let clean = priceStr.replace(/[^0-9.,]/g, '');
      if (clean.includes(',') && clean.includes('.')) {
        clean = clean.replace(/,/g, '');
      } else if (clean.includes(',')) {
        clean = clean.replace(',', '.');
      }
      return Math.round(parseFloat(clean) * 100) || 0;
    };

    // On prépare les produits au format Stripe
    const lineItems = items.map(item => {
      return {
        price_data: {
          currency: item.price.includes('$') ? 'usd' : 'eur',
          product_data: {
            name: item.name,
            images: [item.img], // Photo du produit sur la page Stripe
          },
          unit_amount: parsePriceToCentimes(item.price),
        },
        quantity: item.quantity,
      };
    });

    // On demande à Stripe de créer la session de paiement
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: lineItems,
      mode: 'payment',
      // Redirection après achat (Netlify fournit automatiquement l'URL du site en ligne)
      success_url: `${process.env.URL || 'http://localhost:8888'}?success=true`,
      cancel_url: `${process.env.URL || 'http://localhost:8888'}?canceled=true`,
    });

    // On renvoie l'URL de paiement au site web
    return {
      statusCode: 200,
      body: JSON.stringify({ url: session.url }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message }),
    };
  }
};