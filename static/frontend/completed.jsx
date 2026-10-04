const { useState, useEffect } = React;

function fetchCompleted(){
  return fetch('/api/chores/completed/').then(r=>r.ok ? r.json() : []).catch(()=>[]);
}

function occurrenceKey(item) {
  return `${item.chore_id}:${item.date}`;
}

function CompletedPage(){
  const [items, setItems] = useState(null);
  const [pendingUncompletions, setPendingUncompletions] = useState(() => new Set());
  useEffect(()=>{ fetchCompleted().then(d=>setItems(d)); }, []);

  async function uncompleteOccurrence(item) {
    const key = occurrenceKey(item);
    setPendingUncompletions(current => new Set(current).add(key));
    try {
      const response = await fetch('/api/chores/uncomplete/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({chore_id: item.chore_id, date: item.date}),
      });
      if (!response.ok) throw new Error(`Request failed (${response.status})`);
      const updatedItems = await fetchCompleted();
      setItems(updatedItems);
    } catch (error) {
      console.error(error);
    } finally {
      setPendingUncompletions(current => {
        const updated = new Set(current);
        updated.delete(key);
        return updated;
      });
    }
  }

  if (items === null) return <div className="text-center text-gray-500">Loading completed…</div>;
  if (items.length === 0) return <div className="text-gray-500">No completed chores yet.</div>;
  return (
    <div className="space-y-6 mt-5">
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
              {(() => { const isUncompleting = pendingUncompletions.has(occurrenceKey(it)); return (<button onClick={() => uncompleteOccurrence(it)} disabled={isUncompleting} aria-busy={isUncompleting} className="inline-flex items-center space-x-1 text-sm bg-yellow-100 text-yellow-800 px-4 py-2 rounded disabled:opacity-70">{isUncompleting && <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" aria-hidden="true" />}{isUncompleting ? 'Uncompleting…' : 'Uncomplete'}</button>); })()}
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
