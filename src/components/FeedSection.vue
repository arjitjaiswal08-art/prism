<script setup>
import { ref, computed, watch } from 'vue'
import confetti from 'canvas-confetti'

const props = defineProps({
  posts: {
    type: Array,
    required: true
  },
  user: {
    type: Object,
    required: true
  },
  selectedCity: {
    type: String,
    required: true
  },
  categories: {
    type: Array,
    required: true
  },
  triggerNewPostModal: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['addPost', 'votePost', 'toggleSavePost', 'addComment', 'switchTab'])

watch(() => props.triggerNewPostModal, (newVal) => {
  if (newVal) {
    showNewPostModal.value = true
  }
})

const activeCategory = ref('all')
const searchQuery = ref('')
const isSearchFocused = ref(false)
const showNewPostModal = ref(false)
const expandedComments = ref({})
const expandedPosts = ref({})
const newCommentTexts = ref({})
const toastMessage = ref('')
const activeSidebarTab = ref('ai') // 'ai' | 'crisis' | 'rules'
const isSidebarCollapsed = ref(false)

// New Post Form state
const newPostTitle = ref('')
const newPostContent = ref('')
const newPostCategory = ref('ComingOut')
const newPostCity = ref(props.selectedCity === 'All India' ? 'Delhi NCR' : props.selectedCity)
const hasContentWarning = ref(false)
const contentWarningText = ref('')

// Interactive Daily Prompt Engine
const dailyPromptQuestion = "What was a small moment this week that made you feel safe, affirmed, or proud?"

const promptReactions = ref([
  { emoji: '❤️', count: 142, reacted: false },
  { emoji: '🫂', count: 89, reacted: false },
  { emoji: '🔥', count: 64, reacted: false },
  { emoji: '✨', count: 51, reacted: false },
  { emoji: '💜', count: 78, reacted: false }
])

const showPromptAnswers = ref(false)

const samplePromptAnswers = ref([
  { id: 1, author: 'SolaceEcho', city: 'Bengaluru', text: 'My colleague casually used my correct pronouns in our team standup without making a big deal out of it.' },
  { id: 2, author: 'VelvetGlade', city: 'Pune', text: 'Went to a quiet queer cafe in Koregaon Park and finished reading a gay romance novel without glancing over my shoulder once.' },
  { id: 3, author: 'IndiePhoenix', city: 'Delhi', text: 'My mother asked how my non-binary partner is doing with their art exhibition. Huge step for us.' }
])

const togglePromptReaction = (idx) => {
  const rx = promptReactions.value[idx]
  if (rx.reacted) {
    rx.count--
    rx.reacted = false
  } else {
    rx.count++
    rx.reacted = true
    showToast(`Reaction ${rx.emoji} recorded anonymously! ✨`)
  }
}

const openDailyPromptPost = () => {
  newPostTitle.value = `[Daily Prompt] ${dailyPromptQuestion}`
  newPostCategory.value = 'QueerJoy'
  showNewPostModal.value = true
}

// AI Emotion Auto-Detection for composer & posts
const detectedEmotion = computed(() => {
  const combined = (newPostTitle.value + ' ' + newPostContent.value).toLowerCase()
  if (combined.includes('happy') || combined.includes('biryani') || combined.includes('love') || combined.includes('celebrat') || combined.includes('proud') || combined.includes('won')) {
    return { label: '😊 Uplifting & Joy', class: 'emotion-joy' }
  }
  if (combined.includes('panic') || combined.includes('anxiety') || combined.includes('dysphoria') || combined.includes('scared') || combined.includes('suffocat') || combined.includes('lonely')) {
    return { label: '😰 Anxious / Dysphoria Support', class: 'emotion-anxiety' }
  }
  if (combined.includes('law') || combined.includes('court') || combined.includes('police') || combined.includes('certificate') || combined.includes('rights')) {
    return { label: '⚖️ Legal & Rights Query', class: 'emotion-legal' }
  }
  if (combined.includes('advise') || combined.includes('advice') || combined.includes('how to') || combined.includes('sister') || combined.includes('parents')) {
    return { label: '🌱 Vulnerable / Seeking Advice', class: 'emotion-advice' }
  }
  return { label: '💬 Community Discussion', class: 'emotion-neutral' }
})

// Post Emotion Badge classifier
const getPostEmotion = (post) => {
  const text = (post.title + ' ' + post.content + ' ' + (post.tags || []).join(' ')).toLowerCase()
  if (text.includes('vulnerable') || text.includes('cry') || text.includes('scared') || text.includes('parents') || text.includes('secret')) {
    return { class: 'vulnerable', icon: '😢', label: 'Vulnerable' }
  }
  if (text.includes('happy') || text.includes('joy') || text.includes('celebrate') || text.includes('pride') || text.includes('date') || text.includes('passed')) {
    return { class: 'happy', icon: '😊', label: 'Happy & Joy' }
  }
  if (text.includes('anxiety') || text.includes('panic') || text.includes('dysphoria') || text.includes('harass') || text.includes('nervous')) {
    return { class: 'anxious', icon: '😰', label: 'Anxious' }
  }
  if (text.includes('rights') || text.includes('law') || text.includes('policy') || text.includes('work') || text.includes('empower')) {
    return { class: 'empowered', icon: '💪', label: 'Empowered' }
  }
  return { class: 'hopeful', icon: '💜', label: 'Hopeful' }
}

// Extract Hook line (first sentence) vs remaining
const getPostHook = (content) => {
  if (!content) return ''
  const periodIdx = content.indexOf('.')
  const exclamationIdx = content.indexOf('!')
  const questionIdx = content.indexOf('?')
  
  const endIndices = [periodIdx, exclamationIdx, questionIdx].filter(i => i > 15)
  if (endIndices.length > 0) {
    const minEnd = Math.min(...endIndices)
    return content.slice(0, minEnd + 1)
  }
  return content.slice(0, 110) + '...'
}

const getPostRemaining = (content, postId) => {
  if (!content) return ''
  const hook = getPostHook(content)
  const remainder = content.slice(hook.length).trim()
  if (!remainder) return ''
  
  if (expandedPosts.value[postId]) {
    return remainder
  }
  return remainder.length > 140 ? remainder.slice(0, 140) + '...' : remainder
}

const toggleExpandPost = (postId) => {
  expandedPosts.value[postId] = !expandedPosts.value[postId]
}

// Safety Distress Auto-Detection
const isDistressDetected = computed(() => {
  const combined = (newPostTitle.value + ' ' + newPostContent.value).toLowerCase()
  const triggerWords = ['end it all', 'want to die', 'suicide', 'self harm', 'no point living', 'kill myself', 'hopeless completely']
  return triggerWords.some(w => combined.includes(w))
})

const searchSuggestions = [
  '#ComingOut',
  'Gender Dysphoria',
  'Bangalore Tech DEI',
  'Section 377',
  'Conservative Parents',
  'Small Town'
]

const trendingTopics = [
  '#ComingOut',
  '#FamilySupport',
  '#WorkplaceDEI',
  '#Anxiety',
  '#DatingSafely',
  '#MentalHealth'
]

const filteredPosts = computed(() => {
  return props.posts.filter(post => {
    // Category match
    const categoryMatch = activeCategory.value === 'all' || post.tags.includes(activeCategory.value)
    // City match
    const cityMatch = props.selectedCity === 'All India' || post.city === props.selectedCity || post.city === 'All India'
    // Search query
    const query = searchQuery.value.toLowerCase().trim()
    const searchMatch = !query || 
      post.title.toLowerCase().includes(query) || 
      post.content.toLowerCase().includes(query) ||
      post.tags.some(t => t.toLowerCase().includes(query))

    return categoryMatch && cityMatch && searchMatch
  })
})

const handleVote = (postId, direction) => {
  emit('votePost', { postId, direction })
}

const toggleComments = (postId) => {
  expandedComments.value[postId] = !expandedComments.value[postId]
}

const submitComment = (postId) => {
  const text = (newCommentTexts.value[postId] || '').trim()
  if (!text) return
  emit('addComment', {
    postId,
    comment: {
      id: 'c-' + Date.now(),
      author: props.user.username || props.user.alias || 'Anonymous',
      pronouns: props.user.pronouns || 'they/them',
      timestamp: 'Just now',
      text
    }
  })
  newCommentTexts.value[postId] = ''
}

const submitNewPost = () => {
  if (!newPostTitle.value.trim() || !newPostContent.value.trim()) return

  const newPost = {
    id: 'post-' + Date.now(),
    author: props.user.username || props.user.alias || 'Anonymous',
    pronouns: props.user.pronouns || 'they/them',
    avatarBg: props.user.avatarBg || 'linear-gradient(135deg, #a855f7, #ec4899)',
    city: newPostCity.value,
    tags: [newPostCategory.value],
    timestamp: 'Just now',
    title: newPostTitle.value.trim(),
    content: newPostContent.value.trim(),
    contentWarning: hasContentWarning.value ? (contentWarningText.value.trim() || 'Trigger Warning') : null,
    isBlurred: hasContentWarning.value,
    upvotes: 1,
    downvotes: 0,
    userVote: 1,
    saved: false,
    commentsCount: 0,
    comments: []
  }

  emit('addPost', newPost)
  
  newPostTitle.value = ''
  newPostContent.value = ''
  hasContentWarning.value = false
  contentWarningText.value = ''
  showNewPostModal.value = false

  // Trigger micro-delight pride confetti
  try {
    confetti({
      particleCount: 45,
      spread: 65,
      origin: { y: 0.7 },
      colors: ['#f43f5e', '#fb923c', '#fbbf24', '#10b981', '#06b6d4', '#8b5cf6']
    })
  } catch (e) {}

  showToast('Your anonymous story has been safely published! ✨')
}

const unblurPost = (post) => {
  post.isBlurred = false
}

const copyShareLink = (post) => {
  navigator.clipboard?.writeText(window.location.href)
  showToast('Encrypted post link copied! 🔒')
}

const scrollToPosts = () => {
  const el = document.getElementById('posts-feed-start')
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}

const showToast = (msg) => {
  toastMessage.value = msg
  setTimeout(() => {
    toastMessage.value = ''
  }, 3000)
}
</script>

<template>
  <div class="feed-layout">
    <!-- Main Column -->
    <div class="feed-main">
      <!-- 🎯 Focused, Calm Hero Banner -->
      <section class="focused-hero glass-panel">
        <div class="hero-center-content">
          <!-- Social Proof Badge -->
          <div class="hero-social-proof">
            <span class="pulse-dot"></span>
            <span>🌈 “You’re Not Alone” • <strong>1,200+</strong> stories shared this week</span>
          </div>

          <h1 class="hero-heading">🔥 Share Your Truth Without Fear</h1>
          <p class="hero-subtext">
            A safe, anonymous space for real stories and connection.
          </p>

          <!-- Center Primary & Secondary CTAs -->
          <div class="hero-actions-center">
            <button class="btn-hero-primary" @click="showNewPostModal = true">
              <span class="btn-sparkle">🔥</span> Share Your Story
            </button>
            <button class="btn-hero-secondary" @click="scrollToPosts">
              📖 Browse Stories
            </button>
          </div>
        </div>

        <!-- 🛡️ Trust Indicators (Crucial Trust UX) -->
        <div class="trust-indicators-bar">
          <div class="trust-badge">
            <span class="trust-icon">🔒</span>
            <span>100% Anonymous</span>
          </div>
          <div class="trust-badge">
            <span class="trust-icon">🚫</span>
            <span>No Phone Required</span>
          </div>
          <div class="trust-badge">
            <span class="trust-icon">🛡️</span>
            <span>Moderated Safe Space</span>
          </div>
          <div class="trust-badge">
            <span class="trust-icon">💜</span>
            <span>No Judgment. Ever.</span>
          </div>
        </div>
      </section>

      <!-- 💡 Interactive Daily Reflection Engine -->
      <div class="daily-prompt-card glass-panel">
        <div class="prompt-icon-col">💡</div>
        <div class="prompt-text-col">
          <div class="prompt-badge-row">
            <span class="badge badge-accent">Daily Prompt</span>
            <span class="prompt-hint">Tap a reaction or share your thoughts</span>
          </div>
          <p class="prompt-question">"{{ dailyPromptQuestion }}"</p>

          <!-- Interactive Emoji Reactions -->
          <div class="prompt-reactions-row">
            <button 
              v-for="(rx, idx) in promptReactions" 
              :key="idx"
              :class="['prompt-reaction-pill', { active: rx.reacted }]"
              @click="togglePromptReaction(idx)"
              title="React anonymously"
            >
              <span class="rx-emoji">{{ rx.emoji }}</span>
              <span class="rx-count">{{ rx.count }}</span>
            </button>

            <button 
              class="prompt-answers-toggle"
              @click="showPromptAnswers = !showPromptAnswers"
            >
              {{ showPromptAnswers ? 'Hide Answers ↑' : 'See Others’ Answers (24) ↓' }}
            </button>
          </div>

          <!-- Community Answers Expansion -->
          <div v-if="showPromptAnswers" class="prompt-answers-drawer animate-fade-in">
            <div v-for="ans in samplePromptAnswers" :key="ans.id" class="prompt-answer-item">
              <div class="ans-header">
                <strong class="ans-author">{{ ans.author }}</strong>
                <span class="ans-city">📍 {{ ans.city }}</span>
              </div>
              <p class="ans-text">“{{ ans.text }}”</p>
            </div>
          </div>
        </div>

        <button class="btn-secondary btn-sm prompt-cta" @click="openDailyPromptPost">
          Answer Anonymously ✍️
        </button>
      </div>

      <!-- Categories Filter Bar -->
      <div class="category-pills-bar">
        <button
          v-for="cat in categories"
          :key="cat.id"
          :class="['category-pill', { active: activeCategory === cat.id }]"
          @click="activeCategory = cat.id"
        >
          {{ cat.label }}
        </button>
      </div>

      <!-- 🔍 Upgraded Smart Search Bar -->
      <div class="search-section">
        <div class="search-input-wrap">
          <span class="search-icon">🔍</span>
          <input 
            type="text" 
            v-model="searchQuery" 
            @focus="isSearchFocused = true"
            placeholder="Search stories, feelings, topics..."
            class="search-input"
          />
          <button v-if="searchQuery" @click="searchQuery = ''; isSearchFocused = false" class="clear-btn">✕</button>
        </div>

        <!-- Suggested chips -->
        <div class="search-suggestions-row">
          <span class="try-label">Suggested:</span>
          <button 
            v-for="sug in trendingTopics" 
            :key="sug"
            class="suggestion-chip"
            @click="searchQuery = sug"
          >
            {{ sug }}
          </button>
        </div>
      </div>

      <!-- 🧠 Emotional Reassurance Microcopy Strip (Superpower UX) -->
      <div class="emotional-reassurance-strip">
        <span>🛡️ You’re safe here.</span>
        <span class="strip-dot">•</span>
        <span>✨ Your story matters.</span>
        <span class="strip-dot">•</span>
        <span>💜 No judgment. Ever.</span>
      </div>

      <!-- Post List Anchor -->
      <div id="posts-feed-start" class="posts-list-header">
        <span class="feed-count">
          Showing <strong>{{ filteredPosts.length }}</strong> community voices in 
          <span class="city-name">{{ selectedCity }}</span>
        </span>
      </div>

      <!-- Structured & Whitespace-Polished Posts -->
      <div class="posts-list">
        <div v-if="filteredPosts.length === 0" class="empty-state glass-panel">
          <span class="empty-icon">🌱</span>
          <h3>No posts found matching this topic</h3>
          <p>Be the first gentle voice to share an experience in {{ selectedCity }}!</p>
          <button class="btn-primary mt-2" @click="showNewPostModal = true">Share First Story</button>
        </div>

        <article 
          v-for="post in filteredPosts" 
          :key="post.id"
          class="post-card glass-panel"
        >
          <!-- 💡 AI Highlight (Community Resonance) -->
          <div v-if="post.upvotes >= 100 || post.id === 'post_1'" class="ai-highlight-pill animate-fade-in">
            <span class="ai-sparkle">✨</span>
            <span>👉 People relate to this</span>
          </div>

          <!-- Top: [Avatar] Name • time • location -->
          <div class="post-header-refined">
            <div class="author-meta-cluster">
              <div class="author-avatar" :style="{ background: post.avatarBg }">
                {{ (post.author || 'A').charAt(0) }}
              </div>
              <div class="author-name-group">
                <span class="author-name">{{ post.author }}</span>
                <span class="meta-separator">•</span>
                <span class="author-pronouns">{{ post.pronouns }}</span>
                <span class="meta-separator">•</span>
                <span class="post-time">{{ post.timestamp }}</span>
                <span class="meta-separator">•</span>
                <span class="post-location">📍 {{ post.city }}</span>
              </div>
            </div>

            <div class="post-header-right">
              <!-- Emotion Indicator Badge -->
              <span :class="['emotion-badge', getPostEmotion(post).class]">
                {{ getPostEmotion(post).icon }} {{ getPostEmotion(post).label }}
              </span>
              <div class="post-tags-row">
                <span v-for="tag in post.tags" :key="tag" class="badge badge-tag">
                  #{{ tag }}
                </span>
              </div>
            </div>
          </div>

          <!-- 🔥 Title (Bigger, prominent, clean) -->
          <h2 class="post-title-refined">{{ post.title }}</h2>

          <!-- Content / Content Warning Shield -->
          <div v-if="post.isBlurred" class="cw-shield-container">
            <div class="cw-shield-card">
              <span class="cw-icon">🛡️</span>
              <div class="cw-info">
                <strong>Content Notice:</strong>
                <span>{{ post.contentWarning || 'Sensitive topic discussion' }}</span>
              </div>
              <button class="btn-secondary btn-sm" @click="unblurPost(post)">
                Reveal Safely
              </button>
            </div>
            <p class="post-body-blurred">{{ post.content }}</p>
          </div>

          <!-- Body with Hook & Truncation Read More -->
          <div v-else class="post-body-refined">
            <div class="post-hook-line">
              {{ getPostHook(post.content) }}
            </div>
            <div class="post-body-text" v-if="post.content && post.content.length > getPostHook(post.content).length">
              <p>{{ getPostRemaining(post.content, post.id) }}</p>
              <button 
                v-if="post.content.length > 130" 
                class="read-more-toggle" 
                @click="toggleExpandPost(post.id)"
              >
                {{ expandedPosts[post.id] ? 'Show less ↑' : 'Read more →' }}
              </button>
            </div>
          </div>

          <!-- Actions Bar: ⬆️ Upvote • 💬 Reply • 🔖 Save • ↗ Share -->
          <div class="post-actions-refined">
            <!-- Upvote / Downvote -->
            <div class="vote-group">
              <button 
                :class="['vote-btn upvote', { active: post.userVote === 1 }]"
                @click="handleVote(post.id, 1)"
                title="Upvote"
              >
                ⬆️
              </button>
              <span class="vote-count">{{ post.upvotes - post.downvotes }}</span>
              <button 
                :class="['vote-btn downvote', { active: post.userVote === -1 }]"
                @click="handleVote(post.id, -1)"
                title="Downvote"
              >
                ⬇️
              </button>
            </div>

            <!-- Reply Button -->
            <button 
              class="action-item-btn"
              @click="toggleComments(post.id)"
            >
              💬 <span>{{ post.commentsCount + (post.comments ? post.comments.length : 0) }}</span>
            </button>

            <!-- Save Bookmark -->
            <button 
              :class="['action-item-btn', { active: post.saved }]"
              @click="$emit('toggleSavePost', post.id)"
              title="Bookmark"
            >
              🔖 <span>{{ post.saved ? 'Saved' : 'Save' }}</span>
            </button>

            <!-- Share -->
            <button 
              class="action-item-btn"
              @click="copyShareLink(post)"
              title="Copy secure link"
            >
              ↗ <span>Share</span>
            </button>
          </div>

          <!-- Comments Thread -->
          <div v-if="expandedComments[post.id]" class="comments-section animate-fade-in">
            <div class="comment-input-box">
              <div class="comment-input-avatar" :style="{ background: user.avatarBg }">
                {{ user.username.charAt(0) }}
              </div>
              <input 
                type="text" 
                v-model="newCommentTexts[post.id]"
                :placeholder="`Reply anonymously as ${user.username}...`"
                @keyup.enter="submitComment(post.id)"
                class="comment-input"
              />
              <button class="btn-primary btn-sm" @click="submitComment(post.id)">
                Send
              </button>
            </div>

            <div v-if="post.comments && post.comments.length > 0" class="comments-list">
              <div v-for="c in post.comments" :key="c.id" class="comment-item">
                <div class="comment-meta">
                  <span class="comment-author">{{ c.author }}</span>
                  <span class="comment-pronouns">({{ c.pronouns }})</span>
                  <span class="comment-time">{{ c.timestamp }}</span>
                </div>
                <div class="comment-text">{{ c.text }}</div>
              </div>
            </div>
            <div v-else class="no-comments-hint">
              No replies yet. Send words of love and encouragement! 🌈
            </div>
          </div>
        </article>
      </div>
    </div>

    <!-- ⚡ Optimized & Collapsible Tabbed Sidebar -->
    <aside class="feed-sidebar-clean">
      <div class="sidebar-header-bar">
        <span class="sidebar-mini-label">Support & Rules</span>
        <button class="sidebar-collapse-btn" @click="isSidebarCollapsed = !isSidebarCollapsed">
          {{ isSidebarCollapsed ? 'Show ▾' : 'Collapse ▴' }}
        </button>
      </div>

      <div v-show="!isSidebarCollapsed" class="sidebar-collapsible-body animate-fade-in">
        <div class="sidebar-tab-switcher">
          <button 
            :class="['sidebar-nav-pill', { active: activeSidebarTab === 'ai' }]"
            @click="activeSidebarTab = 'ai'"
          >
            🧠 AI Help
          </button>
          <button 
            :class="['sidebar-nav-pill', { active: activeSidebarTab === 'crisis' }]"
            @click="activeSidebarTab = 'crisis'"
          >
            🚨 Crisis
          </button>
          <button 
            :class="['sidebar-nav-pill', { active: activeSidebarTab === 'rules' }]"
            @click="activeSidebarTab = 'rules'"
          >
            📜 Rules
          </button>
        </div>

        <!-- Tab 1: AI Assistant Widget -->
        <div v-if="activeSidebarTab === 'ai'" class="sidebar-tab-pane glass-panel animate-fade-in">
          <div class="pane-header">
            <span class="badge badge-accent">SafeMode AI</span>
            <span class="pulse-sparkle">✨</span>
          </div>
          <h4>Need Immediate Advice?</h4>
          <p>Get culturally attuned guidance for coming out to Indian parents, navigating workplace DEI, or grounding yourself.</p>
          <button class="btn-primary w-full" @click="$emit('switchTab', 'ai-assistant')">
            Chat With SafeMode AI ↗
          </button>
        </div>

        <!-- Tab 2: 24/7 Helplines Widget -->
        <div v-else-if="activeSidebarTab === 'crisis'" class="sidebar-tab-pane glass-panel animate-fade-in">
          <div class="pane-header">
            <h4>24/7 Verified Helplines</h4>
            <span class="badge badge-crisis">Free</span>
          </div>
          <div class="compact-helplines">
            <div class="c-line">
              <div>
                <strong>Tele-MANAS</strong>
                <small>National 24/7 Mental Health</small>
              </div>
              <a href="tel:14416" class="btn-call">14416</a>
            </div>
            <div class="c-line">
              <div>
                <strong>Vandrevala Foundation</strong>
                <small>Queer Affirmative Line</small>
              </div>
              <a href="tel:+919999666555" class="btn-call">Call</a>
            </div>
            <div class="c-line">
              <div>
                <strong>Sahodari Trans Cell</strong>
                <small>Emergency Abuse Protection</small>
              </div>
              <a href="tel:18002003802" class="btn-call">Call</a>
            </div>
          </div>
          <button class="btn-secondary w-full btn-sm mt-2" @click="$emit('switchTab', 'mental-health')">
            View All Therapists & Clinics ↗
          </button>
        </div>

        <!-- Tab 3: Safe Rules Widget -->
        <div v-else class="sidebar-tab-pane glass-panel animate-fade-in">
          <div class="pane-header">
            <h4>🛡️ Community Rules</h4>
          </div>
          <ul class="clean-rules-list">
            <li><strong>Zero Doxxing:</strong> Never ask for real identities or phone numbers.</li>
            <li><strong>No Hate Speech:</strong> Immediate shadow-ban for toxic behavior.</li>
            <li><strong>Use Content Warnings:</strong> Tag sensitive topics so friends browse safely.</li>
            <li><strong>Respect All Pronouns:</strong> We celebrate every point on the spectrum.</li>
          </ul>
        </div>
      </div>
    </aside>

    <!-- Create Post Modal with Emotion Tagging & Safety Interceptor -->
    <div v-if="showNewPostModal" class="modal-backdrop" @click.self="showNewPostModal = false">
      <div class="modal-card glass-panel animate-fade-in">
        <div class="modal-header">
          <div class="modal-title-wrap">
            <span class="badge badge-tag">🔒 Anonymous Submission</span>
            <h3>Share Your Experience</h3>
          </div>
          <button class="close-modal-btn" @click="showNewPostModal = false">✕</button>
        </div>

        <div class="modal-body">
          <!-- Safety Distress Interceptor Alert -->
          <div v-if="isDistressDetected" class="safety-interceptor-banner animate-fade-in">
            <span class="interceptor-icon">❤️</span>
            <div class="interceptor-text">
              <strong>We care about you deeply.</strong>
              <p>You seem to be going through an intense time. You don't have to carry this alone. Please talk to a free, affirming counselor right now at <strong>Tele-MANAS (14416)</strong> or <strong>Vandrevala (+91 9999 666 555)</strong>.</p>
            </div>
          </div>

          <div class="form-group">
            <label>Posting As</label>
            <div class="anon-preview-pill">
              <span class="pill-avatar" :style="{ background: user.avatarBg }">{{ user.username.charAt(0) }}</span>
              <span>{{ user.username }} ({{ user.pronouns }})</span>
              <span class="ghost-note">• Random anonymous handle</span>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Category Tag</label>
              <select v-model="newPostCategory" class="form-input">
                <option value="ComingOut">🌱 #ComingOut</option>
                <option value="MentalHealth">🧠 #MentalHealth</option>
                <option value="TransPride">🏳️⚧️ #TransPride</option>
                <option value="Career">💼 #Career</option>
                <option value="Dating">💜 #Dating</option>
                <option value="LegalHelp">⚖️ #LegalHelp</option>
                <option value="QueerJoy">🌈 #QueerJoy</option>
              </select>
            </div>

            <div class="form-group">
              <label>Location Context</label>
              <select v-model="newPostCity" class="form-input">
                <option value="All India">All India</option>
                <option value="Delhi NCR">Delhi NCR</option>
                <option value="Mumbai">Mumbai</option>
                <option value="Bengaluru">Bengaluru</option>
                <option value="Kolkata">Kolkata</option>
                <option value="Pune">Pune</option>
                <option value="Hyderabad">Hyderabad</option>
                <option value="Chennai">Chennai</option>
                <option value="Tier 2 / Tier 3 Towns">Tier 2 / Tier 3 Towns</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Post Headline</label>
            <input 
              type="text" 
              v-model="newPostTitle" 
              placeholder="e.g. Came out to my roommate... or need advice in Pune" 
              class="form-input" 
            />
          </div>

          <div class="form-group">
            <div class="label-with-emotion">
              <label>Your Story / Thoughts</label>
              <span v-if="newPostContent.length > 10" :class="['detected-emotion-badge', detectedEmotion.class]">
                Detected: {{ detectedEmotion.label }}
              </span>
            </div>
            <textarea 
              v-model="newPostContent" 
              rows="5" 
              placeholder="Express yourself freely. This post is completely anonymous and encrypted." 
              class="form-textarea"
            ></textarea>
          </div>

          <!-- Content Warning Toggle -->
          <div class="cw-toggle-box">
            <label class="checkbox-label">
              <input type="checkbox" v-model="hasContentWarning" />
              <span>Add Content Warning (CW) / Blur for sensitive topic</span>
            </label>
            <input 
              v-if="hasContentWarning" 
              type="text" 
              v-model="contentWarningText" 
              placeholder="e.g. Discussion of family rejection, dysphoria..." 
              class="form-input mt-2" 
            />
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="showNewPostModal = false">Cancel</button>
          <button 
            class="btn-primary" 
            :disabled="!newPostTitle.trim() || !newPostContent.trim()" 
            @click="submitNewPost"
          >
            Post Anonymously ✨
          </button>
        </div>
      </div>
    </div>

    <!-- Global Floating Add Post Button -->
    <button 
      class="global-fab-post" 
      @click="showNewPostModal = true" 
      title="Share your story anonymously (+)"
      aria-label="New Post"
    >
      <span>+</span>
    </button>

    <!-- Toast Popup -->
    <div v-if="toastMessage" class="toast-popup animate-fade-in">
      {{ toastMessage }}
    </div>
  </div>
</template>

<style scoped>
.feed-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 28px;
  max-width: 1360px;
  margin: 0 auto;
  padding: 24px 20px 80px;
}

