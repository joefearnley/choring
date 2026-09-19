document.addEventListener('DOMContentLoaded', function(){
  // Find selects/inputs with name ending in 'color' inside the inline
  const selects = document.querySelectorAll('select[id$="-color"], input[id$="-color"]');
  function updatePreview(el){
    const val = el.value || 'indigo';
    // find preview span in same inline container
    const container = el.closest('.inline-related') || el.closest('.module');
    let preview = container && container.querySelector('#userprofile-color-preview');
    if (!preview) {
      // try global preview
      preview = document.querySelector('#userprofile-color-preview');
    }
    if (preview) {
      preview.className = `inline-block px-3 py-1 rounded-full text-xs bg-${val}-100 text-${val}-800`;
      preview.textContent = val;
    }
  }
  selects.forEach(s => {
    updatePreview(s);
    s.addEventListener('change', () => updatePreview(s));
  });
});
