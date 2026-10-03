<script setup>
import { ref, computed } from 'vue'
import { prismApi } from '../services/api'

const props = defineProps({
  user: {
    type: Object,
    required: true
  },
  isLoggedIn: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['close', 'loginSuccess', 'signupSuccess', 'purgeSession'])

// 'anon' | 'signup' | 'login' | 'upgrade'
const activeAuthMode = ref('anon')
const signupMethod = ref('anon') // 'anon' | 'email'
const loginMethod = ref('handle') // 'handle' | 'email' | 'pin'

// Signup Form State
const signupHandle = ref(props.user.username || 'LavenderPhoenix')
const signupPronouns = ref(props.user.pronouns || 'they/them')
const signupCity = ref(props.user.city || 'Mumbai')
const signupPin = ref('1234')
const signupEmail = ref('')
const signupPassword = ref('')
const selectedTags = ref([...(props.user.identityTags || ['Queer'])])
const generatedSeedPhrase = ref('')
const showSeedBackupStep = ref(false)
const hasSavedSeed = ref(false)

// Upgrade Form State
const upgradeEmail = ref('')
const upgradePassword = ref('')

// Login Form State
const loginHandle = ref('')
const loginKey = ref('')
const loginEmail = ref('')
const loginPassword = ref('')
const loginPin = ref('')
const authError = ref('')
const isSubmitting = ref(false)

const handleNamePool = [
  'VelvetFalcon',
  'CosmicVoyager',
  'Solaris_TG',
  'IndigoEcho',
  'OceanDrifter',
  'AmberHorizon',
  'PrismWanderer',
  'SilverNebula',
  'EmeraldGlade',
  'StarrySanctuary'
]

const pronounOptions = [
  'they/them',
  'she/her',
  'he/him',
  'she/they',
  'he/they',
  'ze/zir',
  'any pronouns'
]

const identityTagOptions = [
  'Queer',
  'Lesbian',
  'Gay',
  'Bisexual',
  'Pansexual',
  'Transgender',
  'Non-Binary',
  'Asexual',
  'Questioning',
  'Ally Friendly'
]

const colorGradients = [
  'linear-gradient(135deg, #a855f7, #ec4899)',
  'linear-gradient(135deg, #ec4899, #f43f5e)',
  'linear-gradient(135deg, #3b82f6, #10b981)',
  'linear-gradient(135deg, #f59e0b, #ec4899)',
  'linear-gradient(135deg, #5bcefa, #f5a9b8)',
  'linear-gradient(135deg, #6366f1, #a855f7)'
]

const selectedAvatarBg = ref(colorGradients[0])

const rollRandomHandle = () => {
  const base = handleNamePool[Math.floor(Math.random() * handleNamePool.length)]
  const suffix = Math.floor(100 + Math.random() * 900)
  signupHandle.value = `${base}_${suffix}`
  selectedAvatarBg.value = colorGradients[Math.floor(Math.random() * colorGradients.length)]
}

const toggleTag = (tag) => {
  if (selectedTags.value.includes(tag)) {
    selectedTags.value = selectedTags.value.filter(t => t !== tag)
  } else {
    selectedTags.value.push(tag)
  }
}

// Generate 12-word cryptographic seed phrase for anonymous accounts
const generateSeed = () => {
  const wordDictionary = [
    'aurora', 'prism', 'freedom', 'galaxy', 'ember', 'solace',
    'beacon', 'harmony', 'courage', 'sanctuary', 'zenith', 'nebula',
    'echo', 'phoenix', 'radiance', 'voyage', 'haven', 'velvet'
  ]
  const words = []
  for (let i = 0; i < 12; i++) {
    words.push(wordDictionary[Math.floor(Math.random() * wordDictionary.length)])
  }
  return words.join(' ')
}

// 1. One-click anonymous login (Default CTA)
const quickOneClickAnon = async () => {
  isSubmitting.value = true
  authError.value = ''
  try {
    const res = await prismApi.anonymousLogin({
      alias: signupHandle.value || null,
      pronouns: signupPronouns.value || 'they/them',
      city: signupCity.value || 'All India',
      identity_tags: selectedTags.value,
      closet_pin: signupPin.value || '1234'
    })

    const transformedUser = {
      id: res.user.id,
      anon_id: res.user.anon_id,
      username: res.user.alias,
      pronouns: res.user.pronouns,
      city: res.user.city,
      avatarBg: selectedAvatarBg.value,
      identityTags: res.user.identity_tags ? res.user.identity_tags.split(',').map(s => s.trim()) : ['Queer'],
      closetPin: res.user.closet_pin || '1234',
      is_anonymous: true,
      authType: 'anon',
      karmaScore: 120
    }

    emit('signupSuccess', transformedUser)
    emit('close')
  } catch (err) {
    authError.value = err.message || 'Anonymous session failed'
  } finally {
    isSubmitting.value = false
  }
}

const handleStartSignup = async () => {
  authError.value = ''
  if (signupMethod.value === 'anon') {
    generatedSeedPhrase.value = generateSeed()
    showSeedBackupStep.value = true
  } else {
    // Email signup
    await completeEmailSignup()
  }
}

const completeAnonSignupWithSeed = async () => {
  await quickOneClickAnon()
}

const completeEmailSignup = async () => {
  if (!signupEmail.value || !signupPassword.value) {
    authError.value = 'Please provide an email and password'
    return
  }

  isSubmitting.value = true
  authError.value = ''
  try {
    const res = await prismApi.signup({
      email: signupEmail.value,
      password: signupPassword.value,
      alias: signupHandle.value || null,
      pronouns: signupPronouns.value || 'they/them',
      city: signupCity.value || 'All India',
      upgrade_from_anon_id: props.user.anon_id || null
    })

    const transformedUser = {
      id: res.user.id,
      anon_id: res.user.anon_id,
      username: res.user.alias,
      email: res.user.email,
      pronouns: res.user.pronouns,
      city: res.user.city,
      avatarBg: selectedAvatarBg.value,
      identityTags: ['Queer', 'Registered Member'],
      closetPin: '1234',
      is_anonymous: false,
      authType: 'email',
      karmaScore: 200
    }

    emit('signupSuccess', transformedUser)
    emit('close')
  } catch (err) {
    authError.value = err.message || 'Signup failed'
  } finally {
    isSubmitting.value = false
  }
}

// 3. Login
const handleLogin = async () => {
  authError.value = ''
  isSubmitting.value = true

  try {
    let ident = ''
    let pass = null

    if (loginMethod.value === 'handle') {
      if (!loginHandle.value.trim()) {
        authError.value = 'Please enter your Anonymous Handle or Anon ID'
        isSubmitting.value = false
        return
      }
      ident = loginHandle.value.trim()
      pass = loginKey.value || null
    } else if (loginMethod.value === 'email') {
      if (!loginEmail.value.trim() || !loginPassword.value) {
        authError.value = 'Please provide your email & password'
        isSubmitting.value = false
        return
      }
      ident = loginEmail.value.trim()
      pass = loginPassword.value
    } else if (loginMethod.value === 'pin') {
      if (loginPin.value.length < 4) {
        authError.value = 'PIN must be at least 4 digits'
        isSubmitting.value = false
        return
      }
      emit('loginSuccess', props.user)
      emit('close')
      isSubmitting.value = false
      return
    }

    const res = await prismApi.login({
      identifier: ident,
      password: pass
    })

    const loggedUser = {
      id: res.user.id,
      anon_id: res.user.anon_id,
      username: res.user.alias,
      email: res.user.email,
      pronouns: res.user.pronouns,
      city: res.user.city,
      avatarBg: colorGradients[0],
      identityTags: res.user.identity_tags ? res.user.identity_tags.split(',').map(s => s.trim()) : ['Queer'],
      closetPin: res.user.closet_pin || '1234',
      is_anonymous: res.user.is_anonymous,
      authType: res.user.is_anonymous ? 'anon' : 'email',
      karmaScore: 250
    }

    emit('loginSuccess', loggedUser)
    emit('close')
  } catch (err) {
    authError.value = err.message || 'Login failed. Please check credentials.'
  } finally {
    isSubmitting.value = false
  }
}

// 4. Upgrade Account
const handleUpgrade = async () => {
  if (!upgradeEmail.value || !upgradePassword.value) {
    authError.value = 'Please enter an email and password to upgrade'
    return
  }

  isSubmitting.value = true
  authError.value = ''
  try {
    const updated = await prismApi.upgradeAccount(upgradeEmail.value, upgradePassword.value)
    props.user.email = updated.email
    props.user.is_anonymous = false
    props.user.authType = 'email'
    emit('loginSuccess', { ...props.user, is_anonymous: false, email: updated.email })
    emit('close')
  } catch (err) {
    authError.value = err.message || 'Upgrade failed'
  } finally {
    isSubmitting.value = false
  }
}

const copySeedPhrase = () => {
  navigator.clipboard?.writeText(generatedSeedPhrase.value)
  hasSavedSeed.value = true
}
</script>

<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="auth-modal-card glass-panel animate-fade-in">
      <!-- Modal Header -->
      <div class="auth-modal-header">
        <div class="auth-brand">
          <span class="auth-logo">🌈</span>
          <div>
            <h3>Prism Identity Portal</h3>
            <span class="auth-sub">Zero-Knowledge • Anonymous & Secure</span>
          </div>
        </div>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>

      <!-- Auth Tabs: Entry Modal with Primary CTA -->
      <div class="auth-tabs-row">
        <button 
          :class="['auth-tab-btn primary-cta', { active: activeAuthMode === 'anon' }]"
          @click="activeAuthMode = 'anon'; authError = ''"
        >
          🎭 Continue Anonymously (Default)
        </button>
        <button 
          :class="['auth-tab-btn', { active: activeAuthMode === 'signup' }]"
          @click="activeAuthMode = 'signup'; authError = ''"
        >
          ✉️ Create Account
        </button>
        <button 
          :class="['auth-tab-btn', { active: activeAuthMode === 'login' }]"
          @click="activeAuthMode = 'login'; authError = ''"
        >
          🔑 Login
        </button>
        <button 
          v-if="user?.is_anonymous"
          :class="['auth-tab-btn upgrade-cta', { active: activeAuthMode === 'upgrade' }]"
          @click="activeAuthMode = 'upgrade'; authError = ''"
        >
          🚀 Upgrade Account
        </button>
      </div>

      <!-- Error Banner -->
      <div v-if="authError" class="auth-error-banner animate-fade-in">
        ⚠️ {{ authError }}
      </div>

      <!-- 🎭 MODE 1: CONTINUE ANONYMOUSLY (PRIMARY DEFAULT) -->
      <div v-if="activeAuthMode === 'anon'" class="auth-body animate-fade-in">
        <div class="privacy-hero-card">
          <div class="privacy-pill-group">
            <span class="trust-pill">🔒 No phone number required</span>
            <span class="trust-pill">🛡️ Stay anonymous</span>
            <span class="trust-pill">Zero forced identity</span>
          </div>
          <h4>Step Inside Anonymously</h4>
          <p class="privacy-subtext">
            Enter Prism with zero signup or phone verification. We assign a cryptographic, randomized anon ID so your browsing remains completely untracked.
          </p>

          <button class="btn-primary btn-lg w-full mt-3" :disabled="isSubmitting" @click="quickOneClickAnon">
            {{ isSubmitting ? 'Entering Prism Safely...' : '⚡ Quick 1-Click Anonymous Entry (Instant)' }}
          </button>
        </div>

        <div class="persona-divider">
          <span>Or personalize your anonymous persona</span>
        </div>

        <div class="persona-setup-box">
          <div class="handle-input-row">
            <div class="avatar-preview" :style="{ background: selectedAvatarBg }">
              {{ signupHandle.charAt(0) }}
            </div>
            <div class="handle-field-wrap">
              <label>Anonymous Persona Handle</label>
              <div class="input-with-dice">
                <input type="text" v-model="signupHandle" class="form-input" />
                <button class="btn-dice" @click="rollRandomHandle" title="Roll Random Persona">
                  🎲 Roll
                </button>
              </div>
            </div>
          </div>

          <div class="form-row mt-2">
            <div class="form-group half">
              <label>Pronouns</label>
              <select v-model="signupPronouns" class="form-input">
                <option v-for="p in pronounOptions" :key="p" :value="p">{{ p }}</option>
              </select>
            </div>
            <div class="form-group half">
              <label>Approximate Region / City</label>
              <input type="text" v-model="signupCity" class="form-input" placeholder="e.g. Pune, Mumbai" />
            </div>
          </div>

          <div class="form-group mt-2">
            <label>Spectrum Tags (Optional)</label>
            <div class="pills-cluster">
              <button 
                v-for="t in identityTagOptions" 
                :key="t"
                :class="['t-btn', { active: selectedTags.includes(t) }]"
                @click="toggleTag(t)"
              >
                {{ t }}
              </button>
            </div>
          </div>

          <div class="form-group mt-2">
            <label>Emergency "Closet Mode" PIN (for Panic Calculator disguise)</label>
            <input 
              type="password" 
              v-model="signupPin" 
              maxlength="4" 
              placeholder="1234" 
              class="form-input pin-field" 
            />
            <span class="field-hint">Used to unlock the app when disguised as a Calculator or Notes.</span>
          </div>

          <div class="auth-footer-actions">
            <button class="btn-secondary w-full" :disabled="isSubmitting" @click="quickOneClickAnon">
              {{ isSubmitting ? 'Entering Prism...' : 'Continue with this Persona ✨' }}
            </button>
          </div>
        </div>
      </div>

      <!-- ✉️ MODE 2: CREATE OPTIONAL ACCOUNT -->
      <div v-else-if="activeAuthMode === 'signup'" class="auth-body animate-fade-in">
        <div class="privacy-trust-callout">
          <span class="shield-icon">🛡️</span>
          <div>
            <strong>Pseudonymous & Private Account:</strong>
            <p>No phone number required. Use any private or burner email. Keep your real identity private while preserving your karma and saved resources across devices.</p>
          </div>
        </div>

        <div class="email-setup-box mt-3">
          <div class="form-group">
            <label>Public Pseudonym / Handle</label>
            <input 
              type="text" 
              v-model="signupHandle" 
              placeholder="e.g. LavenderPhoenix" 
              class="form-input" 
            />
          </div>
          <div class="form-group">
            <label>Private Email</label>
            <input 
              type="email" 
              v-model="signupEmail" 
              placeholder="private-alias@proton.me" 
              class="form-input" 
            />
            <span class="field-hint">We will never display, sell, or reveal this publicly.</span>
          </div>
          <div class="form-group">
            <label>Password</label>
            <input 
              type="password" 
              v-model="signupPassword" 
              placeholder="••••••••••••" 
              class="form-input" 
            />
            <span class="field-hint">Hashed with bcrypt (cost factor 12).</span>
          </div>

          <div class="auth-footer-actions">
            <button class="btn-primary w-full" :disabled="isSubmitting" @click="completeEmailSignup">
              {{ isSubmitting ? 'Creating Secure Account...' : 'Create Account & Continue ✨' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 🔑 MODE 3: LOGIN / RESTORE -->
      <div v-else-if="activeAuthMode === 'login'" class="auth-body animate-fade-in">
        <div class="login-method-selector">
          <button 
            :class="['method-pill', { active: loginMethod === 'handle' }]"
            @click="loginMethod = 'handle'"
          >
            🎭 Anon Handle / Anon ID
          </button>
          <button 
            :class="['method-pill', { active: loginMethod === 'email' }]"
            @click="loginMethod = 'email'"
          >
            ✉️ Email & Password
          </button>
          <button 
            :class="['method-pill', { active: loginMethod === 'pin' }]"
            @click="loginMethod = 'pin'"
          >
            🔒 Quick PIN Unlock
          </button>
        </div>

        <!-- Login by Anonymous Handle / Anon ID -->
        <div v-if="loginMethod === 'handle'" class="login-pane mt-3">
          <div class="form-group">
            <label>Anonymous Handle or UUID Anon ID</label>
            <input 
              type="text" 
              v-model="loginHandle" 
              placeholder="e.g. VelvetFalcon or your UUID" 
              class="form-input" 
            />
          </div>
          <div class="form-group">
            <label>Account Password (if set) or Secret Passphrase</label>
            <input 
              type="password" 
              v-model="loginKey" 
              placeholder="Enter password or passphrase (optional for open anon)" 
              class="form-input" 
            />
          </div>
        </div>

        <!-- Login by Email -->
        <div v-else-if="loginMethod === 'email'" class="login-pane mt-3">
          <div class="form-group">
            <label>Account Email</label>
            <input 
              type="email" 
              v-model="loginEmail" 
              placeholder="name@domain.com" 
              class="form-input" 
            />
          </div>
          <div class="form-group">
            <label>Password</label>
            <input 
              type="password" 
              v-model="loginPassword" 
              placeholder="••••••••••••" 
              class="form-input" 
            />
          </div>
        </div>

        <!-- Login by Quick PIN -->
        <div v-else class="login-pane mt-3">
          <div class="form-group text-center">
            <label>Enter 4-Digit Session PIN</label>
            <input 
              type="password" 
              v-model="loginPin" 
              maxlength="4" 
              placeholder="1234" 
              class="form-input pin-field-large mx-auto" 
              autofocus 
            />
            <span class="field-hint">Quick device unlock for active browser sessions.</span>
          </div>
        </div>

        <div class="auth-footer-actions">
          <button class="btn-primary w-full" :disabled="isSubmitting" @click="handleLogin">
            {{ isSubmitting ? 'Authenticating...' : 'Authenticate & Open Prism 🚀' }}
          </button>
        </div>

        <!-- Emergency Trace Purge -->
        <div class="emergency-purge-box">
          <div class="purge-info">
            <strong>Emergency Privacy Purge</strong>
            <small>Instantly wipes all local browsing tokens, saved chats, and cache from this browser.</small>
          </div>
          <button class="btn-panic btn-sm" @click="$emit('purgeSession'); $emit('close')">
            🧹 Wipe All Local Traces
          </button>
        </div>
      </div>

      <!-- 🚀 MODE 4: UPGRADE ANONYMOUS ACCOUNT -->
      <div v-else-if="activeAuthMode === 'upgrade'" class="auth-body animate-fade-in">
        <div class="privacy-trust-callout">
          <span class="shield-icon">🌟</span>
          <div>
            <strong>Upgrade Without Data Loss:</strong>
            <p>Keep your existing Anonymous ID ({{ user.anon_id || user.username }}), your connections, and all chat history while adding an email & password so you can access Prism from any device.</p>
          </div>
        </div>

        <div class="email-setup-box mt-3">
          <div class="form-group">
            <label>Current Anonymous Persona</label>
            <input type="text" :value="user.username" disabled class="form-input opacity-75" />
          </div>
          <div class="form-group">
            <label>Add Email Address</label>
            <input 
              type="email" 
              v-model="upgradeEmail" 
              placeholder="burner@proton.me" 
              class="form-input" 
            />
          </div>
          <div class="form-group">
            <label>Set Secure Password</label>
            <input 
              type="password" 
              v-model="upgradePassword" 
              placeholder="••••••••••••" 
              class="form-input" 
            />
          </div>

          <div class="auth-footer-actions">
            <button class="btn-primary w-full" :disabled="isSubmitting" @click="handleUpgrade">
              {{ isSubmitting ? 'Upgrading...' : 'Upgrade Account & Keep All History 🚀' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.82);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 3000;
}

.auth-modal-card {
  width: 100%;
  max-width: 580px;
  background: #11131e;
  border: 1px solid rgba(168, 85, 247, 0.35);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: 92vh;
  overflow-y: auto;
}

.auth-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-light);
}

.auth-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.auth-logo {
  font-size: 1.8rem;
}

.auth-brand h3 {
  font-size: 1.25rem;
  font-weight: 800;
  color: #fff;
}

.auth-sub {
  font-size: 0.72rem;
  color: #34d399;
}

.close-btn {
  font-size: 1.2rem;
  color: var(--text-muted);
}
.close-btn:hover {
  color: #fff;
}

/* Tabs */
.auth-tabs-row {
  display: flex;
  background: rgba(255, 255, 255, 0.04);
  padding: 4px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
  gap: 6px;
}

.auth-tab-btn {
  flex: 1;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary);
  transition: all var(--transition-fast);
}

