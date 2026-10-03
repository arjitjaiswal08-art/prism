<script setup>
import { ref, onMounted, nextTick } from 'vue'

const props = defineProps({
  rooms: {
    type: Array,
    required: true
  },
  user: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['triggerPanic'])

const activeRoomId = ref(props.rooms[0]?.id || 'room-1')
const messageInput = ref('')
const isAutoBlurEnabled = ref(true)
const disappearingTimer = ref('off')
const screenshotAlert = ref(false)
const showReportModal = ref(false)
const reportingUser = ref('')
const reportReason = ref('')
const messagesEndRef = ref(null)
const isTyping = ref(false)

// Local room messages store
const roomMessages = ref(
  props.rooms.reduce((acc, room) => {
    acc[room.id] = [...room.initialMessages]
    return acc
  }, {})
)

// Add 1:1 Direct Message conversation
const dmRoomId = 'dm-anon-peer'
roomMessages.value[dmRoomId] = [
  { id: 'dm1', sender: 'SolaceWanderer', pronouns: 'he/they', text: 'Hey there! Saw your post about finding queer-friendly rentals in Pune. Hope you are holding up well!', time: '11:02 AM', isSensitive: false },
  { id: 'dm2', sender: 'SolaceWanderer', pronouns: 'he/they', text: 'If you need broker contacts who don’t harass, let me know. Happy to share what worked for me.', time: '11:03 AM', isSensitive: false }
]

const currentRoom = () => {
  if (activeRoomId.value === dmRoomId) {
    return {
      id: dmRoomId,
      name: '👤 SolaceWanderer (1:1 Encrypted DM)',
      tag: 'Direct',
      description: 'End-to-end encrypted private session. Zero logs retained.'
    }
  }
  return props.rooms.find(r => r.id === activeRoomId.value) || props.rooms[0]
}

const currentMessages = () => {
  return roomMessages.value[activeRoomId.value] || []
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesEndRef.value) {
      messagesEndRef.value.scrollTop = messagesEndRef.value.scrollHeight
    }
  })
}

const sendMessage = () => {
  const text = messageInput.value.trim()
  if (!text) return

  const newMsg = {
    id: 'm-' + Date.now(),
    sender: props.user.username,
    pronouns: props.user.pronouns,
    text,
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    isSensitive: false,
    isSelf: true
  }

  if (!roomMessages.value[activeRoomId.value]) {
    roomMessages.value[activeRoomId.value] = []
  }

  roomMessages.value[activeRoomId.value].push(newMsg)
  messageInput.value = ''
  scrollToBottom()

  // Automated friendly simulation response after 1.5s
  simulatePeerReply()
}

const simulatePeerReply = () => {
  isTyping.value = true
  setTimeout(() => {
    isTyping.value = false
    const replies = [
      "Thank you for sharing this! You've got an entire community behind you here.",
      "Totally agree! So glad we have this safe space to speak up without fear.",
      "Sending you so much strength and warmth! Stay safe friend. 🌈",
      "That is a really valid point. It takes time, but things definitely get better."
    ]
    const randomReply = replies[Math.floor(Math.random() * replies.length)]

    const peerMsg = {
      id: 'm-reply-' + Date.now(),
      sender: activeRoomId.value === dmRoomId ? 'SolaceWanderer' : 'StarlightAlly',
      pronouns: 'they/them',
      text: randomReply,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isSensitive: false
    }

    roomMessages.value[activeRoomId.value].push(peerMsg)
    scrollToBottom()
  }, 1800)
}

const triggerScreenshotSimulation = () => {
  screenshotAlert.value = true
  setTimeout(() => {
    screenshotAlert.value = false
  }, 5000)
}

const openReport = (sender) => {
  reportingUser.value = sender
  reportReason.value = ''
  showReportModal.value = true
}

const submitReport = () => {
  showReportModal.value = false
  screenshotAlert.value = false
  alert(`User "${reportingUser.value}" has been flagged. Moderation algorithm will shadow-ban them if policy violation is confirmed.`)
}

