/**
 * Chat component — conversational interface to NutriGenie agents.
 */

let _chatHistory = [];
let _chatInitialized = false;

function renderChat() {
  const root = document.getElementById('chat-root');
  if (!root) return;

  if (_chatInitialized) return; // Already rendered
  _chatInitialized = true;

  root.innerHTML = `
    <div class="card max-w-3xl mx-auto" style="height: 70vh; display: flex; flex-direction: column;">
      <div class="flex items-center justify-between mb-3">
        <div>
          <h2 class="text-xl font-bold text-green-800">💬 Ask NutriGenie</h2>
          <p class="text-xs text-gray-500">Ask about nutrition, get health guidance, or request a meal plan.</p>
        </div>
        <button class="btn-secondary text-xs" id="chat-clear">🗑️ Clear</button>
      </div>

      <!-- Messages -->
      <div id="chat-messages" class="flex-1 overflow-y-auto flex flex-col gap-3 py-2 px-1"
           style="min-height: 0;">
        <!-- Welcome message -->
        <div class="chat-bubble-agent">
          👋 Hi! I'm <strong>NutriGenie</strong>, your AI-powered nutrition assistant.<br><br>
          You can ask me things like:<br>
          • "How many calories in 100g of brown rice?"<br>
          • "Give me a high-protein meal plan for muscle gain"<br>
          • "What should I eat if I have diabetes?"<br>
          • "Analyse my lunch: dal, 2 rotis, and sabzi"
        </div>
      </div>

      <!-- Input area -->
      <div class="flex gap-2 mt-3 pt-3 border-t border-gray-100">
        <select id="chat-type" class="form-input w-40 flex-shrink-0 text-xs">
          <option value="">Auto-detect</option>
          <option value="nutrition_query">Nutrition Query</option>
          <option value="meal_plan">Meal Plan</option>
          <option value="health_advice">Health Advice</option>
          <option value="food_log">Food Analysis</option>
        </select>
        <input id="chat-input" class="form-input flex-1" type="text"
               placeholder="Ask about nutrition, meal plans, food analysis…"
               autocomplete="off" />
        <button class="btn-primary flex-shrink-0" id="chat-send">Send</button>
      </div>
    </div>

    <!-- Example prompts -->
    <div class="max-w-3xl mx-auto mt-4">
      <p class="text-xs text-gray-500 mb-2 font-semibold">💡 Try these example prompts:</p>
      <div class="flex flex-wrap gap-2" id="example-prompts">
        ${_examplePrompts().map(p => `
          <button class="text-xs bg-green-50 text-green-800 border border-green-200 rounded-full px-3 py-1 hover:bg-green-100 example-prompt-btn"
                  data-prompt="${p.text}" data-type="${p.type}">${p.label}</button>
        `).join('')}
      </div>
    </div>
  `;

  document.getElementById('chat-send').addEventListener('click', _sendChat);
  document.getElementById('chat-clear').addEventListener('click', _clearChat);
  document.getElementById('chat-input').addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); _sendChat(); }
  });

  document.getElementById('example-prompts').addEventListener('click', e => {
    const btn = e.target.closest('.example-prompt-btn');
    if (!btn) return;
    document.getElementById('chat-input').value = btn.dataset.prompt;
    document.getElementById('chat-type').value  = btn.dataset.type || '';
    _sendChat();
  });
}

function _examplePrompts() {
  return [
    { label: '🍚 Brown rice calories',   text: 'How many calories are in 100g of brown rice?', type: 'nutrition_query' },
    { label: '💪 High-protein plan',     text: 'Generate a high-protein 1-day meal plan for muscle gain', type: 'meal_plan' },
    { label: '🩺 Diabetes guidance',     text: 'What should I eat to manage type 2 diabetes?', type: 'health_advice' },
    { label: '🥗 Vegetarian protein',    text: 'How can vegetarians get enough protein in Indian diet?', type: 'nutrition_query' },
    { label: '❤️ Heart health',          text: 'What nutrition tips help with hypertension?', type: 'health_advice' },
    { label: '⚖️ Weight loss plan',      text: 'Create a 1500 calorie weight loss meal plan', type: 'meal_plan' },
    { label: '🫘 Dal nutrition',         text: 'What are the nutritional benefits of dal?', type: 'nutrition_query' },
    { label: '🌾 Iron rich foods',       text: 'Which Indian foods are highest in iron for anemia?', type: 'health_advice' },
  ];
}

async function _sendChat() {
  const input = document.getElementById('chat-input');
  const typeSelect = document.getElementById('chat-type');
  const message = input.value.trim();
  if (!message) return;

  const requestType = typeSelect.value || null;
  input.value = '';

  // Add user bubble
  _addBubble('user', message);

  // Add typing indicator
  const typingId = 'typing-' + Date.now();
  _addTypingIndicator(typingId);

  const btn = document.getElementById('chat-send');
  btn.disabled = true;

  try {
    const data = await apiPost('/chat', {
      user_id: currentUserId,
      message,
      request_type: requestType,
    });

    _removeTypingIndicator(typingId);
    _addBubble('agent', data.response, data.agent_used, data.disclaimer);
    _chatHistory.push({ role: 'user', content: message });
    _chatHistory.push({ role: 'agent', content: data.response });
  } catch (err) {
    _removeTypingIndicator(typingId);
    _addBubble('agent', `❌ Error: ${err.message}`, 'error', null);
  } finally {
    btn.disabled = false;
    input.focus();
  }
}

function _addBubble(role, text, agentUsed, disclaimer) {
  const container = document.getElementById('chat-messages');
  if (!container) return;

  const bubble = document.createElement('div');
  bubble.className = role === 'user' ? 'chat-bubble-user' : 'chat-bubble-agent';
  bubble.textContent = text;

  if (role === 'agent' && agentUsed && agentUsed !== 'error') {
    const meta = document.createElement('p');
    meta.className = 'text-xs text-gray-400 mt-1';
    meta.textContent = `Agent: ${agentUsed.replace(/_/g,' ')}`;
    bubble.appendChild(meta);
  }

  container.appendChild(bubble);

  if (disclaimer) {
    const disc = document.createElement('div');
    disc.className = 'chat-bubble-disclaimer';
    disc.textContent = disclaimer;
    container.appendChild(disc);
  }

  container.scrollTop = container.scrollHeight;
}

function _addTypingIndicator(id) {
  const container = document.getElementById('chat-messages');
  if (!container) return;
  const indicator = document.createElement('div');
  indicator.id = id;
  indicator.className = 'chat-bubble-agent';
  indicator.innerHTML = '<span class="spinner" style="width:16px;height:16px;border-width:2px;"></span> <span class="text-gray-400 text-xs ml-1">NutriGenie is thinking…</span>';
  container.appendChild(indicator);
  container.scrollTop = container.scrollHeight;
}

function _removeTypingIndicator(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function _clearChat() {
  _chatHistory = [];
  const container = document.getElementById('chat-messages');
  if (container) {
    container.innerHTML = `
      <div class="chat-bubble-agent">Chat cleared. How can I help you with nutrition today?</div>
    `;
  }
}