.feed-main {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 🎯 Focused Hero */
.focused-hero {
  padding: 36px 30px 24px;
  background: var(--bg-card-matte);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.hero-social-proof {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(168, 85, 247, 0.1);
  border: 1px solid rgba(168, 85, 247, 0.25);
  padding: 4px 14px;
  border-radius: var(--radius-full);
  font-size: 0.78rem;
  color: #d8b4fe;
  margin-bottom: 6px;
}
.hero-social-proof strong {
  color: #fff;
}
.pulse-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #34d399;
  box-shadow: 0 0 8px #34d399;
  animation: pulse-ring 2s infinite;
}

.prompt-reactions-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.prompt-reaction-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-size: 0.8rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.prompt-reaction-pill:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(168, 85, 247, 0.35);
  transform: translateY(-1px);
}

.prompt-reaction-pill.active {
  background: rgba(168, 85, 247, 0.22);
  border-color: rgba(168, 85, 247, 0.5);
  color: #fff;
}

.rx-count {
  font-size: 0.74rem;
  font-weight: 600;
}

.prompt-answers-toggle {
  background: none;
  border: none;
  font-size: 0.78rem;
  color: #c084fc;
  cursor: pointer;
  font-weight: 600;
  padding: 4px 8px;
}
.prompt-answers-toggle:hover {
  text-decoration: underline;
}