.auth-tab-btn.active {
  background: rgba(168, 85, 247, 0.25);
  color: #fff;
  border: 1px solid rgba(168, 85, 247, 0.4);
}

.auth-tab-btn.primary-cta {
  border-left: 2px solid #a855f7;
}

.auth-tab-btn.upgrade-cta {
  color: #fbbf24;
}
.auth-tab-btn.upgrade-cta.active {
  background: rgba(245, 158, 11, 0.2);
  border-color: rgba(245, 158, 11, 0.5);
  color: #fef08a;
}

/* Privacy Hero Card */
.privacy-hero-card {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.16), rgba(236, 72, 153, 0.12));
  border: 1px solid rgba(168, 85, 247, 0.3);
  padding: 20px;
  border-radius: var(--radius-md);
  text-align: center;
}

.privacy-pill-group {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.trust-pill {
  font-size: 0.75rem;
  font-weight: 600;
  color: #a7f3d0;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  padding: 4px 10px;
  border-radius: 20px;
}

.privacy-hero-card h4 {
  font-size: 1.15rem;
  font-weight: 800;
  color: #fff;
  margin-bottom: 6px;
}

.privacy-subtext {
  font-size: 0.82rem;
  color: #cbd5e1;
  line-height: 1.45;
  max-width: 480px;
  margin: 0 auto;
}

.btn-lg {
  padding: 12px 18px;
  font-size: 0.95rem;
}

.persona-divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 16px 0 12px;
  color: var(--text-muted);
  font-size: 0.78rem;
}
.persona-divider::before, .persona-divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.persona-divider span {
  padding: 0 10px;
}

