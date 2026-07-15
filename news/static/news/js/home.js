
function toggleLike(e, articleId) {
  e.preventDefault();
  e.stopPropagation();
  
  // Check if user is authenticated (variable HTML se aayega)
  if (window.DjangoConfig && window.DjangoConfig.isAuthenticated) {
    fetch(`/article/${articleId}/like/`, {
      method: 'POST',
      headers: { 
        'X-CSRFToken': window.DjangoConfig.csrfToken, 
        'Content-Type': 'application/json' 
      }
    })
    .then(r => r.json())
    .then(data => {
      const btn = document.querySelector(`[data-article-id="${articleId}"]`);
      const cnt = document.getElementById(`like-count-${articleId}`);
      if (btn) btn.classList.toggle('liked', data.liked);
      if (cnt) cnt.textContent = data.count;
      if (btn.firstChild) btn.firstChild.textContent = data.liked ? '♥' : '♡';
    });
  } else {
    
    window.location.href = window.DjangoConfig.loginUrl + '?next=' + encodeURIComponent(window.location.pathname);
  }
}
function toggleDateDropdown() {
        const menu = document.getElementById('date-dropdown-menu');
        const form = document.getElementById('custom-date-form');
        menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
        form.style.display = 'none';
    }

    function showCustomDateForm() {
        document.getElementById('date-dropdown-menu').style.display = 'none';
        document.getElementById('custom-date-form').style.display = 'block';
    }

    window.onclick = function(event) {
        if (!event.target.matches('#date-filter-btn') && !event.target.closest('.date-filter-wrapper')) {
            document.getElementById('date-dropdown-menu').style.display = 'none';
            document.getElementById('custom-date-form').style.display = 'none';
        }
    }