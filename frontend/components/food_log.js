/**
 * Food Log component — log food entries, view today's log and totals.
 */

function renderFoodLog() {
  const root = document.getElementById('food-log-root');
  if (!root) return;

  root.innerHTML = `
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Log form -->
      <div class="card">
        <h2 class="text-xl font-bold text-green-800 mb-1">📝 Log a Meal</h2>
        <p class="text-sm text-gray-500 mb-4">Enter what you ate and get instant nutritional analysis.</p>

        <div class="space-y-3">
          <div>
            <label class="form-label">Food Name <span class="text-red-500">*</span></label>
            <input id="fl-food" class="form-input" type="text" placeholder="e.g. brown rice, paneer curry, oats" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="form-label">Quantity <span class="text-red-500">*</span></label>
              <input id="fl-qty" class="form-input" type="number" min="1" placeholder="100" />
            </div>
            <div>
              <label class="form-label">Unit</label>
              <select id="fl-unit" class="form-input">
                <option value="g">grams (g)</option>
                <option value="ml">ml</option>
                <option value="cup">cup</option>
                <option value="piece">piece</option>
                <option value="serving">serving</option>
                <option value="tbsp">tablespoon</option>
                <option value="oz">oz</option>
              </select>
            </div>
          </div>
          <div>
            <label class="form-label">Meal Type</label>
            <select id="fl-meal-type" class="form-input">
              <option value="breakfast">Breakfast</option>
              <option value="morning_snack">Morning Snack</option>
              <option value="lunch">Lunch</option>
              <option value="evening_snack">Evening Snack</option>
              <option value="dinner">Dinner</option>
              <option value="other">Other</option>
            </select>
          </div>
          <button class="btn-primary w-full" id="fl-log-btn">📊 Analyse & Log</button>
        </div>

        <div id="fl-feedback" class="mt-4 hidden"></div>
      </div>

      <!-- Today's summary -->
      <div>
        <div class="card">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold text-gray-700">Today's Intake</h3>
            <button class="btn-secondary text-xs" id="fl-refresh">🔄</button>
          </div>
          <div id="fl-totals" class="text-sm text-gray-600">Loading…</div>
        </div>
        <div class="card">
          <h3 class="font-semibold text-gray-700 mb-3">Today's Log</h3>
          <div id="fl-entries">Loading…</div>
        </div>
      </div>
    </div>
  `;

  document.getElementById('fl-log-btn').addEventListener('click', _logFood);
  document.getElementById('fl-refresh').addEventListener('click', _loadTodayLog);
  _loadTodayLog();
}

async function _logFood() {
  const food     = document.getElementById('fl-food').value.trim();
  const qty      = parseFloat(document.getElementById('fl-qty').value);
  const unit     = document.getElementById('fl-unit').value;
  const mealType = document.getElementById('fl-meal-type').value;

  if (!food || !qty) {
    showToast('Please enter food name and quantity.', 'error');
    return;
  }

  const btn = document.getElementById('fl-log-btn');
  const feedback = document.getElementById('fl-feedback');
  btn.disabled = true;
  btn.textContent = '⏳ Analysing…';
  feedback.classList.add('hidden');

  try {
    const entry = await apiPost('/log', {
      user_id: currentUserId, food_name: food,
      quantity: qty, unit, meal_type: mealType,
    });

    feedback.classList.remove('hidden');
    feedback.innerHTML = `
      <div class="bg-green-50 border border-green-200 rounded-lg p-3">
        <p class="font-semibold text-green-800 text-sm mb-1">✅ Logged: ${entry.food_name}</p>
        <div class="grid grid-cols-2 gap-1 text-xs text-gray-700">
          <span>🔥 ${entry.nutrition.calories.toFixed(1)} kcal</span>
          <span>💪 ${entry.nutrition.protein_g.toFixed(1)}g protein</span>
          <span>🍞 ${entry.nutrition.carbs_g.toFixed(1)}g carbs</span>
          <span>🫒 ${entry.nutrition.fat_g.toFixed(1)}g fat</span>
          <span>🌾 ${entry.nutrition.fiber_g.toFixed(1)}g fiber</span>
        </div>
        ${entry.feedback ? `<p class="mt-2 text-xs text-gray-600 italic">${entry.feedback.substring(0, 300)}</p>` : ''}
      </div>
    `;

    // Clear form
    document.getElementById('fl-food').value = '';
    document.getElementById('fl-qty').value = '';
    showToast('Food logged!', 'success');
    _loadTodayLog();
  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = '📊 Analyse & Log';
  }
}

