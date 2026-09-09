const { useState, useEffect } = React;

function fetchWeek() {
  return fetch('/api/chores/week/').then(res => {
    if (!res.ok) throw new Error('Network response not ok');
    return res.json();
  }).catch(err => { console.error(err); return []; });
}

function groupByDate(items){
  const map = {};
  items.forEach(it => { (map[it.date] = map[it.date] || []).push(it); });
  return map;
}

function escapeHtml(str){
  if (!str) return '';
  return String(str).replace(/[&<>"']/g, function(m){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"}[m];});
}

function DayColumn({date, items}){
  const dt = new Date(date);
  return (
    <div className="bg-white shadow rounded p-4">
      <h3 className="font-semibold mb-2">{dt.toLocaleDateString(undefined, {weekday:'long', month:'short', day:'numeric'})}</h3>
      <ul className="space-y-2">
        {items.map((item,i) => (
          <li key={i} className="p-2 border rounded flex justify-between items-center">
            <div>
              <div className="font-medium">{item.title}</div>
              <div className="text-xs text-gray-500">{item.recurrence}</div>
            </div>
            <div className="text-sm text-gray-700">{item.assigned_to || 'Unassigned'}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}

function App(){
  const [items, setItems] = useState(null);
  useEffect(() => {
    fetchWeek().then(data => setItems(data));
  }, []);

  if (items === null) return <div className="text-center text-gray-500">Loading chores…</div>;
  if (items.length === 0) return <div className="text-center text-gray-500">No chores this week.</div>;

  const grouped = groupByDate(items);
  const dates = Object.keys(grouped).sort();

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {dates.map(d => <DayColumn key={d} date={d} items={grouped[d]} />)}
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
