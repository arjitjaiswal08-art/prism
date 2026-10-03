<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import L from 'leaflet'

const props = defineProps({
  spaces: {
    type: Array,
    required: true
  },
  selectedCity: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['addSpace', 'addReview', 'update:selectedCity'])

const activeCategory = ref('all')
const searchQuery = ref('')
const selectedSpace = ref(null)
const showReviewModal = ref(false)
const showNominateModal = ref(false)
const showApiSettingsModal = ref(false)

// Map Providers & API Keys
// Check localStorage or Vite environment variable
const storedProvider = localStorage.getItem('prism_map_provider') || 'esri-dark'
const storedGmapsKey = localStorage.getItem('prism_gmaps_api_key') || import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ''
const storedCartoKey = localStorage.getItem('prism_carto_api_key') || ''

const currentProvider = ref(storedProvider)
const gmapsApiKey = ref(storedGmapsKey)
const cartoApiKey = ref(storedCartoKey)

const mapContainer = ref(null)
const gmapsContainer = ref(null)
let leafletMap = null
let leafletTileLayer = null
let leafletLabelsLayer = null
let markersLayer = null

// Google Maps instances
let gmapInstance = null
let gmapMarkers = []
let activeInfoWindow = null

// New Review Form
const newReviewRating = ref(5)
const newReviewText = ref('')
const newReviewAuthor = ref('Anon_Visitor')

// Nominate Form
const nominateName = ref('')
const nominateCategory = ref('Cafe')
const nominateCity = ref('Delhi NCR')
const nominateAddress = ref('')
const nominateReason = ref('')
const toastMessage = ref('')

const categories = [
  { id: 'all', label: 'All Safe Spaces', icon: '✨' },
  { id: 'Cafe', label: 'Cafes & Hangouts', icon: '☕' },
  { id: 'Clinic', label: 'Affirming Clinics', icon: '🏥' },
  { id: 'Therapist', label: 'Therapists & Psych', icon: '🧠' },
  { id: 'NGO', label: 'NGOs & Shelters', icon: '🤝' }
]

const cityCoordinates = {
  'All India': { center: [20.5937, 78.9629], zoom: 5 },
  'Delhi NCR': { center: [28.6139, 77.2090], zoom: 12 },
  'Mumbai': { center: [19.0760, 72.8777], zoom: 12 },
  'Bengaluru': { center: [12.9716, 77.5946], zoom: 12 },
  'Kolkata': { center: [22.5726, 88.3639], zoom: 12 },
  'Pune': { center: [18.5204, 73.8567], zoom: 12 },
  'Hyderabad': { center: [17.3850, 78.4867], zoom: 12 },
  'Chennai': { center: [13.0827, 80.2707], zoom: 12 },
  'Tier 2 / Tier 3 Towns': { center: [22.0, 79.0], zoom: 6 }
}

const filteredSpaces = computed(() => {
  return props.spaces.filter(space => {
    const categoryMatch = activeCategory.value === 'all' || space.category === activeCategory.value
    const cityMatch = props.selectedCity === 'All India' || space.city === props.selectedCity
    const query = searchQuery.value.toLowerCase().trim()
    const searchMatch = !query || 
      space.name.toLowerCase().includes(query) || 
      space.neighborhood.toLowerCase().includes(query) ||
      space.amenities.some(a => a.toLowerCase().includes(query))

    return categoryMatch && cityMatch && searchMatch
  })
})

// Provider URLs
const getLeafletTileConfig = () => {
  if (currentProvider.value === 'osm') {
    return {
      url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
      options: {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 19
      }
    }
  }

  if (currentProvider.value === 'carto' && cartoApiKey.value) {
    return {
      url: `https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png?api_key=${cartoApiKey.value}`,
      options: {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 19
      }
    }
  }

  // Default: ESRI Dark Canvas (100% Free, High Res, Zero Watermark & No Key Required)
  return {
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
    labelsUrl: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}',
    options: {
      attribution: '&copy; Esri &copy; OpenStreetMap',
      maxZoom: 16
    }
  }
}

// Leaflet Map Initialization
const initLeafletMap = () => {
  if (!mapContainer.value) return
  if (leafletMap) {
    leafletMap.remove()
    leafletMap = null
  }

  const cityConfig = cityCoordinates[props.selectedCity] || cityCoordinates['All India']

  leafletMap = L.map(mapContainer.value, {
    center: cityConfig.center,
    zoom: cityConfig.zoom,
    zoomControl: true
  })

  const tileConfig = getLeafletTileConfig()
  leafletTileLayer = L.tileLayer(tileConfig.url, tileConfig.options).addTo(leafletMap)

  if (tileConfig.labelsUrl) {
    leafletLabelsLayer = L.tileLayer(tileConfig.labelsUrl, { maxZoom: 16, pane: 'shadowPane' }).addTo(leafletMap)
  }

  markersLayer = L.layerGroup().addTo(leafletMap)
  updateLeafletMarkers()
}

