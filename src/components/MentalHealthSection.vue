<script setup>
import { ref } from 'vue'

const props = defineProps({
  helplines: {
    type: Array,
    required: true
  },
  therapists: {
    type: Array,
    required: true
  }
})

const selectedTherapist = ref(null)
const showBookingModal = ref(false)
const bookingSuccess = ref(false)
const filterSlidingScaleOnly = ref(false)

// Booking form
const bookingDate = ref('2026-10-10')
const bookingTime = ref('16:00')
const bookingMode = ref('Google Meet (Confidential)')
const bookingName = ref('')
const bookingNotes = ref('')
const toastMessage = ref('')

const filteredTherapists = () => {
  if (filterSlidingScaleOnly.value) {
    return props.therapists.filter(t => t.slidingScale)
  }
  return props.therapists
}

const openBooking = (therapist) => {
  selectedTherapist.value = therapist
  bookingSuccess.value = false
  bookingName.value = ''
  bookingNotes.value = ''
  showBookingModal.value = true
}

const confirmBooking = () => {
  bookingSuccess.value = true
  setTimeout(() => {
    showBookingModal.value = false
    bookingSuccess.value = false
    showToast(`Appointment request sent to ${selectedTherapist.value.name}! You will receive encrypted meeting details.`)
  }, 2000)
}

const copyHelpline = (num, name) => {
  navigator.clipboard?.writeText(num)
  showToast(`Copied ${name} number: ${num}`)
}

const showToast = (msg) => {
  toastMessage.value = msg
  setTimeout(() => {
    toastMessage.value = ''
  }, 3500)
}
</script>

