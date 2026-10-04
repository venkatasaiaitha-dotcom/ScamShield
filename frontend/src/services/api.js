const API_BASE = '/api';

let memoryToken = null;

export function setAuthToken(token) {
  memoryToken = token;
}

export function getAuthToken() {
  return memoryToken;
}

async function request(url, options = {}, isRetry = false) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  if (memoryToken) {
    headers['Authorization'] = `Bearer ${memoryToken}`;
  }

  const config = {
    ...options,
    headers,
    credentials: 'include', // Ensures HttpOnly cookies are automatically passed
  };

  let res;
  try {
    res = await fetch(url, config);
  } catch {
    if (!isRetry) {
      await new Promise((resolve) => setTimeout(resolve, 350));
      return request(url, options, true);
    }
    throw new Error('Connection error. Server or tunnel is unreachable. Please try again.');
  }

  // Auto-recovery for gateway timeouts (502, 503, 504) via tunnel proxy: retry once after brief backoff
  if ((res.status === 502 || res.status === 503 || res.status === 504) && !isRetry) {
    await new Promise((resolve) => setTimeout(resolve, 350));
    return request(url, options, true);
  }

  // Auto-recovery: If 401 occurs and not already refreshing/logging in, attempt refresh and retry once
  if (res.status === 401 && !isRetry && !url.includes('/auth/login') && !url.includes('/auth/me') && !url.includes('/auth/refresh')) {
    try {
      const refreshRes = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      });
      if (refreshRes.ok) {
        const refreshData = await refreshRes.json();
        if (refreshData?.access_token) {
          setAuthToken(refreshData.access_token);
          return request(url, options, true);
        }
      }
    } catch {
      // Continue to handle 401 error normally
    }
  }

  if (!res.ok) {
    let errorDetail = '';
    try {
      const errorData = await res.json();
      if (typeof errorData?.detail === 'string') {
        errorDetail = errorData.detail;
      } else if (Array.isArray(errorData?.detail)) {
        errorDetail = errorData.detail.map((d) => d.msg || d.message || JSON.stringify(d)).join(', ');
      } else if (errorData?.message) {
        errorDetail = errorData.message;
      }
    } catch {
      if (res.status === 504) {
        errorDetail = 'Gateway Timeout (HTTP 504) from connection proxy. Please retry.';
      } else if (res.status === 502 || res.status === 503) {
        errorDetail = `Gateway error (HTTP ${res.status}). Server temporarily busy. Please retry.`;
      } else {
        errorDetail = res.statusText || (res.status ? `Server error (HTTP ${res.status})` : 'Request failed');
      }
    }

    const error = new Error(errorDetail || 'Request failed. Please check your connection.');
    error.status = res.status;
    throw error;
  }

  return res.json();
}

