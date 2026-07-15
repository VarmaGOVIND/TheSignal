
const isAdmin = window.DjangoConfig && window.DjangoConfig.isAdmin;
const panels = isAdmin 
  ? ['articles','users','comments','stats','breaking-news','activity']
  : ['articles','comments','breaking-news','activity'];

function showTab(name) {
  const allPossiblePanels = ['articles','users','comments','stats','breaking-news','activity'];
  allPossiblePanels.forEach(p => {
    const panel = document.getElementById(`panel-${p}`);
    if (panel) panel.style.display = 'none';
    document.querySelectorAll(`[data-tab="${p}"]`).forEach(btn => btn.classList.remove('active'));
    const side = document.getElementById(`side-${p}`);
    if (side) side.classList.remove('active');
  });
  
  const targetPanel = document.getElementById(`panel-${name}`);
  if (targetPanel) targetPanel.style.display = 'block';
  document.querySelectorAll(`[data-tab="${name}"]`).forEach(btn => btn.classList.add('active'));
  const sideEl = document.getElementById(`side-${name}`);
  if (sideEl) sideEl.classList.add('active');
  
  return false;
}


if (window.DjangoConfig && window.DjangoConfig.isAdmin) {
  const rootStyles = getComputedStyle(document.documentElement);
  const accentColor = rootStyles.getPropertyValue('--accent').trim() || '#e8ff47';
  const textColor = rootStyles.getPropertyValue('--text-sub').trim() || '#aaaaaa';
  const borderColor = rootStyles.getPropertyValue('--border').trim() || '#1e1e22';

  new Chart(document.getElementById('categoryChart'), {
    type: 'doughnut',
    data: {
      labels: window.DjangoConfig.catLabels,
      datasets: [{
        data: window.DjangoConfig.catCounts,
        backgroundColor: ['#e8ff47', '#47c8ff', '#ff4444', '#47ff8f', '#a855f7', '#f59e0b'],
        borderWidth: 0,
        hoverOffset: 10
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom', labels: { color: textColor, font: { size: 11 } } } }
    }
  });

  new Chart(document.getElementById('topArticlesChart'), {
    type: 'bar',
    data: {
      labels: window.DjangoConfig.artLabels,
      datasets: [{
        label: 'Views',
        data: window.DjangoConfig.artViews,
        backgroundColor: accentColor,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true, grid: { color: borderColor }, ticks: { color: textColor } },
        x: { grid: { display: false }, ticks: { color: textColor, font: { size: 10 } } }
      },
      plugins: { legend: { display: false } }
    }
  });

  new Chart(document.getElementById('trendChart'), {
    type: 'line',
    data: {
      labels: window.DjangoConfig.lineLabels,
      datasets: [{
        label: 'Articles Published',
        data: window.DjangoConfig.lineCounts,
        borderColor: '#47c8ff',
        backgroundColor: 'rgba(71, 200, 255, 0.1)',
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#47c8ff',
        pointRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true, grid: { color: borderColor }, ticks: { color: textColor, stepSize: 1 } },
        x: { grid: { display: false }, ticks: { color: textColor } }
      },
      plugins: { legend: { display: false } }
    }
  });
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


window.addEventListener('DOMContentLoaded', () => {
  const hash = window.location.hash.replace('#', '');
  if (hash && panels.includes(hash)) {
    showTab(hash);
  }
});

const originalShowTab = showTab;
showTab = function(name) {
  originalShowTab(name);
  window.location.hash = name;
};


document.addEventListener('DOMContentLoaded', function() {
  const loadMoreBtn = document.getElementById('load-more-activity');
  const activityList = document.getElementById('activity-list');

  if (loadMoreBtn && activityList) {
    let offset = activityList.children.length; 
    let isLoading = false;

    loadMoreBtn.addEventListener('click', function() {
      if (isLoading) return;
      
      isLoading = true;
      loadMoreBtn.textContent = 'Loading...';
      loadMoreBtn.disabled = true;

      fetch(`/admin-panel/activity/load-more/?offset=${offset}`)
        .then(response => response.json())
        .then(data => {
          if (data.activities && data.activities.length > 0) {
            data.activities.forEach(act => {
              const itemHTML = `
                <div class="activity-item">
                  <div class="activity-dot"></div>
                  <span class="activity-text"><strong>@${act.user}</strong> — ${act.action}</span>
                  <span class="activity-time">${act.time_ago}</span>
                </div>
              `;
              activityList.insertAdjacentHTML('beforeend', itemHTML);
            });

            offset += data.activities.length;

            if (!data.has_more) {
              loadMoreBtn.parentElement.style.display = 'none';
            }
          }
          
          isLoading = false;
          loadMoreBtn.textContent = 'Load More Activity';
          loadMoreBtn.disabled = false;
        })
        .catch(error => {
          console.error('Error loading activities:', error);
          isLoading = false;
          loadMoreBtn.textContent = 'Load More Activity';
          loadMoreBtn.disabled = false;
        });
    });
  }
});