async function _loadTodayLog() {
  const totalsEl  = document.getElementById('fl-totals');
  const entriesEl = document.getElementById('fl-entries');
  if (!totalsEl || !entriesEl) return;

  try {
    const data = await apiGet(`/log/today?user_id=${currentUserId}`);
    const t = data.daily_totals;

    totalsEl.innerHTML = `
      <div class="grid grid-cols-2 gap-2 text-xs">
        <div class="bg-green-50 rounded p-2 text-center">
          <p class="font-bold text-green-800 text-base">${t.calories.toFixed(0)}</p>
          <p class="text-gray-500">kcal / ${data.calorie_target.toFixed(0)}</p>
        </div>
        <div class="bg-blue-50 rounded p-2 text-center">
          <p class="font-bold text-blue-800 text-base">${t.protein_g.toFixed(1)}g</p>
          <p class="text-gray-500">protein / ${data.protein_target_g.toFixed(0)}g</p>
        </div>
        <div class="bg-amber-50 rounded p-2 text-center">
          <p class="font-bold text-amber-800 text-base">${t.carbs_g.toFixed(1)}g</p>
          <p class="text-gray-500">carbs</p>
        </div>
        <div class="bg-red-50 rounded p-2 text-center">
          <p class="font-bold text-red-800 text-base">${t.fat_g.toFixed(1)}g</p>
          <p class="text-gray-500">fat</p>
        </div>
      </div>
      <p class="text-xs text-gray-400 mt-2">${t.entries_count} item(s) logged today</p>
    `;

    if (data.entries.length === 0) {
      entriesEl.innerHTML = '<p class="text-xs text-gray-400">No entries yet. Log your first meal!</p>';
    } else {
      entriesEl.innerHTML = `
        <table class="w-full text-xs">
          <thead>
            <tr class="text-left text-gray-500 border-b">
              <th class="pb-1">Food</th>
              <th class="pb-1">Qty</th>
              <th class="pb-1">kcal</th>
              <th class="pb-1">P/C/F</th>
              <th class="pb-1"></th>
            </tr>
          </thead>
          <tbody>
            ${data.entries.map(e => `
              <tr class="border-b border-gray-100">
                <td class="py-1 font-medium">${e.food_name}</td>
                <td class="py-1 text-gray-500">${e.quantity_g.toFixed(0)}g</td>
                <td class="py-1">${e.nutrition.calories.toFixed(0)}</td>
                <td class="py-1 text-gray-500">${e.nutrition.protein_g.toFixed(0)}/${e.nutrition.carbs_g.toFixed(0)}/${e.nutrition.fat_g.toFixed(0)}</td>
                <td class="py-1">
                  <button class="text-red-400 hover:text-red-600 text-xs" onclick="_deleteEntry(${e.entry_id})">✕</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `;
    }
  } catch (err) {
    totalsEl.innerHTML = '<p class="text-xs text-gray-400">Could not load today\'s log.</p>';
    entriesEl.innerHTML = `<p class="text-xs text-red-400">${err.message}</p>`;
  }
}

async function _deleteEntry(entryId) {
  try {
    await apiDelete(`/log/${entryId}?user_id=${currentUserId}`);
    showToast('Entry deleted', 'success');
    _loadTodayLog();
  } catch (err) {
    showToast(`Could not delete: ${err.message}`, 'error');
  }
}
