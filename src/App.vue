<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import confetti from 'canvas-confetti'

import Navbar from './components/Navbar.vue'
import FeedSection from './components/FeedSection.vue'
import SafeSpacesMap from './components/SafeSpacesMap.vue'
import SafeChatSection from './components/SafeChatSection.vue'
import MentalHealthSection from './components/MentalHealthSection.vue'
import SafeModeAI from './components/SafeModeAI.vue'
import LegalHubSection from './components/LegalHubSection.vue'
import PanicCalculator from './components/PanicCalculator.vue'
import IdentityModal from './components/IdentityModal.vue'
import AuthModal from './components/AuthModal.vue'
import ConnectionModeSection from './components/ConnectionModeSection.vue'

import {
  INITIAL_USER,
  CITIES,
  FEED_CATEGORIES,
  INITIAL_POSTS,
  SAFE_SPACES,
  CRISIS_HELPLINES,
  THERAPISTS,
  CHAT_ROOMS,
  LEGAL_RESOURCES
} from './data/mockData'

// State
const activeTab = ref('feed')
const user = ref({ ...INITIAL_USER })
const isLoggedIn = ref(true)
const selectedCity = ref('All India')
const posts = ref([...INITIAL_POSTS])
const spaces = ref([...SAFE_SPACES])
const helplines = ref([...CRISIS_HELPLINES])
const therapists = ref([...THERAPISTS])
const rooms = ref([...CHAT_ROOMS])
const legalResources = ref([...LEGAL_RESOURCES])
const categories = ref([...FEED_CATEGORIES])

const isPanicMode = ref(false)
const showIdentityModal = ref(false)
const showAuthModal = ref(false)
const showMoreSheet = ref(false)
const globalToast = ref('')

// Helper to guarantee standard fields across backend API models & client state
const normalizeUser = (raw) => {
  if (!raw) return { ...INITIAL_USER }
  const uname = raw.username || raw.alias || 'Anonymous'
  return {
    ...INITIAL_USER,
    ...raw,
    username: uname,
    alias: raw.alias || uname,
    pronouns: raw.pronouns || 'they/them',
    avatarBg: raw.avatarBg || 'linear-gradient(135deg, #a855f7, #ec4899)',
    identityTags: raw.identityTags || (raw.identity_tags ? raw.identity_tags.split(',').map(s => s.trim()) : ['Queer'])
  }
}

// Check if user has saved credentials in localStorage
const initSavedAuth = () => {
  const savedUser = localStorage.getItem('prism_auth_user')
  if (savedUser) {
    try {
      const parsed = JSON.parse(savedUser)
      user.value = normalizeUser(parsed)
      isLoggedIn.value = true
    } catch (e) {
      console.error(e)
    }
  }
}

const showToast = (msg) => {
  globalToast.value = msg
  setTimeout(() => {
    globalToast.value = ''
  }, 3500)
}

const handleSignupSuccess = (newUser) => {
  user.value = normalizeUser(newUser)
  isLoggedIn.value = true
  triggerPrideConfetti()
  showToast(`Welcome to Prism, ${user.value.username}! Your anonymous identity is secured. 🌈`)
}

const handleLoginSuccess = (restoredUser) => {
  user.value = normalizeUser(restoredUser)
  isLoggedIn.value = true
  showToast(`Welcome back, ${user.value.username}! Session restored. 🔑`)
}

const handlePurgeSession = () => {
  localStorage.removeItem('prism_auth_user')
  localStorage.removeItem('prism_map_provider')
  localStorage.removeItem('prism_gmaps_api_key')
  user.value = {
    id: 'usr_guest_' + Date.now(),
    username: 'GuestVoyager',
    pronouns: 'they/them',
    avatarBg: 'linear-gradient(135deg, #a855f7, #ec4899)',
    identityTags: ['Guest'],
    closetPin: '1234',
    autoBlurContent: true,
    karmaScore: 0
  }
  isLoggedIn.value = false
  showToast('All local browsing traces, keys, and session cache purged. 🧹')
}

// Panic mode trigger
const triggerPanic = () => {
  isPanicMode.value = true
}

const exitPanic = () => {
  isPanicMode.value = false
}

// URL Hash sync so direct links like #spaces work
const syncTabFromUrl = () => {
  const hash = window.location.hash.replace('#', '')
  if (['feed', 'connections', 'spaces', 'chat', 'mental-health', 'ai-assistant', 'legal'].includes(hash)) {
    activeTab.value = hash
  }
}

// Global Hotkeys (Escape or Ctrl+Shift+P for instant panic disguise)
const handleKeydown = (e) => {
  if (e.key === 'Escape' || (e.ctrlKey && e.shiftKey && e.key === 'P')) {
    if (!isPanicMode.value) {
      triggerPanic()
    }
  }
}

