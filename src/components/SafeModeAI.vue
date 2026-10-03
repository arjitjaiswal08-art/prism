<script setup>
import { ref, onMounted, nextTick } from 'vue'

const props = defineProps({
  user: {
    type: Object,
    required: true
  },
  selectedCity: {
    type: String,
    required: true
  }
})

const userInput = ref('')
const isThinking = ref(false)
const showBreathingWidget = ref(false)
const breathingPhase = ref('Inhale (4s)')
const breathingCounter = ref(4)
let breathingTimer = null

const chatHistory = ref([
  {
    id: 'ai-init',
    sender: 'SafeMode AI',
    isAi: true,
    time: 'Just now',
    text: `Hello friend 🌈! I am your SafeMode Companion. Whether you need coming-out strategies tailored for Indian families, immediate grounding when dysphoria or anxiety peaks, safe verified spots in ${props.selectedCity}, or quick legal rights explainers — I'm right here. How can I support you today?`
  }
])

const promptChips = [
  { id: 'p1', label: '🌱 How to safely come out to conservative parents?', query: 'How to safely come out to conservative Indian parents?' },
  { id: 'p2', label: '🧘 Having intense panic / dysphoria (Ground Me)', query: 'I am feeling overwhelmed with panic and gender dysphoria right now, help me ground myself' },
  { id: 'p3', label: '🗺️ Safe queer hangouts in my city', query: `Recommend safe verified LGBTQ cafes and spaces in ${props.selectedCity}` },
  { id: 'p4', label: '⚖️ What are my rights if harassed by police in India?', query: 'What are my legal rights if stopped or harassed by police in India?' }
]

const startBreathingExercise = () => {
  showBreathingWidget.value = true
  let phaseIndex = 0
  const phases = ['Inhale (4s)', 'Hold (4s)', 'Exhale (4s)', 'Hold (4s)']
  breathingCounter.value = 4

  if (breathingTimer) clearInterval(breathingTimer)

  breathingTimer = setInterval(() => {
    breathingCounter.value -= 1
    if (breathingCounter.value <= 0) {
      phaseIndex = (phaseIndex + 1) % phases.length
      breathingPhase.value = phases[phaseIndex]
      breathingCounter.value = 4
    }
  }, 1000)
}

const stopBreathingExercise = () => {
  showBreathingWidget.value = false
  if (breathingTimer) clearInterval(breathingTimer)
}

const sendQuery = (queryText) => {
  const text = (queryText || userInput.value).trim()
  if (!text) return

  // Push user message
  chatHistory.value.push({
    id: 'usr-' + Date.now(),
    sender: props.user.username,
    isAi: false,
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    text
  })

  userInput.value = ''
  isThinking.value = true
  scrollToBottom()

  // Generate intelligent context-aware reply
  setTimeout(() => {
    isThinking.value = false
    const reply = generateAiReply(text)
    chatHistory.value.push({
      id: 'ai-' + Date.now(),
      sender: 'SafeMode AI',
      isAi: true,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      text: reply.text,
      hasAction: reply.hasAction,
      actionType: reply.actionType
    })

    if (reply.actionType === 'breathing') {
      startBreathingExercise()
    }

    scrollToBottom()
  }, 1200)
}

