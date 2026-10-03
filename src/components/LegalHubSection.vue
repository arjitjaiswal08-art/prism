<script setup>
import { ref } from 'vue'

const props = defineProps({
  resources: {
    type: Array,
    required: true
  }
})

const activeLawId = ref(props.resources[0]?.id || 'leg-1')
const toastMessage = ref('')

const safetyChecklist = ref([
  { id: 1, text: 'Financial safety cushion: Have at least 2-3 months of emergency expenses saved in an individual bank account.', checked: true },
  { id: 2, text: 'Identify emergency anchor: At least one trusted queer friend or ally whose home you can go to if tensions flare.', checked: true },
  { id: 3, text: 'Secure personal documents: Keep your original Aadhaar, PAN card, educational degrees, and passport in a safe spot.', checked: false },
  { id: 4, text: 'Digital privacy hygiene: Enable app PIN lock, biometric login, and hide preview banners for dating & queer apps.', checked: true },
  { id: 5, text: 'Mental health readiness: Have contact numbers for Tele-MANAS (14416) or a queer-affirmative counselor saved.', checked: true }
])

const activeResource = () => {
  return props.resources.find(r => r.id === activeLawId.value) || props.resources[0]
}

const copyChecklist = () => {
  const text = safetyChecklist.value
    .map(item => `[${item.checked ? 'X' : ' '}] ${item.text}`)
    .join('\n')
  navigator.clipboard?.writeText(text)
  showToast('Coming-Out Safety Checklist copied to clipboard! 📋')
}

const showToast = (msg) => {
  toastMessage.value = msg
  setTimeout(() => {
    toastMessage.value = ''
  }, 3500)
}
</script>

<template>
  <div class="legal-hub-layout">
    <!-- Header Banner -->
    <div class="legal-hero glass-panel pride-border">
      <div class="hero-text">
        <span class="badge badge-tag">Know Your Constitutional Rights</span>
        <h2>India LGBTQ+ Legal & Education Hub</h2>
        <p>
          Authoritative legal clarity on decriminalization, transgender statutory rights, workplace protections, and partnership benefits under Indian law.
        </p>
      </div>

      <div class="hero-metric">
        <div class="metric-num">Article 21</div>
        <div class="metric-label">Right to Privacy & Autonomy</div>
      </div>
    </div>

    <!-- Main Grid -->
    <div class="legal-grid">
      <!-- Landmark Judgments & Laws Navigator -->
      <div class="laws-navigator">
        <h3>Statutes & Judgments</h3>
        <div class="laws-list">
          <button 
            v-for="law in resources" 
            :key="law.id"
            :class="['law-item-btn', 'glass-panel', { active: activeLawId === law.id }]"
            @click="activeLawId = law.id"
          >
            <div class="law-btn-meta">
              <span class="badge badge-verified">{{ law.category }}</span>
              <span class="law-year">{{ law.year }}</span>
            </div>
            <h4 class="law-title">{{ law.title }}</h4>
          </button>
        </div>
      </div>

      <!-- Law Detail Viewer -->
      <div class="law-detail-card glass-panel">
        <div class="detail-header">
          <div class="detail-badge-row">
            <span class="badge badge-tag">{{ activeResource().category }}</span>
            <span class="law-year-tag">{{ activeResource().year }}</span>
          </div>
          <h3>{{ activeResource().title }}</h3>
          <p class="summary-text">{{ activeResource().summary }}</p>
        </div>

        <div class="key-rights-box">
          <h4>Key Rights Guaranteed by Law</h4>
          <div class="rights-list">
            <div v-for="(right, idx) in activeResource().keyRights" :key="idx" class="right-bullet">
              <span class="bullet-icon">⚖️</span>
              <p>{{ right }}</p>
            </div>
          </div>
        </div>

        <div class="practical-application">
          <h4>💡 Practical Guidance for Citizens</h4>
          <div class="practical-tips">
            <div class="tip-card">
              <strong>If Police Confront You:</strong>
              <p>Politely remind them that Section 377 IPC has been read down for consenting adults. Under law, they cannot demand mobile phone inspection without an official FIR.</p>
            </div>
            <div class="tip-card">
              <strong>At Financial Institutions:</strong>
              <p>RBI directives permit same-sex partners to open joint accounts under 'Either or Survivor' mode and nominate each other for deposits and fixed deposits.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Safety Checklist Section -->
    <section class="safety-checklist-card glass-panel">
      <div class="checklist-header">
        <div>
          <span class="badge badge-warning">Essential Precaution</span>
          <h3>Coming Out Safety & Independence Checklist</h3>
          <p>Carefully review these safeguards before sharing your identity in non-affirming or traditional households.</p>
        </div>

        <button class="btn-secondary" @click="copyChecklist">
          📋 Copy Checklist
        </button>
      </div>

      <div class="checklist-items">
        <label 
          v-for="item in safetyChecklist" 
          :key="item.id" 
          :class="['checklist-row', { done: item.checked }]"
        >
          <input type="checkbox" v-model="item.checked" />
          <span>{{ item.text }}</span>
        </label>
      </div>
    </section>

    <!-- Toast Notification -->
    <div v-if="toastMessage" class="toast-popup animate-fade-in">
      {{ toastMessage }}
    </div>
  </div>