const getCategoryIconHtml = (category) => {
  const iconMap = {
    'Cafe': '☕',
    'Clinic': '🏥',
    'Therapist': '🧠',
    'NGO': '🤝'
  }
  const emoji = iconMap[category] || '🌈'
  return `<div class="custom-map-pin"><span class="pin-emoji">${emoji}</span><div class="pin-glow"></div></div>`
}

const updateLeafletMarkers = () => {
  if (!markersLayer || !leafletMap) return
  markersLayer.clearLayers()

  const bounds = []

  filteredSpaces.value.forEach(space => {
    if (space.lat && space.lng) {
      bounds.push([space.lat, space.lng])

      const icon = L.divIcon({
        className: 'custom-leaflet-marker',
        html: getCategoryIconHtml(space.category),
        iconSize: [38, 38],
        iconAnchor: [19, 38],
        popupAnchor: [0, -38]
      })

      const marker = L.marker([space.lat, space.lng], { icon })
      
      const popupHtml = `
        <div style="font-family: inherit;">
          <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
            <span style="background: rgba(16, 185, 129, 0.2); color: #34d399; font-size: 11px; padding: 2px 6px; border-radius: 99px; font-weight: 600;">✓ Verified</span>
            <span style="font-size: 11px; color: #fbbf24;">★ ${space.rating}</span>
          </div>
          <h4 style="font-size: 14px; margin: 0 0 4px 0; color: #fff; font-weight: 700;">${space.name}</h4>
          <p style="font-size: 12px; color: #cbd5e1; margin: 0 0 6px 0;">📍 ${space.neighborhood}, ${space.city}</p>
          <div style="font-size: 11px; color: #94a3b8; margin-bottom: 8px;">${space.amenities.slice(0, 2).join(' • ')}</div>
          <button id="pin-view-${space.id}" style="background: linear-gradient(135deg, #ec4899, #8b5cf6); color: white; border: none; border-radius: 6px; padding: 4px 10px; font-size: 11px; font-weight: 600; cursor: pointer; width: 100%;">
            View Safe Space Details
          </button>
        </div>
      `
      
      marker.bindPopup(popupHtml)
      marker.on('popupopen', () => {
        const btn = document.getElementById(`pin-view-${space.id}`)
        if (btn) {
          btn.onclick = () => {
            selectedSpace.value = space
          }
        }
      })

      marker.addTo(markersLayer)
    }
  })

  if (bounds.length > 0 && props.selectedCity === 'All India') {
    leafletMap.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 })
  } else {
    const config = cityCoordinates[props.selectedCity] || cityCoordinates['All India']
    leafletMap.setView(config.center, config.zoom)
  }
}

// Google Maps API Loader & Integration
const darkGmapStyle = [
  { elementType: "geometry", stylers: [{ color: "#161928" }] },
  { elementType: "labels.text.stroke", stylers: [{ color: "#161928" }] },
  { elementType: "labels.text.fill", stylers: [{ color: "#8a94a6" }] },
  { featureType: "administrative.locality", elementType: "labels.text.fill", stylers: [{ color: "#c084fc" }] },
  { featureType: "poi", elementType: "labels.text.fill", stylers: [{ color: "#94a3b8" }] },
  { featureType: "poi.park", elementType: "geometry", stylers: [{ color: "#122026" }] },
  { featureType: "road", elementType: "geometry", stylers: [{ color: "#252b44" }] },
  { featureType: "road", elementType: "geometry.stroke", stylers: [{ color: "#1b1f33" }] },
  { featureType: "road.highway", elementType: "geometry", stylers: [{ color: "#363f63" }] },
  { featureType: "transit", elementType: "geometry", stylers: [{ color: "#1f2438" }] },
  { featureType: "water", elementType: "geometry", stylers: [{ color: "#0c0e18" }] },
  { featureType: "water", elementType: "labels.text.fill", stylers: [{ color: "#38bdf8" }] }
]