<template>
  <div class="mental-health-layout">
    <!-- SOS Emergency Crisis Banner -->
    <div class="crisis-sos-banner glass-panel">
      <div class="sos-icon-wrap">
        <span class="sos-icon">🚨</span>
      </div>
      <div class="sos-content">
        <div class="sos-badge-row">
          <span class="badge badge-crisis">Immediate Crisis Support</span>
          <span class="sos-hours">24/7 • Free • Confidential</span>
        </div>
        <h2>In Emotional Distress or Facing Harm? You Are Not Alone.</h2>
        <p>
          Trained counselors in India are on standby right now. You do not have to justify your identity.
        </p>
      </div>
      <div class="sos-action">
        <a href="tel:14416" class="btn-emergency">
          <span>📞</span> Call Tele-MANAS (14416)
        </a>
      </div>
    </div>

    <!-- Verified Helplines Grid -->
    <section class="helplines-section">
      <div class="section-title-wrap">
        <span class="badge badge-tag">Nationwide Network</span>
        <h3>Verified LGBTQ+ Affirming Helplines in India</h3>
      </div>

      <div class="helplines-grid">
        <div 
          v-for="line in helplines" 
          :key="line.name" 
          class="helpline-card glass-panel"
        >
          <div class="card-header">
            <span class="badge badge-verified">{{ line.type }}</span>
            <span v-if="line.tollFree" class="badge badge-accent">Toll Free</span>
          </div>

          <h4 class="helpline-name">{{ line.name }}</h4>
          <p class="helpline-desc">{{ line.description }}</p>

          <div class="helpline-meta">
            <div class="meta-item">
              <span class="meta-label">Hours:</span>
              <span class="meta-val">{{ line.hours }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Languages:</span>
              <span class="meta-val">{{ line.languages }}</span>
            </div>
          </div>

          <div class="helpline-actions">
            <a :href="`tel:${line.number.replace(/\s+/g, '')}`" class="btn-call-direct">
              📞 Call {{ line.number }}
            </a>
            <button class="btn-copy" @click="copyHelpline(line.number, line.name)" title="Copy Number">
              📋
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Verified Affirming Therapists Directory -->
    <section class="therapists-section">
      <div class="therapist-header-row">
        <div>
          <span class="badge badge-tag">Mental Health Care</span>
          <h3>Book Verified Queer-Affirmative Therapists</h3>
          <p class="section-subtitle">
            All practitioners are vetted against conversion therapy practices and trained in gender identity & relational diversity.
          </p>
        </div>

        <div class="filter-toggle-wrap">
          <label class="toggle-control">
            <input type="checkbox" v-model="filterSlidingScaleOnly" />
            <span>Show Sliding Scale / Student Rates Only</span>
          </label>
        </div>
      </div>

      <div class="therapists-grid">
        <div 
          v-for="therapist in filteredTherapists()" 
          :key="therapist.id" 
          class="therapist-card glass-panel"
        >
          <div class="therapist-top">
            <img :src="therapist.avatar" :alt="therapist.name" class="therapist-avatar" />
            <div class="therapist-info">
              <div class="therapist-name-row">
                <h4>{{ therapist.name }}</h4>
                <span class="rating-badge">★ {{ therapist.rating }}</span>
              </div>
              <p class="qualification">{{ therapist.qualification }}</p>
              <p class="experience">⏱️ {{ therapist.experience }}</p>
            </div>
          </div>

          <div class="specialties-wrap">
            <span v-for="spec in therapist.specialties" :key="spec" class="spec-chip">
              {{ spec }}
            </span>
          </div>

          <div class="therapist-footer">
            <div class="fee-meta">
              <span class="fee-text">{{ therapist.fee }}</span>
              <span v-if="therapist.slidingScale" class="sliding-badge">Sliding Scale Available</span>
              <span class="mode-text">📍 {{ therapist.mode }}</span>
            </div>

            <button class="btn-primary" @click="openBooking(therapist)">
              Book Confidential Session
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Booking Modal -->
    <div v-if="showBookingModal" class="modal-backdrop" @click.self="showBookingModal = false">
      <div class="modal-card glass-panel animate-fade-in">
        <div class="modal-header">
          <div>
            <span class="badge badge-verified">Confidential Healthcare Booking</span>
            <h3>Book with {{ selectedTherapist?.name }}</h3>
          </div>
          <button class="close-modal-btn" @click="showBookingModal = false">✕</button>
        </div>

        <div v-if="!bookingSuccess" class="modal-body">
          <div class="booking-summary-box">
            <div>
              <strong>Fee:</strong> {{ selectedTherapist?.fee }}
            </div>
            <div>
              <strong>Specialties:</strong> {{ selectedTherapist?.specialties.join(', ') }}
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Preferred Date</label>
              <input type="date" v-model="bookingDate" class="form-input" />
            </div>

            <div class="form-group">
              <label>Preferred Time Slot</label>
              <select v-model="bookingTime" class="form-input">
                <option value="11:00">11:00 AM – 12:00 PM</option>
                <option value="14:00">02:00 PM – 03:00 PM</option>
                <option value="16:00">04:00 PM – 05:00 PM</option>
                <option value="19:00">07:00 PM – 08:00 PM</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Session Mode</label>
            <select v-model="bookingMode" class="form-input">
              <option value="Google Meet (Confidential)">Confidential Google Meet (Encrypted)</option>
              <option value="Audio Call Only (No Camera)">Audio Call Only (Complete Anonymity)</option>
              <option value="In-Person Clinic">In-Person Clinic Consultation</option>
            </select>
          </div>

          <div class="form-group">
            <label>Name or Preferred Pseudonym</label>
            <input 
              type="text" 
              v-model="bookingName" 
              placeholder="e.g. Phoenix (legal name not mandatory)" 
              class="form-input" 
            />
          </div>

          <div class="form-group">
            <label>What would you like support with? (Optional & Confidential)</label>
            <textarea 
              v-model="bookingNotes" 
              rows="3" 
              placeholder="e.g. Coming out anxiety, gender dysphoria, navigating family relations..." 
              class="form-textarea"
            ></textarea>
          </div>

          <div class="privacy-disclaimer">
            🔒 <em>We do not share any details with third parties, parents, or employers. Total confidentiality guaranteed.</em>
          </div>
        </div>

        <div v-else class="booking-success-view">
          <span class="success-icon">✨</span>
          <h3>Consultation Requested!</h3>
          <p>Your session request with {{ selectedTherapist?.name }} has been encrypted and submitted.</p>
        </div>

        <div v-if="!bookingSuccess" class="modal-footer">
          <button class="btn-secondary" @click="showBookingModal = false">Cancel</button>
          <button class="btn-primary" :disabled="!bookingName.trim()" @click="confirmBooking">
            Confirm & Send Request
          </button>
        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <div v-if="toastMessage" class="toast-popup animate-fade-in">
      {{ toastMessage }}
    </div>
  </div>
</template>

<style scoped>
.mental-health-layout {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px 20px 60px;
  display: flex;
  flex-direction: column;
  gap: 36px;
}

/* SOS Banner */
.crisis-sos-banner {
  background: linear-gradient(135deg, rgba(185, 28, 28, 0.4), rgba(30, 20, 40, 0.85));
  border: 1px solid rgba(239, 68, 68, 0.4);
  border-radius: var(--radius-lg);
  padding: 28px;
  display: flex;
  align-items: center;
  gap: 24px;
  box-shadow: 0 10px 30px rgba(239, 68, 68, 0.2);
  flex-wrap: wrap;
}

.sos-icon-wrap {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
}

.sos-content {
  flex: 1;
  min-width: 280px;
}

.sos-badge-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.sos-hours {
  font-size: 0.75rem;
  color: #fca5a5;
  font-weight: 600;
}

.sos-content h2 {
  font-size: 1.5rem;
  font-weight: 800;
  color: #fff;
  margin-bottom: 4px;
}

.sos-content p {
  color: #fecaca;
  font-size: 0.92rem;
}

.btn-emergency {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: #fff;
  padding: 12px 24px;
  border-radius: var(--radius-md);
  font-size: 1rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 4px 18px rgba(239, 68, 68, 0.5);
  transition: transform var(--transition-fast);
}
.btn-emergency:hover {
  transform: translateY(-2px);
}

/* Helplines Grid */
.section-title-wrap {
  margin-bottom: 20px;
}

.section-title-wrap h3 {
  font-size: 1.5rem;
  font-weight: 800;
  color: #fff;
  margin-top: 4px;
}

.helplines-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(310px, 1fr));
  gap: 20px;
}