</template>

<style scoped>
.legal-hub-layout {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px 20px 60px;
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.legal-hero {
  padding: 28px;
  border-radius: var(--radius-lg);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, rgba(20, 24, 40, 0.9), rgba(30, 20, 48, 0.8));
  flex-wrap: wrap;
  gap: 20px;
}

.hero-text h2 {
  font-size: 1.8rem;
  font-weight: 800;
  margin: 6px 0;
  background: var(--gradient-pride);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-text p {
  color: var(--text-secondary);
  font-size: 0.95rem;
  max-width: 700px;
}

.hero-metric {
  background: rgba(168, 85, 247, 0.1);
  border: 1px solid rgba(168, 85, 247, 0.3);
  padding: 16px 24px;
  border-radius: var(--radius-md);
  text-align: center;
}

.metric-num {
  font-size: 1.6rem;
  font-weight: 800;
  color: #c084fc;
}

.metric-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Grid */
.legal-grid {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 24px;
}

.laws-navigator h3 {
  font-size: 1.2rem;
  margin-bottom: 14px;
  color: #fff;
}

.laws-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.law-item-btn {
  padding: 16px;
  border-radius: var(--radius-md);
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 8px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.law-item-btn:hover {
  background: var(--bg-card-hover);
  border-color: rgba(168, 85, 247, 0.3);
}

.law-item-btn.active {
  border-color: #38bdf8;
  background: rgba(14, 165, 233, 0.12);
  box-shadow: 0 0 16px rgba(14, 165, 233, 0.2);
}

.law-btn-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.law-year {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.law-title {
  font-size: 0.95rem;
  color: #f1f5f9;
  font-weight: 600;
  line-height: 1.4;
}

/* Detail Card */
.law-detail-card {
  padding: 28px;
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-badge-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.law-year-tag {
  font-size: 0.75rem;
  color: #94a3b8;
}

.detail-header h3 {
  font-size: 1.45rem;
  font-weight: 800;
  color: #fff;
  margin-bottom: 8px;
}

.summary-text {
  font-size: 0.95rem;
  color: #cbd5e1;
  line-height: 1.6;
}

.key-rights-box h4, .practical-application h4 {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 12px;
  color: #e2e8f0;
}

.rights-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.right-bullet {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: rgba(255, 255, 255, 0.03);
  padding: 12px 16px;
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.bullet-icon {
  font-size: 1.1rem;
  margin-top: 2px;
}

.right-bullet p {
  font-size: 0.9rem;
  color: #f1f5f9;
  line-height: 1.5;
}

.practical-tips {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.tip-card {
  background: rgba(168, 85, 247, 0.07);
  border: 1px solid rgba(168, 85, 247, 0.2);
  padding: 14px;
  border-radius: var(--radius-md);
}

.tip-card strong {
  display: block;
  font-size: 0.85rem;
  color: #d8b4fe;
  margin-bottom: 4px;
}

.tip-card p {
  font-size: 0.82rem;
  color: #cbd5e1;
  line-height: 1.5;
}

/* Checklist */
.safety-checklist-card {
  padding: 28px;
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.checklist-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 14px;
}

.checklist-header h3 {
  font-size: 1.35rem;
  font-weight: 700;
  margin-top: 4px;
}

.checklist-header p {
  font-size: 0.88rem;
  color: var(--text-secondary);
}

.checklist-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.checklist-row {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.03);
  padding: 12px 18px;
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.05);
  font-size: 0.9rem;
  color: #e2e8f0;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.checklist-row:hover {
  background: rgba(255, 255, 255, 0.06);
}

.checklist-row.done span {
  color: #94a3b8;
  text-decoration: line-through;
}

.toast-popup {
  position: fixed;
  bottom: 24px;
  right: 24px;
  background: #1e1b4b;
  border: 1px solid #818cf8;
  color: #e0e7ff;
  padding: 12px 20px;
  border-radius: var(--radius-md);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
  font-size: 0.9rem;
  font-weight: 500;
  z-index: 3000;
}

@media (max-width: 900px) {
  .legal-grid {
    grid-template-columns: 1fr;
  }
  .practical-tips {
    grid-template-columns: 1fr;
  }
}
</style>