const generateAiReply = (text) => {
  const lower = text.toLowerCase()

  if (lower.includes('panic') || lower.includes('dysphoria') || lower.includes('overwhelm') || lower.includes('anxiety') || lower.includes('ground')) {
    return {
      text: `Take a gentle, soft breath with me. You are safe in this moment. The physical sensations of anxiety and dysphoria are real, but they will pass.\n\nLet's try Box Breathing together (4-4-4-4). Notice the breathing guide widget above.\n\nAlso try the 5-4-3-2-1 Sensory Grounding:\n• 5 things you can see around you right now\n• 4 things you can physically touch (fabric, table)\n• 3 sounds you hear in your room\n• 2 scents you notice\n• 1 kind truth about yourself: You are valid, authentic, and whole.`,
      hasAction: true,
      actionType: 'breathing'
    }
  }

  if (lower.includes('come out') || lower.includes('coming out') || lower.includes('parents') || lower.includes('family')) {
    return {
      text: `Coming out is deeply personal and never a one-time race. In the Indian context, physical and financial safety must ALWAYS come first.\n\nKey Strategic Principles:\n1. **The Safety Test:** Are you financially independent? Do you have an emergency fund or a trusted friend's couch if tensions flare up?\n2. **Identify First Allies:** Can you confide in a supportive sibling or cousin first before elder relatives?\n3. **Provide Educational Buffers:** Parents often react out of fear or societal shame ('Log kya kahenge'). Having books like *'Queeristan'* or videos by affirming parents (like Sridhar Rangayan's films) can demystify myths.\n4. **Give Them Time:** It took you years to understand and embrace yourself; grant them some days to unlearn generations of conditioning.\n\nRemember: Staying in the closet until you are safe is NOT cowardice. It is strategic self-preservation.`,
      hasAction: false
    }
  }

  if (lower.includes('police') || lower.includes('law') || lower.includes('legal') || lower.includes('rights') || lower.includes('harass')) {
    return {
      text: `Important Legal Facts under Indian Law:\n\n1. **Section 377 is Decriminalized:** Consensual adult same-sex relationships in private are 100% legal (Navtej Singh Johar, 2018). Police cannot arrest or threaten you under 377.\n2. **No Blackmail / Extortion:** Police or hotel staff demanding money under threat of calling your parents is extortion under Section 384 IPC. You have the right to demand their badge ID and file a complaint with the Police Complaints Authority.\n3. **Transgender Persons Act 2019:** Trans persons have statutory rights against harassment. Violence or forcing trans individuals into begging carries penal consequences.\n4. **Emergency Cell:** If in immediate danger from rogue elements, dial **112 (National Emergency)** or the **Sahodari Transgender Emergency Cell at 1800 200 3802**.`,
      hasAction: false
    }
  }

  if (lower.includes('cafe') || lower.includes('hangout') || lower.includes('space') || lower.includes('place')) {
    return {
      text: `Based on our verified community audit directory in ${props.selectedCity}:\n\n• Check out the **Verified Safe Spaces Map** in the top navigation tab for GPS-located venues!\n• Top verified spots include community bookstores, queer-affirming clinics with gender-neutral restrooms, and independent cafes like Champaca (Bangalore), Subko (Mumbai), and Potboiler (Kolkata).\n• You can also filter by 'Therapist' or 'NGO & Shelter' directly in the map tab.`,
      hasAction: false
    }
  }

  return {
    text: `I hear you loud and clear. Navigating queer life in our society can feel like an emotional marathon, but you don't have to carry the weight alone.\n\nWhether you need safe spaces, confidential therapy slots with sliding scale fees, or anonymous solidarity from friends in our Feed and Chat rooms — Prism is built to protect your peace. What specific aspect would you like to explore next?`,
    hasAction: false
  }
}

const chatContainerRef = ref(null)
const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainerRef.value) {
      chatContainerRef.value.scrollTop = chatContainerRef.value.scrollHeight
    }
  })
}

onMounted(() => {
  scrollToBottom()
})
</script>

