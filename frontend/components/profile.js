/**
 * Profile component — user profile form with save/load.
 */

function renderProfile() {
  const root = document.getElementById('profile-root');
  if (!root) return;

  root.innerHTML = `
    <div class="card max-w-2xl mx-auto">
      <h2 class="text-xl font-bold text-green-800 mb-1">👤 Your Profile</h2>
      <p class="text-sm text-gray-500 mb-5">Set up your profile to get personalised meal plans and nutrition advice.</p>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="form-label">User ID <span class="text-red-500">*</span></label>
          <input id="p-user-id" class="form-input" type="text" value="${currentUserId}" placeholder="e.g. user_001" />
        </div>
        <div>
          <label class="form-label">Age <span class="text-red-500">*</span></label>
          <input id="p-age" class="form-input" type="number" min="1" max="120" placeholder="25" />
        </div>
        <div>
          <label class="form-label">Sex <span class="text-red-500">*</span></label>
          <select id="p-sex" class="form-input">
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div>
          <label class="form-label">Height (cm) <span class="text-red-500">*</span></label>
          <input id="p-height" class="form-input" type="number" min="50" max="300" placeholder="170" />
        </div>
        <div>
          <label class="form-label">Weight (kg) <span class="text-red-500">*</span></label>
          <input id="p-weight" class="form-input" type="number" min="10" max="500" placeholder="65" />
        </div>
        <div>
          <label class="form-label">Activity Level <span class="text-red-500">*</span></label>
          <select id="p-activity" class="form-input">
            <option value="sedentary">Sedentary (desk job, little exercise)</option>
            <option value="lightly_active">Lightly Active (1-3 days/week)</option>
            <option value="moderately_active" selected>Moderately Active (3-5 days/week)</option>
            <option value="very_active">Very Active (6-7 days/week)</option>
            <option value="extra_active">Extra Active (physical job + exercise)</option>
          </select>
        </div>
        <div>
          <label class="form-label">Primary Goal <span class="text-red-500">*</span></label>
          <select id="p-goal" class="form-input">
            <option value="healthy_eating">General Healthy Eating</option>
            <option value="weight_loss">Weight Loss</option>
            <option value="weight_gain">Weight Gain</option>
            <option value="muscle_gain">Muscle Gain</option>
            <option value="maintenance">Maintenance</option>
          </select>
        </div>
        <div>
          <label class="form-label">Dietary Preference</label>
          <select id="p-diet" class="form-input">
            <option value="none">No Restriction</option>
            <option value="vegetarian">Vegetarian</option>
            <option value="vegan">Vegan</option>
            <option value="eggetarian">Eggetarian</option>
            <option value="halal">Halal</option>
            <option value="jain">Jain</option>
          </select>
        </div>
        <div>
          <label class="form-label">Allergies</label>
          <input id="p-allergies" class="form-input" type="text" placeholder="e.g. peanuts, gluten, lactose" />
          <p class="text-xs text-gray-400 mt-1">Comma-separated list</p>
        </div>
        <div>
          <label class="form-label">Health Conditions</label>
          <input id="p-conditions" class="form-input" type="text" placeholder="e.g. diabetes, hypertension" />
          <p class="text-xs text-gray-400 mt-1">Comma-separated list</p>
        </div>
        <div class="sm:col-span-2">
          <label class="form-label">Cuisine / Cultural Preferences</label>
          <input id="p-cuisine" class="form-input" type="text" placeholder="e.g. Indian, South Indian, Gujarati" />
        </div>
      </div>

      <div class="mt-6 flex gap-3 flex-wrap">
        <button class="btn-primary" id="p-save-btn">💾 Save Profile</button>
        <button class="btn-secondary" id="p-load-btn">🔄 Load Profile</button>
      </div>

      <div id="p-status" class="mt-4 text-sm hidden"></div>
    </div>

    <div id="p-summary" class="card max-w-2xl mx-auto hidden">
      <h3 class="text-lg font-semibold text-green-800 mb-3">✅ Profile Saved</h3>
      <div id="p-summary-content" class="text-sm text-gray-700 space-y-1"></div>
      <p class="mt-3 text-xs text-green-700 font-medium">
        👉 Head to the Dashboard or Meal Plan tabs to get started!
      </p>
    </div>
  `;

  // Load existing profile if available
  _loadProfileIntoForm();

  document.getElementById('p-save-btn').addEventListener('click', _saveProfile);
  document.getElementById('p-load-btn').addEventListener('click', _loadProfileIntoForm);
}