const loadGoogleMapsScript = (apiKey) => {
  return new Promise((resolve, reject) => {
    if (window.google && window.google.maps) {
      resolve(window.google.maps)
      return
    }

    const existingScript = document.getElementById('google-maps-script')
    if (existingScript) {
      existingScript.remove()
    }

    const script = document.createElement('script')
    script.id = 'google-maps-script'
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places`
    script.async = true
    script.defer = true
    script.onload = () => resolve(window.google.maps)
    script.onerror = (err) => reject(err)
    document.head.appendChild(script)
  })
}

const initGoogleMap = async () => {
  if (!gmapsApiKey.value) {
    showToast('Please enter your Google Maps API Key or switch to Free Dark Canvas')
    return
  }

  try {
    const maps = await loadGoogleMapsScript(gmapsApiKey.value)
    if (!gmapsContainer.value) return

    const cityConfig = cityCoordinates[props.selectedCity] || cityCoordinates['All India']

    gmapInstance = new maps.Map(gmapsContainer.value, {
      center: { lat: cityConfig.center[0], lng: cityConfig.center[1] },
      zoom: cityConfig.zoom,
      styles: darkGmapStyle,
      disableDefaultUI: false,
      zoomControl: true,
      mapTypeControl: false,
      streetViewControl: false
    })

    activeInfoWindow = new maps.InfoWindow()
    updateGoogleMapMarkers()
  } catch (err) {
    console.error('Google Maps API failed to load:', err)
    showToast('Failed to load Google Maps. Switching to Free Dark Canvas fallback.')
    currentProvider.value = 'esri-dark'
    initLeafletMap()
  }
}

const updateGoogleMapMarkers = () => {
  if (!gmapInstance || !window.google) return

  // Clear existing markers
  gmapMarkers.forEach(m => m.setMap(null))
  gmapMarkers = []

  const bounds = new window.google.maps.LatLngBounds()

  filteredSpaces.value.forEach(space => {
    if (space.lat && space.lng) {
      const position = { lat: space.lat, lng: space.lng }
      bounds.extend(position)

      const marker = new window.google.maps.Marker({
        position,
        map: gmapInstance,
        title: space.name,
        icon: {
          url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
            <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 36 36">
              <circle cx="18" cy="18" r="16" fill="#181c2e" stroke="#c084fc" stroke-width="2"/>
              <text x="18" y="24" font-size="16" text-anchor="middle">🌈</text>
            </svg>
          `),
          scaledSize: new window.google.maps.Size(36, 36)
        }
      })

      marker.addListener('click', () => {
        selectedSpace.value = space
        const content = `
          <div style="color: #0f172a; padding: 6px; font-family: sans-serif;">
            <div style="font-weight: 700; font-size: 14px; margin-bottom: 2px;">${space.name}</div>
            <div style="font-size: 12px; color: #475569;">📍 ${space.neighborhood}, ${space.city}</div>
            <div style="color: #d97706; font-size: 11px; margin-top: 4px;">★ ${space.rating} (Community Verified)</div>
          </div>
        `
        activeInfoWindow.setContent(content)
        activeInfoWindow.open(gmapInstance, marker)
      })

      gmapMarkers.push(marker)
    }
  })

  if (filteredSpaces.value.length > 0) {
    if (props.selectedCity === 'All India') {
      gmapInstance.fitBounds(bounds)
    } else {
      const cityConfig = cityCoordinates[props.selectedCity] || cityCoordinates['All India']
      gmapInstance.setCenter({ lat: cityConfig.center[0], lng: cityConfig.center[1] })
      gmapInstance.setZoom(cityConfig.zoom)
    }
  }
}

const focusSpaceOnMap = (space) => {
  selectedSpace.value = space

  if (currentProvider.value === 'google' && gmapInstance && space.lat && space.lng) {
    gmapInstance.panTo({ lat: space.lat, lng: space.lng })
    gmapInstance.setZoom(15)
  } else if (leafletMap && space.lat && space.lng) {
    leafletMap.flyTo([space.lat, space.lng], 15, { duration: 1.2 })
  }
}

// Master Render Method
const renderCurrentMap = () => {
  nextTick(() => {
    if (currentProvider.value === 'google' && gmapsApiKey.value) {
      initGoogleMap()
    } else {
      initLeafletMap()
    }
  })
}

const saveApiSettings = () => {
  localStorage.setItem('prism_map_provider', currentProvider.value)
  if (gmapsApiKey.value) {
    localStorage.setItem('prism_gmaps_api_key', gmapsApiKey.value.trim())
  }
  if (cartoApiKey.value) {
    localStorage.setItem('prism_carto_api_key', cartoApiKey.value.trim())
  }

  showApiSettingsModal.value = false
  showToast(`Map updated to ${providerLabels[currentProvider.value] || 'Selected Provider'}!`)
  renderCurrentMap()
}

const providerLabels = {
  'esri-dark': 'Dark Canvas (Free • No Key Required)',
  'google': 'Google Maps JavaScript API',
  'osm': 'OpenStreetMap Standard (Free)',
  'carto': 'CartoDB Dark Matter (API Key)'
}

watch(() => props.selectedCity, () => {
  if (currentProvider.value === 'google') {
    const cityConfig = cityCoordinates[props.selectedCity] || cityCoordinates['All India']
    if (gmapInstance) {
      gmapInstance.setCenter({ lat: cityConfig.center[0], lng: cityConfig.center[1] })
      gmapInstance.setZoom(cityConfig.zoom)
    }
  } else {
    const config = cityCoordinates[props.selectedCity] || cityCoordinates['All India']
    if (leafletMap) {
      leafletMap.setView(config.center, config.zoom)
      updateLeafletMarkers()
    }
  }
})