.helpline-card {
  padding: 22px;
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  gap: 12px;
  border: 1px solid var(--border-light);
  transition: transform var(--transition-fast), border-color var(--transition-fast);
}
.helpline-card:hover {
  transform: translateY(-2px);
  border-color: rgba(168, 85, 247, 0.4);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.helpline-name {
  font-size: 1.15rem;
  font-weight: 700;
  color: #fff;
}

.helpline-desc {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.5;
  flex: 1;
}

.helpline-meta {
  background: rgba(255, 255, 255, 0.03);
  padding: 10px 12px;
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.78rem;
}

.meta-item {
  display: flex;
  justify-content: space-between;
}

.meta-label {
  color: var(--text-muted);
}
.meta-val {
  color: #e2e8f0;
  font-weight: 500;
}

.helpline-actions {
  display: flex;
  gap: 8px;
  margin-top: 6px;
}

.btn-call-direct {
  flex: 1;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #34d399;
  padding: 8px 14px;
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.btn-call-direct:hover {
  background: #10b981;
  color: #fff;
}

.btn-copy {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-light);
  color: #cbd5e1;
  padding: 8px 12px;
  border-radius: var(--radius-md);
}

/* Therapists Directory */
.therapist-header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 22px;
  flex-wrap: wrap;
  gap: 16px;
}

.therapist-header-row h3 {
  font-size: 1.5rem;
  font-weight: 800;
  margin-top: 4px;
}

.section-subtitle {
  font-size: 0.9rem;
  color: var(--text-secondary);
  max-width: 650px;
}

.toggle-control {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #c084fc;
  cursor: pointer;
}

.therapists-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: 24px;
}

.therapist-card {
  padding: 24px;
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  gap: 16px;
  border: 1px solid var(--border-light);
}

.therapist-top {
  display: flex;
  gap: 16px;
}

.therapist-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(168, 85, 247, 0.4);
}

.therapist-info {
  flex: 1;
}

.therapist-name-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.therapist-name-row h4 {
  font-size: 1.15rem;
  font-weight: 700;
  color: #fff;
}

.rating-badge {
  font-size: 0.8rem;
  color: #fbbf24;
  font-weight: 700;
}

.qualification {
  font-size: 0.82rem;
  color: var(--text-secondary);
  margin-top: 2px;
}

.experience {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-top: 2px;
}

.specialties-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.spec-chip {
  background: rgba(168, 85, 247, 0.12);
  border: 1px solid rgba(168, 85, 247, 0.25);
  color: #d8b4fe;
  font-size: 0.75rem;
  padding: 3px 8px;
  border-radius: var(--radius-full);
}

.therapist-footer {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: auto;
  padding-top: 14px;
  border-top: 1px solid var(--border-light);
}

.fee-meta {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.fee-text {
  font-size: 1rem;
  font-weight: 700;
  color: #fff;
}

.sliding-badge {
  font-size: 0.72rem;
  color: #34d399;
  font-weight: 600;
}

.mode-text {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Modals */
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
  max-width: 540px;
  background: #121422;
  border: 1px solid rgba(168, 85, 247, 0.3);
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.booking-summary-box {
  background: rgba(255, 255, 255, 0.04);
  padding: 12px 16px;
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  color: var(--text-secondary);
  display: flex;
  flex-direction: column;
  gap: 4px;
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-input, .form-textarea {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 10px 14px;
  color: #fff;
  font-size: 0.9rem;
  outline: none;
}
.form-input option {
  background: #121422;
}

.privacy-disclaimer {
  font-size: 0.78rem;
  color: #94a3b8;
  background: rgba(16, 185, 129, 0.08);
  padding: 8px 12px;
  border-radius: var(--radius-md);
  border-left: 3px solid #10b981;
}

.booking-success-view {
  text-align: center;
  padding: 30px 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.success-icon {
  font-size: 3rem;
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
</style>
