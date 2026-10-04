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

function occurrenceKey(item) {
  return `${item.chore_id || item.id}:${item.date}`;
}

function escapeHtml(str){
  if (!str) return '';
  return String(str).replace(/[&<>"']/g, function(m){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"}[m];});
}

function DayColumn({date, items, onComplete, pendingCompletions}){
  const dt = new Date(date);
  return (
    <div className="bg-white shadow-lg rounded-lg p-4 hover:shadow-xl transition-shadow">
      <h3 className="font-semibold mb-2 text-indigo-700 text-lg">{dt.toLocaleDateString(undefined, {weekday:'long', month:'short', day:'numeric'})}</h3>
      <ul className="space-y-3">
        {items.map((item,i) => (
          <li key={i} className="p-3 border border-gray-100 rounded-lg flex justify-between items-center hover:bg-gray-50 transition-colors">
            <div className="flex-1">
              <div className={`font-medium text-gray-900 ${item.completed ? 'line-through text-gray-400' : ''}`}>{item.title}</div>
              {item.recurrence ? <div className="text-xs text-gray-500 mt-1">{item.recurrence}</div> : null}
              {item.due_date ? <div className="text-xs text-gray-500 mt-1">Due {new Date(item.due_date).toLocaleDateString()}</div> : null}
            </div>
            <div className="text-sm flex items-center space-x-3">
              {item.assigned_to ? (
                (() => {
                  const color = item.assigned_color || 'indigo';
                  const cls = `inline-block bg-${color}-100 text-${color}-800 px-3 py-1 rounded-full text-xs font-semibold`;
                  return <span className={cls}>{item.assigned_to}</span>;
                })()
              ) : (
                <span className="inline-block bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-xs font-semibold">Unassigned</span>
              )}
              {item.completed ? (
                <span className="inline-block bg-green-50 text-green-700 px-3 py-1 rounded-full text-xs font-semibold">Done</span>
              ) : (
                <button onClick={() => onComplete(item)} disabled={pendingCompletions.has(occurrenceKey(item))} aria-busy={pendingCompletions.has(occurrenceKey(item))} className="inline-flex items-center space-x-1 text-sm bg-blue-100 text-blue-800 border border-blue-200 px-4 py-2 rounded hover:bg-blue-200 transition-colors disabled:opacity-70">
                  {pendingCompletions.has(occurrenceKey(item)) && <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" aria-hidden="true" />}
                  {pendingCompletions.has(occurrenceKey(item)) ? 'Completing…' : 'Complete'}
                </button>
              )}
            </div>
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
  const [completionFeedback, setCompletionFeedback] = useState(null);
  const [pendingCompletions, setPendingCompletions] = useState(() => new Set());
  useEffect(() => {
    const today = new Date();
    const start = startOfISODate(addDays(today, -28));
    const end = startOfISODate(addDays(today, 28));
    fetchRange(start, end).then(data => setItems(data));
  }, []);

  async function completeOccurrence(item) {
    const key = occurrenceKey(item);
    setPendingCompletions(current => new Set(current).add(key));
    setCompletionFeedback(null);
    try {
      const response = await fetch('/api/chores/complete/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({chore_id: item.chore_id || item.id, date: item.date}),
      });
      if (!response.ok) throw new Error(`Request failed (${response.status})`);

      const today = new Date();
      const start = startOfISODate(addDays(today, -28));
      const end = startOfISODate(addDays(today, 28));
      const updatedItems = await fetchRange(start, end);
      setItems(updatedItems);
      setCompletionFeedback({type: 'success', text: `${item.title} marked complete.`});
    } catch (error) {
      console.error(error);
      setCompletionFeedback({type: 'error', text: `Could not complete ${item.title}. Please try again.`});
    } finally {
      setPendingCompletions(current => {
        const updated = new Set(current);
        updated.delete(key);
        return updated;
      });
    }
  }

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
      {completionFeedback && (
        <div role={completionFeedback.type === 'error' ? 'alert' : 'status'} className={completionFeedback.type === 'error' ? 'rounded border border-red-200 bg-red-50 p-3 text-sm text-red-800' : 'rounded border border-green-200 bg-green-50 p-3 text-sm text-green-800'}>
          {completionFeedback.text}
        </div>
      )}
      {overdue.length > 0 && (
        <section>
          <h2 className="text-xl font-semibold text-red-700">Past Due</h2>
          <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(groupByDate(overdue)).sort().reverse().map(([d, items]) => (
              <div key={d} className="bg-white shadow-lg rounded-lg p-4 border-l-4 border-red-300">
                <h3 className="font-semibold mb-2 text-red-600">{new Date(d).toLocaleDateString()}</h3>
                <ul className="space-y-3">
                  {items.map((it,i)=>(
                    <li key={i} className="p-3 border border-gray-100 rounded-lg flex justify-between items-center hover:bg-gray-50 transition-colors">
                      <div className={`font-medium text-gray-900 ${it.completed ? 'line-through text-gray-400' : ''}`}>{it.title}
                        {it.due_date ? <div className="text-xs text-gray-500 mt-1">Due {new Date(it.due_date).toLocaleDateString()}</div> : null}
                      </div>
                      <div className="flex items-center space-x-3">
                        {it.assigned_to ? (() => { const color = it.assigned_color || 'indigo'; const cls = `inline-block bg-${color}-100 text-${color}-800 px-3 py-1 rounded-full text-xs font-semibold`; return <span className={cls}>{it.assigned_to}</span>; })() : (<span className="inline-block bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-xs font-semibold">Unassigned</span>)}
                        {it.completed ? (<span className="inline-block bg-green-50 text-green-700 px-3 py-1 rounded-full text-xs font-semibold">Done</span>) : (() => { const isCompleting = pendingCompletions.has(occurrenceKey(it)); return (<button onClick={() => completeOccurrence(it)} disabled={isCompleting} aria-busy={isCompleting} className="inline-flex items-center space-x-1 text-sm bg-blue-100 text-blue-800 border border-blue-200 px-4 py-2 rounded hover:bg-blue-200 transition-colors disabled:opacity-70">{isCompleting && <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" aria-hidden="true" />}{isCompleting ? 'Completing…' : 'Complete'}</button>); })()}
                      </div>
                    </li>
                  ))}
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
              <h3 className="font-semibold mb-2 text-indigo-600">Week of {new Date(wk).toLocaleDateString()}</h3>
              <ul className="space-y-2">
                {weeks[wk].map((it,i)=>(
                  <li key={i} className="p-3 border border-gray-100 rounded-lg flex justify-between items-center hover:bg-gray-50 transition-colors">
                    <div>
                      <div className={`font-medium ${it.completed ? 'line-through text-gray-400' : ''}`}>{it.title}</div>
                      {it.recurrence ? <div className="text-xs text-gray-500">{it.recurrence}</div> : null}
                      {it.due_date ? <div className="text-xs text-gray-500">Due {new Date(it.due_date).toLocaleDateString()}</div> : null}
                    </div>
                    <div className="text-sm flex items-center space-x-3">
                      {it.assigned_to ? (() => { const color = it.assigned_color || 'indigo'; const cls = `inline-block bg-${color}-100 text-${color}-800 px-3 py-1 rounded-full text-xs font-semibold`; return <span className={cls}>{it.assigned_to}</span>; })() : (<span className="inline-block bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-xs font-semibold">Unassigned</span>)}
                      {it.completed ? (<span className="inline-block bg-green-50 text-green-700 px-3 py-1 rounded-full text-xs font-semibold">Done</span>) : (() => { const isCompleting = pendingCompletions.has(occurrenceKey(it)); return (<button onClick={() => completeOccurrence(it)} disabled={isCompleting} aria-busy={isCompleting} className="inline-flex items-center space-x-1 text-sm bg-blue-100 text-blue-800 border border-blue-200 px-4 py-2 rounded hover:bg-blue-200 transition-colors disabled:opacity-70">{isCompleting && <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" aria-hidden="true" />}{isCompleting ? 'Completing…' : 'Complete'}</button>); })()}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
