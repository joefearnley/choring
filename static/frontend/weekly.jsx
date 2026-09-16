const { useState, useEffect } = React;

function fetchRange(start, end) {
  return fetch(`/api/chores/range/?start=${start}&end=${end}`).then(res => {
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

function startOfISODate(d) {
  const dt = new Date(d);
  return new Date(Date.UTC(dt.getFullYear(), dt.getMonth(), dt.getDate())).toISOString().split('T')[0];
}

function addDays(d, days){
  const dt = new Date(d);
  dt.setDate(dt.getDate() + days);
  return dt;
}

function weekStartISO(d){
  const dt = new Date(d);
  const diff = dt.getUTCDay() === 0 ? 6 : dt.getUTCDay() - 1; // Monday=0
  dt.setUTCDate(dt.getUTCDate() - diff);
  return dt.toISOString().split('T')[0];
}

function App(){
  const [items, setItems] = useState(null);
  useEffect(() => {
    const today = new Date();
    const start = startOfISODate(addDays(today, -28));
    const end = startOfISODate(addDays(today, 28));
    fetchRange(start, end).then(data => setItems(data));
  }, []);

  if (items === null) return <div className="text-center text-gray-500">Loading chores…</div>;

  const todayISO = new Date().toISOString().split('T')[0];
  const overdue = items.filter(i => i.date < todayISO);
  const upcoming = items.filter(i => i.date >= todayISO);

  // group upcoming by week start (next 4 weeks only)
  const weeks = {};
  upcoming.forEach(it => {
    const wk = weekStartISO(it.date);
    weeks[wk] = weeks[wk] || [];
    weeks[wk].push(it);
  });
  const weekKeys = Object.keys(weeks).sort().slice(0,4);

  return (
    <div className="space-y-6">
      {overdue.length > 0 && (
        <section>
          <h2 className="text-xl font-semibold">Past Due</h2>
          <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(groupByDate(overdue)).sort().reverse().map(([d, items]) => (
              <div key={d} className="bg-white shadow rounded p-4">
                <h3 className="font-semibold mb-2">{new Date(d).toLocaleDateString()}</h3>
                <ul className="space-y-2">
                  {items.map((it,i)=>(<li key={i} className="p-2 border rounded flex justify-between items-center"><div className="font-medium">{it.title}</div><div className="text-sm text-gray-700">{it.assigned_to||'Unassigned'}</div></li>))}
                </ul>
              </div>
            ))}
          </div>
        </section>
      )}

      <section>
        <h2 className="text-xl font-semibold">Next 4 Weeks</h2>
        <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-4">
          {weekKeys.length === 0 && <div className="text-gray-500">No upcoming chores.</div>}
          {weekKeys.map(wk => (
            <div key={wk} className="bg-white shadow rounded p-4">
              <h3 className="font-semibold mb-2">Week of {new Date(wk).toLocaleDateString()}</h3>
              <ul className="space-y-2">
                {weeks[wk].map((it,i)=>(<li key={i} className="p-2 border rounded flex justify-between items-center"><div><div className="font-medium">{it.title}</div><div className="text-xs text-gray-500">{it.recurrence}</div></div><div className="text-sm text-gray-700">{it.assigned_to||'Unassigned'}</div></li>))}
              </ul>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
