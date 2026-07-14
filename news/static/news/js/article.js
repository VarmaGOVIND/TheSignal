
function toggleLike(articleId) {
  if (window.DjangoConfig && window.DjangoConfig.isAuthenticated) {
    fetch(`/article/${articleId}/like/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': window.DjangoConfig.csrfToken }
    })
    .then(r => r.json())
    .then(data => {
      document.getElementById('like-icon').textContent = data.liked ? '♥' : '♡';
      document.getElementById('like-count').textContent = data.count;
      document.getElementById('like-btn').classList.toggle('liked', data.liked);
    });
  } else {
    window.location.href = window.DjangoConfig.loginUrl + '?next=' + encodeURIComponent(window.location.pathname);
  }
}


function toggleEdit(commentId) {
  const text = document.getElementById(`comment-text-${commentId}`);
  const form = document.getElementById(`edit-form-${commentId}`);
  const hidden = text.style.display === 'none';
  text.style.display = hidden ? 'block' : 'none';
  form.style.display = hidden ? 'none' : 'block';
}


function toggleReply(commentId) {
  const form = document.getElementById(`reply-form-${commentId}`);
  form.style.display = form.style.display === 'none' ? 'block' : 'none';
  if (form.style.display === 'block') form.querySelector('textarea').focus();
}


const detBtn = document.getElementById('theme-toggle-detail');
if (detBtn) {
  const detL = document.getElementById('dtl-icon-l');
  const detR = document.getElementById('dtl-icon-r');
  function syncDetailIcons(t) {
    if (t === 'dark') { detL.textContent='🌙'; detR.textContent='☀️'; }
    else              { detL.textContent='☀️'; detR.textContent='🌙'; }
  }
  syncDetailIcons(document.documentElement.getAttribute('data-theme'));
  detBtn.addEventListener('click', () => {
    const t = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', t);
    localStorage.setItem('signal-theme', t);
    syncDetailIcons(t);
  });
}


function copyToClipboard(btn) {
  navigator.clipboard.writeText(window.location.href).then(() => {
    const originalText = btn.textContent;
    btn.textContent = '✓ Copied!';
    setTimeout(() => {
      btn.textContent = originalText;
    }, 2000);
  });
}

function shareTwitter() {
    window.open('https://twitter.com/intent/tweet?url=' + encodeURIComponent(window.location.href) + '&text=' + encodeURIComponent(document.title), '_blank');
}
function shareLinkedIn() {
    window.open('https://www.linkedin.com/sharing/share-offsite/?url=' + encodeURIComponent(window.location.href), '_blank');
}
function shareFacebook() {
    window.open('https://www.facebook.com/' + encodeURIComponent(window.location.href) + '&quote=' + encodeURIComponent(document.title), '_blank');
}


function showDeleteModal(formId, message) {
  const modal = document.getElementById('delete-modal');
  const msg = document.getElementById('delete-modal-message');
  const confirmBtn = document.getElementById('delete-confirm-btn');
  
  msg.textContent = message || 'Are you sure?';
  modal.style.display = 'flex';
  
  const newBtn = confirmBtn.cloneNode(true);
  confirmBtn.parentNode.replaceChild(newBtn, confirmBtn);
  
  newBtn.addEventListener('click', () => {
    const form = document.getElementById(formId);
    if (form) form.submit();
    closeDeleteModal();
  });
}

function closeDeleteModal() {
  document.getElementById('delete-modal').style.display = 'none';
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeDeleteModal();
});

document.getElementById('delete-modal').addEventListener('click', (e) => {
  if (e.target.id === 'delete-modal') closeDeleteModal();
});


function smartBack(e) {
  e.preventDefault();
  if (window.history.length > 1) {
    window.history.back();
  } else {
    window.location.href = '/';
  }
}