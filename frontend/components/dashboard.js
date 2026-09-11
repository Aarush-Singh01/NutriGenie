/**
 * Dashboard component — calorie ring, macro pie, progress bars, weekly trend.
 */

let _calorieDonutChart = null;
let _macroPieChart = null;
let _weeklyLineChart = null;

async function renderDashboard() {
  const root = document.getElementById('dashboard-root');
  if (!root) return;

  root.innerHTML = `
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-bold text-green-800">📊 Dashboard</h2>
      <button class="btn-secondary text-xs" id="dash-refresh">🔄 Refresh</button>
    </div>
    <div id="dash-loading" class="text-center py-12 text-gray-400">
      <span class="spinner"></span>
      <p class="mt-2 text-sm">Loading dashboard…</p>
    </div>
    <div id="dash-content" class="hidden"></div>
    <div id="dash-error" class="hidden text-red-500 text-sm card"></div>
  `;

  document.getElementById('dash-refresh').addEventListener('click', renderDashboard);
  await _loadDashboard();
}

async function _loadDashboard() {
  const loading = document.getElementById('dash-loading');
  const content = document.getElementById('dash-content');
  const errEl   = document.getElementById('dash-error');

  loading.classList.remove('hidden');
  content.classList.add('hidden');
  errEl.classList.add('hidden');

  try {
    const [daily, weekly] = await Promise.all([
      apiGet(`/dashboard/daily?user_id=${currentUserId}`),
      apiGet(`/dashboard/weekly?user_id=${currentUserId}`),
    ]);

    loading.classList.add('hidden');
    content.classList.remove('hidden');
    _renderDashboardContent(content, daily, weekly);
  } catch (err) {
    loading.classList.add('hidden');
    errEl.classList.remove('hidden');
    errEl.textContent = `Could not load dashboard: ${err.message}`;
  }
}

