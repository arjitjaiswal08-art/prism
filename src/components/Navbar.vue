<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  activeTab: {
    type: String,
    required: true
  },
  user: {
    type: Object,
    required: true
  },
  isLoggedIn: {
    type: Boolean,
    default: true
  },
  selectedCity: {
    type: String,
    required: true
  },
  cities: {
    type: Array,
    required: true
  }
})

const emit = defineEmits([
  'update:activeTab',
  'update:selectedCity',
  'openIdentityModal',
  'openAuthModal'
])

const isMoreDropdownOpen = ref(false)
const isMobileMenuOpen = ref(false)

// Primary Tabs (clean, zero-clutter)
const primaryTabs = [
  { id: 'feed', label: 'Feed', icon: '📰' },
  { id: 'connections', label: 'Connect', icon: '🤝' },
  { id: 'spaces', label: 'Map', icon: '🗺️' },
  { id: 'chat', label: 'Chat', icon: '💬' }
]

// Secondary Tabs (nested in More dropdown)
const secondaryTabs = [
  { id: 'mental-health', label: 'Support & Crisis', icon: '🧠', tag: '24/7 Aid' },
  { id: 'legal', label: 'Legal & Rights', icon: '⚖️', tag: 'Sec 377' },
  { id: 'ai-assistant', label: 'AI Companion', icon: '🤖', tag: 'AI' }
]

const handleTabSelect = (tabId) => {
  emit('update:activeTab', tabId)
  isMoreDropdownOpen.value = false
  isMobileMenuOpen.value = false
}

const isSecondaryActive = () => {
  return secondaryTabs.some(t => t.id === props.activeTab)
}

// Close dropdown on outside click
const closeDropdown = (e) => {
  if (!e.target.closest('.dropdown-wrap')) {
    isMoreDropdownOpen.value = false
  }
}

onMounted(() => {
  window.addEventListener('click', closeDropdown)
})

onUnmounted(() => {
  window.removeEventListener('click', closeDropdown)
})
</script>

