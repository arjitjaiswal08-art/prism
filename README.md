# 🌈 Prism — Safe & Empowering LGBTQ+ Community Platform

> **A safe, private, and empowering sanctuary for LGBTQ+ individuals across Tier 1, 2, and 3 India.**  
> *"Reddit + Discord + Practo + Google Maps (Safe Spaces)" — built with privacy-first engineering.*

---

## 🚀 Key Features Implemented in MVP

### 🟢 1. Anonymous Social Feed
- **100% Pseudonymous:** Post without revealing real name, email, or phone numbers.
- **Categorized Tags:** `#ComingOut`, `#MentalHealth`, `#TransPride`, `#Career`, `#Dating`, `#LegalHelp`, `#QueerJoy`.
- **Sensitive Content Shield:** Content Warning (CW) toggles that blur sensitive posts until safely revealed by the user.
- **Engaging Interactions:** Upvoting, downvoting, bookmarking, and nested anonymous comment threads.
- **Celebration Effects:** Canvas confetti pride celebration triggers.

### 🟢 2. Verified Safe Spaces Map (Interactive Leaflet Map)
- **Interactive Map:** Dark-styled CartoDB Leaflet map with custom emoji pins (☕ Cafes, 🏥 Clinics, 🧠 Therapists, 🤝 NGOs & Shelters).
- **City-Specific Zoom:** Delhi NCR, Mumbai, Bengaluru, Kolkata, Pune, Hyderabad, Chennai, and Tier 2/3 Towns.
- **Vetted Safety Amenities:** Checks for gender-neutral restrooms, discreet entrances, pride flag displays, and trained affirming staff.
- **Community Safety Audits:** Read real anonymous reviews and submit new ratings.
- **Community Crowdsourcing:** "Nominate a Safe Space" flow for expanding queer sanctuaries.

### 🟢 3. Emergency "Closet Mode" & Panic Calculator Disguise
- **Instant UI Disguise:** Hitting **`Esc`**, **`Ctrl+Shift+P`**, or clicking **`PANIC (Esc)`** immediately hides the entire platform and transforms it into a functional scientific Calculator.
- **Tab Disguise:** Changes the browser tab title to *"Calculator"* and swaps favicons.
- **Stealth Unlock:** Entering the master PIN (default: `1234`) and hitting `=` or clicking the secret header dot returns safely to Prism.

### 🟢 4. Safe Encrypted Chat Rooms
- **Group Circles & 1:1 DMs:** Specialized channels for College & Youth, Trans & Non-Binary, Workplace Pride, and 1:1 Encrypted sessions.
- **Screenshot Interception Alert:** Simulates Snapchat-style interception banners notifying all room members when a screenshot attempt is made.
- **Auto-Blur Sensitive Media & Messages:** Blur toggle protects against unexpected media or sensitive content.
- **Report & Shadow-Ban:** Moderation flag system to quarantine bad actors without confrontation.

### 🟢 5. Mental Health & 24/7 Crisis Support Hub
- **24/7 Verified Indian Helplines:** 1-click direct calling and number copying for:
  - **Tele-MANAS:** `14416` (National 24/7 Mental Health Helpline, Toll-Free)
  - **Vandrevala Foundation:** `+91 9999 666 555` (Queer-affirming crisis counseling)
  - **iCall (TISS):** `9152987821` (Psychosocial support)
  - **Sahodari Transgender Emergency Cell:** `1800 200 3802` (Abuse & violence defense)
  - **Naz Foundation:** `011 4057 0400`
- **Verified Affirming Therapists Directory:** Filter by sliding scale / student rates, online/offline consultation, and confidential booking flow.

### 🟢 6. SafeMode AI Assistant (The Differentiator)
- **Context-Aware Queer Support:** Coming-out scripts tailored for Indian family dynamics, legal guidance, and dysphoria grounding.
- **Interactive Box Breathing Tool (4-4-4-4):** Animated pulsing circle guide for de-escalating panic attacks and anxiety.

### 🟢 7. Legal & Education Hub (India Focus)
- **Section 377 Landmark Facts:** *Navtej Singh Johar (2018)* breakdown and police harassment defense.
- **Transgender Persons Act 2019 / Rules 2020:** Statutory identity certificate application process (transgender.dosje.gov.in).
- **Supreme Court Supriyo Guidelines:** Joint bank accounts under 'Either or Survivor' mode, gratuity/EPF nomination, and medical proxy rights.
- **Coming Out Safety & Independence Checklist:** Interactive checklist ensuring financial and physical security before coming out.

---

## 🛠️ Tech Stack

- **Frontend:** Vue 3 (Composition API) + Vite
- **Styling:** Custom CSS Design System with Pride gradients, glassmorphism, responsive tokens, and dark aesthetic
- **Map:** Leaflet.js with CartoDB Dark Matter tiles
- **Micro-interactions:** Canvas-Confetti, Hotkey event listeners, CSS keyframe animations
- **State Management:** Reactive Vue Composition Store with zero local data leakage

---

## 🏃 Quick Start Guide

### 1. Install Dependencies
```bash
npm install
```

### 2. Run Development Server
```bash
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

### 3. Build for Production
```bash
npm run build
```
The optimized production bundle will be generated in `dist/`.

---

## 🔐 Privacy & Security Guardrails
- **Zero Real Names / Identity Independence:** Users are given anonymous generated pseudonyms (`LavenderPhoenix`, `CosmicVoyager`).
- **No IP or Phone Logging:** No phone number verification required.
- **Instant Panic Trigger:** Keyboard shortcut `Esc` available on every screen.
- **Master PIN:** Default master code `1234` configured to restore from calculator disguise.