watch([filteredSpaces, activeCategory], () => {
  nextTick(() => {
    if (currentProvider.value === 'google') {
      updateGoogleMapMarkers()
    } else {
      updateLeafletMarkers()
    }
  })
})

onMounted(() => {
  renderCurrentMap()
  if (filteredSpaces.value.length > 0) {
    selectedSpace.value = filteredSpaces.value[0]
  }
})

const submitReview = () => {
  if (!newReviewText.value.trim() || !selectedSpace.value) return

  const review = {
    user: newReviewAuthor.value.trim() || 'Anon_Visitor',
    rating: Number(newReviewRating.value),
    text: newReviewText.value.trim()
  }

  emit('addReview', { spaceId: selectedSpace.value.id, review })
  selectedSpace.value.reviews.unshift(review)
  selectedSpace.value.reviewsCount += 1

  newReviewText.value = ''
  showReviewModal.value = false
  showToast('Safety audit recorded anonymously! 🛡️')
}

const submitNomination = () => {
  if (!nominateName.value.trim() || !nominateAddress.value.trim()) return

  emit('addSpace', {
    id: 'space-' + Date.now(),
    name: nominateName.value.trim(),
    category: nominateCategory.value,
    city: nominateCity.value,
    neighborhood: nominateAddress.value.split(',')[0] || nominateAddress.value,
    lat: 28.6139 + (Math.random() - 0.5) * 0.1,
    lng: 77.2090 + (Math.random() - 0.5) * 0.1,
    rating: 5.0,
    reviewsCount: 1,
    verifiedBadge: true,
    amenities: ['Community Nominated', 'Safe Haven', 'Affirming Atmosphere'],
    contact: '+91 Available on Visit',
    hours: '10:00 AM – 8:00 PM',
    description: nominateReason.value.trim() || 'Community-recommended safe space for queer individuals.',
    reviews: [
      { user: 'CommunityMember', rating: 5, text: nominateReason.value.trim() || 'Recommended safe sanctuary.' }
    ]
  })

  nominateName.value = ''
  nominateAddress.value = ''
  nominateReason.value = ''
  showNominateModal.value = false
  showToast('Space submitted! Added to community map. 🌈')
}

const showToast = (msg) => {
  toastMessage.value = msg
  setTimeout(() => {
    toastMessage.value = ''
  }, 3500)
}
</script>