onMounted(() => {
  scrollToBottom()
})
</script>

<template>
  <div class="chat-container">
    <!-- Screenshot Warning Banner -->
    <div v-if="screenshotAlert" class="screenshot-banner animate-fade-in">
      <span class="alert-icon">⚠️</span>
      <div class="alert-text">
        <strong>SCREENSHOT ATTEMPT INTERCEPTED:</strong>
        <span>A screenshot capture was detected. All chat members have been alerted to preserve confidentiality.</span>
      </div>
      <button class="alert-dismiss" @click="screenshotAlert = false">✕</button>
    </div>

    <!-- Chat Card Wrapper -->
    <div class="chat-card glass-panel">
      <!-- Left Channels Sidebar -->
      <aside class="chat-sidebar">
        <div class="sidebar-top">
          <div class="channel-title-row">
            <h3>💬 Safe Rooms</h3>
            <span class="badge badge-verified">E2EE</span>
          </div>
          <p class="sidebar-sub">No real names required</p>
        </div>

        <!-- Community Channels -->
        <div class="rooms-nav">
          <span class="group-label">Community Circles</span>
          <button 
            v-for="room in rooms" 
            :key="room.id"
            :class="['room-nav-btn', { active: activeRoomId === room.id }]"
            @click="activeRoomId = room.id; scrollToBottom()"
          >
            <span class="room-name">{{ room.name }}</span>
            <span class="member-count">{{ room.members }}</span>
          </button>

          <span class="group-label mt-3">Direct Encrypted Messages</span>
          <button 
            :class="['room-nav-btn', { active: activeRoomId === dmRoomId }]"
            @click="activeRoomId = dmRoomId; scrollToBottom()"
          >
            <span class="dm-status-dot"></span>
            <span class="room-name">SolaceWanderer</span>
            <span class="badge badge-tag">1:1</span>
          </button>
        </div>

        <!-- Privacy Safety Toolbox -->
        <div class="safety-toolbox">
          <span class="toolbox-title">🛡️ Safety Controls</span>
          
          <button class="tool-btn" @click="triggerScreenshotSimulation">
            <span>📸</span> Test Screenshot Alert
          </button>

          <div class="tool-toggle">
            <span>Blur Sensitive:</span>
            <input type="checkbox" v-model="isAutoBlurEnabled" />
          </div>

          <div class="tool-toggle">
            <span>Auto-Delete:</span>
            <select v-model="disappearingTimer" class="timer-select">
              <option value="off">Never</option>
              <option value="30s">30 Seconds</option>
              <option value="1hr">1 Hour</option>
              <option value="24hr">24 Hours</option>
            </select>
          </div>
        </div>
      </aside>

      <!-- Right Chat Window -->
      <main class="chat-main">
        <!-- Room Header -->
        <div class="chat-room-header">
          <div class="room-title-meta">
            <h2>{{ currentRoom().name }}</h2>
            <p>{{ currentRoom().description }}</p>
          </div>

          <div class="header-right-tools">
            <span class="badge badge-tag">🔒 End-to-End Encrypted</span>
            <button class="btn-panic btn-sm" @click="$emit('triggerPanic')">
              🚨 Hide Chat (Esc)
            </button>
          </div>
        </div>

        <!-- Messages History Viewport -->
        <div ref="messagesEndRef" class="messages-viewport">
          <div class="encryption-notice">
            <span class="lock-icon">🔒</span>
            <p>
              Messages in this room are encrypted end-to-end with temporary ephemeral session keys.
              No IP addresses or device logs are stored on our servers.
            </p>
          </div>

          <div 
            v-for="msg in currentMessages()" 
            :key="msg.id"
            :class="['message-row', { 'self-msg': msg.isSelf }]"
          >
            <div class="message-bubble">
              <div class="msg-header">
                <span class="msg-author">{{ msg.sender }}</span>
                <span v-if="msg.pronouns" class="msg-pronouns">({{ msg.pronouns }})</span>
                <span class="msg-time">{{ msg.time }}</span>

                <button 
                  v-if="!msg.isSelf" 
                  class="btn-report-flag" 
                  title="Report harassment"
                  @click="openReport(msg.sender)"
                >
                  🚩
                </button>
              </div>

              <!-- Message Text (with Blur option if sensitive) -->
              <div v-if="msg.isSensitive && isAutoBlurEnabled" class="sensitive-blurred-text">
                <span>⚠️ Sensitive message. Click to unblur</span>
              </div>
              <p v-else class="msg-text">{{ msg.text }}</p>
            </div>
          </div>

          <!-- Typing indicator -->
          <div v-if="isTyping" class="typing-indicator animate-fade-in">
            <span>Someone is typing</span>
            <div class="typing-dots">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>

        <!-- Message Composer -->
        <div class="chat-composer">
          <input 
            type="text" 
            v-model="messageInput" 
            :placeholder="`Message anonymously as ${user.username}...`"
            @keyup.enter="sendMessage"
            class="composer-input"
          />
          <button 
            class="btn-primary" 
            :disabled="!messageInput.trim()"
            @click="sendMessage"
          >
            <span>Send</span> ✈️
          </button>
        </div>
      </main>
    </div>

    <!-- Report Modal -->
    <div v-if="showReportModal" class="modal-backdrop" @click.self="showReportModal = false">
      <div class="modal-card glass-panel animate-fade-in">
        <div class="modal-header">
          <h3>Report User: {{ reportingUser }}</h3>
          <button class="close-modal-btn" @click="showReportModal = false">✕</button>
        </div>
        <div class="modal-body">
          <p class="report-intro">
            Prism maintains a strict zero-tolerance policy against hate speech, outing, or doxxing.
          </p>
          <div class="form-group">
            <label>Reason for Report</label>
            <select v-model="reportReason" class="form-input">
              <option value="hate">Harassment or Hate Speech</option>
              <option value="outing">Threatening to out / asking real identity</option>
              <option value="spam">Commercial Spam / Dating Solicitation</option>
              <option value="violence">Violence or self-harm incitement</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showReportModal = false">Cancel</button>
          <button class="btn-panic" @click="submitReport">Submit Report & Shadow-Ban</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px 20px 60px;
}

