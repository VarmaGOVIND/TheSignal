/* ── HAMBURGER MENU FUNCTIONALITY ─── */
document.addEventListener('DOMContentLoaded', function() {
  const hamburger = document.getElementById('hamburger-btn');
  const mobileNav = document.getElementById('mobile-nav');
  const mobileNavOverlay = document.getElementById('mobile-nav-overlay');
  const mobileNavClose = document.getElementById('mobile-nav-close');
  
  // Open mobile nav
  if (hamburger) {
    hamburger.addEventListener('click', function() {
      mobileNav.classList.add('active');
      mobileNavOverlay.classList.add('active');
      document.body.style.overflow = 'hidden';
    });
  }
  
  // Close mobile nav
  function closeMobileNav() {
    mobileNav.classList.remove('active');
    mobileNavOverlay.classList.remove('active');
    document.body.style.overflow = '';
  }
  
  if (mobileNavClose) {
    mobileNavClose.addEventListener('click', closeMobileNav);
  }
  
  if (mobileNavOverlay) {
    mobileNavOverlay.addEventListener('click', closeMobileNav);
  }
  
  // Close on escape key
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && mobileNav.classList.contains('active')) {
      closeMobileNav();
    }
  });
  
  // Close when clicking nav links
  const mobileNavLinks = document.querySelectorAll('.mobile-nav-links a');
  mobileNavLinks.forEach(link => {
    link.addEventListener('click', closeMobileNav);
  });
});

/* ─── RESPONSIVE TABLE HANDLER ─── */
document.addEventListener('DOMContentLoaded', function() {
  const tables = document.querySelectorAll('.adm-table, .admin-table');
  tables.forEach(table => {
    const wrapper = document.createElement('div');
    wrapper.style.overflowX = 'auto';
    wrapper.style.webkitOverflowScrolling = 'touch';
    table.parentNode.insertBefore(wrapper, table);
    wrapper.appendChild(table);
  });
});

/* ─── IMAGE LAZY LOADING ─── */
document.addEventListener('DOMContentLoaded', function() {
  const images = document.querySelectorAll('img[data-src]');
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.removeAttribute('data-src');
        observer.unobserve(img);
      }
    });
  });
  images.forEach(img => imageObserver.observe(img));
});