export const api = {
  // Authentication & Identity
  async login(email, password) {
    const data = await request(`${API_BASE}/auth/login`, {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    if (data.access_token) {
      setAuthToken(data.access_token);
    }
    return data;
  },

  async register(email, password) {
    const data = await request(`${API_BASE}/auth/register`, {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    if (data.access_token) {
      setAuthToken(data.access_token);
    }
    return data;
  },

  async getCurrentUser() {
    return request(`${API_BASE}/auth/me`);
  },

  async logout() {
    try {
      await request(`${API_BASE}/auth/logout`, { method: 'POST' });
    } finally {
      setAuthToken(null);
    }
    return { status: 'logged_out' };
  },

  async changePassword(oldPassword, newPassword) {
    return request(`${API_BASE}/auth/change-password`, {
      method: 'POST',
      body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
    });
  },

  // Security Health Dashboard
  async getSecurityHealth() {
    return request(`${API_BASE}/security/health`);
  },

  // Agent Status & Controls
  async getAgentStatus(dateRange = 'all') {
    return request(`${API_BASE}/agent/status?date_range=${encodeURIComponent(dateRange)}`);
  },

  async startProtection() {
    return request(`${API_BASE}/agent/start`, { method: 'POST' });
  },

  async pauseProtection() {
    return request(`${API_BASE}/agent/pause`, { method: 'POST' });
  },

  // Incoming Messages & Simulator
  async simulateScenario(scenarioType = 'RANDOM') {
    return request(`${API_BASE}/messages/simulate-scenario`, {
      method: 'POST',
      body: JSON.stringify({ scenario_type: scenarioType }),
    });
  },

  async sendIncomingMessage(messageData) {
    return request(`${API_BASE}/messages/incoming`, {
      method: 'POST',
      body: JSON.stringify(messageData),
    });
  },

  async getScenarios() {
    return request(`${API_BASE}/messages/scenarios`);
  },

  // Direct Manual Inspections
  async analyzeMessage(content, sender = 'Manual Inspection') {
    return request(`${API_BASE}/analyze/message`, {
      method: 'POST',
      body: JSON.stringify({ content, sender }),
    });
  },

  async analyzeUrl(url) {
    return request(`${API_BASE}/analyze/url`, {
      method: 'POST',
      body: JSON.stringify({ url }),
    });
  },

  // Alerts
  async getAlerts(unreadOnly = false) {
    return request(`${API_BASE}/alerts?unread_only=${unreadOnly}`);
  },

  async markAlertRead(alertId) {
    return request(`${API_BASE}/alerts/${alertId}/read`, { method: 'POST' });
  },

  async markAllAlertsRead() {
    return request(`${API_BASE}/alerts/mark-all-read`, { method: 'POST' });
  },

  // History
  async getHistory(risk = 'ALL', search = '', limit = 50) {
    let url = `${API_BASE}/history?limit=${limit}`;
    if (risk && risk !== 'ALL') url += `&risk=${risk}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    return request(url);
  },

  async getHistoryDetail(analysisId) {
    return request(`${API_BASE}/history/${analysisId}`);
  },

  async deleteHistoryEntry(analysisId) {
    return request(`${API_BASE}/history/${analysisId}`, { method: 'DELETE' });
  },

  async clearMyHistory() {
    return request(`${API_BASE}/history/clear-my-history`, { method: 'POST' });
  },

  async clearAllHistoryAdmin() {
    return request(`${API_BASE}/history/clear`, { method: 'POST' });
  },

  // Sources
  async getSources() {
    return request(`${API_BASE}/sources`);
  },

  async toggleSource(sourceId, enable) {
    const action = enable ? 'enable' : 'disable';
    return request(`${API_BASE}/sources/${sourceId}/${action}`, { method: 'POST' });
  },

  // Settings
  async getSettings() {
    return request(`${API_BASE}/settings`);
  },

  async updateSettings(settingsData) {
    return request(`${API_BASE}/settings`, {
      method: 'POST',
      body: JSON.stringify(settingsData),
    });
  },

  // Gmail Connector
  async getGmailStatus() {
    return request(`${API_BASE}/gmail/status`);
  },

  async inputGmailMessage(sender, subject, body) {
    return request(`${API_BASE}/gmail/input`, {
      method: 'POST',
      body: JSON.stringify({ sender, subject, body }),
    });
  },

  async disconnectGmail() {
    return request(`${API_BASE}/gmail/disconnect`, { method: 'POST' });
  },

  async wipeAllDataAdmin() {
    return request(`${API_BASE}/gmail/wipe-data`, { method: 'POST' });
  },
};

// WebSocket Client for Real-Time Threat Detection with Auth Token
export function createWebSocketClient(onMessage, onStatusChange, token = null) {
  let ws = null;
  let reconnectTimer = null;
  let heartbeatTimer = null;
  let isClosing = false;

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host;
  const currentToken = token || memoryToken;
  const wsUrl = currentToken
    ? `${protocol}//${host}/ws?token=${encodeURIComponent(currentToken)}`
    : `${protocol}//${host}/ws`;

  function connect() {
    if (isClosing) return;

    try {
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        if (onStatusChange) onStatusChange(true);
        heartbeatTimer = setInterval(() => {
          if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send('ping');
          }
        }, 15000);
      };

      ws.onmessage = (event) => {
        try {
          if (event.data === 'pong') return;
          const parsed = JSON.parse(event.data);
          if (onMessage) onMessage(parsed);
        } catch {
          // ignore non-json ping/pong
        }
      };

      ws.onclose = (event) => {
        if (onStatusChange) onStatusChange(false);
        clearInterval(heartbeatTimer);
        // If closed with 1008 policy violation (unauthorized), do not spam reconnect
        if (event.code === 1008) {
          console.warn('WebSocket connection requires authentication');
          return;
        }
        if (!isClosing) {
          reconnectTimer = setTimeout(connect, 3000);
        }
      };

      ws.onerror = () => {
        if (ws) ws.close();
      };
    } catch {
      if (!isClosing) {
        reconnectTimer = setTimeout(connect, 3000);
      }
    }
  }

  connect();

  return {
    disconnect() {
      isClosing = true;
      clearTimeout(reconnectTimer);
      clearInterval(heartbeatTimer);
      if (ws) ws.close();
    },
  };
}

// Subtle audio alert helper using Web Audio API (cached context for instant low-latency audio)
let cachedAudioCtx = null;

export function playAlertChime(isHighRisk = true) {
  try {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) return;
    if (!cachedAudioCtx || cachedAudioCtx.state === 'closed') {
      cachedAudioCtx = new AudioContextClass();
    }
    if (cachedAudioCtx.state === 'suspended') {
      cachedAudioCtx.resume().catch(() => {});
    }
    const ctx = cachedAudioCtx;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.connect(gain);
    gain.connect(ctx.destination);

    if (isHighRisk) {
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(587.33, ctx.currentTime);
      osc.frequency.setValueAtTime(880.00, ctx.currentTime + 0.12);
      gain.gain.setValueAtTime(0.15, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.35);
      osc.start(ctx.currentTime);
      osc.stop(ctx.currentTime + 0.35);
    } else {
      osc.type = 'sine';
      osc.frequency.setValueAtTime(659.25, ctx.currentTime);
      gain.gain.setValueAtTime(0.08, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.2);
      osc.start(ctx.currentTime);
      osc.stop(ctx.currentTime + 0.2);
    }
  } catch {
    // Audio context may be blocked by browser policy until user interacts
  }
}