<template>
  <header class="app-navbar glass-panel">
    <div class="nav-container">
      <!-- Left: Logo & Micro Trust Badge -->
      <div class="nav-left">
        <div class="brand-wrapper" @click="handleTabSelect('feed')">
          <div class="brand-logo-icon">🌈</div>
          <div class="brand-text">
            <span class="brand-name">Prism</span>
            <span class="brand-tagline">Safe Queer Space</span>
          </div>
        </div>

        <div class="security-chip" title="Client-side encryption, zero tracking">
          <span class="status-dot"></span>
          <span>100% Anonymous</span>
        </div>
      </div>

      <!-- Center: Simplified Primary Navigation Tabs -->
      <nav class="nav-links">
        <button 
          v-for="tab in primaryTabs" 
          :key="tab.id"
          :class="['nav-item', { active: activeTab === tab.id }]"
          @click="handleTabSelect(tab.id)"
        >
          <span class="nav-icon">{{ tab.icon }}</span>
          <span class="nav-label">{{ tab.label }}</span>
        </button>

        <!-- Secondary Dropdown ("Support & Resources ▾") -->
        <div class="dropdown-wrap">
          <button 
            :class="['nav-item', 'dropdown-trigger', { active: isSecondaryActive() }]"
            @click.stop="isMoreDropdownOpen = !isMoreDropdownOpen"
          >
            <span>✨ Support & Tools</span>
            <span class="caret">{{ isMoreDropdownOpen ? '▴' : '▾' }}</span>
          </button>

          <!-- Dropdown Menu -->
          <div v-if="isMoreDropdownOpen" class="dropdown-menu animate-fade-in">
            <button 
              v-for="sub in secondaryTabs" 
              :key="sub.id"
              :class="['dropdown-item', { active: activeTab === sub.id }]"
              @click="handleTabSelect(sub.id)"
            >
              <span class="sub-icon">{{ sub.icon }}</span>
              <div class="sub-text">
                <span class="sub-label">{{ sub.label }}</span>
                <span class="sub-tag">{{ sub.tag }}</span>
              </div>
            </button>
          </div>
        </div>
      </nav>

      <!-- Right: City Filter & Anonymous Persona -->
      <div class="nav-right">
        <!-- City Selector -->
        <div class="city-selector-wrap">
          <span class="geo-icon">📍</span>
          <select 
            :value="selectedCity" 
            @change="$emit('update:selectedCity', $event.target.value)"
            class="city-dropdown"
          >
            <option v-for="c in cities" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>

        <!-- Login / Account Button -->
        <button 
          class="auth-trigger-btn" 
          @click="$emit('openAuthModal')"
          title="Login or Sign Up with Anonymous Identity"
        >
          <span class="auth-key-icon">🔑</span>
          <span class="auth-btn-label">{{ isLoggedIn ? 'Account / Key' : 'Log In / Join' }}</span>
        </button>

        <!-- Anonymous Profile Persona Chip -->
        <button 
          class="anon-persona-btn" 
          @click="$emit('openIdentityModal')"
          title="Customize Anonymous Persona & Privacy"
        >
          <div class="persona-avatar" :style="{ background: user.avatarBg || 'linear-gradient(135deg, #a855f7, #ec4899)' }">
            {{ (user?.username || user?.alias || 'P').charAt(0) }}
          </div>
          <div class="persona-meta">
            <span class="persona-name">{{ user?.username || user?.alias || 'Anonymous' }}</span>
            <span class="persona-pronouns">{{ user?.pronouns || 'they/them' }}</span>
          </div>
          <span class="edit-icon">⚙️</span>
        </button>

        <!-- Mobile Hamburger Toggle -->
        <button 
          class="mobile-toggle"
          @click="isMobileMenuOpen = !isMobileMenuOpen"
          aria-label="Toggle Navigation"
        >
          <span>{{ isMobileMenuOpen ? '✕' : '☰' }}</span>
        </button>
      </div>
    </div>

    <!-- Mobile Drawer -->
    <div v-if="isMobileMenuOpen" class="mobile-drawer animate-fade-in">
      <div class="mobile-drawer-city">
        <span>City Filter:</span>
        <select 
          :value="selectedCity" 
          @change="$emit('update:selectedCity', $event.target.value); isMobileMenuOpen = false"
          class="city-dropdown"
        >
          <option v-for="c in cities" :key="c" :value="c">{{ c }}</option>
        </select>
      </div>

      <div class="mobile-drawer-links">
        <button 
          v-for="tab in [...primaryTabs, ...secondaryTabs]" 
          :key="tab.id"
          :class="['mobile-nav-item', { active: activeTab === tab.id }]"
          @click="handleTabSelect(tab.id)"
        >
          <span class="nav-icon">{{ tab.icon }}</span>
          <span>{{ tab.label }}</span>
        </button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.app-navbar {
  position: sticky;
  top: 12px;
  z-index: 1000;
  max-width: 1260px;
  margin: 12px auto 0;
  border-radius: var(--radius-full);
  background: rgba(13, 16, 26, 0.78);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.09);
  box-shadow: 0 10px 32px rgba(0, 0, 0, 0.45);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.nav-container {
  max-width: 100%;
  margin: 0 auto;
  padding: 8px 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

.brand-logo-icon {
  font-size: 1.6rem;
  filter: drop-shadow(0 0 8px rgba(168, 85, 247, 0.4));
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-family: var(--font-heading);
  font-weight: 800;
  font-size: 1.35rem;
  background: var(--gradient-pride);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1.1;
}

.brand-tagline {
  font-size: 0.65rem;
  color: var(--text-muted);
  font-weight: 500;
}

.security-chip {
  display: flex;
  align-items: center;
  gap: 5px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.25);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: 0.7rem;
  color: #34d399;
}

.status-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #10b981;
}

/* Primary Tabs Bar */
.nav-links {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(255, 255, 255, 0.025);
  padding: 3px;
  border-radius: var(--radius-full);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 16px;
  border-radius: var(--radius-full);
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-secondary);
  transition: all var(--transition-fast);
  cursor: pointer;
  position: relative;
}