<template>
  <div class="safe-spaces-layout">
    <!-- Top Action Bar -->
    <div class="spaces-header glass-panel">
      <div class="header-info">
        <div class="title-row">
          <span class="badge badge-verified">🛡️ Community Verified Directory</span>
          <h2>Verified Safe Spaces Map</h2>
        </div>
        <p>
          Discover verified queer-affirming cafes, clinics, therapists, and crisis shelters across Indian cities.
        </p>
      </div>

      <div class="header-actions">
        <!-- Maps API Switcher Button -->
        <button class="btn-secondary" @click="showApiSettingsModal = true" title="Configure Map API (Google Maps / Free Dark Canvas)">
          <span>🗺️</span> Maps API Settings
        </button>
        <button class="btn-primary" @click="showNominateModal = true">
          <span>➕</span> Nominate a Safe Space
        </button>
      </div>
    </div>

    <!-- Category Filter Tabs & Search -->
    <div class="category-filter-row">
      <div class="category-buttons">
        <button 
          v-for="cat in categories" 
          :key="cat.id"
          :class="['cat-btn', { active: activeCategory === cat.id }]"
          @click="activeCategory = cat.id"
        >
          <span>{{ cat.icon }}</span>
          <span>{{ cat.label }}</span>
        </button>
      </div>

      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Filter by name, neighborhood, amenities..." 
          class="search-input"
        />
      </div>
    </div>

    <!-- Map & Details Grid -->
    <div class="map-grid">
      <!-- Map Viewport Container -->
      <div class="map-viewport-card glass-panel">
        <!-- Floating City Jump Bar & API Indicator -->
        <div class="map-floating-bar">
          <div class="city-jump-cluster">
            <span class="pill-label">City:</span>
            <button 
              v-for="city in ['Delhi NCR', 'Mumbai', 'Bengaluru', 'Kolkata', 'Pune', 'Hyderabad']"
              :key="city"
              :class="['city-jump-btn', { active: selectedCity === city }]"
              @click="$emit('update:selectedCity', city)"
            >
              {{ city }}
            </button>
          </div>

          <button class="api-status-badge" @click="showApiSettingsModal = true">
            <span class="api-dot"></span>
            <span>{{ currentProvider === 'google' ? 'Google Maps API' : 'Dark Canvas (No Key)' }}</span>
            <span class="api-gear">⚙️</span>
          </button>
        </div>

        <!-- Google Map Container (when Google Maps mode is active) -->
        <div 
          v-if="currentProvider === 'google'" 
          ref="gmapsContainer" 
          class="gmaps-wrapper"
        ></div>

        <!-- Leaflet Map Container (Default / Fallback Free) -->
        <div 
          v-else 
          ref="mapContainer" 
          class="leaflet-map-wrapper"
        ></div>
      </div>

      <!-- Spaces Directory Sidebar -->
      <div class="spaces-directory-col">
        <div class="directory-header">
          <span class="results-count">
            Found <strong>{{ filteredSpaces.length }}</strong> safe locations
          </span>
          <span class="audit-note">All vetted for zero harassment</span>
        </div>

        <div class="spaces-scroll-list">
          <div 
            v-for="space in filteredSpaces" 
            :key="space.id"
            :class="['space-card', 'glass-panel', { selected: selectedSpace?.id === space.id }]"
            @click="focusSpaceOnMap(space)"
          >
            <div class="space-card-top">
              <span class="space-category-pill">
                {{ space.category }}
              </span>
              <div class="space-rating">
                <span class="star">★</span>
                <strong>{{ space.rating }}</strong>
                <span class="reviews-num">({{ space.reviewsCount }})</span>
              </div>
            </div>

            <h3 class="space-name">{{ space.name }}</h3>
            <p class="space-location">📍 {{ space.neighborhood }}, {{ space.city }}</p>

            <div class="amenities-tags">
              <span 
                v-for="amenity in space.amenities.slice(0, 3)" 
                :key="amenity" 
                class="amenity-chip"
              >
                ✓ {{ amenity }}
              </span>
              <span v-if="space.amenities.length > 3" class="amenity-chip more">
                +{{ space.amenities.length - 3 }} more
              </span>
            </div>

            <p class="space-snippet">{{ space.description }}</p>

            <div class="space-card-footer">
              <button class="btn-secondary btn-sm" @click.stop="focusSpaceOnMap(space)">
                Focus on Map
              </button>
              <a 
                :href="`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(space.name + ' ' + space.city)}`" 
                target="_blank" 
                rel="noopener"
                class="directions-link"
                @click.stop
              >
                🗺️ Google Maps ↗
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Selected Safe Space Deep Dive Dock -->
    <div v-if="selectedSpace" class="space-details-dock glass-panel animate-fade-in">
      <div class="dock-header">
        <div class="dock-title-group">
          <div class="dock-badge-row">
            <span class="badge badge-verified">✓ Verified Community Safe Space</span>
            <span class="badge badge-tag">{{ selectedSpace.category }}</span>
            <span class="space-rating-score">★ {{ selectedSpace.rating }} / 5.0 ({{ selectedSpace.reviewsCount }} audits)</span>
          </div>
          <h2>{{ selectedSpace.name }}</h2>
          <p class="dock-address">📍 {{ selectedSpace.neighborhood }}, {{ selectedSpace.city }} • 📞 {{ selectedSpace.contact }} • 🕒 {{ selectedSpace.hours }}</p>
        </div>

        <div class="dock-actions">
          <button class="btn-primary" @click="showReviewModal = true">
            ✍️ Add Safe Review
          </button>
          <a 
            :href="`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(selectedSpace.name + ' ' + selectedSpace.city)}`"
            target="_blank" 
            rel="noopener"
            class="btn-secondary"
          >
            Google Maps Directions ↗
          </a>
          <button class="dock-close-btn" @click="selectedSpace = null">✕</button>
        </div>
      </div>

      <div class="dock-body-grid">
        <div class="dock-amenities-col">
          <h4>Vetted Safety Features</h4>
          <div class="features-checklist">
            <div v-for="amenity in selectedSpace.amenities" :key="amenity" class="feature-item">
              <span class="check-icon">✓</span>
              <span>{{ amenity }}</span>
            </div>
          </div>
          <p class="dock-desc">{{ selectedSpace.description }}</p>
        </div>

        <div class="dock-reviews-col">
          <div class="reviews-header">
            <h4>Recent Community Audits</h4>
            <span class="reviews-anon-note">Anonymous verification</span>
          </div>

          <div class="reviews-list">
            <div v-for="(rev, idx) in selectedSpace.reviews" :key="idx" class="review-box">
              <div class="review-header">
                <span class="reviewer-name">{{ rev.user }}</span>
                <span class="reviewer-stars">★ {{ rev.rating }}/5</span>
              </div>
              <p class="review-text">"{{ rev.text }}"</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 🗺️ Maps API Configuration Modal -->
    <div v-if="showApiSettingsModal" class="modal-backdrop" @click.self="showApiSettingsModal = false">
      <div class="modal-card glass-panel animate-fade-in">
        <div class="modal-header">
          <div>
            <span class="badge badge-tag">Map Engine Configuration</span>
            <h3>Choose Maps API Provider</h3>
          </div>
          <button class="close-modal-btn" @click="showApiSettingsModal = false">✕</button>
        </div>

        <div class="modal-body">
          <p class="api-help-text">
            Choose your preferred map renderer. Prism supports <strong>Google Maps JavaScript API</strong> as well as <strong>100% Free, Keyless Dark Canvas</strong> with zero watermarks.
          </p>

          <!-- Provider Radio Options -->
          <div class="provider-radio-group">
            <label :class="['provider-option', { active: currentProvider === 'esri-dark' }]">
              <input type="radio" value="esri-dark" v-model="currentProvider" />
              <div class="provider-info">
                <strong>Dark Canvas (Recommended - Free & Keyless)</strong>
                <small>High resolution, dark modern styling, 0 watermarks, no API key required.</small>
              </div>
            </label>

            <label :class="['provider-option', { active: currentProvider === 'google' }]">
              <input type="radio" value="google" v-model="currentProvider" />
              <div class="provider-info">
                <strong>Google Maps JavaScript API</strong>
                <small>Native Google Maps with custom dark theme & places search.</small>
              </div>
            </label>

            <label :class="['provider-option', { active: currentProvider === 'osm' }]">
              <input type="radio" value="osm" v-model="currentProvider" />
              <div class="provider-info">
                <strong>OpenStreetMap Standard</strong>
                <small>Classic open-source map tiles, free & no key required.</small>
              </div>
            </label>
          </div>

          <!-- Google Maps API Key Input (if Google selected) -->
          <div v-if="currentProvider === 'google'" class="gmaps-key-input-box animate-fade-in">
            <label>Google Maps API Key (from Google Cloud Console)</label>
            <input 
              type="text" 
              v-model="gmapsApiKey" 
              placeholder="e.g. AIzaSy..."
              class="form-input" 
            />
            <span class="field-hint">
              Get an API key at <strong>console.cloud.google.com</strong> with <em>Maps JavaScript API</em> enabled, or set <code>VITE_GOOGLE_MAPS_API_KEY</code> in <code>.env</code>.
            </span>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="showApiSettingsModal = false">Cancel</button>
          <button class="btn-primary" @click="saveApiSettings">Save & Apply Map</button>
        </div>
      </div>
    </div>

    <!-- Review Modal -->
    <div v-if="showReviewModal" class="modal-backdrop" @click.self="showReviewModal = false">
      <div class="modal-card glass-panel animate-fade-in">
        <div class="modal-header">
          <div>
            <span class="badge badge-tag">Anonymous Community Audit</span>
            <h3>Review {{ selectedSpace?.name }}</h3>
          </div>
          <button class="close-modal-btn" @click="showReviewModal = false">✕</button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label>Safety Rating</label>
            <div class="rating-selector">
              <button 
                v-for="star in 5" 
                :key="star"
                :class="['star-btn', { active: newReviewRating >= star }]"
                @click="newReviewRating = star"
              >
                ★
              </button>
              <span class="rating-label">{{ newReviewRating }} / 5 Stars</span>
            </div>
          </div>

          <div class="form-group">
            <label>Your Anonymous Pseudonym</label>
            <input type="text" v-model="newReviewAuthor" class="form-input" />
          </div>

          <div class="form-group">
            <label>Your Safety Experience</label>
            <textarea 
              v-model="newReviewText" 
              rows="4" 
              placeholder="Was the staff respectful of pronouns? Did you feel safe expressing your authentic self?" 
              class="form-textarea"
            ></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="showReviewModal = false">Cancel</button>
          <button class="btn-primary" :disabled="!newReviewText.trim()" @click="submitReview">
            Publish Anonymous Review
          </button>
        </div>
      </div>
    </div>

    <!-- Nominate Space Modal -->
    <div v-if="showNominateModal" class="modal-backdrop" @click.self="showNominateModal = false">
      <div class="modal-card glass-panel animate-fade-in">
        <div class="modal-header">
          <div>
            <span class="badge badge-verified">Community Crowdsourcing</span>
            <h3>Nominate an LGBTQ+ Safe Space</h3>
          </div>
          <button class="close-modal-btn" @click="showNominateModal = false">✕</button>
        </div>

        <div class="modal-body">
          <div class="form-row">
            <div class="form-group">
              <label>Place Name</label>
              <input type="text" v-model="nominateName" placeholder="e.g. Queer Haven Books" class="form-input" />
            </div>

            <div class="form-group">
              <label>Category</label>
              <select v-model="nominateCategory" class="form-input">
                <option value="Cafe">Cafe / Hangout ☕</option>
                <option value="Clinic">Clinic / Health 🏥</option>
                <option value="Therapist">Therapist / Counselor 🧠</option>
                <option value="NGO">NGO / Crisis Shelter 🤝</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>City</label>
              <select v-model="nominateCity" class="form-input">
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

            <div class="form-group">
              <label>Neighborhood / Area</label>
              <input type="text" v-model="nominateAddress" placeholder="e.g. Bandra West, Mumbai" class="form-input" />
            </div>
          </div>

          <div class="form-group">
            <label>Why is this space safe?</label>
            <textarea 
              v-model="nominateReason" 
              rows="3" 
              placeholder="Gender-neutral bathrooms, affirming staff, queer events hosted..." 
              class="form-textarea"
            ></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="showNominateModal = false">Cancel</button>
          <button class="btn-primary" :disabled="!nominateName.trim() || !nominateAddress.trim()" @click="submitNomination">
            Submit for Community Audit
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
.safe-spaces-layout {
  max-width: 1360px;
  margin: 0 auto;
  padding: 24px 20px 80px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.spaces-header {
  padding: 24px 28px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  background: var(--bg-card-matte);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  flex-wrap: wrap;
}

.title-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 4px;
}