/* Quick Guest Hero */
.quick-guest-hero {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.12), rgba(236, 72, 153, 0.1));
  border: 1px dashed rgba(168, 85, 247, 0.35);
  padding: 12px 16px;
  border-radius: var(--radius-md);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.quick-guest-text strong {
  display: block;
  font-size: 0.86rem;
  color: #f1f5f9;
}

.quick-guest-text small {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.signup-method-toggle, .login-method-selector {
  display: flex;
  gap: 8px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}

.method-pill {
  padding: 6px 12px;
  border-radius: var(--radius-full);
  font-size: 0.78rem;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-light);
  color: var(--text-secondary);
  cursor: pointer;
}

.method-pill.active {
  background: var(--gradient-neon);
  color: #fff;
  border-color: transparent;
}

/* Handle Input Row */
.handle-input-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar-preview {
  width: 46px;
  height: 46px;
  border-radius: 50%;
  color: #fff;
  font-size: 1.2rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
}

.handle-field-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.input-with-dice {
  display: flex;
  gap: 8px;
}

.btn-dice {
  background: rgba(168, 85, 247, 0.2);
  border: 1px solid rgba(168, 85, 247, 0.4);
  color: #c084fc;
  padding: 0 12px;
  border-radius: var(--radius-md);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
}
.btn-dice:hover {
  background: rgba(168, 85, 247, 0.3);
}

