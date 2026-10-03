<script setup>
import { ref } from 'vue'

const props = defineProps({
  user: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'updateUser', 'triggerPanic'])

const pseudonym = ref(props.user.username)
const pronouns = ref(props.user.pronouns)
const pinCode = ref(props.user.closetPin || '1234')
const autoBlur = ref(props.user.autoBlurContent)
const activeTags = ref([...props.user.identityTags])

const availablePronouns = [
  'they/them',
  'she/her',
  'he/him',
  'she/they',
  'he/they',
  'ze/zir',
  'any pronouns'
]

const availableTags = [
  'Queer',
  'Lesbian',
  'Gay',
  'Bisexual',
  'Pansexual',
  'Transgender',
  'Non-Binary',
  'Asexual',
  'Aromantic',
  'Questioning',
  'Two-Spirit',
  'Intersex',
  'Ally Friendly'
]

const namePool = [
  'LavenderPhoenix',
  'CosmicVoyager',
  'VelvetStar',
  'IndigoEcho',
  'Solaris_TG',
  'PrismWanderer',
  'OceanDrifter',
  'AmberHorizon',
  'EmeraldGlade',
  'SilverNebula'
]

const colorGradients = [
  'linear-gradient(135deg, #a855f7, #ec4899)',
  'linear-gradient(135deg, #ec4899, #f43f5e)',
  'linear-gradient(135deg, #3b82f6, #10b981)',
  'linear-gradient(135deg, #f59e0b, #ec4899)',
  'linear-gradient(135deg, #5bcefa, #f5a9b8)',
  'linear-gradient(135deg, #6366f1, #a855f7)'
]

const selectedAvatarBg = ref(props.user.avatarBg)

const randomizePersona = () => {
  const randomName = namePool[Math.floor(Math.random() * namePool.length)]
  pseudonym.value = `${randomName}_${Math.floor(100 + Math.random() * 900)}`
  selectedAvatarBg.value = colorGradients[Math.floor(Math.random() * colorGradients.length)]
}

const toggleTag = (tag) => {
  if (activeTags.value.includes(tag)) {
    activeTags.value = activeTags.value.filter(t => t !== tag)
  } else {
    activeTags.value.push(tag)
  }
}

const saveChanges = () => {
  emit('updateUser', {
    username: pseudonym.value.trim() || 'Anon_Prism',
    pronouns: pronouns.value,
    avatarBg: selectedAvatarBg.value,
    identityTags: [...activeTags.value],
    closetPin: pinCode.value,
    autoBlurContent: autoBlur.value
  })
  emit('close')
}
</script>