.title-row h2 {
  font-size: 1.7rem;
  font-weight: 800;
  color: #fff;
}

.header-info p {
  color: var(--text-secondary);
  font-size: 0.92rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.category-filter-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.category-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.cat-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-light);
  color: var(--text-secondary);
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.cat-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.cat-btn.active {
  background: var(--gradient-safe);
  color: #032015;
  font-weight: 700;
  border-color: transparent;
}

.search-box {
  position: relative;
  min-width: 260px;
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
  padding: 9px 36px;
  border-radius: var(--radius-full);
  color: #fff;
  font-size: 0.85rem;
  outline: none;
}
.search-input:focus {
  border-color: var(--border-active);
}

/* Map Grid */
.map-grid {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 20px;
  min-height: 560px;
}

.map-viewport-card {
  position: relative;
  border-radius: var(--radius-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: #0d0f1a;
  border: 1px solid var(--border-light);
}

.map-floating-bar {
  position: absolute;
  top: 14px;
  left: 14px;
  right: 14px;
  z-index: 500;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  pointer-events: none;
}

.city-jump-cluster {
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(13, 15, 26, 0.9);
  backdrop-filter: blur(12px);
  padding: 6px 12px;
  border-radius: var(--radius-full);
  border: 1px solid var(--border-light);
  max-width: 75%;
  overflow-x: auto;
}

.pill-label {
  font-size: 0.72rem;
  color: var(--text-muted);
  font-weight: 600;
  white-space: nowrap;
}

.city-jump-btn {
  padding: 3px 9px;
  border-radius: var(--radius-full);
  font-size: 0.72rem;
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.04);
  white-space: nowrap;
}
.city-jump-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}
.city-jump-btn.active {
  background: #38bdf8;
  color: #032035;
  font-weight: 700;
}