<template>
  <div class="ai-assistant-layout">
    <!-- Header -->
    <div class="ai-header glass-panel">
      <div class="ai-header-left">
        <div class="ai-avatar-glow">🤖</div>
        <div>
          <div class="ai-badge-row">
            <span class="badge badge-accent">Unique Differentiator</span>
            <span class="ai-status">● Live Neural Support</span>
          </div>
          <h2>SafeMode AI Assistant</h2>
          <p>Empathetic, culturally aware LGBTQ+ guidance for mental wellness, coming out, and legal protection in India.</p>
        </div>
      </div>

      <div class="ai-header-right">
        <button 
          v-if="!showBreathingWidget"
          class="btn-secondary" 
          @click="startBreathingExercise"
        >
          🌬️ Open Breathing Exercise
        </button>
        <button 
          v-else 
          class="btn-secondary" 
          @click="stopBreathingExercise"
        >
          ✕ Close Breathing Guide
        </button>
      </div>
    </div>

    <!-- Interactive Breathing / Panic Relief Tool -->
    <div v-if="showBreathingWidget" class="breathing-widget glass-panel animate-fade-in">
      <div class="breathing-content">
        <h3>Box Breathing (4-4-4-4 Technique)</h3>
        <p>Inhale calmness, hold steadily, release physical tension, pause in silence.</p>
        <div class="breathing-circle-wrap">
          <div :class="['breathing-circle', breathingPhase.toLowerCase().split(' ')[0]]">
            <span class="phase-name">{{ breathingPhase }}</span>
            <span class="countdown-num">{{ breathingCounter }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Chat Window -->
    <div class="ai-chat-card glass-panel">
      <!-- Conversation History -->
      <div ref="chatContainerRef" class="chat-messages-container">
        <div 
          v-for="msg in chatHistory" 
          :key="msg.id"
          :class="['chat-bubble-row', { 'is-user': !msg.isAi }]"
        >
          <div class="bubble-avatar">
            {{ msg.isAi ? '🤖' : user.username.charAt(0) }}
          </div>

          <div class="bubble-content">
            <div class="bubble-meta">
              <span class="bubble-sender">{{ msg.sender }}</span>
              <span class="bubble-time">{{ msg.time }}</span>
            </div>
            <div class="bubble-text">
              <p v-for="(paragraph, pIdx) in msg.text.split('\n\n')" :key="pIdx">
                {{ paragraph }}
              </p>
            </div>
          </div>
        </div>

        <!-- Thinking indicator -->
        <div v-if="isThinking" class="chat-bubble-row">
          <div class="bubble-avatar">🤖</div>
          <div class="bubble-content thinking-bubble">
            <span>Consulting queer-affirmative knowledge base</span>
            <div class="typing-dots">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Prompt Chips -->
      <div class="prompt-chips-bar">
        <span class="chips-label">Quick Prompts:</span>
        <button 
          v-for="chip in promptChips" 
          :key="chip.id"
          class="prompt-chip"
          @click="sendQuery(chip.query)"
        >
          {{ chip.label }}
        </button>
      </div>

      <!-- Composer Input -->
      <div class="ai-composer">
        <input 
          type="text" 
          v-model="userInput" 
          placeholder="Ask anything (e.g. How to handle coming out to parents, legal rights, therapist search)..."
          @keyup.enter="sendQuery()"
          class="ai-input"
        />
        <button 
          class="btn-primary" 
          :disabled="!userInput.trim()"
          @click="sendQuery()"
        >
          <span>Ask SafeMode</span> 🚀
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ai-assistant-layout {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 20px 60px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.ai-header {
  padding: 24px 28px;
  border-radius: var(--radius-lg);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, rgba(30, 20, 50, 0.85), rgba(18, 22, 38, 0.8));
  border: 1px solid rgba(236, 72, 153, 0.3);
  box-shadow: 0 8px 30px rgba(236, 72, 153, 0.15);
  flex-wrap: wrap;
  gap: 16px;
}

.ai-header-left {
  display: flex;
  align-items: center;
  gap: 18px;
}

.ai-avatar-glow {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ec4899, #8b5cf6);
  font-size: 1.8rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 20px rgba(236, 72, 153, 0.5);
}

.ai-badge-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
}

.ai-status {
  font-size: 0.72rem;
  color: #34d399;
  font-weight: 600;
}

.ai-header h2 {
  font-size: 1.6rem;
  font-weight: 800;
  color: #fff;
}

.ai-header p {
  color: var(--text-secondary);
  font-size: 0.88rem;
}