const setActiveTab = (tabId) => {
  activeTab.value = tabId
  window.location.hash = tabId
}

onMounted(() => {
  initSavedAuth()
  syncTabFromUrl()
  window.addEventListener('hashchange', syncTabFromUrl)
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('hashchange', syncTabFromUrl)
  window.removeEventListener('keydown', handleKeydown)
})

// Feed Handlers
const handleAddPost = (newPost) => {
  posts.value.unshift(newPost)
  triggerPrideConfetti()
}

const handleVotePost = ({ postId, direction }) => {
  const post = posts.value.find(p => p.id === postId)
  if (post) {
    if (post.userVote === direction) {
      if (direction === 1) post.upvotes--
      if (direction === -1) post.downvotes--
      post.userVote = 0
    } else {
      if (post.userVote === 1) post.upvotes--
      if (post.userVote === -1) post.downvotes--

      if (direction === 1) post.upvotes++
      if (direction === -1) post.downvotes++
      post.userVote = direction
    }
  }
}

const handleToggleSavePost = (postId) => {
  const post = posts.value.find(p => p.id === postId)
  if (post) {
    post.saved = !post.saved
  }
}

const handleAddComment = ({ postId, comment }) => {
  const post = posts.value.find(p => p.id === postId)
  if (post) {
    if (!post.comments) post.comments = []
    post.comments.push(comment)
  }
}

// Spaces Handlers
const handleAddSpace = (newSpace) => {
  spaces.value.unshift(newSpace)
}

const handleAddReview = ({ spaceId, review }) => {
  const space = spaces.value.find(s => s.id === spaceId)
  if (space) {
    if (!space.reviews) space.reviews = []
    space.reviews.unshift(review)
    space.reviewsCount++
  }
}

// User Update Handler
const handleUpdateUser = (updatedData) => {
  user.value = { ...user.value, ...updatedData }
  localStorage.setItem('prism_auth_user', JSON.stringify(user.value))
}

const triggerPrideConfetti = () => {
  confetti({
    particleCount: 35,
    spread: 55,
    origin: { y: 0.8 },
    colors: ['#f43f5e', '#fb923c', '#fbbf24', '#10b981', '#06b6d4', '#8b5cf6']
  })
}

const triggerNewPostModalTimestamp = ref(0)

const selectTabFromMobile = (tabId) => {
  activeTab.value = tabId
  showMoreSheet.value = false
}

const handleMobileCompose = () => {
  activeTab.value = 'feed'
  showMoreSheet.value = false
  triggerNewPostModalTimestamp.value = Date.now()
}
</script>