.prompt-answers-drawer {
  margin-top: 12px;
  padding: 12px 14px;
  border-radius: var(--radius-md);
  background: rgba(15, 17, 26, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.prompt-answer-item {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  padding-bottom: 8px;
}
.prompt-answer-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}
.ans-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.75rem;
  margin-bottom: 2px;
}
.ans-author { color: #f1f5f9; font-weight: 600; }
.ans-city { color: #94a3b8; font-size: 0.7rem; }
.ans-text { font-size: 0.82rem; color: #cbd5e1; font-style: italic; }

.post-header-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.hero-center-content {
  max-width: 720px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.hero-pill {
  font-size: 0.78rem;
  font-weight: 700;
  color: #c084fc;
  letter-spacing: 0.04em;
  background: rgba(168, 85, 247, 0.12);
  padding: 3px 12px;
  border-radius: var(--radius-full);
}

.hero-heading {
  font-size: 2.1rem;
  font-weight: 800;
  background: var(--gradient-pride);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1.2;
}

.hero-subtext {
  font-size: 0.98rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

.hero-actions-center {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-top: 14px;
  flex-wrap: wrap;
  justify-content: center;
}

.btn-hero-primary {
  background: var(--gradient-neon);
  color: white;
  padding: 13px 28px;
  border-radius: var(--radius-md);
  font-size: 1.05rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 18px rgba(168, 85, 247, 0.35);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}

.btn-hero-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(236, 72, 153, 0.45);
}

.btn-hero-secondary {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-light);
  color: var(--text-primary);
  padding: 12px 22px;
  border-radius: var(--radius-md);
  font-size: 0.95rem;
  font-weight: 600;
  transition: all var(--transition-fast);
}

.btn-hero-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* 🛡️ Trust Indicators Bar */
.trust-indicators-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-top: 26px;
  padding-top: 20px;
  border-top: 1px solid var(--border-subtle);
  flex-wrap: wrap;
}

.trust-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.76rem;
  font-weight: 600;
  color: #94a3b8;
}

.trust-icon {
  font-size: 0.85rem;
}

/* 💡 Daily Prompt Card */
.daily-prompt-card {
  padding: 18px 22px;
  border-radius: var(--radius-md);
  background: rgba(168, 85, 247, 0.08);
  border: 1px solid rgba(168, 85, 247, 0.25);
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.prompt-icon-col {
  font-size: 1.8rem;
}

.prompt-text-col {
  flex: 1;
  min-width: 260px;
}

.prompt-badge-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.prompt-hint {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.prompt-question {
  font-size: 0.95rem;
  font-weight: 600;
  color: #f1f5f9;
}

.prompt-cta {
  white-space: nowrap;
}

/* Category Pills Bar */
.category-pills-bar {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  scrollbar-width: none;
  padding-bottom: 4px;
}
.category-pills-bar::-webkit-scrollbar {
  display: none;
}

.category-pill {
  white-space: nowrap;
  padding: 8px 16px;
  border-radius: var(--radius-full);
  font-size: 0.84rem;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.03);
  color: var(--text-secondary);
  border: 1px solid var(--border-light);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.category-pill:hover {
  background: rgba(255, 255, 255, 0.07);
  color: #fff;
}

.category-pill.active {
  background: var(--gradient-neon);
  color: #ffffff;
  border-color: transparent;
}

/* 🔍 Search Section */
.search-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.search-input-wrap {
  position: relative;
  width: 100%;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.85rem;
  opacity: 0.6;
}

.search-input {
  width: 100%;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-light);
  padding: 10px 38px;
  border-radius: var(--radius-full);
  color: #fff;
  font-size: 0.88rem;
  outline: none;
  transition: border-color var(--transition-fast);
}

.search-input:focus {
  border-color: var(--border-active);
  background: rgba(255, 255, 255, 0.05);
}

.clear-btn {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 0.75rem;
}

.search-suggestions-row {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  padding: 0 4px;
}

.try-label {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.suggestion-chip {
  font-size: 0.72rem;
  color: #a855f7;
  background: rgba(168, 85, 247, 0.08);
  border: 1px solid rgba(168, 85, 247, 0.2);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  cursor: pointer;
}
.suggestion-chip:hover {
  background: rgba(168, 85, 247, 0.15);
  color: #d8b4fe;
}

.posts-list-header {
  font-size: 0.84rem;
  color: var(--text-secondary);
  padding: 0 4px;
}

.posts-list-header strong {
  color: #38bdf8;
}

.city-name {
  color: #f472b6;
  font-weight: 600;
}

/* 📜 Structured Post Cards */
.posts-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.post-card {
  padding: 24px;
  background: var(--bg-card-matte);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  gap: 14px;
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}

.post-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
  border-color: rgba(168, 85, 247, 0.35);
}

/* 💡 AI Highlight Badge */
.ai-highlight-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(168, 85, 247, 0.12);
  border: 1px solid rgba(168, 85, 247, 0.3);
  color: #c084fc;
  font-size: 0.76rem;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: var(--radius-full);
  align-self: flex-start;
  margin-bottom: -4px;
}

.ai-sparkle {
  font-size: 0.85rem;
}

/* 🧠 Emotional Reassurance Strip */
.emotional-reassurance-strip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px dashed rgba(255, 255, 255, 0.08);
  padding: 8px 16px;
  border-radius: var(--radius-md);
  font-size: 0.82rem;
  color: #94a3b8;
  font-weight: 500;
  margin: 6px 0 14px;
  flex-wrap: wrap;
}

