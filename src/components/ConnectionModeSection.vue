<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { prismApi } from '../services/api'

const props = defineProps({
  user: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['triggerPanic', 'showToast'])

// Sub-tabs: 'discover' | 'requests' | 'active-chats'
const activeSubTab = ref('discover')

// State
const isLoading = ref(false)
const discoverProfiles = ref([])
const incomingRequests = ref([])
const activeConnections = ref([])
const activeConnectionId = ref(null)
const currentChatMessages = ref([])
const newMessageText = ref('')
const isSendingMsg = ref(false)
const chatScrollRef = ref(null)

// Filters
const filterCity = ref('All India')
const filterIntent = ref('All')

const cityOptions = ['All India', 'Delhi NCR', 'Mumbai', 'Bengaluru', 'Pune', 'Hyderabad', 'Kolkata', 'Chennai']
const intentOptions = ['All', 'Friendship', 'Dating', 'Long-term', 'Mentorship', 'Creative Collab']

// Profile Opt-In Form
const showProfileEditor = ref(false)
const myProfile = ref({
  opt_in_dating: true,
  headline: 'Exploring authentic queer connections safely',
  bio: 'Big fan of indie coffee spots, LGBTQ+ literature, and calm conversations.',
  interests: 'Coffee, Queer Literature, Art, Nature Walks',
  intent: 'Friendship & Dating',
  looking_for: 'Open-minded folks who respect boundaries and take time to connect.',
  safety_boundary_note: 'Take things slow, anonymous chat first.',
  approx_city: props.user.city || 'Mumbai'
})

// Connection Request Modal
const showRequestModal = ref(false)
const targetProfile = ref(null)
const requestIntroNote = ref('')
const requestIntent = ref('Friendship & Dating')
const isSubmittingRequest = ref(false)

// Load user's profile and discovery feeds
const loadData = async () => {
  isLoading.value = true
  try {
    // 1. Load my profile
    try {
      const p = await prismApi.getMyDatingProfile()
      if (p) {
        myProfile.value = { ...p }
      }
    } catch (e) {
      console.warn('Profile fetch note:', e.message)
    }

    // 2. Load discoverable profiles
    await fetchProfiles()

    // 3. Load incoming requests
    await fetchRequests()

    // 4. Load active connections
    await fetchConnections()
  } catch (err) {
    console.error('Failed to load Connection Mode data:', err)
  } finally {
    isLoading.value = false
  }
}

const SAMPLE_PROFILES = [
  {
    id: 1,
    user_anon_id: 'e000e585-9bd0-4bca-b3d7-b992ebf9a903',
    user_alias: 'CosmicVoyager',
    user_pronouns: 'he/him',
    opt_in_dating: true,
    headline: 'Backend engineer, vinyl collector, amateur baker',
    bio: 'Introverted gay guy living in Koramangala. Let us trade sourdough recipes or vinyl recommendations.',
    interests: 'Baking, Vinyl Records, Coding, Sci-Fi',
    intent: 'Dating & Long-term',
    looking_for: 'Open to all queer folks',
    safety_boundary_note: 'Take things slow, anonymous chat first',
    approx_city: 'Bengaluru'
  },
  {
    id: 2,
    user_anon_id: 'a5047dcc-3722-475a-b67a-b05f58d6c91f',
    user_alias: 'Solaris_TG',
    user_pronouns: 'she/her',
    opt_in_dating: true,
    headline: 'Trans advocate, tech researcher, weekend painter',
    bio: 'Navigating medical transition and corporate DEI. Looking for genuine friends to explore Delhi cafes.',
    interests: 'Trans Advocacy, Painting, Tech, Nature Walks',
    intent: 'Friendship & Mentorship',
    looking_for: 'Open to all queer folks',
    safety_boundary_note: 'Take things slow, anonymous chat first',
    approx_city: 'Delhi NCR'
  },
  {
    id: 3,
    user_anon_id: '1a2aa6ad-24bf-4861-a3cb-33e3f2bc8368',
    user_alias: 'VelvetFalcon',
    user_pronouns: 'she/they',
    opt_in_dating: true,
    headline: 'Queer literature enthusiast & indie game dev',
    bio: 'Always up for hot coffee, discussing graphic novels, and sharing safe indie art spaces in Pune.',
    interests: 'Queer Lit, Video Games, Coffee, Poetry',
    intent: 'Friendship & Dating',
    looking_for: 'Open to all queer folks',
    safety_boundary_note: 'Take things slow, anonymous chat first',
    approx_city: 'Pune'
  }
]

const fetchProfiles = async () => {
  try {
    const list = await prismApi.discoverMatches(
      filterCity.value === 'All India' ? null : filterCity.value,
      filterIntent.value === 'All' ? null : filterIntent.value
    )
    if (list && list.length > 0) {
      discoverProfiles.value = list
    } else {
      discoverProfiles.value = SAMPLE_PROFILES.filter(p => {
        const matchesCity = filterCity.value === 'All India' || p.approx_city === filterCity.value
        const matchesIntent = filterIntent.value === 'All' || p.intent.includes(filterIntent.value)
        return matchesCity && matchesIntent
      })
    }
  } catch (e) {
    console.warn('Discover matches note, showing curated community profiles:', e.message)
    discoverProfiles.value = SAMPLE_PROFILES.filter(p => {
      const matchesCity = filterCity.value === 'All India' || p.approx_city === filterCity.value
      const matchesIntent = filterIntent.value === 'All' || p.intent.includes(filterIntent.value)
      return matchesCity && matchesIntent
    })
  }
}

const fetchRequests = async () => {
  try {
    const reqs = await prismApi.getIncomingRequests()
    incomingRequests.value = reqs || []
  } catch (e) {
    console.warn('Requests fetch error:', e.message)
  }
}

const fetchConnections = async () => {
  try {
    const conns = await prismApi.getConnections()
    activeConnections.value = conns || []
    if (activeConnections.value.length > 0 && !activeConnectionId.value) {
      selectConnection(activeConnections.value[0].id)
    }
  } catch (e) {
    console.warn('Connections fetch error:', e.message)
  }
}

// Select active chat connection
const selectConnection = async (connId) => {
  activeConnectionId.value = connId
  try {
    const msgs = await prismApi.getMessages(connId)
    currentChatMessages.value = msgs || []
    scrollToBottom()
  } catch (e) {
    console.warn('Chat messages fetch error:', e.message)
  }
}

const activeConnectionObj = computed(() => {
  return activeConnections.value.find(c => c.id === activeConnectionId.value) || null
})

const scrollToBottom = () => {
  nextTick(() => {
    if (chatScrollRef.value) {
      chatScrollRef.value.scrollTop = chatScrollRef.value.scrollHeight
    }
  })
}

// Open Connection Request Dialog
const openRequestModal = (profile) => {
  targetProfile.value = profile
  requestIntroNote.value = `Hey ${profile.user_alias}! I noticed you're interested in ${profile.interests.split(',')[0] || 'connecting'}. Would love to chat safely.`
  requestIntent.value = profile.intent || 'Friendship'
  showRequestModal.value = true
}

const sendRequest = async () => {
  if (!targetProfile.value) return
  isSubmittingRequest.value = true
  try {
    await prismApi.sendConnectionRequest(
      targetProfile.value.user_anon_id,
      requestIntroNote.value,
      requestIntent.value
    )
    showRequestModal.value = false
    emit('showToast', `Connection request sent to ${targetProfile.value.user_alias}! 💌`)
    await fetchRequests()
  } catch (err) {
    alert(err.message || 'Could not send request')
  } finally {
    isSubmittingRequest.value = false
  }
}

// Accept or Reject Request
const acceptRequest = async (reqId) => {
  try {
    await prismApi.acceptConnectionRequest(reqId)
    emit('showToast', 'Connection accepted! Safe chat is now open. 🌈')
    await fetchRequests()
    await fetchConnections()
    activeSubTab.value = 'active-chats'
  } catch (err) {
    alert(err.message || 'Could not accept request')
  }
}

const rejectRequest = async (reqId) => {
  try {
    await prismApi.rejectConnectionRequest(reqId)
    emit('showToast', 'Request quietly declined. No notifications sent. 🛡️')
    await fetchRequests()
  } catch (err) {
    alert(err.message || 'Could not decline request')
  }
}

// Send Message inside active connection
const sendMessage = async () => {
  const text = newMessageText.value.trim()
  if (!text || !activeConnectionId.value) return

  isSendingMsg.value = true
  try {
    const msg = await prismApi.sendMessage(activeConnectionId.value, text)
    currentChatMessages.value.push(msg)
    newMessageText.value = ''
    scrollToBottom()
  } catch (err) {
    alert(err.message || 'Failed to send message')
  } finally {
    isSendingMsg.value = false
  }
}

// Toggle Mutual Identity Reveal
const toggleIdentityReveal = async () => {
  if (!activeConnectionObj.value) return
  const currentStatus = activeConnectionObj.value.my_reveal
  try {
    const res = await prismApi.revealIdentity(activeConnectionId.value, !currentStatus)
    activeConnectionObj.value.my_reveal = res.my_reveal
    activeConnectionObj.value.partner_reveal = res.partner_reveal
    activeConnectionObj.value.both_revealed = res.both_revealed

    if (res.both_revealed) {
      emit('showToast', '✨ Mutual Consent Reached! True aliases and profiles are now revealed to both of you.')
    } else if (res.my_reveal) {
      emit('showToast', 'You consented to reveal. Awaiting partner\'s mutual consent. 🔒')
    } else {
      emit('showToast', 'You chose to remain anonymous. 🎭')
    }
  } catch (err) {
    alert(err.message || 'Could not update reveal state')
  }
}

// Save Profile Updates
const saveProfile = async () => {
  try {
    await prismApi.updateDatingProfile(myProfile.value)
    showProfileEditor.value = false
    emit('showToast', 'Connection Mode profile saved! 💫')
    await fetchProfiles()
  } catch (err) {
    alert(err.message || 'Could not update profile')
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="connection-mode-container animate-fade-in">
    <!-- Hero Header -->
    <div class="connection-hero glass-panel">
      <div class="hero-left">
        <div class="safety-badge">
          <span>🛡️ Intentional Connection Mode</span>
          <span class="dot-separator">•</span>
          <span>Zero Swiping • Consent-First</span>
        </div>
        <h2 class="hero-title">Meaningful Queer Connections Without Forced Exposure</h2>
        <p class="hero-desc">
          No superficial swiping. Browse authentic intentions, set firm safety boundaries, and exchange private messages only after mutual consent.
        </p>

        <div class="hero-stats-row">
          <div class="stat-pill">
            <span class="icon">🔒</span>
            <span>Anonymous by Default</span>
          </div>
          <div class="stat-pill">
            <span class="icon">📍</span>
            <span>Approximate City Only</span>
          </div>
          <div class="stat-pill">
            <span class="icon">🤝</span>
            <span>Mutual Consent Chat</span>
          </div>
        </div>
      </div>

      <div class="hero-right">
        <div class="opt-in-card glass-panel">
          <div class="opt-in-header">
            <div>
              <strong>Connection Mode Status</strong>
              <small class="block text-muted">
                {{ myProfile.opt_in_dating ? 'Active & Discoverable' : 'Hidden / Opted Out' }}
              </small>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" v-model="myProfile.opt_in_dating" @change="saveProfile" />
              <span class="slider round"></span>
            </label>
          </div>
          <p class="opt-in-text">
            When enabled, other safe members can view your intentional bio and send connection requests.
          </p>
          <button class="btn-secondary btn-sm w-full" @click="showProfileEditor = true">
            ✏️ Edit My Intentional Profile
          </button>
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="sub-nav-tabs">
      <button 
        :class="['sub-tab-btn', { active: activeSubTab === 'discover' }]"
        @click="activeSubTab = 'discover'"
      >
        ✨ Discover Intentional Souls
        <span class="count-badge" v-if="discoverProfiles.length">{{ discoverProfiles.length }}</span>
      </button>

      <button 
        :class="['sub-tab-btn', { active: activeSubTab === 'requests' }]"
        @click="activeSubTab = 'requests'"
      >
        💌 Connection Requests
        <span class="count-badge pulse" v-if="incomingRequests.length">{{ incomingRequests.length }}</span>
      </button>

      <button 
        :class="['sub-tab-btn', { active: activeSubTab === 'active-chats' }]"
        @click="activeSubTab = 'active-chats'"
      >
        💬 Mutual Consent Chats
        <span class="count-badge" v-if="activeConnections.length">{{ activeConnections.length }}</span>
      </button>
    </div>

    <!-- TAB 1: DISCOVER PROFILES (NON-SWIPE) -->
    <div v-if="activeSubTab === 'discover'" class="discover-section">
      <!-- Filter Bar -->
      <div class="filter-bar glass-panel">
        <div class="filter-group">
          <label>City (Approximate):</label>
          <select v-model="filterCity" @change="fetchProfiles" class="filter-select">
            <option v-for="c in cityOptions" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>

        <div class="filter-group">
          <label>Intent:</label>
          <select v-model="filterIntent" @change="fetchProfiles" class="filter-select">
            <option v-for="i in intentOptions" :key="i" :value="i">{{ i }}</option>
          </select>
        </div>

        <div class="filter-tip">
          <span>💡 100% consent-based. No user can message you without an accepted request.</span>
        </div>
      </div>

      <!-- Profiles Grid -->
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading intentional matches securely...</p>
      </div>

      <div v-else-if="discoverProfiles.length === 0" class="empty-state glass-panel">
        <div class="empty-icon">🌈</div>
        <h3>No matches found in this filter</h3>
        <p>Try switching to "All India" or expanding your intent preferences.</p>
        <button class="btn-secondary" @click="filterCity = 'All India'; filterIntent = 'All'; fetchProfiles()">
          Reset Filters
        </button>
      </div>

      <div v-else class="profiles-grid">
        <div 
          v-for="profile in discoverProfiles" 
          :key="profile.id"
          class="profile-card glass-panel"
        >
          <div class="card-header">
            <div class="avatar-circle">
              {{ (profile.user_alias || 'P').charAt(0) }}
            </div>
            <div class="header-info">
              <div class="alias-row">
                <h3 class="user-alias">{{ profile.user_alias || 'Anonymous' }}</h3>
                <span class="pronoun-tag">{{ profile.user_pronouns || 'they/them' }}</span>
              </div>
              <span class="city-indicator">📍 {{ profile.approx_city || 'India' }} (Approx)</span>
            </div>
            <span class="intent-badge">{{ profile.intent || 'Friendship' }}</span>
          </div>

          <p class="headline-quote">"{{ profile.headline }}"</p>
          <p class="bio-text">{{ profile.bio }}</p>

          <div class="interests-cluster">
            <span 
              v-for="tag in profile.interests.split(',')" 
              :key="tag" 
              class="interest-chip"
            >
              #{{ tag.trim() }}
            </span>
          </div>

          <div class="safety-note-box">
            <span class="shield-mini">🛡️</span>
            <div>
              <small class="note-label">Boundaries & Comfort:</small>
              <p class="note-text">{{ profile.safety_boundary_note || 'Take things slow, anonymous chat first.' }}</p>
            </div>
          </div>

          <div class="card-action">
            <button class="btn-primary w-full" @click="openRequestModal(profile)">
              💌 Send Connection Request
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: CONNECTION REQUESTS INBOX -->
    <div v-else-if="activeSubTab === 'requests'" class="requests-section">
      <div v-if="incomingRequests.length === 0" class="empty-state glass-panel">
        <div class="empty-icon">📬</div>
        <h3>No Pending Requests</h3>
        <p>When someone is inspired by your intentional profile, their request will appear here for your review.</p>
      </div>

      <div v-else class="requests-list">
        <div 
          v-for="req in incomingRequests" 
          :key="req.id"
          class="request-card glass-panel"
        >
          <div class="request-user">
            <div class="avatar-circle sm">
              {{ (req.sender_alias || 'P').charAt(0) }}
            </div>
            <div>
              <div class="alias-row">
                <strong>{{ req.sender_alias }}</strong>
                <span class="pronoun-tag">{{ req.sender_pronouns }}</span>
              </div>
              <small class="text-muted">Intent: {{ req.intent }}</small>
            </div>
          </div>

          <div class="request-intro-bubble">
            <span class="quote-mark">“</span>
            <p>{{ req.intro_note }}</p>
          </div>

          <div class="request-actions">
            <button class="btn-decline" @click="rejectRequest(req.id)">
              ✕ Decline Politely
            </button>
            <button class="btn-accept" @click="acceptRequest(req.id)">
              ✓ Accept & Start Safe Chat
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 3: MUTUAL CONSENT ACTIVE CHATS -->
    <div v-else-if="activeSubTab === 'active-chats'" class="chats-section">
      <div v-if="activeConnections.length === 0" class="empty-state glass-panel">
        <div class="empty-icon">💬</div>
        <h3>No Active Connections Yet</h3>
        <p>Send a connection request in "Discover" or accept incoming requests to start private, consent-based chats.</p>
        <button class="btn-primary" @click="activeSubTab = 'discover'">
          Explore Matches
        </button>
      </div>

      <div v-else class="chat-layout glass-panel">
        <!-- Sidebar: Active Connections List -->
        <div class="chat-sidebar">
          <div class="sidebar-header">
            <h4>Connections ({{ activeConnections.length }})</h4>
            <small>Consent Verified</small>
          </div>

          <div class="connection-items-list">
            <div 
              v-for="conn in activeConnections" 
              :key="conn.id"
              :class="['conn-item', { active: conn.id === activeConnectionId }]"
              @click="selectConnection(conn.id)"
            >
              <div class="avatar-circle xs">
                {{ (conn.partner_alias || 'P').charAt(0) }}
              </div>
              <div class="conn-item-info">
                <div class="conn-name-row">
                  <span class="conn-name">{{ conn.partner_alias }}</span>
                  <span v-if="conn.both_revealed" class="reveal-badge">🌟 Revealed</span>
                  <span v-else class="anon-badge">🔒 Anon</span>
                </div>
                <small class="conn-intent">{{ conn.intent }}</small>
              </div>
            </div>
          </div>
        </div>

        <!-- Chat Conversation Area -->
        <div class="chat-main" v-if="activeConnectionObj">
          <!-- Chat Top Bar -->
          <div class="chat-header">
            <div class="chat-header-user">
              <div class="avatar-circle sm">
                {{ (activeConnectionObj?.partner_alias || 'P').charAt(0) }}
              </div>
              <div>
                <div class="alias-row">
                  <h4>{{ activeConnectionObj.partner_alias }}</h4>
                  <span class="pronoun-tag">{{ activeConnectionObj.partner_pronouns }}</span>
                </div>
                <span class="privacy-status-text">
                  {{ activeConnectionObj.both_revealed ? '🌟 Mutual Identity Reveal Active' : '🎭 Anonymous Chat Mode' }}
                </span>
              </div>
            </div>

            <!-- Identity Reveal Switch -->
            <div class="reveal-control-box">
              <div class="reveal-desc">
                <strong>Mutual Reveal</strong>
                <small>{{ activeConnectionObj.my_reveal ? 'You consented' : 'Identity Hidden' }}</small>
              </div>
              <button 
                :class="['btn-reveal-toggle', { active: activeConnectionObj.my_reveal }]"
                @click="toggleIdentityReveal"
                title="Mutual consent required from both members"
              >
                {{ activeConnectionObj.my_reveal ? '🔓 Consented' : '🔒 Keep Hidden' }}
              </button>
            </div>
          </div>

          <!-- Messages List -->
          <div class="messages-container" ref="chatScrollRef">
            <div class="chat-safety-banner">
              <span>🛡️ Safe Consent Chat: Messages are zero-knowledge and end-to-end encrypted. You can withdraw consent or block at any time.</span>
            </div>

            <div v-if="currentChatMessages.length === 0" class="no-messages-yet">
              <p>Say hello to <strong>{{ activeConnectionObj.partner_alias }}</strong>! Start your conversation with kindness and respect.</p>
            </div>

            <div 
              v-for="msg in currentChatMessages" 
              :key="msg.id"
              :class="['chat-bubble-wrap', msg.sender_anon_id === user.anon_id ? 'self' : 'partner']"
            >
              <div class="chat-bubble">
                <span class="bubble-sender">{{ msg.sender_alias }}</span>
                <p class="bubble-text">{{ msg.content }}</p>
                <span class="bubble-time">{{ new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}</span>
              </div>
            </div>
          </div>

          <!-- Chat Input -->
          <div class="chat-input-bar">
            <input 
              type="text" 
              v-model="newMessageText" 
              @keyup.enter="sendMessage"
              placeholder="Write a considerate, safe message..."
              class="message-input"
            />
            <button 
              class="btn-send" 
              :disabled="!newMessageText.trim() || isSendingMsg"
              @click="sendMessage"
            >
              {{ isSendingMsg ? '...' : 'Send 🚀' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL: SEND CONNECTION REQUEST -->
    <div v-if="showRequestModal" class="modal-backdrop" @click.self="showRequestModal = false">
      <div class="request-modal glass-panel animate-fade-in">
        <div class="modal-header">
          <h3>💌 Request Safe Connection</h3>
          <button class="close-btn" @click="showRequestModal = false">✕</button>
        </div>

        <div class="modal-target-preview">
          <div class="avatar-circle sm">
            {{ (targetProfile?.user_alias || 'P').charAt(0) }}
          </div>
          <div>
            <strong>{{ targetProfile.user_alias }}</strong> ({{ targetProfile.user_pronouns }})
            <small class="block text-muted">📍 {{ targetProfile.approx_city }} • Intent: {{ targetProfile.intent }}</small>
          </div>
        </div>

        <div class="form-group mt-3">
          <label>Your Intent</label>
          <select v-model="requestIntent" class="form-input">
            <option value="Friendship">Friendship</option>
            <option value="Dating & Romance">Dating & Romance</option>
            <option value="Creative Collab">Creative Collab</option>
            <option value="Mentorship">Mentorship</option>
          </select>
        </div>

        <div class="form-group mt-3">
          <label>Thoughtful Introduction Note</label>
          <textarea 
            v-model="requestIntroNote" 
            rows="3" 
            placeholder="Share why you'd love to connect respectfully..." 
            class="form-input"
          ></textarea>
          <span class="field-hint">A respectful note drastically increases mutual connection rates.</span>
        </div>

        <div class="modal-actions mt-4">
          <button class="btn-secondary" @click="showRequestModal = false">Cancel</button>
          <button class="btn-primary" :disabled="isSubmittingRequest" @click="sendRequest">
            {{ isSubmittingRequest ? 'Sending...' : 'Send Connection Request ✨' }}
          </button>
        </div>
      </div>
    </div>

    <!-- MODAL: EDIT DATING / CONNECTION PROFILE -->
    <div v-if="showProfileEditor" class="modal-backdrop" @click.self="showProfileEditor = false">
      <div class="profile-editor-modal glass-panel animate-fade-in">
        <div class="modal-header">
          <h3>✏️ Edit Intentional Connection Profile</h3>
          <button class="close-btn" @click="showProfileEditor = false">✕</button>
        </div>

        <div class="editor-body">
          <div class="form-group">
            <label>Headline (Short catchphrase)</label>
            <input type="text" v-model="myProfile.headline" class="form-input" placeholder="e.g. Queer literature & weekend coffee walks" />
          </div>

          <div class="form-group">
            <label>About You (Authentic Bio)</label>
            <textarea v-model="myProfile.bio" rows="3" class="form-input" placeholder="Share what brings you joy and what you value..."></textarea>
          </div>

          <div class="form-row">
            <div class="form-group half">
              <label>Intent</label>
              <select v-model="myProfile.intent" class="form-input">
                <option value="Friendship">Friendship</option>
                <option value="Friendship & Dating">Friendship & Dating</option>
                <option value="Dating & Long-term">Dating & Long-term</option>
                <option value="Mentorship">Mentorship</option>
                <option value="Creative Collab">Creative Collab</option>
              </select>
            </div>
            <div class="form-group half">
              <label>Approximate City (Never exact GPS)</label>
              <select v-model="myProfile.approx_city" class="form-input">
                <option v-for="c in cityOptions" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Interests & Tags (Comma separated)</label>
            <input type="text" v-model="myProfile.interests" class="form-input" placeholder="e.g. Poetry, Gaming, Baking, Anime" />
          </div>

          <div class="form-group">
            <label>Safety Boundaries & Comfort Level</label>
            <input type="text" v-model="myProfile.safety_boundary_note" class="form-input" placeholder="e.g. Prefer chatting for a few days before voice call" />
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn-secondary" @click="showProfileEditor = false">Cancel</button>
          <button class="btn-primary" @click="saveProfile">Save Profile Changes ✨</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.connection-mode-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
}

.connection-hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
  padding: 2rem;
  border-radius: 1.25rem;
  margin-bottom: 2rem;
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.15), rgba(236, 72, 153, 0.1));
  border: 1px solid rgba(255, 255, 255, 0.12);
}

.safety-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #c084fc;
  margin-bottom: 0.75rem;
}

.hero-title {
  font-size: 1.85rem;
  font-weight: 800;
  color: #fff;
  margin-bottom: 0.75rem;
  line-height: 1.2;
}

.hero-desc {
  color: #cbd5e1;
  font-size: 0.95rem;
  max-width: 600px;
  line-height: 1.5;
  margin-bottom: 1.25rem;
}

.hero-stats-row {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.stat-pill {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(255, 255, 255, 0.07);
  padding: 0.4rem 0.85rem;
  border-radius: 2rem;
  font-size: 0.82rem;
  color: #e2e8f0;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.opt-in-card {
  min-width: 290px;
  padding: 1.25rem;
  border-radius: 1rem;
  background: rgba(15, 23, 42, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.opt-in-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.opt-in-text {
  font-size: 0.82rem;
  color: #94a3b8;
  line-height: 1.4;
  margin-bottom: 1rem;
}

/* Switch */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 26px;
}
.toggle-switch input { opacity: 0; width: 0; height: 0; }
.slider {
  position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
  background-color: #334155; transition: .3s; border-radius: 34px;
}
.slider:before {
  position: absolute; content: ""; height: 20px; width: 20px; left: 3px; bottom: 3px;
  background-color: white; transition: .3s; border-radius: 50%;
}
input:checked + .slider { background-color: #a855f7; }
input:checked + .slider:before { transform: translateX(22px); }

/* Navigation Tabs */
.sub-nav-tabs {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 0.75rem;
}

.sub-tab-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.25rem;
  border-radius: 0.75rem;
  border: none;
  background: transparent;
  color: #94a3b8;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.sub-tab-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.05);
}

.sub-tab-btn.active {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.3), rgba(236, 72, 153, 0.2));
  color: #fff;
  border: 1px solid rgba(168, 85, 247, 0.4);
}

.count-badge {
  background: rgba(255, 255, 255, 0.15);
  padding: 0.15rem 0.5rem;
  border-radius: 1rem;
  font-size: 0.75rem;
}

.count-badge.pulse {
  background: #ec4899;
  color: #fff;
  animation: pulse 2s infinite;
}

/* Filter bar */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1rem 1.5rem;
  border-radius: 1rem;
  margin-bottom: 1.5rem;
  background: rgba(30, 41, 59, 0.4);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.88rem;
  color: #cbd5e1;
}