<template>
  <div class="app-root">
    <!-- Panic Disguise Screen (Swaps entire UI to working Notes / Calculator) -->
    <PanicCalculator 
      v-if="isPanicMode" 
      @exitPanic="exitPanic" 
    />

    <!-- Main Prism Community Platform -->
    <div v-else class="prism-app-wrapper">
      <!-- Clean Top Navbar -->
      <Navbar 
        :activeTab="activeTab"
        :user="user"
        :isLoggedIn="isLoggedIn"
        :selectedCity="selectedCity"
        :cities="CITIES"
        @update:activeTab="setActiveTab($event)"
        @update:selectedCity="selectedCity = $event"
        @openIdentityModal="showIdentityModal = true"
        @openAuthModal="showAuthModal = true"
      />

      <!-- Content Views -->
      <main class="main-content-area">
        <!-- Feed View -->
        <FeedSection 
          v-if="activeTab === 'feed'"
          :posts="posts"
          :user="user"
          :selectedCity="selectedCity"
          :categories="categories"
          :triggerNewPostModal="triggerNewPostModalTimestamp"
          @addPost="handleAddPost"
          @votePost="handleVotePost"
          @toggleSavePost="handleToggleSavePost"
          @addComment="handleAddComment"
          @switchTab="setActiveTab($event)"
        />

        <!-- Intentional Connection Mode & Consent Connections -->
        <ConnectionModeSection 
          v-else-if="activeTab === 'connections'"
          :user="user"
          @triggerPanic="triggerPanic"
          @showToast="showToast"
        />

        <!-- Safe Spaces Map View -->
        <SafeSpacesMap 
          v-else-if="activeTab === 'spaces'"
          :spaces="spaces"
          :selectedCity="selectedCity"
          @update:selectedCity="selectedCity = $event"
          @addSpace="handleAddSpace"
          @addReview="handleAddReview"
        />

        <!-- Safe Chat View -->
        <SafeChatSection 
          v-else-if="activeTab === 'chat'"
          :rooms="rooms"
          :user="user"
          @triggerPanic="triggerPanic"
        />

        <!-- Mental Health & Crisis View -->
        <MentalHealthSection 
          v-else-if="activeTab === 'mental-health'"
          :helplines="helplines"
          :therapists="therapists"
        />

        <!-- SafeMode AI Assistant View -->
        <SafeModeAI 
          v-else-if="activeTab === 'ai-assistant'"
          :user="user"
          :selectedCity="selectedCity"
        />

        <!-- Legal & Education View -->
        <LegalHubSection 
          v-else-if="activeTab === 'legal'"
          :resources="legalResources"
        />
      </main>

      <!-- 🚨 Floating Panic Button (Accessible Everywhere, Not in Navbar) -->
      <button 
        class="floating-panic-btn" 
        @click="triggerPanic"
        title="Quick Exit: Instantly disguises app as work notes / calculator (Keyboard shortcut: Esc)"
      >
        <span class="panic-pulse-ring"></span>
        <span>Quick Disguise</span>
        <kbd class="panic-kbd-hint">Esc</kbd>
      </button>

      <!-- 📱 Mobile Bottom Navigation Bar (Elevated App Experience) -->
      <nav class="mobile-bottom-nav">
        <button 
          :class="['mobile-nav-btn', { active: activeTab === 'feed' }]"
          @click="selectTabFromMobile('feed')"
        >
          <span class="m-icon">📰</span>
          <span>Feed</span>
        </button>

        <button 
          :class="['mobile-nav-btn', { active: activeTab === 'connections' }]"
          @click="selectTabFromMobile('connections')"
        >
          <span class="m-icon">🤝</span>
          <span>Connect</span>
        </button>

        <!-- Center Mobile Post Button -->
        <button 
          class="mobile-post-fab"
          @click="handleMobileCompose"
          title="Share Story Anonymously"
        >
          <span>+</span>
        </button>

        <button 
          :class="['mobile-nav-btn', { active: activeTab === 'spaces' }]"
          @click="selectTabFromMobile('spaces')"
        >
          <span class="m-icon">🗺️</span>
          <span>Spaces</span>
        </button>

        <button 
          :class="['mobile-nav-btn', { active: showMoreSheet }]"
          @click="showMoreSheet = !showMoreSheet"
        >
          <span class="m-icon">✨</span>
          <span>More</span>
        </button>
      </nav>

      <!-- Mobile More Sheet Modal -->
      <div v-if="showMoreSheet" class="mobile-sheet-overlay" @click.self="showMoreSheet = false">
        <div class="mobile-sheet-menu animate-fade-in">
          <div class="sheet-drag-handle"></div>
          <div class="sheet-header">
            <h4>Support, Tools & Privacy</h4>
            <button class="sheet-close" @click="showMoreSheet = false">✕</button>
          </div>
          <div class="sheet-links">
            <button class="sheet-link-btn" @click="selectTabFromMobile('chat')">
              <span>💬</span> Safe Chat Rooms & DMs
            </button>
            <button class="sheet-link-btn" @click="selectTabFromMobile('mental-health')">
              <span>🧠</span> Mental Health & Helplines (24/7)
            </button>
            <button class="sheet-link-btn" @click="selectTabFromMobile('ai-assistant')">
              <span>🤖</span> SafeMode AI Assistant
            </button>
            <button class="sheet-link-btn" @click="selectTabFromMobile('legal')">
              <span>⚖️</span> India Legal Hub (Sec 377 & Trans Act)
            </button>
            <button class="sheet-link-btn" @click="showAuthModal = true; showMoreSheet = false">
              <span>🔑</span> Prism Identity Portal & Account
            </button>
            <button class="sheet-link-btn" @click="showIdentityModal = true; showMoreSheet = false">
              <span>⚙️</span> Anonymous Persona & PIN Settings
            </button>
            <button class="sheet-link-btn panic-item" @click="triggerPanic(); showMoreSheet = false">
              <span>🚨</span> Instant Disguise (Calculator Mode)
            </button>
            <button class="sheet-link-btn purge-item" @click="handlePurgeSession(); showMoreSheet = false">
              <span>🧹</span> Emergency Privacy Purge (Clear Cache)
            </button>
          </div>
        </div>
      </div>

      <!-- App Footer -->
      <footer class="app-footer glass-panel">
        <div class="footer-container">
          <div class="footer-brand-col">
            <div class="footer-brand">
              <span>🌈</span>
              <strong>Prism Community India</strong>
            </div>
            <p>
              A zero-compromise, encrypted sanctuary built for queer, trans, non-binary, and questioning individuals across Tier 1, 2, and 3 India.
            </p>
            <div class="privacy-pledge">
              🛡️ Zero tracking cookies • No real names required • Client-side encryption
            </div>
          </div>

          <div class="footer-links-col">
            <h5>24/7 Toll-Free Helplines</h5>
            <ul>
              <li>Tele-MANAS Mental Health: <a href="tel:14416" class="footer-link">14416</a></li>
              <li>National Emergency: <a href="tel:112" class="footer-link">112</a></li>
              <li>Sahodari Transgender Cell: <a href="tel:18002003802" class="footer-link">1800-200-3802</a></li>
              <li>Vandrevala Helpline: <a href="tel:+919999666555" class="footer-link">9999-666-555</a></li>
            </ul>
          </div>

          <div class="footer-panic-col">
            <h5>Privacy Safeguard</h5>
            <p>Press <kbd class="kbd-pill">Esc</kbd> anytime to instantly hide this website into discreet corporate notes or a calculator.</p>
            <button class="pride-sparkle-btn mt-2" @click="triggerPrideConfetti">
              ✨ Celebrate Pride
            </button>
          </div>
        </div>
      </footer>

      <!-- Identity & Privacy Modal -->
      <IdentityModal 
        v-if="showIdentityModal"
        :user="user"
        @close="showIdentityModal = false"
        @updateUser="handleUpdateUser"
        @triggerPanic="triggerPanic"
      />

      <!-- Upgraded Login & Signup Modal -->
      <AuthModal 
        v-if="showAuthModal"
        :user="user"
        :isLoggedIn="isLoggedIn"
        @close="showAuthModal = false"
        @signupSuccess="handleSignupSuccess"
        @loginSuccess="handleLoginSuccess"
        @purgeSession="handlePurgeSession"
      />

      <!-- Global Notification Toast -->
      <div v-if="globalToast" class="toast-popup animate-fade-in">
        {{ globalToast }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-root {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.prism-app-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content-area {
  flex: 1;
}

/* Mobile Sheet Overlay */
.mobile-sheet-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  z-index: 2200;
  display: flex;
  align-items: flex-end;
}

.mobile-sheet-menu {
  width: 100%;
  background: #11131e;
  border-top: 1px solid var(--border-light);
  border-radius: 20px 20px 0 0;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.sheet-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sheet-header h4 {
  font-size: 1.1rem;
  color: #fff;
}

.sheet-close {
  color: var(--text-muted);
  font-size: 1.2rem;
}

.sheet-drag-handle {
  width: 36px;
  height: 4px;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.2);
  margin: 0 auto 4px;
}

.sheet-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 70vh;
  overflow-y: auto;
}

