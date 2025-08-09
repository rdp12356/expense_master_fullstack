async function loadKeys(){
  const res = await fetch('/apikeys/list');
  const keys = await res.json();
  const list = document.getElementById('keyList');
  list.innerHTML = '';
  keys.forEach(k=>{
    const div = document.createElement('div');
    div.innerHTML = `<b>${k.name}</b> — created: ${k.created_at} — revoked: ${k.revoked} <button onclick="revoke(${k.id})">Revoke</button>`;
    list.appendChild(div);
  });
}
async function createKey(){
  const name = document.getElementById('newKeyName').value || 'default';
  const res = await fetch('/apikeys/create', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name})});
  const j = await res.json();
  if (j.api_key) {
    alert('API key created (copy now):\\n' + j.api_key);
    loadKeys();
  } else alert(JSON.stringify(j));
}
async function revoke(id){
  await fetch('/apikeys/revoke', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({key_id:id})});
  loadKeys();
}
async function loadUsage(){
  const res = await fetch('/usage');
  const j = await res.json();
  document.getElementById('usageCount').innerText = 'Calls last 24h: ' + (j.last_24h_calls || 0);
}
async function convert(){
  const base = document.getElementById('cbase').value;
  const target = document.getElementById('ctarget').value;
  const amount = document.getElementById('camount').value;
  // convert via server admin (requires API key normally). For convenience, call /admin/fetch or display instruction
  const res = await fetch(`/convert?base=${encodeURIComponent(base)}&target=${encodeURIComponent(target)}&amount=${encodeURIComponent(amount)}`, {headers:{'X-API-Key':prompt('Enter your API key for convert:')}});
  const j = await res.json();
  document.getElementById('convertResult').innerText = JSON.stringify(j);
}
window.addEventListener('load', ()=>{ loadKeys(); loadUsage(); });
