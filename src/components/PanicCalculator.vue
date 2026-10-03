<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const emit = defineEmits(['exitPanic'])

const disguiseMode = ref('notes') // 'calculator' | 'notes'
const display = ref('0')
const prevValue = ref(null)
const operator = ref(null)
const waitingForOperand = ref(false)
const inputPinBuffer = ref('')
const showUnlockPrompt = ref(false)
const unlockPinInput = ref('')
const unlockError = ref(false)

const TARGET_PIN = '1234'

// Calculator logic
const handleDigit = (digit) => {
  inputPinBuffer.value += digit
  if (inputPinBuffer.value.length > 8) {
    inputPinBuffer.value = inputPinBuffer.value.slice(-8)
  }

  if (inputPinBuffer.value.endsWith(TARGET_PIN)) {
    restoreApp()
    return
  }

  if (waitingForOperand.value) {
    display.value = String(digit)
    waitingForOperand.value = false
  } else {
    display.value = display.value === '0' ? String(digit) : display.value + digit
  }
}

const handleDecimal = () => {
  if (waitingForOperand.value) {
    display.value = '0.'
    waitingForOperand.value = false
    return
  }
  if (!display.value.includes('.')) {
    display.value += '.'
  }
}

const clearAll = () => {
  display.value = '0'
  prevValue.value = null
  operator.value = null
  waitingForOperand.value = false
  inputPinBuffer.value = ''
}

const handleOperator = (nextOp) => {
  const inputValue = parseFloat(display.value)

  if (prevValue.value == null) {
    prevValue.value = inputValue
  } else if (operator.value) {
    const currentValue = prevValue.value || 0
    const newValue = performCalculation(operator.value, currentValue, inputValue)
    display.value = String(newValue)
    prevValue.value = newValue
  }

  waitingForOperand.value = true
  operator.value = nextOp
}

const performCalculation = (op, a, b) => {
  switch (op) {
    case '+': return a + b
    case '-': return a - b
    case '×': return a * b
    case '÷': return b !== 0 ? a / b : 'Error'
    default: return b
  }
}

const handleEquals = () => {
  if (display.value === TARGET_PIN || inputPinBuffer.value.includes(TARGET_PIN)) {
    restoreApp()
    return
  }

  const inputValue = parseFloat(display.value)
  if (operator.value && prevValue.value != null) {
    const result = performCalculation(operator.value, prevValue.value, inputValue)
    display.value = String(result)
    prevValue.value = null
    operator.value = null
    waitingForOperand.value = true
  }
}

const restoreApp = () => {
  emit('exitPanic')
}

const handleUnlockSubmit = () => {
  if (unlockPinInput.value === TARGET_PIN) {
    restoreApp()
  } else {
    unlockError.value = true
    setTimeout(() => {
      unlockError.value = false
      unlockPinInput.value = ''
    }, 1500)
  }
}

// Disguise document title while in panic mode
let originalTitle = ''
onMounted(() => {
  originalTitle = document.title
  document.title = disguiseMode.value === 'notes' ? 'Meeting Notes - Q4 Operations & Deliverables' : 'Calculator'
})

onUnmounted(() => {
  document.title = originalTitle
})
</script>