.api-status-badge {
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(13, 15, 26, 0.9);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border-light);
  padding: 6px 12px;
  border-radius: var(--radius-full);
  font-size: 0.72rem;
  color: #d8b4fe;
  cursor: pointer;
  white-space: nowrap;
}
.api-status-badge:hover {
  border-color: var(--border-active);
  background: rgba(25, 20, 40, 0.95);
}

.api-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10b981;
}

.api-gear {
  font-size: 0.75rem;
}

.leaflet-map-wrapper, .gmaps-wrapper {
  width: 100%;
  height: 100%;
  min-height: 560px;
}

/* Directory Sidebar */
.spaces-directory-col {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 600px;
}

.directory-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
}

.results-count strong {
  color: #38bdf8;
}

.audit-note {
  font-size: 0.72rem;
  color: #10b981;
}

.spaces-scroll-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
  padding-right: 4px;
}

.space-card {
  padding: 16px;
  border-radius: var(--radius-md);
  background: var(--bg-card-matte);
  border: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  gap: 8px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.space-card:hover {
  border-color: rgba(168, 85, 247, 0.35);
  background: var(--bg-card-hover);
}

.space-card.selected {
  border-color: #38bdf8;
  background: rgba(14, 165, 233, 0.08);
}

.space-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.space-category-pill {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #c084fc;
}

.space-rating {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
}

.star {
  color: #fbbf24;
}

.reviews-num {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.space-name {
  font-size: 1.05rem;
  font-weight: 700;
  color: #fff;
}

.space-location {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.amenities-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.amenity-chip {
  font-size: 0.68rem;
  background: rgba(16, 185, 129, 0.1);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.2);
  padding: 2px 7px;
  border-radius: var(--radius-full);
}

.amenity-chip.more {
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-muted);
  border-color: transparent;
}

.space-snippet {
  font-size: 0.82rem;
  color: var(--text-secondary);
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.space-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 8px;
  border-top: 1px solid var(--border-subtle);
}

.directions-link {
  font-size: 0.78rem;
  color: #38bdf8;
  font-weight: 600;
}

/* Dock Details */
.space-details-dock {
  padding: 24px;
  border-radius: var(--radius-lg);
  border: 1px solid rgba(56, 189, 248, 0.3);
  background: var(--bg-card-matte);
}

.dock-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-light);
  flex-wrap: wrap;
}

