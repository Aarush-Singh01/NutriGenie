/**
 * NutriGenie app.js — tab routing and global API utility.
 */

const API_BASE = 'http://localhost:8000/api';

// ── Current user ID (stored in localStorage) ────────────────────────────
let currentUserId = localStorage.getItem('nutrigenie_user_id') || 'user_001';

function setUserId(id) {
  currentUserId = id;
  localStorage.setItem('nutrigenie_user_id', id);
}

// ── HTTP helpers ─────────────────────────────────────────────────────────
async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

async function apiDelete(path) {
  const res = await fetch(`${API_BASE}${path}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// ── Toast notifications ──────────────────────────────────────────────────
function showToast(message, type = 'success') {
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  t.textContent = message;
  document.body.appendChild(t);
  setTimeout(() => { t.style.opacity = '0'; }, 3000);
  setTimeout(() => t.remove(), 3400);
}

// ── Tab routing ──────────────────────────────────────────────────────────
function activateTab(name) {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === name);
  });
  document.querySelectorAll('.tab-content').forEach(el => {
    el.classList.add('hidden');
  });
  const target = document.getElementById(`tab-${name}`);
  if (target) target.classList.remove('hidden');

  // Trigger render callbacks
  if (name === 'dashboard')  renderDashboard();
  if (name === 'meal-plan')  renderMealPlan();
  if (name === 'food-log')   renderFoodLog();
  if (name === 'chat')       renderChat();
  if (name === 'profile')    renderProfile();
}

// ── Init ─────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => activateTab(btn.dataset.tab));
  });

  // Render the default tab (profile)
  renderProfile();
});