<template>
  <div class="panic-container">
    <!-- Disguise Mode 1: Corporate Work Notes (Default innocuous screen) -->
    <div v-if="disguiseMode === 'notes'" class="notes-disguise-layout">
      <!-- Notes Top Header Bar -->
      <header class="notes-header">
        <div class="notes-doc-title-row">
          <span class="doc-icon">📄</span>
          <div class="doc-title-info">
            <span class="doc-title">Project Roadmap & Sprint Review — Q4 Deliverables</span>
            <span class="doc-meta">Saved to Cloud • Last edit 3 mins ago</span>
          </div>
        </div>

        <div class="notes-right-tools">
          <button class="mode-toggle-link" @click="disguiseMode = 'calculator'">
            Switch to Calculator
          </button>
          <button 
            class="discreet-restore-dot" 
            title="Restore session"
            @click="showUnlockPrompt = true"
          >
            •
          </button>
        </div>
      </header>

      <!-- Notes Document Body -->
      <main class="notes-doc-body">
        <article class="doc-paper">
          <h2>1. Executive Summary & Objective</h2>
          <p>
            The cross-functional alignment review for the upcoming infrastructure sprint was finalized on Wednesday. Key priority involves standardizing containerized deployment pipelines, reducing cache latency on CDN edges, and streamlining daily standup action items.
          </p>

          <h3>2. Key Milestones & Owner Allocation</h3>
          <ul>
            <li><strong>Database Index Optimization:</strong> Schema migrations scheduled for Saturday maintenance window (Lead: Sarah K.)</li>
            <li><strong>API Contract Standardization:</strong> Deprecating legacy v1 JSON endpoints by end of month (Lead: David T.)</li>
            <li><strong>QA Automated Regression Suite:</strong> Coverage targeted at 88% before regional rollouts.</li>
          </ul>

          <h3>3. Risk Mitigation & Action Items</h3>
          <p>
            Dependencies on external microservices require fallback circuit breakers. Weekly progress will be logged in the centralized repository wiki.
          </p>

          <div class="notes-footer-hint">
            <span>Press the discreet dot in header or switch mode to unlock</span>
          </div>
        </article>
      </main>
    </div>

    <!-- Disguise Mode 2: Standard Calculator -->
    <div v-else class="calculator-card">
      <div class="calc-top-bar">
        <span class="calc-brand">Standard Scientific</span>
        <div class="calc-actions">
          <button class="mode-toggle-link" @click="disguiseMode = 'notes'">
            Switch to Notes
          </button>
          <button 
            class="discreet-restore-dot" 
            title="Quick Access"
            @click="showUnlockPrompt = true"
          >
            •
          </button>
        </div>
      </div>

      <!-- Main Display -->
      <div class="calc-screen">
        <div class="calc-history">{{ prevValue != null ? `${prevValue} ${operator || ''}` : '' }}</div>
        <div class="calc-main-num">{{ display }}</div>
      </div>

      <!-- Keypad -->
      <div class="calc-keypad">
        <button class="calc-btn btn-func" @click="clearAll">C</button>
        <button class="calc-btn btn-func" @click="display = String(-parseFloat(display))">±</button>
        <button class="calc-btn btn-func" @click="display = String(parseFloat(display) / 100)">%</button>
        <button class="calc-btn btn-op" @click="handleOperator('÷')">÷</button>

        <button class="calc-btn" @click="handleDigit(7)">7</button>
        <button class="calc-btn" @click="handleDigit(8)">8</button>
        <button class="calc-btn" @click="handleDigit(9)">9</button>
        <button class="calc-btn btn-op" @click="handleOperator('×')">×</button>

        <button class="calc-btn" @click="handleDigit(4)">4</button>
        <button class="calc-btn" @click="handleDigit(5)">5</button>
        <button class="calc-btn" @click="handleDigit(6)">6</button>
        <button class="calc-btn btn-op" @click="handleOperator('-')">−</button>

        <button class="calc-btn" @click="handleDigit(1)">1</button>
        <button class="calc-btn" @click="handleDigit(2)">2</button>
        <button class="calc-btn" @click="handleDigit(3)">3</button>
        <button class="calc-btn btn-op" @click="handleOperator('+')">+</button>

        <button class="calc-btn btn-zero" @click="handleDigit(0)">0</button>
        <button class="calc-btn" @click="handleDecimal">.</button>
        <button class="calc-btn btn-op btn-equals" @click="handleEquals">=</button>
      </div>

      <div class="calc-footer-hint">
        <span>Memory Ready • Rad</span>
      </div>
    </div>

    <!-- Discreet PIN Modal -->
    <div v-if="showUnlockPrompt" class="unlock-overlay" @click.self="showUnlockPrompt = false">
      <div class="unlock-modal">
        <h3>Session Authentication</h3>
        <p>Enter Master PIN to restore application:</p>
        <div class="pin-input-group">
          <input 
            type="password" 
            v-model="unlockPinInput" 
            placeholder="PIN (Default: 1234)" 
            maxlength="6"
            @keyup.enter="handleUnlockSubmit"
            autofocus
          />
          <button class="btn-primary" @click="handleUnlockSubmit">Unlock</button>
        </div>
        <p v-if="unlockError" class="unlock-err">Incorrect PIN. Please try again.</p>
        <div class="unlock-actions">
          <button class="btn-cancel" @click="showUnlockPrompt = false">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.panic-container {
  min-height: 100vh;
  background: #191920;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: #fff;
}

/* Notes App Disguise Layout */
.notes-disguise-layout {
  width: 100%;
  min-height: 100vh;
  background: #1e1e24;
  color: #e2e8f0;
  display: flex;
  flex-direction: column;
}