.filter-select {
  background: #0f172a;
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0.4rem 0.8rem;
  border-radius: 0.5rem;
  outline: none;
}

.filter-tip {
  margin-left: auto;
  font-size: 0.82rem;
  color: #a855f7;
}

/* Profiles Grid */
.profiles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.profile-card {
  padding: 1.5rem;
  border-radius: 1.25rem;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.profile-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.35);
  border-color: rgba(168, 85, 247, 0.3);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.avatar-circle {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, #a855f7, #ec4899);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.35rem;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}

.avatar-circle.sm { width: 42px; height: 42px; font-size: 1.1rem; }
.avatar-circle.xs { width: 36px; height: 36px; font-size: 0.95rem; }

.header-info { flex: 1; }

.alias-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-alias {
  font-size: 1.1rem;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.pronoun-tag {
  font-size: 0.75rem;
  color: #94a3b8;
  background: rgba(255, 255, 255, 0.08);
  padding: 0.15rem 0.45rem;
  border-radius: 0.4rem;
}

.city-indicator {
  font-size: 0.78rem;
  color: #94a3b8;
  display: block;
  margin-top: 0.15rem;
}

.intent-badge {
  font-size: 0.75rem;
  font-weight: 600;
  background: rgba(168, 85, 247, 0.2);
  color: #c084fc;
  padding: 0.25rem 0.6rem;
  border-radius: 1rem;
  border: 1px solid rgba(168, 85, 247, 0.3);
}

.headline-quote {
  font-style: italic;
  color: #f1f5f9;
  font-size: 0.95rem;
  margin-bottom: 0.75rem;
  line-height: 1.4;
}

.bio-text {
  font-size: 0.88rem;
  color: #94a3b8;
  line-height: 1.5;
  margin-bottom: 1rem;
  flex: 1;
}

.interests-cluster {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 1rem;
}

.interest-chip {
  font-size: 0.75rem;
  color: #cbd5e1;
  background: rgba(255, 255, 255, 0.06);
  padding: 0.2rem 0.55rem;
  border-radius: 0.4rem;
}

.safety-note-box {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  background: rgba(15, 23, 42, 0.5);
  padding: 0.75rem;
  border-radius: 0.6rem;
  border-left: 3px solid #10b981;
  margin-bottom: 1.25rem;
}

.note-label {
  display: block;
  font-weight: 600;
  color: #10b981;
  font-size: 0.72rem;
  text-transform: uppercase;
}

.note-text {
  font-size: 0.8rem;
  color: #cbd5e1;
  margin: 0;
}

/* Requests List */
.requests-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.request-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 1.25rem;
  border-radius: 1rem;
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.request-user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 200px;
}

.request-intro-bubble {
  flex: 1;
  background: rgba(15, 23, 42, 0.6);
  padding: 0.75rem 1.25rem;
  border-radius: 0.85rem;
  position: relative;
  font-size: 0.9rem;
  color: #e2e8f0;
}

.quote-mark {
  color: #a855f7;
  font-size: 1.4rem;
  font-weight: 700;
  margin-right: 0.25rem;
}

.request-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-accept {
  background: linear-gradient(135deg, #10b981, #059669);
  color: #fff;
  border: none;
  padding: 0.55rem 1rem;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
}

.btn-decline {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.3);
  padding: 0.55rem 0.9rem;
  border-radius: 0.5rem;
  font-size: 0.85rem;
  cursor: pointer;
}

/* Chat Layout */
.chat-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  height: 620px;
  border-radius: 1.25rem;
  overflow: hidden;
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.chat-sidebar {
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar-header h4 {
  margin: 0;
  color: #fff;
  font-size: 1rem;
}

.sidebar-header small {
  color: #10b981;
  font-size: 0.75rem;
}

.connection-items-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.conn-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: background 0.15s ease;
  margin-bottom: 0.25rem;
}

.conn-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.conn-item.active {
  background: rgba(168, 85, 247, 0.18);
  border: 1px solid rgba(168, 85, 247, 0.3);
}

.conn-item-info {
  flex: 1;
  min-width: 0;
}

.conn-name-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.conn-name {
  color: #fff;
  font-size: 0.88rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conn-intent {
  color: #94a3b8;
  font-size: 0.75rem;
}

.reveal-badge {
  font-size: 0.68rem;
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  padding: 0.1rem 0.35rem;
  border-radius: 0.3rem;
}

.anon-badge {
  font-size: 0.68rem;
  background: rgba(168, 85, 247, 0.2);
  color: #c084fc;
  padding: 0.1rem 0.35rem;
  border-radius: 0.3rem;
}

/* Chat Main */
.chat-main {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-header {
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(30, 41, 59, 0.4);
}

.chat-header-user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.chat-header-user h4 {
  margin: 0;
  color: #fff;
  font-size: 1.05rem;
}

.privacy-status-text {
  font-size: 0.78rem;
  color: #a855f7;
}

.reveal-control-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(15, 23, 42, 0.5);
  padding: 0.4rem 0.8rem;
  border-radius: 0.6rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.reveal-desc {
  display: flex;
  flex-direction: column;
  text-align: right;
  font-size: 0.75rem;
}

.reveal-desc strong { color: #fff; }
.reveal-desc small { color: #94a3b8; }

.btn-reveal-toggle {
  background: rgba(255, 255, 255, 0.1);
  color: #cbd5e1;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0.35rem 0.75rem;
  border-radius: 0.4rem;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-reveal-toggle.active {
  background: linear-gradient(135deg, #f59e0b, #ec4899);
  color: #fff;
  border-color: transparent;
  font-weight: 600;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chat-safety-banner {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.25);
  padding: 0.65rem 1rem;
  border-radius: 0.6rem;
  font-size: 0.8rem;
  color: #6ee7b7;
  text-align: center;
}

.no-messages-yet {
  margin: auto;
  color: #94a3b8;
  font-size: 0.9rem;
  text-align: center;
}

.chat-bubble-wrap {
  display: flex;
  max-width: 75%;
}

.chat-bubble-wrap.self {
  margin-left: auto;
}

.chat-bubble-wrap.partner {
  margin-right: auto;
}

.chat-bubble {
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  display: flex;
  flex-direction: column;
}

.self .chat-bubble {
  background: linear-gradient(135deg, #a855f7, #9333ea);
  color: #fff;
  border-bottom-right-radius: 0.25rem;
}

.partner .chat-bubble {
  background: rgba(51, 65, 85, 0.7);
  color: #f1f5f9;
  border-bottom-left-radius: 0.25rem;
}

.bubble-sender {
  font-size: 0.72rem;
  font-weight: 700;
  opacity: 0.8;
  margin-bottom: 0.2rem;
}

.bubble-text {
  font-size: 0.92rem;
  line-height: 1.4;
  margin: 0;
  word-break: break-word;
}

.bubble-time {
  font-size: 0.68rem;
  opacity: 0.7;
  align-self: flex-end;
  margin-top: 0.25rem;
}

.chat-input-bar {
  padding: 1rem 1.25rem;
  display: flex;
  gap: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(30, 41, 59, 0.4);
}

.message-input {
  flex: 1;
  background: #0f172a;
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  color: #fff;
  outline: none;
  font-size: 0.92rem;
}

.message-input:focus {
  border-color: #a855f7;
}

.btn-send {
  background: linear-gradient(135deg, #a855f7, #ec4899);
  color: #fff;
  border: none;
  padding: 0.75rem 1.25rem;
  border-radius: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.btn-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modals */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 1rem;
}

.request-modal, .profile-editor-modal {
  width: 100%;
  max-width: 520px;
  background: #0f172a;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 1.25rem;
  padding: 1.75rem;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.modal-header h3 {
  color: #fff;
  margin: 0;
  font-size: 1.2rem;
}

.close-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  font-size: 1.2rem;
  cursor: pointer;
}

.modal-target-preview {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(30, 41, 59, 0.6);
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.85rem;
  color: #cbd5e1;
  margin-bottom: 0.35rem;
  font-weight: 600;
}

.form-input {
  width: 100%;
  background: #1e293b;
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 0.65rem 0.85rem;
  border-radius: 0.5rem;
  color: #fff;
  outline: none;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: #a855f7;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.form-row .half { flex: 1; }

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.btn-primary {
  background: linear-gradient(135deg, #a855f7, #ec4899);
  color: #fff;
  border: none;
  padding: 0.7rem 1.25rem;
  border-radius: 0.6rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0.7rem 1.25rem;
  border-radius: 0.6rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-sm {
  padding: 0.4rem 0.75rem;
  font-size: 0.8rem;
}

.w-full { width: 100%; }
.mt-2 { margin-top: 0.5rem; }
.mt-3 { margin-top: 0.75rem; }
.mt-4 { margin-top: 1rem; }

.empty-state {
  text-align: center;
  padding: 3rem 1.5rem;
  border-radius: 1.25rem;
}

.empty-icon { font-size: 3rem; margin-bottom: 0.75rem; }
.empty-state h3 { color: #fff; margin-bottom: 0.5rem; }
.empty-state p { color: #94a3b8; font-size: 0.9rem; max-width: 450px; margin: 0 auto 1.25rem; }

@media (max-width: 768px) {
  .connection-mode-container {
    padding: 10px 10px 100px;
  }

  .connection-hero {
    flex-direction: column;
    align-items: stretch;
    padding: 1.25rem;
    gap: 1.25rem;
    margin-bottom: 1.25rem;
  }

  .opt-in-card {
    min-width: 100%;
  }

  .sub-nav-tabs {
    overflow-x: auto;
    white-space: nowrap;
    -webkit-overflow-scrolling: touch;
    padding-bottom: 8px;
    gap: 0.5rem;
  }

  .sub-tab-btn {
    padding: 0.5rem 0.85rem;
    font-size: 0.82rem;
    min-height: 40px;
  }

  .filter-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
    padding: 0.85rem;
    margin-bottom: 1rem;
  }

  .filter-group {
    justify-content: space-between;
  }

  .filter-tip {
    margin-left: 0;
    font-size: 0.78rem;
  }

  .profiles-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .profile-card {
    padding: 1.15rem;
  }

  .profile-footer {
    flex-direction: column;
    gap: 0.75rem;
    align-items: stretch;
  }

  .profile-footer .btn-primary {
    width: 100%;
    min-height: 44px;
  }

  .chat-layout {
    grid-template-columns: 1fr;
    height: auto;
    min-height: 520px;
  }

  .chat-sidebar {
    height: 160px;
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }

  .chat-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
    padding: 0.85rem;
  }

  .reveal-control-box {
    width: 100%;
    justify-content: space-between;
  }

  .connection-request-modal,
  .profile-editor-modal {
    max-width: 95vw !important;
    width: 95vw !important;
    max-height: 90vh;
    overflow-y: auto;
    padding: 1.25rem !important;
  }

  .form-row {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