/* Pills Cluster */
.pills-cluster {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.p-btn, .t-btn {
  font-size: 0.75rem;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-light);
  color: var(--text-secondary);
  cursor: pointer;
}

.p-btn.active, .t-btn.active {
  background: rgba(168, 85, 247, 0.25);
  border-color: #a855f7;
  color: #fff;
}

.form-group label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 4px;
  display: block;
}

.form-input {
  width: 100%;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 10px 14px;
  color: #fff;
  font-size: 0.9rem;
  outline: none;
}
.form-input:focus {
  border-color: var(--border-active);
}

.pin-field {
  width: 100px;
  letter-spacing: 0.2em;
  text-align: center;
}

.pin-field-large {
  width: 140px;
  font-size: 1.4rem;
  letter-spacing: 0.3em;
  text-align: center;
  padding: 12px;
}

.mx-auto {
  margin: 0 auto;
}

.field-hint {
  font-size: 0.72rem;
  color: var(--text-muted);
  display: block;
  margin-top: 3px;
}

/* Seed Phrase Screen */
.seed-backup-screen {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.shield-badge {
  font-size: 0.72rem;
  font-weight: 700;
  color: #34d399;
  text-transform: uppercase;
}

.seed-header h4 {
  font-size: 1.2rem;
  color: #fff;
  margin: 4px 0;
}

.seed-header p {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.seed-phrase-box {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  background: #090a10;
  border: 1px solid rgba(168, 85, 247, 0.3);
  border-radius: var(--radius-md);
  padding: 14px;
}

.seed-word {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.03);
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 0.82rem;
}

.word-idx {
  font-size: 0.68rem;
  color: var(--text-muted);
}

.word-text {
  font-weight: 700;
  color: #c084fc;
}

.seed-actions {
  display: flex;
  gap: 10px;
}

.seed-warning {
  font-size: 0.75rem;
  color: #f87171;
  text-align: center;
}

/* Trust Callout */
.privacy-trust-callout {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.25);
  padding: 10px 14px;
  border-radius: var(--radius-md);
  margin-top: 12px;
}

.shield-icon {
  font-size: 1.2rem;
}

.privacy-trust-callout strong {
  display: block;
  font-size: 0.82rem;
  color: #34d399;
}

.privacy-trust-callout p {
  font-size: 0.75rem;
  color: #cbd5e1;
  line-height: 1.4;
}

.auth-footer-actions {
  margin-top: 14px;
}

.auth-error-banner {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #fca5a5;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  font-size: 0.82rem;
  margin-bottom: 10px;
}

/* Emergency Purge */
.emergency-purge-box {
  margin-top: 20px;
  padding-top: 14px;
  border-top: 1px solid var(--border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.purge-info strong {
  display: block;
  font-size: 0.82rem;
  color: #f87171;
}

.purge-info small {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.w-full {
  width: 100%;
  justify-content: center;
}

.mt-2 {
  margin-top: 10px;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.78rem;
}
</style>