async function _saveProfile() {
  const userId = document.getElementById('p-user-id').value.trim();
  const age    = parseInt(document.getElementById('p-age').value);
  const sex    = document.getElementById('p-sex').value;
  const height = parseFloat(document.getElementById('p-height').value);
  const weight = parseFloat(document.getElementById('p-weight').value);
  const activity = document.getElementById('p-activity').value;
  const goal     = document.getElementById('p-goal').value;
  const diet     = document.getElementById('p-diet').value;
  const allergiesRaw   = document.getElementById('p-allergies').value;
  const conditionsRaw  = document.getElementById('p-conditions').value;
  const cuisine = document.getElementById('p-cuisine').value;

  if (!userId || !age || !height || !weight) {
    showToast('Please fill in all required fields.', 'error');
    return;
  }

  const allergies   = allergiesRaw.split(',').map(s => s.trim()).filter(Boolean);
  const conditions  = conditionsRaw.split(',').map(s => s.trim()).filter(Boolean);

  const btn = document.getElementById('p-save-btn');
  btn.disabled = true;
  btn.textContent = '⏳ Saving…';

  try {
    const data = await apiPost('/profile', {
      user_id: userId, age, sex,
      height_cm: height, weight_kg: weight,
      activity_level: activity, primary_goal: goal,
      dietary_preference: diet, allergies, health_conditions: conditions,
      cuisine_preferences: cuisine,
    });

    setUserId(userId);
    _showProfileSummary(data);
    showToast('Profile saved!', 'success');
  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = '💾 Save Profile';
  }
}

async function _loadProfileIntoForm() {
  try {
    const data = await apiGet(`/profile/${currentUserId}`);
    document.getElementById('p-user-id').value   = data.user_id || currentUserId;
    document.getElementById('p-age').value        = data.age || '';
    document.getElementById('p-sex').value        = data.sex || 'male';
    document.getElementById('p-height').value     = data.height_cm || '';
    document.getElementById('p-weight').value     = data.weight_kg || '';
    document.getElementById('p-activity').value   = data.activity_level || 'moderately_active';
    document.getElementById('p-goal').value       = data.primary_goal || 'healthy_eating';
    document.getElementById('p-diet').value       = data.dietary_preference || 'none';
    document.getElementById('p-allergies').value  = (data.allergies || []).join(', ');
    document.getElementById('p-conditions').value = (data.health_conditions || []).join(', ');
    document.getElementById('p-cuisine').value    = data.cuisine_preferences || '';
    _showProfileSummary(data);
  } catch (_) {
    // Profile not found — that's OK, user fills in form
  }
}

function _showProfileSummary(data) {
  const summary = document.getElementById('p-summary');
  const content = document.getElementById('p-summary-content');
  if (!summary || !content) return;
  summary.classList.remove('hidden');
  content.innerHTML = `
    <p><strong>Name / ID:</strong> ${data.user_id}</p>
    <p><strong>Age:</strong> ${data.age} · <strong>Sex:</strong> ${data.sex}</p>
    <p><strong>Height:</strong> ${data.height_cm} cm · <strong>Weight:</strong> ${data.weight_kg} kg</p>
    <p><strong>Goal:</strong> ${data.primary_goal.replace(/_/g,' ')} · <strong>Activity:</strong> ${data.activity_level.replace(/_/g,' ')}</p>
    <p><strong>Diet:</strong> ${data.dietary_preference} · <strong>Cuisine:</strong> ${data.cuisine_preferences || 'Not specified'}</p>
    <p><strong>Allergies:</strong> ${(data.allergies||[]).join(', ')||'None'}</p>
    <p><strong>Health Conditions:</strong> ${(data.health_conditions||[]).join(', ')||'None'}</p>
  `;
}