.screenshot-banner {
  background: linear-gradient(135deg, #ef4444, #b91c1c);
  color: #fff;
  padding: 14px 20px;
  border-radius: var(--radius-md);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 4px 20px rgba(239, 68, 68, 0.4);
}

.alert-icon {
  font-size: 1.5rem;
}

.alert-text {
  flex: 1;
  font-size: 0.88rem;
}

.alert-dismiss {
  color: #fff;
  font-size: 1.2rem;
  padding: 4px;
}

.chat-card {
  display: grid;
  grid-template-columns: 320px 1fr;
  height: 720px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--border-light);
}

/* Sidebar */
.chat-sidebar {
  background: rgba(14, 16, 26, 0.9);
  border-right: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
}

.sidebar-top {
  padding: 20px;
  border-bottom: 1px solid var(--border-light);
}

.channel-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.channel-title-row h3 {
  font-size: 1.2rem;
  font-weight: 700;
}

.sidebar-sub {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 2px;
}

.rooms-nav {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  overflow-y: auto;
}

.group-label {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}

.mt-3 {
  margin-top: 14px;
}

.room-nav-btn {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 0.88rem;
  text-align: left;
  transition: all var(--transition-fast);
}

.room-nav-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.room-nav-btn.active {
  background: rgba(168, 85, 247, 0.2);
  color: #fff;
  border: 1px solid rgba(168, 85, 247, 0.3);
  font-weight: 600;
}

.member-count {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.dm-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 6px #10b981;
  margin-right: 6px;
}

.safety-toolbox {
  padding: 16px;
  border-top: 1px solid var(--border-light);
  background: rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.toolbox-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: #c084fc;
  text-transform: uppercase;
}