.notes-header {
  height: 56px;
  background: #252530;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
}

.notes-doc-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.doc-icon {
  font-size: 1.3rem;
}

.doc-title-info {
  display: flex;
  flex-direction: column;
}

.doc-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #ffffff;
}

.doc-meta {
  font-size: 0.72rem;
  color: #888899;
}

.notes-right-tools {
  display: flex;
  align-items: center;
  gap: 14px;
}

.mode-toggle-link {
  font-size: 0.75rem;
  color: #8888aa;
  background: none;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 4px 10px;
  border-radius: 6px;
  cursor: pointer;
}
.mode-toggle-link:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.05);
}

.discreet-restore-dot {
  color: #444455;
  font-size: 1.4rem;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
}
.discreet-restore-dot:hover {
  color: #a855f7;
}

.notes-doc-body {
  flex: 1;
  display: flex;
  justify-content: center;
  padding: 40px 20px;
  background: #18181f;
}

.doc-paper {
  max-width: 760px;
  width: 100%;
  background: #22222c;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 8px;
  padding: 48px;
  line-height: 1.7;
}

.doc-paper h2 {
  font-size: 1.4rem;
  margin-bottom: 12px;
  color: #fff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding-bottom: 6px;
}

.doc-paper h3 {
  font-size: 1.15rem;
  margin: 24px 0 10px;
  color: #f1f5f9;
}

.doc-paper p {
  font-size: 0.92rem;
  color: #cbd5e1;
  margin-bottom: 14px;
}

.doc-paper ul {
  margin-left: 20px;
  font-size: 0.9rem;
  color: #cbd5e1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.notes-footer-hint {
  margin-top: 40px;
  font-size: 0.75rem;
  color: #555566;
  text-align: right;
}

/* Calculator Card */
.calculator-card {
  width: 100%;
  max-width: 360px;
  background: #2b2b36;
  border-radius: 20px;
  box-shadow: 0 20px 50px rgba(0,0,0,0.5);
  padding: 24px;
  border: 1px solid rgba(255,255,255,0.1);
}

.calc-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #888899;
  font-size: 0.8rem;
  margin-bottom: 12px;
}

.calc-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.calc-screen {
  background: #1e1e26;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 20px;
  text-align: right;
  min-height: 80px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.calc-history {
  font-size: 0.85rem;
  color: #8888aa;
  min-height: 18px;
}

.calc-main-num {
  font-size: 2.2rem;
  font-weight: 500;
  letter-spacing: -0.02em;
  color: #ffffff;
}

.calc-keypad {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.calc-btn {
  height: 56px;
  border-radius: 14px;
  font-size: 1.25rem;
  font-weight: 500;
  background: #363644;
  color: #ffffff;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.calc-btn:hover { background: #444455; }
.calc-btn:active { transform: scale(0.96); }

.btn-func { background: #474758; color: #cbd5e1; }
.btn-op { background: #f97316; color: #ffffff; font-weight: 600; }
.btn-op:hover { background: #ea580c; }
.btn-equals { background: #059669; }
.btn-equals:hover { background: #047857; }
.btn-zero { grid-column: span 2; border-radius: 14px; }

.calc-footer-hint {
  margin-top: 18px;
  text-align: center;
  font-size: 0.75rem;
  color: #64748b;
}

/* Unlock overlay */
.unlock-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.unlock-modal {
  background: #1a1c29;
  border: 1px solid rgba(168, 85, 247, 0.3);
  border-radius: 16px;
  padding: 28px;
  width: 90%;
  max-width: 380px;
  text-align: center;
}

.unlock-modal h3 {
  font-size: 1.2rem;
  margin-bottom: 8px;
  color: #f8fafc;
}

.unlock-modal p {
  font-size: 0.85rem;
  color: #94a3b8;
  margin-bottom: 20px;
}

.pin-input-group {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.pin-input-group input {
  flex: 1;
  background: #0f111a;
  border: 1px solid rgba(255,255,255,0.15);
  padding: 10px 14px;
  border-radius: 10px;
  color: #fff;
  font-size: 1rem;
  text-align: center;
  letter-spacing: 0.1em;
}

.unlock-err {
  color: #f87171 !important;
  font-size: 0.8rem !important;
  margin-top: 6px;
}

.btn-cancel {
  background: none;
  border: none;
  color: #64748b;
  font-size: 0.8rem;
  cursor: pointer;
  margin-top: 10px;
}
</style>