function _renderDashboardContent(container, daily, weekly) {
  const calPct = Math.min(daily.calorie_percent, 100);
  const calColor = daily.calorie_percent > 110 ? 'text-red-600' : 'text-green-700';

  container.innerHTML = `
    <!-- Top stat cards -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
      ${_statCard('🔥 Calories', `${daily.calorie_consumed.toFixed(0)} / ${daily.calorie_target.toFixed(0)}`, 'kcal', daily.calorie_percent)}
      ${_statCard('💪 Protein',  `${daily.protein_g.toFixed(1)} / ${daily.protein_target_g.toFixed(1)}`, 'g', (daily.protein_g/daily.protein_target_g*100).toFixed(0))}
      ${_statCard('🍞 Carbs',    `${daily.carbs_g.toFixed(1)} / ${daily.carbs_target_g.toFixed(1)}`, 'g', (daily.carbs_g/daily.carbs_target_g*100).toFixed(0))}
      ${_statCard('🫒 Fat',      `${daily.fat_g.toFixed(1)} / ${daily.fat_target_g.toFixed(1)}`, 'g', (daily.fat_g/daily.fat_target_g*100).toFixed(0))}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <!-- Calorie donut -->
      <div class="card">
        <h3 class="font-semibold text-gray-700 mb-3">Daily Calories</h3>
        <div class="chart-container" style="height:220px">
          <canvas id="calorie-donut"></canvas>
        </div>
        <p class="text-center text-sm mt-2 ${calColor} font-semibold">${daily.calorie_percent.toFixed(0)}% of daily target</p>
      </div>
      <!-- Macro pie -->
      <div class="card">
        <h3 class="font-semibold text-gray-700 mb-3">Macro Breakdown (today)</h3>
        <div class="chart-container" style="height:220px">
          <canvas id="macro-pie"></canvas>
        </div>
      </div>
    </div>

    <!-- Progress bars -->
    <div class="card mb-6">
      <h3 class="font-semibold text-gray-700 mb-4">Nutrient Progress vs Targets</h3>
      <div id="progress-bars" class="space-y-3"></div>
    </div>

    <!-- Weekly trend -->
    <div class="card">
      <h3 class="font-semibold text-gray-700 mb-3">Weekly Calorie Trend</h3>
      <p class="text-xs text-gray-400 mb-3">
        Avg: <strong>${weekly.avg_calories} kcal/day</strong> ·
        Goal hit: <strong>${weekly.goal_hit_days} / 7 days</strong> (±15% of target)
      </p>
      <div class="chart-container" style="height:200px">
        <canvas id="weekly-line"></canvas>
      </div>
    </div>
  `;

  // Progress bars
  const pbContainer = document.getElementById('progress-bars');
  for (const n of daily.nutrients) {
    const pct = Math.min(n.percent, 100);
    const over = n.percent > 110;
    pbContainer.innerHTML += `
      <div>
        <div class="flex justify-between text-xs text-gray-600 mb-1">
          <span>${n.name}</span>
          <span>${n.current} / ${n.target} ${n.unit} (${n.percent.toFixed(0)}%)</span>
        </div>
        <div class="progress-bar-track">
          <div class="progress-bar-fill ${over?'over':''}" style="width:${pct}%"></div>
        </div>
      </div>
    `;
  }

  // Calorie donut
  const calorieCtx = document.getElementById('calorie-donut');
  if (calorieCtx) {
    if (_calorieDonutChart) _calorieDonutChart.destroy();
    _calorieDonutChart = new Chart(calorieCtx, {
      type: 'doughnut',
      data: {
        labels: ['Consumed', 'Remaining'],
        datasets: [{
          data: [
            Math.min(daily.calorie_consumed, daily.calorie_target),
            Math.max(daily.calorie_target - daily.calorie_consumed, 0),
          ],
          backgroundColor: ['#16a34a', '#e5e7eb'],
          borderWidth: 0,
        }],
      },
      options: {
        cutout: '70%',
        plugins: { legend: { position: 'bottom' } },
        responsive: true, maintainAspectRatio: false,
      },
    });
  }

  // Macro pie
  const macroCtx = document.getElementById('macro-pie');
  if (macroCtx) {
    if (_macroPieChart) _macroPieChart.destroy();
    _macroPieChart = new Chart(macroCtx, {
      type: 'pie',
      data: {
        labels: ['Protein', 'Carbohydrates', 'Fat'],
        datasets: [{
          data: [
            daily.protein_g * 4,   // kcal from protein
            daily.carbs_g * 4,     // kcal from carbs
            daily.fat_g * 9,       // kcal from fat
          ],
          backgroundColor: ['#3b82f6', '#f59e0b', '#ef4444'],
          borderWidth: 0,
        }],
      },
      options: {
        plugins: { legend: { position: 'bottom' } },
        responsive: true, maintainAspectRatio: false,
      },
    });
  }

  // Weekly line chart
  const weeklyCtx = document.getElementById('weekly-line');
  if (weeklyCtx) {
    if (_weeklyLineChart) _weeklyLineChart.destroy();
    const labels = weekly.weekly_data.map(w => w.date.slice(5)); // MM-DD
    const calories = weekly.weekly_data.map(w => w.calories);
    _weeklyLineChart = new Chart(weeklyCtx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Calories',
            data: calories,
            borderColor: '#16a34a',
            backgroundColor: 'rgba(22,163,74,0.08)',
            tension: 0.3, fill: true, pointRadius: 4,
          },
          {
            label: 'Target',
            data: Array(7).fill(weekly.calorie_target),
            borderColor: '#f59e0b',
            borderDash: [6, 3],
            pointRadius: 0,
          },
        ],
      },
      options: {
        plugins: { legend: { position: 'bottom' } },
        scales: { y: { beginAtZero: true } },
        responsive: true, maintainAspectRatio: false,
      },
    });
  }
}

function _statCard(label, value, unit, pct) {
  const numPct = parseFloat(pct) || 0;
  const color = numPct > 110 ? 'text-red-600' : numPct >= 80 ? 'text-green-700' : 'text-amber-600';
  return `
    <div class="card text-center py-3">
      <p class="text-xs text-gray-500 mb-1">${label}</p>
      <p class="font-bold text-base ${color}">${value}</p>
      <p class="text-xs text-gray-400">${unit} · ${numPct.toFixed(0)}%</p>
    </div>
  `;
}