<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-card glass-panel animate-fade-in">
      <div class="modal-header">
        <div>
          <span class="badge badge-tag">Identity & Privacy Controls</span>
          <h3>Anonymous Persona Settings</h3>
        </div>
        <button class="close-modal-btn" @click="$emit('close')">✕</button>
      </div>

      <div class="modal-body">
        <!-- Persona Avatar Preview -->
        <div class="avatar-preview-row">
          <div class="big-avatar" :style="{ background: selectedAvatarBg }">
            {{ pseudonym.charAt(0) }}
          </div>
          <div class="avatar-meta">
            <h4>{{ pseudonym }}</h4>
            <span class="pronoun-display">{{ pronouns }}</span>
            <button class="btn-secondary btn-sm mt-1" @click="randomizePersona">
              🎲 Generate New Anon Identity
            </button>
          </div>
        </div>

        <!-- Username Input -->
        <div class="form-group">
          <label>Anonymous Handle</label>
          <input type="text" v-model="pseudonym" class="form-input" />
          <span class="field-hint">Never use your legal or real name. Keep it completely pseudonymous.</span>
        </div>

        <!-- Pronouns -->
        <div class="form-group">
          <label>Pronouns</label>
          <div class="pronouns-pills">
            <button 
              v-for="p in availablePronouns" 
              :key="p"
              :class="['p-pill', { active: pronouns === p }]"
              @click="pronouns = p"
            >
              {{ p }}
            </button>
          </div>
        </div>

        <!-- Identity Spectrum Tags -->
        <div class="form-group">
          <label>Identity Tags (Optional)</label>
          <div class="tags-cloud">
            <button 
              v-for="tag in availableTags" 
              :key="tag"
              :class="['tag-chip', { active: activeTags.includes(tag) }]"
              @click="toggleTag(tag)"
            >
              {{ tag }}
            </button>
          </div>
        </div>

        <!-- Closet Mode / Privacy Safeguards -->
        <div class="closet-settings-box">
          <h4>🔒 "Closet Mode" Emergency Safeguards</h4>
          
          <div class="setting-item">
            <div>
              <strong>Emergency PIN Lock</strong>
              <small>Required to unlock application from Panic disguise</small>
            </div>
            <input 
              type="password" 
              v-model="pinCode" 
              maxlength="4" 
              class="pin-field" 
              placeholder="1234"
            />
          </div>

          <div class="setting-item">
            <div>
              <strong>Auto-Blur Sensitive Media & Posts</strong>
              <small>Hides potentially triggering content behind a privacy shield</small>
            </div>
            <input type="checkbox" v-model="autoBlur" />
          </div>

          <button class="btn-panic w-full mt-2" @click="$emit('triggerPanic'); $emit('close')">
            🚨 Test Panic Button Right Now (Switch to Calculator)
          </button>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-secondary" @click="$emit('close')">Cancel</button>
        <button class="btn-primary" @click="saveChanges">Save Persona</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
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
  max-width: 560px;
  background: #121422;
  border: 1px solid rgba(168, 85, 247, 0.35);
  border-radius: var(--radius-lg);
  padding: 26px;
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.close-modal-btn {
  font-size: 1.2rem;
  color: var(--text-muted);
}

.avatar-preview-row {
  display: flex;
  align-items: center;
  gap: 16px;
  background: rgba(255, 255, 255, 0.03);
  padding: 14px;
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.big-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  color: #fff;
  font-size: 1.6rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 16px rgba(168, 85, 247, 0.4);
}

.avatar-meta h4 {
  font-size: 1.15rem;
  font-weight: 700;
  color: #fff;
}

.pronoun-display {
  font-size: 0.8rem;
  color: var(--text-secondary);
  display: block;
}

.mt-1 {
  margin-top: 6px;
}
.mt-2 {
  margin-top: 10px;
}
.w-full {
  width: 100%;
  justify-content: center;
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

.form-input {
  background: rgba(255, 255, 255, 0.05);
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

.field-hint {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.pronouns-pills {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.p-pill {
  padding: 6px 12px;
  border-radius: var(--radius-full);
  font-size: 0.78rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-light);
  color: var(--text-secondary);
  cursor: pointer;
}
.p-pill:hover {
  color: #fff;
}
.p-pill.active {
  background: rgba(168, 85, 247, 0.25);
  border-color: #a855f7;
  color: #fff;
  font-weight: 600;
}

.tags-cloud {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag-chip {
  padding: 5px 10px;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-light);
  color: var(--text-muted);
  cursor: pointer;
}
.tag-chip:hover {
  color: #fff;
}
.tag-chip.active {
  background: rgba(236, 72, 153, 0.2);
  border-color: #ec4899;
  color: #f472b6;
  font-weight: 600;
}

.closet-settings-box {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-md);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.closet-settings-box h4 {
  font-size: 0.95rem;
  color: #f8fafc;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.setting-item strong {
  display: block;
  font-size: 0.82rem;
  color: #e2e8f0;
}

.setting-item small {
  display: block;
  font-size: 0.72rem;
  color: var(--text-muted);
}

.pin-field {
  width: 80px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid var(--border-light);
  padding: 6px 10px;
  border-radius: 8px;
  color: #fff;
  text-align: center;
  font-size: 1rem;
  letter-spacing: 0.2em;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--border-light);
}

.btn-sm {
  padding: 4px 10px;
  font-size: 0.75rem;
}
</style>
