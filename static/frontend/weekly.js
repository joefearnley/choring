(function(){
  async function fetchWeek() {
    try {
      const res = await fetch('/api/chores/week/');
      if (!res.ok) throw new Error('Network response was not ok');
      return await res.json();
    } catch (e) {
      console.error(e);
      return [];
    }
  }

  function groupByDate(items) {
    const map = {};
    items.forEach(it => {
      map[it.date] = map[it.date] || [];
      map[it.date].push(it);
    });
    return map;
  }

  function render(items) {
    const container = document.getElementById('week');
    if (!container) return;
    container.innerHTML = '';
    if (!items.length) {
      container.innerHTML = '<div class="text-center text-gray-500">No chores this week.</div>';
      return;
    }
    const grouped = groupByDate(items);
    const dates = Object.keys(grouped).sort();

    const grid = document.createElement('div');
    grid.className = 'grid grid-cols-1 md:grid-cols-2 gap-4';

    dates.forEach(d => {
      const col = document.createElement('div');
      col.className = 'bg-white shadow rounded p-4';

      const h = document.createElement('h3');
      h.className = 'font-semibold mb-2';
      const dt = new Date(d);
      h.textContent = dt.toLocaleDateString(undefined, {weekday:'long', month:'short', day:'numeric'});
      col.appendChild(h);

      const list = document.createElement('ul');
      list.className = 'space-y-2';
      grouped[d].forEach(item => {
        const li = document.createElement('li');
        li.className = 'p-2 border rounded flex justify-between items-center';
        const left = document.createElement('div');
        left.innerHTML = `<div class="font-medium">${escapeHtml(item.title)}</div><div class="text-xs text-gray-500">${item.recurrence}</div>`;
        const right = document.createElement('div');
        right.className = 'text-sm text-gray-700';
        right.textContent = item.assigned_to || 'Unassigned';
        li.appendChild(left);
        li.appendChild(right);
        list.appendChild(li);
      });

      col.appendChild(list);
      grid.appendChild(col);
    });

    container.appendChild(grid);
  }

  function escapeHtml(str){
    if(!str) return '';
    return str.replace(/[&<>"']/g, function(m){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"}[m];});
  }

  // init
  fetchWeek().then(render);
})();
