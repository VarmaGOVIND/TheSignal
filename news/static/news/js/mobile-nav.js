
document.addEventListener('DOMContentLoaded', function() {
 const hamburger = document.getElementById('hamburger-btn');
const mobileNav = document.getElementById('mobile-menu');
const overlay = document.getElementById('mobile-overlay');
const closeBtn = document.getElementById('mobile-close');
  
  
  if (hamburger) {
    hamburger.addEventListener('click', function() {
      mobileNav.classList.add('active');
      mobileNavOverlay.classList.add('active');
      document.body.style.overflow = 'hidden';
    });
  }
  
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
  
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && mobileNav.classList.contains('active')) {
      closeMobileNav();
    }
  });
  
  const mobileNavLinks = document.querySelectorAll('.mobile-nav-links a');
  mobileNavLinks.forEach(link => {
    link.addEventListener('click', closeMobileNav);
  });
});


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