.strip-dot {
  color: rgba(255, 255, 255, 0.2);
}

/* Sidebar header bar */
.sidebar-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 6px 10px;
  border-bottom: 1px solid var(--border-subtle);
  margin-bottom: 10px;
}

.sidebar-mini-label {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.sidebar-collapse-btn {
  font-size: 0.75rem;
  color: #a855f7;
  background: rgba(168, 85, 247, 0.08);
  padding: 3px 8px;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.sidebar-collapse-btn:hover {
  background: rgba(168, 85, 247, 0.2);
  color: #d8b4fe;
}

/* Top Header */
.post-header-refined {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.author-meta-cluster {
  display: flex;
  align-items: center;
  gap: 10px;
}

.author-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  color: #fff;
  font-size: 0.85rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.author-name-group {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.82rem;
  flex-wrap: wrap;
}

.author-name {
  font-weight: 700;
  color: var(--text-primary);
}

.author-pronouns {
  color: var(--text-secondary);
}

.meta-separator {
  color: var(--border-active);
  font-size: 0.7rem;
}

.post-time, .post-location {
  color: var(--text-muted);
  font-size: 0.75rem;
}

/* 🔥 Big Prominent Title */
.post-title-refined {
  font-size: 1.35rem;
  font-weight: 700;
  line-height: 1.35;
  color: #ffffff;
}

/* Body */
.post-body-refined p {
  color: #cbd5e1;
  font-size: 0.95rem;
  line-height: 1.7;
  max-width: 72ch;
  white-space: pre-line;
}

/* Content Warning Shield */
.cw-shield-container {
  border-radius: var(--radius-md);
  overflow: hidden;
  background: rgba(0, 0, 0, 0.3);
  padding: 16px;
}

.cw-shield-card {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
  padding: 12px 16px;
  border-radius: var(--radius-md);
  margin-bottom: 10px;
}

.cw-icon {
  font-size: 1.4rem;
}

.cw-info {
  display: flex;
  flex-direction: column;
  font-size: 0.85rem;
  color: #fef3c7;
  flex: 1;
}

.post-body-blurred {
  filter: blur(8px);
  user-select: none;
  opacity: 0.35;
  font-size: 0.9rem;
}

/* Refined Post Actions */
.post-actions-refined {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--border-subtle);
  flex-wrap: wrap;
}

.vote-group {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-full);
  padding: 2px 8px;
}

.vote-btn {
  font-size: 0.8rem;
  padding: 4px 6px;
  color: var(--text-muted);
}
.vote-btn:hover {
  color: #fff;
}
.vote-btn.upvote.active {
  color: #10b981;
}
.vote-btn.downvote.active {
  color: #ef4444;
}

.vote-count {
  font-size: 0.82rem;
  font-weight: 700;
  min-width: 22px;
  text-align: center;
}

.action-item-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.82rem;
  color: var(--text-secondary);
  padding: 6px 12px;
  border-radius: var(--radius-md);
}