.sheet-link-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-light);
  padding: 12px 16px;
  border-radius: var(--radius-md);
  color: #f1f5f9;
  font-size: 0.9rem;
  text-align: left;
  transition: all var(--transition-fast);
}

.sheet-link-btn:active {
  transform: scale(0.98);
}

.sheet-link-btn.panic-item {
  background: rgba(239, 68, 68, 0.12);
  border-color: rgba(239, 68, 68, 0.3);
  color: #fca5a5;
}

.sheet-link-btn.purge-item {
  background: rgba(245, 158, 11, 0.08);
  border-color: rgba(245, 158, 11, 0.25);
  color: #fef08a;
}

/* Footer */
.app-footer {
  margin-top: auto;
  border-left: none;
  border-right: none;
  border-bottom: none;
  border-radius: 0;
  background: rgba(9, 10, 16, 0.95);
  border-top: 1px solid var(--border-light);
  padding: 36px 20px 84px;
}

.footer-container {
  max-width: 1360px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 2fr 1.5fr 1fr;
  gap: 32px;
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.15rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 8px;
}

.footer-brand-col p {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.6;
  max-width: 480px;
}

.privacy-pledge {
  margin-top: 10px;
  font-size: 0.75rem;
  color: #34d399;
  font-weight: 600;
}

.footer-links-col h5, .footer-panic-col h5 {
  font-size: 0.88rem;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.footer-links-col ul {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 0.82rem;
  color: var(--text-secondary);
}

.footer-link {
  color: #38bdf8;
  font-weight: 600;
}
.footer-link:hover {
  text-decoration: underline;
}

.footer-panic-col p {
  font-size: 0.82rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.kbd-pill {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
  color: #fca5a5;
  font-family: monospace;
}

.pride-sparkle-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(168, 85, 247, 0.3);
  color: #c084fc;
  padding: 6px 14px;
  border-radius: var(--radius-md);
  font-size: 0.8rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all var(--transition-fast);
}
.pride-sparkle-btn:hover {
  background: rgba(168, 85, 247, 0.15);
  border-color: #a855f7;
}

.mt-2 {
  margin-top: 10px;
}

@media (max-width: 900px) {
  .footer-container {
    grid-template-columns: 1fr;
    gap: 24px;
  }
}
</style>