.tool-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-light);
  color: var(--text-secondary);
  padding: 6px 12px;
  border-radius: var(--radius-md);
  font-size: 0.78rem;
  display: flex;
  align-items: center;
  gap: 6px;
}
.tool-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.tool-toggle {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.78rem;
  color: var(--text-secondary);
}

.timer-select {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid var(--border-light);
  color: #fff;
  border-radius: 6px;
  padding: 2px 6px;
  font-size: 0.75rem;
}
.timer-select option {
  background: #121422;
}

/* Chat Main */
.chat-main {
  display: flex;
  flex-direction: column;
  background: rgba(18, 20, 32, 0.7);
}

.chat-room-header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(14, 16, 26, 0.6);
}

.room-title-meta h2 {
  font-size: 1.15rem;
  font-weight: 700;
  color: #fff;
}

.room-title-meta p {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.header-right-tools {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Messages Viewport */
.messages-viewport {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.encryption-notice {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(168, 85, 247, 0.08);
  border: 1px dashed rgba(168, 85, 247, 0.3);
  padding: 10px 16px;
  border-radius: var(--radius-md);
  margin-bottom: 10px;
}

.lock-icon {
  font-size: 1.2rem;
}

.encryption-notice p {
  font-size: 0.75rem;
  color: #d8b4fe;
}

.message-row {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.message-row.self-msg {
  align-items: flex-end;
}

.message-bubble {
  max-width: 75%;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-light);
  border-radius: 16px 16px 16px 4px;
  padding: 10px 14px;
}

.self-msg .message-bubble {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.25), rgba(236, 72, 153, 0.25));
  border-color: rgba(168, 85, 247, 0.4);
  border-radius: 16px 16px 4px 16px;
}

.msg-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
  font-size: 0.75rem;
}

.msg-author {
  font-weight: 600;
  color: #38bdf8;
}

.self-msg .msg-author {
  color: #f472b6;
}

.msg-pronouns {
  color: var(--text-muted);
}

.msg-time {
  color: var(--text-muted);
  font-size: 0.7rem;
  margin-left: 4px;
}

.btn-report-flag {
  margin-left: 6px;
  font-size: 0.7rem;
  opacity: 0.4;
  cursor: pointer;
}
.btn-report-flag:hover {
  opacity: 1;
}

.msg-text {
  font-size: 0.9rem;
  color: #f1f5f9;
  line-height: 1.5;
}

.sensitive-blurred-text {
  background: rgba(0, 0, 0, 0.4);
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 0.8rem;
  color: #fbbf24;
  cursor: pointer;
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.78rem;
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
  background: #a855f7;
  animation: blink 1.2s infinite ease-in-out;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes blink {
  0%, 80%, 100% { opacity: 0.2; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1.2); }
}

/* Composer */
.chat-composer {
  padding: 16px 24px;
  background: rgba(14, 16, 26, 0.8);
  border-top: 1px solid var(--border-light);
  display: flex;
  gap: 12px;
}

.composer-input {
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-light);
  padding: 12px 18px;
  border-radius: var(--radius-full);
  color: #fff;
  font-size: 0.9rem;
  outline: none;
}
.composer-input:focus {
  border-color: var(--border-active);
}

.btn-sm {
  padding: 5px 10px;
  font-size: 0.75rem;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 2000;
}

.modal-card {
  width: 100%;
  max-width: 480px;
  background: #121422;
  border: 1px solid rgba(239, 68, 68, 0.4);
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  font-size: 1.15rem;
  color: #f87171;
}

.close-modal-btn {
  color: #94a3b8;
  font-size: 1.2rem;
}

.report-intro {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 10px;
}

.form-group label {
  font-size: 0.8rem;
  color: var(--text-secondary);
  display: block;
  margin-bottom: 6px;
}

.form-input {
  width: 100%;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-light);
  padding: 8px 12px;
  border-radius: var(--radius-md);
  color: #fff;
}
.form-input option {
  background: #121422;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--border-light);
}

@media (max-width: 860px) {
  .chat-card {
    grid-template-columns: 1fr;
    height: auto;
  }
  .chat-sidebar {
    max-height: 250px;
  }
}
</style>