.action-item-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.action-item-btn.active {
  color: #fbbf24;
}

/* Comments Section */
.comments-section {
  background: rgba(0, 0, 0, 0.2);
  border-radius: var(--radius-md);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comment-input-box {
  display: flex;
  align-items: center;
  gap: 10px;
}

.comment-input-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  color: #fff;
  font-size: 0.72rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.comment-input {
  flex: 1;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-light);
  padding: 8px 14px;
  border-radius: var(--radius-full);
  color: #fff;
  font-size: 0.85rem;
  outline: none;
}
.comment-input:focus {
  border-color: var(--border-active);
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.comment-item {
  background: rgba(255, 255, 255, 0.02);
  padding: 10px 14px;
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.comment-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  margin-bottom: 4px;
}

.comment-author {
  font-weight: 600;
  color: #c084fc;
}

.comment-pronouns, .comment-time {
  color: var(--text-muted);
}
.comment-time {
  margin-left: auto;
}

.comment-text {
  font-size: 0.88rem;
  color: #e2e8f0;
}

.no-comments-hint {
  text-align: center;
  font-size: 0.82rem;
  color: var(--text-muted);
  padding: 8px;
}

/* ⚡ Optimized Tabbed Sidebar */
.feed-sidebar-clean {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.sidebar-tab-switcher {
  display: flex;
  gap: 4px;
  background: rgba(255, 255, 255, 0.03);
  padding: 4px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
}

.sidebar-nav-pill {
  flex: 1;
  padding: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 8px;
  color: var(--text-secondary);
  text-align: center;
  cursor: pointer;
}

.sidebar-nav-pill.active {
  background: rgba(168, 85, 247, 0.2);
  color: #fff;
  border: 1px solid rgba(168, 85, 247, 0.3);
}

.sidebar-tab-pane {
  padding: 20px;
  border-radius: var(--radius-lg);
  background: var(--bg-card-matte);
  border: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.pane-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-tab-pane h4 {
  font-size: 1.05rem;
  font-weight: 700;
  color: #fff;
}

.sidebar-tab-pane p {
  font-size: 0.84rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.compact-helplines {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 4px 0;
}

.c-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.02);
  padding: 8px 10px;
  border-radius: var(--radius-md);
}

.c-line strong {
  display: block;
  font-size: 0.8rem;
  color: #fff;
}
.c-line small {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.btn-call {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.35);
  padding: 3px 8px;
  border-radius: var(--radius-full);
  font-size: 0.72rem;
  font-weight: 700;
}

.clean-rules-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 0.82rem;
  color: var(--text-secondary);
}
.clean-rules-list li strong {
  color: #f1f5f9;
}

.w-full {
  width: 100%;
  justify-content: center;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.8rem;
}
.mt-2 {
  margin-top: 8px;
}

/* Modals */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.82);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 3000;
}

