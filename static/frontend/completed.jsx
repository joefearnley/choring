const { useState, useEffect } = React;

function fetchCompleted(){
  return fetch('/api/chores/completed/').then(r=>r.ok ? r.json() : []).catch(()=>[]);
}

function CompletedPage(){
  const [items, setItems] = useState(null);
  useEffect(()=>{ fetchCompleted().then(d=>setItems(d)); }, []);
  if (items === null) return <div className="text-center text-gray-500">Loading completed…</div>;
  if (items.length === 0) return <div className="text-gray-500">No completed chores yet.</div>;
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Recently Completed</h2>
        <div className="text-sm text-gray-500">Showing last {items.length} items</div>
      </div>
      <ul className="space-y-3">
        {items.map((it,i)=>(
          <li key={i} className="p-4 bg-white rounded-lg shadow border border-gray-100 flex justify-between items-center hover:shadow-md transition-shadow">
            <div>
              <div className="font-medium text-gray-900">{it.title}</div>
              {it.due_date ? <div className="text-xs text-gray-500 mt-1">Due {new Date(it.due_date).toLocaleDateString()}</div> : null}
              <div className="text-xs text-gray-500 mt-1">{it.date} • {it.completed_at}</div>
            </div>
            <div className="flex items-center space-x-3">
              {it.assigned_to ? (()=>{ const color = it.assigned_color||'indigo'; const cls = `inline-block bg-${color}-100 text-${color}-800 px-3 py-1 rounded-full text-xs font-semibold`; return <span className={cls}>{it.assigned_to}</span> })() : (<span className="inline-block bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-xs font-semibold">Unassigned</span>)}
              <button onClick={async (e)=>{ e.currentTarget.disabled = true; await fetch('/api/chores/uncomplete/', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({chore_id: it.chore_id, date: it.date})}); fetchCompleted().then(d=>setItems(d)); }} className="text-sm bg-yellow-100 text-yellow-800 px-3 py-1 rounded">Uncomplete</button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

// Auto-insert to DOM if mount exists
const completedMount = document.getElementById('completed-root');
if (completedMount) ReactDOM.createRoot(completedMount).render(<CompletedPage />);