.dock-badge-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.space-rating-score {
  font-size: 0.82rem;
  color: #fbbf24;
  font-weight: 600;
}

.dock-title-group h2 {
  font-size: 1.45rem;
  font-weight: 800;
  color: #fff;
}

.dock-address {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 4px;
}

.dock-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.dock-close-btn {
  font-size: 1.2rem;
  color: var(--text-muted);
  padding: 4px 8px;
}

.dock-body-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.dock-amenities-col h4, .dock-reviews-col h4 {
  font-size: 0.95rem;
  margin-bottom: 12px;
  color: #e2e8f0;
}

.features-checklist {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.82rem;
  color: #cbd5e1;
}

.check-icon {
  color: #10b981;
  font-weight: 800;
}

.dock-desc {
  font-size: 0.88rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

.reviews-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.reviews-anon-note {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 220px;
  overflow-y: auto;
}

.review-box {
  background: rgba(255, 255, 255, 0.02);
  padding: 10px 14px;
  border-radius: var(--radius-md);
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.review-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.78rem;
  margin-bottom: 4px;
}

.reviewer-name {
  color: #c084fc;
  font-weight: 600;
}

.reviewer-stars {
  color: #fbbf24;
}

.review-text {
  font-size: 0.85rem;
  color: #e2e8f0;
  font-style: italic;
}

/* API Settings Modal Styling */
.api-help-text {
  font-size: 0.86rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 14px;
}

.provider-radio-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}

.provider-option {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-light);
  padding: 12px 14px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.provider-option:hover {
  background: rgba(255, 255, 255, 0.06);
}

.provider-option.active {
  border-color: #38bdf8;
  background: rgba(14, 165, 233, 0.08);
}

.provider-info {
  display: flex;
  flex-direction: column;
}

.provider-info strong {
  font-size: 0.9rem;
  color: #f8fafc;
}

.provider-info small {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.gmaps-key-input-box {
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.gmaps-key-input-box label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.field-hint {
  font-size: 0.72rem;
  color: var(--text-muted);
}

/* Common Modals */
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
  background: #11131e;
  border: 1px solid rgba(168, 85, 247, 0.3);
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
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

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
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
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 10px 14px;
  color: #fff;
  font-size: 0.88rem;
  outline: none;
}
.form-input:focus, .form-textarea:focus {
  border-color: var(--border-active);
}
.form-input option {
  background: #11131e;
}

.rating-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.star-btn {
  font-size: 1.5rem;
  color: #475569;
}
.star-btn.active {
  color: #fbbf24;
}

.rating-label {
  font-size: 0.82rem;
  color: #fbbf24;
  font-weight: 600;
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
  background: #064e3b;
  border: 1px solid #10b981;
  color: #ecfdf5;
  padding: 12px 20px;
  border-radius: var(--radius-md);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
  font-size: 0.9rem;
  font-weight: 500;
  z-index: 3500;
}

/* Custom Marker Styling */
:deep(.custom-map-pin) {
  width: 36px;
  height: 36px;
  background: #161a2e;
  border: 2px solid #a855f7;
  border-radius: 50% 50% 50% 0;
  transform: rotate(-45deg);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.6);
  position: relative;
}

:deep(.custom-map-pin .pin-emoji) {
  transform: rotate(45deg);
  font-size: 16px;
}

:deep(.custom-map-pin .pin-glow) {
  position: absolute;
  inset: -4px;
  border-radius: inherit;
  background: radial-gradient(circle, rgba(236, 72, 153, 0.35), transparent 70%);
  pointer-events: none;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.8rem;
}

@media (max-width: 1024px) {
  .map-grid {
    grid-template-columns: 1fr;
  }
  .dock-body-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .spaces-container {
    padding: 10px 10px 100px;
  }

  .spaces-hero {
    padding: 20px 14px;
    margin-bottom: 16px;
  }

  .spaces-hero h2 {
    font-size: 1.5rem;
  }

  .map-grid {
    gap: 14px;
  }

  .map-viewport-card {
    min-height: 340px;
    height: 360px;
  }

  .map-floating-bar {
    top: 8px;
    left: 8px;
    right: 8px;
  }

  .city-jump-cluster {
    max-width: 80%;
    padding: 4px 8px;
  }

  .city-pill-btn {
    font-size: 0.72rem;
    padding: 3px 8px;
  }

  .spaces-list-card {
    padding: 14px;
  }

  .form-row {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .modal-card {
    max-width: 95vw !important;
    width: 95vw !important;
    padding: 18px 14px !important;
    max-height: 90vh !important;
    overflow-y: auto;
  }
}
</style>
