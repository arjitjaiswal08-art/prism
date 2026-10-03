/**
 * Prism API Client
 * Privacy-First, JWT-Based Auth, Safe Connections & Connection Mode
 */

const API_BASE = 'http://127.0.0.1:8000';

class PrismApiClient {
  constructor() {
    this.token = localStorage.getItem('prism_access_token') || null;
    this.refreshToken = localStorage.getItem('prism_refresh_token') || null;
  }

  setTokens(accessToken, refreshToken) {
    this.token = accessToken;
    this.refreshToken = refreshToken;
    if (accessToken) {
      localStorage.setItem('prism_access_token', accessToken);
    } else {
      localStorage.removeItem('prism_access_token');
    }
    if (refreshToken) {
      localStorage.setItem('prism_refresh_token', refreshToken);
    } else {
      localStorage.removeItem('prism_refresh_token');
    }
  }

  clearTokens() {
    this.token = null;
    this.refreshToken = null;
    localStorage.removeItem('prism_access_token');
    localStorage.removeItem('prism_refresh_token');
    localStorage.removeItem('prism_auth_user');
  }

  async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
      });

      if (response.status === 401 && this.token) {
        // Token might be expired, clear tokens
        this.clearTokens();
        throw new Error('Session expired. Please log in again.');
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Request failed (${response.status})`);
      }

      return await response.json();
    } catch (err) {
      console.warn(`[Prism API] ${endpoint} error:`, err.message);
      throw err;
    }
  }

  /* ========================================================
     PHASE 1: AUTH & IDENTITY APIS
     ======================================================== */

  // 1. Anonymous Login (Default)
  async anonymousLogin(payload = {}) {
    const res = await this.request('/auth/anonymous-login', {
      method: 'POST',
      body: JSON.stringify({
        alias: payload.alias || null,
        pronouns: payload.pronouns || 'they/them',
        city: payload.city || 'All India',
        identity_tags: payload.identity_tags || ['Queer'],
        closet_pin: payload.closet_pin || '1234',
        device_info: navigator.userAgent
      })
    });
    this.setTokens(res.access_token, res.refresh_token);
    localStorage.setItem('prism_auth_user', JSON.stringify(res.user));
    return res;
  }

  // 2. Optional Signup
  async signup(payload) {
    const res = await this.request('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({
        email: payload.email,
        password: payload.password,
        alias: payload.alias || null,
        pronouns: payload.pronouns || 'they/them',
        city: payload.city || 'All India',
        upgrade_from_anon_id: payload.upgrade_from_anon_id || null
      })
    });
    this.setTokens(res.access_token, res.refresh_token);
    localStorage.setItem('prism_auth_user', JSON.stringify(res.user));
    return res;
  }

  // 3. Login
  async login(payload) {
    const res = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        identifier: payload.identifier,
        password: payload.password || null,
        device_info: navigator.userAgent
      })
    });
    this.setTokens(res.access_token, res.refresh_token);
    localStorage.setItem('prism_auth_user', JSON.stringify(res.user));
    return res;
  }

  // 4. Get Current User (/auth/me)
  async getMe() {
    const user = await this.request('/auth/me');
    localStorage.setItem('prism_auth_user', JSON.stringify(user));
    return user;
  }

  // 5. Upgrade Account (anon -> registered)
  async upgradeAccount(email, password) {
    const user = await this.request('/auth/upgrade-account', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    localStorage.setItem('prism_auth_user', JSON.stringify(user));
    return user;
  }

  // 6. Logout
  async logout() {
    try {
      await this.request('/auth/logout', { method: 'POST' });
    } finally {
      this.clearTokens();
    }
  }

  // 7. Right to be Forgotten (Account Deletion)
  async deleteAccount() {
    try {
      return await this.request('/auth/me', { method: 'DELETE' });
    } finally {
      this.clearTokens();
    }
  }

  /* ========================================================
     PHASE 2: CONSENT-BASED CONNECTION SYSTEM
     ======================================================== */

  // Send a connection request
  async sendConnectionRequest(receiverAnonId, introNote, intent = 'Friendship') {
    return await this.request('/connections/request', {
      method: 'POST',
      body: JSON.stringify({
        receiver_anon_id: receiverAnonId,
        intro_note: introNote,
        intent
      })
    });
  }

  // Get incoming pending requests
  async getIncomingRequests() {
    return await this.request('/connections/requests');
  }

  // Accept a connection request
  async acceptConnectionRequest(requestId) {
    return await this.request(`/connections/requests/${requestId}/accept`, {
      method: 'POST'
    });
  }

  // Reject a connection request
  async rejectConnectionRequest(requestId) {
    return await this.request(`/connections/requests/${requestId}/reject`, {
      method: 'POST'
    });
  }

  // List active connections
  async getConnections() {
    return await this.request('/connections');
  }

  // Get chat messages for a connection
  async getMessages(connectionId) {
    return await this.request(`/connections/${connectionId}/messages`);
  }

  // Send message inside connection
  async sendMessage(connectionId, content) {
    return await this.request(`/connections/${connectionId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ content })
    });
  }

  // Mutual identity reveal toggle
  async revealIdentity(connectionId, reveal = true) {
    return await this.request(`/connections/${connectionId}/reveal`, {
      method: 'POST',
      body: JSON.stringify({ reveal })
    });
  }

  /* ========================================================
     PHASE 3: INTENTIONAL CONNECTION MODE (DATING / DISCOVERY)
     ======================================================== */

  // Get my dating profile
  async getMyDatingProfile() {
    return await this.request('/dating/profile');
  }

  // Update dating profile
  async updateDatingProfile(profileData) {
    return await this.request('/dating/profile', {
      method: 'POST',
      body: JSON.stringify(profileData)
    });
  }

  // Discover intentional matches
  async discoverMatches(city = null, intent = null) {
    const params = new URLSearchParams();
    if (city && city !== 'All India') params.append('city', city);
    if (intent && intent !== 'All') params.append('intent', intent);
    const query = params.toString() ? `?${params.toString()}` : '';
    return await this.request(`/dating/discover${query}`);
  }
}

export const prismApi = new PrismApiClient();
