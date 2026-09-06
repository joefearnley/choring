async function login() {
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const res = await fetch('/api/token/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json();
  if (data.access) {
    localStorage.setItem('access', data.access);
    localStorage.setItem('refresh', data.refresh);
    document.getElementById('output').textContent = 'Logged in';
  } else {
    document.getElementById('output').textContent = JSON.stringify(data);
  }
}

async function getProfile() {
  const token = localStorage.getItem('access');
  const res = await fetch('/api/accounts/profile/', {
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await res.json();
  document.getElementById('output').textContent = JSON.stringify(data, null, 2);
}

document.getElementById('login').addEventListener('click', login);
document.getElementById('profile').addEventListener('click', getProfile);