.nav-item:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
}

.nav-item.active {
  color: #ffffff;
  background: rgba(168, 85, 247, 0.18);
  border: 1px solid rgba(168, 85, 247, 0.32);
  font-weight: 600;
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: 2px;
  left: 25%;
  right: 25%;
  height: 2px;
  background: var(--gradient-pride);
  border-radius: 9999px;
  box-shadow: 0 0 8px rgba(168, 85, 247, 0.7);
}

/* Dropdown */
.dropdown-wrap {
  position: relative;
}

.dropdown-trigger {
  padding-right: 12px;
}

.caret {
  font-size: 0.7rem;
  opacity: 0.6;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 260px;
  background: #131522;
  border: 1px solid rgba(168, 85, 247, 0.25);
  border-radius: var(--radius-md);
  padding: 8px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  gap: 4px;
  z-index: 1500;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 8px;
  color: var(--text-secondary);
  text-align: left;
  font-size: 0.82rem;
  transition: all var(--transition-fast);
}

.dropdown-item:hover {
  background: rgba(255, 255, 255, 0.06);
  color: #fff;
}

.dropdown-item.active {
  background: rgba(168, 85, 247, 0.2);
  color: #c084fc;
}

.sub-icon {
  font-size: 1.1rem;
}

.sub-text {
  display: flex;
  flex-direction: column;
}

.sub-label {
  font-weight: 600;
}

.sub-tag {
  font-size: 0.68rem;
  color: var(--text-muted);
}

/* Right Controls */
.nav-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.city-selector-wrap {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 4px 8px;
}

.geo-icon {
  font-size: 0.85rem;
}

.city-dropdown {
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 0.8rem;
  outline: none;
  cursor: pointer;
}
.city-dropdown option {
  background: #11131f;
  color: #fff;
}

.auth-trigger-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(168, 85, 247, 0.12);
  border: 1px solid rgba(168, 85, 247, 0.3);
  padding: 6px 12px;
  border-radius: var(--radius-full);
  font-size: 0.78rem;
  font-weight: 600;
  color: #d8b4fe;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.auth-trigger-btn:hover {
  background: rgba(168, 85, 247, 0.22);
  border-color: #a855f7;
  color: #fff;
}

.auth-key-icon {
  font-size: 0.85rem;
}

.anon-persona-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-light);
  padding: 4px 10px 4px 6px;
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.anon-persona-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--border-active);
}

.persona-avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  color: #fff;
  font-size: 0.72rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.persona-meta {
  display: flex;
  flex-direction: column;
  text-align: left;
}

.persona-name {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-primary);
  max-width: 90px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.persona-pronouns {
  font-size: 0.65rem;
  color: var(--text-muted);
}

.edit-icon {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.mobile-toggle {
  display: none;
  color: #fff;
  font-size: 1.25rem;
  padding: 6px;
}

.mobile-drawer {
  background: #0f111c;
  border-top: 1px solid var(--border-light);
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mobile-drawer-city {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.mobile-drawer-links {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mobile-nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 0.88rem;
  text-align: left;
}

.mobile-nav-item.active {
  background: rgba(168, 85, 247, 0.2);
  color: #fff;
  border: 1px solid rgba(168, 85, 247, 0.3);
}

@media (max-width: 900px) {
  .app-navbar {
    top: 6px;
    margin: 6px 10px 0;
    border-radius: var(--radius-lg);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  }
  .nav-container {
    padding: 6px 10px;
  }
  .nav-links {
    display: none;
  }
  .brand-tagline, .security-chip {
    display: none;
  }
  .brand-name {
    font-size: 1.15rem;
  }
  .persona-meta {
    display: none;
  }
  .auth-btn-label {
    display: none;
  }
  .auth-trigger-btn {
    padding: 6px 10px;
  }
  .anon-persona-btn {
    padding: 4px;
  }
  .edit-icon {
    display: none;
  }
  .mobile-toggle {
    display: none;
  }
}
</style>