/* Breathing Widget */
.breathing-widget {
  padding: 28px;
  border-radius: var(--radius-lg);
  text-align: center;
  background: linear-gradient(135deg, rgba(16, 24, 40, 0.95), rgba(20, 30, 50, 0.9));
  border: 1px solid rgba(56, 189, 248, 0.3);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
}

.breathing-content h3 {
  font-size: 1.4rem;
  color: #38bdf8;
  margin-bottom: 4px;
}

.breathing-content p {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: 24px;
}

.breathing-circle-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 10px 0;
}

.breathing-circle {
  width: 170px;
  height: 170px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.25) 0%, rgba(168, 85, 247, 0.1) 70%);
  border: 3px solid #38bdf8;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 30px rgba(56, 189, 248, 0.4);
  transition: transform 4s ease-in-out, border-color 1s;
}

.breathing-circle.inhale {
  transform: scale(1.3);
  border-color: #34d399;
  box-shadow: 0 0 40px rgba(52, 211, 153, 0.6);
}

.breathing-circle.exhale {
  transform: scale(0.9);
  border-color: #f472b6;
  box-shadow: 0 0 25px rgba(244, 114, 182, 0.5);
}

.breathing-circle.hold {
  border-color: #fbbf24;
}

.phase-name {
  font-size: 1rem;
  font-weight: 700;
  color: #fff;
}

.countdown-num {
  font-size: 2.2rem;
  font-weight: 800;
  color: #38bdf8;
}

/* Chat Card */
.ai-chat-card {
  height: 640px;
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--border-light);
}

.chat-messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chat-bubble-row {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  max-width: 85%;
}

.chat-bubble-row.is-user {
  margin-left: auto;
  flex-direction: row-reverse;
}

.bubble-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
}

.is-user .bubble-avatar {
  background: linear-gradient(135deg, #a855f7, #ec4899);
  color: #fff;
  font-weight: 700;
}

.bubble-content {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-light);
  border-radius: 16px;
  padding: 14px 18px;
}

.is-user .bubble-content {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.25), rgba(236, 72, 153, 0.2));
  border-color: rgba(168, 85, 247, 0.35);
}

.bubble-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.bubble-sender {
  font-weight: 700;
  font-size: 0.8rem;
  color: #c084fc;
}

.is-user .bubble-sender {
  color: #f472b6;
}

.bubble-time {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.bubble-text p {
  font-size: 0.92rem;
  color: #e2e8f0;
  line-height: 1.6;
  margin-bottom: 8px;
}
.bubble-text p:last-child {
  margin-bottom: 0;
}

.thinking-bubble {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.typing-dots {
  display: flex;
  gap: 4px;
}
.typing-dots span {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #ec4899;
  animation: blink 1.2s infinite ease-in-out;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes blink {
  0%, 80%, 100% { opacity: 0.2; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1.2); }
}

/* Chips Bar */
.prompt-chips-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid var(--border-light);
  overflow-x: auto;
}

.chips-label {
  font-size: 0.72rem;
  color: var(--text-muted);
  font-weight: 600;
  white-space: nowrap;
}

.prompt-chip {
  white-space: nowrap;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-light);
  color: var(--text-secondary);
  font-size: 0.78rem;
  padding: 5px 12px;
  border-radius: var(--radius-full);
}
.prompt-chip:hover {
  background: rgba(168, 85, 247, 0.2);
  border-color: rgba(168, 85, 247, 0.4);
  color: #fff;
}

/* Composer */
.ai-composer {
  padding: 16px 20px;
  background: rgba(12, 14, 24, 0.85);
  border-top: 1px solid var(--border-light);
  display: flex;
  gap: 12px;
}

.ai-input {
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-light);
  padding: 12px 18px;
  border-radius: var(--radius-full);
  color: #fff;
  font-size: 0.9rem;
  outline: none;
}
.ai-input:focus {
  border-color: var(--border-active);
}
</style>