.modal-card {
  width: 100%;
  max-width: 580px;
  background: #11131e;
  border: 1px solid rgba(168, 85, 247, 0.3);
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.modal-title-wrap h3 {
  font-size: 1.3rem;
  font-weight: 700;
  margin-top: 4px;
}

.close-modal-btn {
  font-size: 1.2rem;
  color: var(--text-muted);
}

.safety-interceptor-banner {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(185, 28, 28, 0.3));
  border: 1px solid rgba(239, 68, 68, 0.5);
  padding: 12px 16px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.interceptor-icon {
  font-size: 1.4rem;
}

.interceptor-text strong {
  display: block;
  color: #fca5a5;
  font-size: 0.9rem;
  margin-bottom: 2px;
}

.interceptor-text p {
  font-size: 0.82rem;
  color: #fecaca;
  line-height: 1.4;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.label-with-emotion {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detected-emotion-badge {
  font-size: 0.72rem;
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.emotion-joy {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.3);
}
.emotion-anxiety {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.3);
}
.emotion-legal {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.3);
}
.emotion-advice {
  background: rgba(168, 85, 247, 0.15);
  color: #d8b4fe;
  border: 1px solid rgba(168, 85, 247, 0.3);
}
.emotion-neutral {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-muted);
}

.anon-preview-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-light);
  padding: 8px 12px;
  border-radius: var(--radius-md);
  font-size: 0.85rem;
}

