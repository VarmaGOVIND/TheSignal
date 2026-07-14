
const introOverlay = document.getElementById('intro-overlay');
const introShown = sessionStorage.getItem('introShown');

if (introOverlay && !introShown) {
  document.body.classList.add('intro-active');
  sessionStorage.setItem('introShown', 'true');
  
  setTimeout(() => {
    introOverlay.style.opacity = '0';
    introOverlay.style.transition = 'opacity 0.5s ease';
    
    setTimeout(() => {
      introOverlay.style.display = 'none';
      document.body.classList.remove('intro-active');
    }, 500);
  }, 2000); 
} else if (introOverlay) {
  introOverlay.style.display = 'none';
  document.body.classList.remove('intro-active');
}


const ring = document.getElementById('cursor-ring');
const dot  = document.getElementById('cursor-dot');
let rx = -100, ry = -100, mx = -100, my = -100;

document.addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; });
document.addEventListener('mouseover', e => {
  const el = e.target.closest('button,a,[data-cursor="pointer"],.card,.trending-item');
  ring.classList.toggle('hovering', !!el);
});

(function animCursor() {
  rx += (mx - rx) * 0.12;
  ry += (my - ry) * 0.12;
  ring.style.left = rx + 'px'; ring.style.top = ry + 'px';
  dot.style.left  = mx + 'px'; dot.style.top  = my + 'px';
  requestAnimationFrame(animCursor);
})();


const html = document.documentElement;
const toggleBtn = document.getElementById('theme-toggle');
const iconL  = document.getElementById('theme-icon-left');
const iconR  = document.getElementById('theme-icon-right');

function applyTheme(t) {
  html.setAttribute('data-theme', t);
  localStorage.setItem('signal-theme', t);
  if (t === 'dark') { iconL.textContent = '🌙'; iconR.textContent = '☀️'; }
  else              { iconL.textContent = '☀️'; iconR.textContent = '🌙'; }
}

applyTheme(localStorage.getItem('signal-theme') || 'dark');
toggleBtn.addEventListener('click', () => {
  applyTheme(html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
});


const tickerEl = document.getElementById('ticker-text');
const tickerLink = document.getElementById('ticker-link');
let tickerItems = [];
let tickerIdx = 0;

// API  breaking news fetch 
fetch('/api/breaking-news/')
  .then(response => response.json())
  .then(data => {
    tickerItems = data;
    
    
    if (tickerItems.length > 0 && tickerEl) {
      updateTicker();
      setInterval(updateTicker, 3500);
    }
  })
  .catch(error => {
    console.log('No breaking news available');
  });

function updateTicker() {
  if (tickerItems.length === 0) return;
  
  const currentItem = tickerItems[tickerIdx];
  
  
  tickerEl.classList.remove('animate');
  void tickerEl.offsetWidth;
  tickerEl.textContent = currentItem.text;
  tickerEl.classList.add('animate');
  
  
  if (tickerLink) {
    if (currentItem.is_clickable && currentItem.url !== '#') {
      tickerLink.href = currentItem.url;
      tickerLink.style.cursor = 'pointer';
      tickerLink.style.textDecoration = 'none';
      
      if (currentItem.url.startsWith('http')) {
        tickerLink.target = '_blank';
      } else {
        tickerLink.target = '_self';
      }
    } else {
      tickerLink.href = '#';
      tickerLink.style.cursor = 'default';
      tickerLink.onclick = (e) => e.preventDefault();
    }
  }
  
  
  tickerIdx = (tickerIdx + 1) % tickerItems.length;
}


document.querySelectorAll('.notification-toast').forEach(el => {
  setTimeout(() => { 
    el.style.opacity = '0'; 
    el.style.transform = 'translateY(-10px)';
    el.style.transition = 'opacity .4s, transform .4s';
    setTimeout(() => el.remove(), 400);
  }, 8000);
});


document.querySelectorAll('.spotlight-wrap').forEach(wrap => {
  const overlay = wrap.querySelector('.spotlight-overlay');
  if (!overlay) return;
  wrap.addEventListener('mousemove', e => {
    const r = wrap.getBoundingClientRect();
    overlay.style.background =
      `radial-gradient(320px circle at ${e.clientX - r.left}px ${e.clientY - r.top}px,
        rgba(232,255,71,0.13) 0%, transparent 70%)`;
    overlay.style.opacity = '1';
  });
  wrap.addEventListener('mouseleave', () => { overlay.style.opacity = '0'; });
});


function toggleMobileMenu() {
  const menu = document.getElementById('mobile-menu');
  const overlay = document.getElementById('mobile-menu-overlay');
  if (menu && overlay) {
    menu.classList.toggle('active');
    overlay.classList.toggle('active');
    document.body.style.overflow = menu.classList.contains('active') ? 'hidden' : '';
  }
}

function closeMobileMenu() {
  const menu = document.getElementById('mobile-menu');
  const overlay = document.getElementById('mobile-menu-overlay');
  if (menu && overlay) {
    menu.classList.remove('active');
    overlay.classList.remove('active');
    document.body.style.overflow = '';
  }
}

function toggleProfileDropdown() {
  const dropdown = document.getElementById('profile-dropdown');
  if (dropdown) {
    dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
  }
}


document.addEventListener('click', function(event) {
  const dropdown = document.getElementById('profile-dropdown');
  const trigger = document.querySelector('.profile-dropdown-trigger');
  
  if (dropdown && trigger && !trigger.contains(event.target)) {
    dropdown.style.display = 'none';
  }
});


document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    closeMobileMenu();
  }
});