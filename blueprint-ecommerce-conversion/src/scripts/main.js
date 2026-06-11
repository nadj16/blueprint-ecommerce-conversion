/**
 * ⚡ Moteur JavaScript de Conversion E-Commerce
 */

document.addEventListener('DOMContentLoaded', () => {
  initCartDrawer();
  initStickyMobileCTA();
  initGA4TrackingPlaceholders();
});

/**
 * Gestion du tiroir panier glissant (Slide-out Cart)
 */
function initCartDrawer() {
  const drawer = document.getElementById('cartDrawer');
  const openButtons = document.querySelectorAll('.js-open-cart');
  const closeButton = document.getElementById('closeCart');

  openButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      drawer.classList.add('active');
      trackGA4Event('view_cart', { value: 49.90, currency: 'EUR', items: [] });
    });
  });

  if (closeButton) {
    closeButton.addEventListener('click', () => {
      drawer.classList.remove('active');
    });
  }
}

/**
 * Activation du bouton d'ajout au panier Sticky sur Mobile au défilement
 */
function initStickyMobileCTA() {
  const mainCta = document.getElementById('mainProductCTA');
  const stickyCta = document.getElementById('stickyMobileCTA');

  if (!mainCta || !stickyCta) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      // Si le CTA principal n'est plus visible, on affiche le sticky en bas sur mobile
      if (!entry.isIntersecting && window.innerWidth < 768) {
        stickyCta.classList.add('visible');
      } else {
        stickyCta.classList.remove('visible');
      }
    });
  }, { threshold: 0 });

  observer.observe(mainCta);
}

/**
 * Placeholders d'Événements Google Analytics 4 (DataLayer)
 */
function trackGA4Event(eventName, eventData) {
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({
    event: eventName,
    ecommerce: eventData
  });
  console.log(`[GA4 Tracked]: ${eventName}`, eventData);
}
