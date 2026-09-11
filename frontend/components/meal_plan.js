/**
 * Meal Plan component — generate 1-day or 7-day plan with meal cards.
 */

let _currentPlan = null;

function renderMealPlan() {
  const root = document.getElementById('meal-plan-root');
  if (!root) return;

  root.innerHTML = `
    <div class="card max-w-3xl mx-auto">
      <h2 class="text-xl font-bold text-green-800 mb-1">🍽️ Personalised Meal Plan</h2>
      <p class="text-sm text-gray-500 mb-4">Generate a meal plan based on your profile, goals, and dietary preferences.</p>
      <div class="flex flex-wrap gap-3 items-center">
        <label class="form-label mb-0">Plan Duration:</label>
        <select id="mp-days" class="form-input w-auto">
          <option value="1">1 Day</option>
          <option value="3">3 Days</option>
          <option value="7">7 Days</option>
        </select>
        <button class="btn-primary" id="mp-generate-btn">✨ Generate Plan</button>
        <button class="btn-secondary" id="mp-latest-btn">📋 Load Latest</button>
      </div>
      <div id="mp-status" class="mt-3 text-sm text-gray-500 hidden"></div>
    </div>

    <div id="mp-result" class="max-w-3xl mx-auto"></div>
  `;

  document.getElementById('mp-generate-btn').addEventListener('click', _generatePlan);
  document.getElementById('mp-latest-btn').addEventListener('click', _loadLatestPlan);
}

async function _generatePlan() {
  const days = parseInt(document.getElementById('mp-days').value);
  const btn = document.getElementById('mp-generate-btn');
  const status = document.getElementById('mp-status');

  btn.disabled = true;
  btn.textContent = '⏳ Generating…';
  status.classList.remove('hidden');
  status.textContent = 'Generating your personalised meal plan with IBM Granite…';

  try {
    const plan = await apiPost('/meal-plan', { user_id: currentUserId, duration_days: days });
    _currentPlan = plan;
    _renderPlanResult(plan);
    showToast('Meal plan generated!', 'success');
  } catch (err) {
    document.getElementById('mp-result').innerHTML =
      `<div class="card text-red-600 text-sm">Error: ${err.message}</div>`;
    showToast(`Error: ${err.message}`, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = '✨ Generate Plan';
    status.classList.add('hidden');
  }
}

async function _loadLatestPlan() {
  try {
    const plan = await apiGet(`/meal-plan/latest?user_id=${currentUserId}`);
    _currentPlan = plan;
    _renderPlanResult(plan);
  } catch (err) {
    document.getElementById('mp-result').innerHTML =
      `<div class="card text-gray-500 text-sm">No meal plan found. Click "Generate Plan" to create one.</div>`;
  }
}

function _renderPlanResult(plan) {
  const container = document.getElementById('mp-result');
  if (!container) return;

  const disclaimerHtml = plan.disclaimer
    ? `<div class="bg-amber-50 border border-amber-200 rounded-lg p-3 text-xs text-amber-800 mb-4">⚠️ ${plan.disclaimer}</div>`
    : '';

  let daysHtml = '';
  for (const day of (plan.days || [])) {
    daysHtml += `
      <div class="card">
        <h3 class="font-bold text-green-800 text-base mb-3">
          📅 Day ${day.day}
          <span class="text-xs font-normal text-gray-500 ml-2">
            ~${(day.daily_calories||0).toFixed(0)} kcal ·
            P: ${(day.daily_protein_g||0).toFixed(0)}g ·
            C: ${(day.daily_carbs_g||0).toFixed(0)}g ·
            F: ${(day.daily_fat_g||0).toFixed(0)}g
          </span>
        </h3>
        <div class="space-y-2">
          ${_mealSection('🌅 Breakfast', day.breakfast)}
          ${_mealSection('🍎 Morning Snack', day.morning_snack)}
          ${_mealSection('☀️ Lunch', day.lunch)}
          ${_mealSection('🍵 Evening Snack', day.evening_snack)}
          ${_mealSection('🌙 Dinner', day.dinner)}
        </div>
      </div>
    `;
  }

  container.innerHTML = `
    <div class="mt-4">
      <div class="flex justify-between items-center mb-3">
        <p class="text-sm text-gray-600">
          <strong>Calorie Target:</strong> ${(plan.calorie_target||0).toFixed(0)} kcal/day
          <span class="ml-3 text-xs text-gray-400">${plan.duration_days}-day plan · Generated ${new Date(plan.created_at).toLocaleDateString()}</span>
        </p>
      </div>
      ${disclaimerHtml}
      ${daysHtml}
    </div>
  `;
}

function _mealSection(title, items) {
  if (!items || items.length === 0) return '';
  const itemsHtml = items.map(item => `
    <div class="meal-card">
      <p class="font-medium text-sm text-gray-800">${item.name}</p>
      <p class="text-xs text-gray-500">${item.portion}</p>
      <p class="text-xs text-gray-400 mt-0.5">
        ${item.calories.toFixed(0)} kcal · P: ${item.protein_g.toFixed(1)}g · C: ${item.carbs_g.toFixed(1)}g · F: ${item.fat_g.toFixed(1)}g
      </p>
    </div>
  `).join('');
  return `
    <div>
      <p class="text-xs font-semibold text-green-700 uppercase tracking-wide mb-1">${title}</p>
      ${itemsHtml}
    </div>
  `;
}