.pill-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  color: #fff;
  font-size: 0.7rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ghost-note {
  color: var(--text-muted);
  font-size: 0.75rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-input, .form-textarea {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 10px 14px;
  color: #fff;
  font-size: 0.9rem;
  outline: none;
}
.form-input:focus, .form-textarea:focus {
  border-color: var(--border-active);
}
.form-input option {
  background: #11131e;
}

.cw-toggle-box {
  background: rgba(255, 255, 255, 0.02);
  border: 1px dashed var(--border-light);
  padding: 12px;
  border-radius: var(--radius-md);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: var(--text-secondary);
  cursor: pointer;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--border-light);
}

.toast-popup {
  position: fixed;
  bottom: 84px;
  right: 24px;
  background: #1e1b4b;
  border: 1px solid #818cf8;
  color: #e0e7ff;
  padding: 12px 20px;
  border-radius: var(--radius-md);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
  font-size: 0.9rem;
  font-weight: 500;
  z-index: 3500;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.empty-icon {
  font-size: 2.5rem;
}

@media (max-width: 990px) {
  .feed-layout {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  .feed-sidebar-clean {
    margin-top: 10px;
  }
}

@media (max-width: 768px) {
  .feed-container {
    padding: 8px 10px 100px;
  }

  .hero-section-focused {
    padding: 22px 14px;
    border-radius: var(--radius-lg);
    margin-bottom: 16px;
  }

  .hero-badge-live {
    font-size: 0.72rem;
    padding: 4px 10px;
    margin-bottom: 10px;
  }

  .hero-title {
    font-size: 1.55rem;
    line-height: 1.25;
    letter-spacing: -0.01em;
  }

  .hero-subtitle {
    font-size: 0.88rem;
    line-height: 1.5;
    margin: 8px auto 14px;
  }

  .hero-actions-center {
    flex-direction: column;
    width: 100%;
    gap: 10px;
    margin-top: 12px;
  }

  .btn-hero-primary,
  .btn-hero-secondary {
    width: 100%;
    justify-content: center;
    padding: 13px 20px;
    font-size: 0.95rem;
    min-height: 48px;
  }

  /* 2x2 Grid for Trust Badges on Mobile */
  .trust-indicators-bar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px 12px;
    margin-top: 18px;
    padding-top: 14px;
    border-top: 1px solid var(--border-subtle);
  }

  .trust-badge {
    font-size: 0.72rem;
    justify-content: flex-start;
  }

  /* Daily Prompt Card */
  .daily-prompt-card {
    padding: 14px;
    gap: 12px;
    flex-direction: column;
    align-items: stretch;
  }

  .prompt-icon-col {
    display: none;
  }

  .prompt-text-col {
    min-width: 100%;
  }

  .prompt-question {
    font-size: 0.9rem;
    line-height: 1.4;
  }

  .prompt-cta {
    width: 100%;
  }

  .prompt-cta button {
    width: 100%;
    justify-content: center;
    min-height: 42px;
  }

  .prompt-reactions-row {
    justify-content: space-between;
    overflow-x: auto;
    padding-bottom: 4px;
  }

  .reaction-pill {
    padding: 6px 10px;
    font-size: 0.85rem;
  }

  /* Category pills */
  .category-pills-bar {
    gap: 6px;
    padding-bottom: 6px;
    -webkit-overflow-scrolling: touch;
  }

  .category-pill {
    font-size: 0.78rem;
    padding: 7px 12px;
    min-height: 38px;
  }

  /* Posts */
  .posts-list {
    gap: 14px;
  }

  .post-card {
    padding: 16px 14px;
    gap: 12px;
    border-radius: var(--radius-md);
  }

  .post-header-refined {
    gap: 8px;
  }

  .author-avatar {
    width: 32px;
    height: 32px;
    font-size: 0.78rem;
  }

  .author-name {
    font-size: 0.82rem;
  }

  .post-title-refined {
    font-size: 1.15rem;
    line-height: 1.35;
  }

  .post-body-refined p {
    font-size: 0.9rem;
    line-height: 1.55;
  }

  .post-actions-refined {
    gap: 6px;
    justify-content: space-between;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    padding-bottom: 2px;
    flex-wrap: nowrap;
  }

  .action-item-btn {
    padding: 6px 8px;
    font-size: 0.75rem;
    white-space: nowrap;
    min-height: 36px;
  }

  .vote-group {
    padding: 2px 4px;
    min-height: 36px;
  }

  /* Mobile Modals */
  .modal-card {
    max-width: 95vw !important;
    width: 95vw !important;
    padding: 18px 14px !important;
    max-height: 90vh !important;
    overflow-y: auto;
    border-radius: var(--radius-lg);
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .modal-footer {
    flex-direction: column-reverse;
    gap: 8px;
  }

  .modal-footer button {
    width: 100%;
    min-height: 44px;
  }

  .comment-input-box {
    gap: 6px;
  }

  .comment-input {
    font-size: 16px !important;
  }
}
</style>
