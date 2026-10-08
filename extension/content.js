// ScamShield Content Script - Proactive Live Link Scanner & Active Threat Defense
(function() {
  const HIGH_ABUSE_TLDS = ['.xyz', '.top', '.tk', '.site', '.online', '.club', '.buzz', '.click', '.work', '.ml', '.ga', '.cf', '.gq', '.loan', '.win'];
  const SHORTENERS = ['bit.ly', 'tinyurl.com', 'is.gd', 'cutt.ly', 'rb.gy', 'shorturl.at', 'bl.ink', 'v.gd'];
  const TYPOSQUAT_PATTERNS = ['paypa1', 'amaz0n', 'micros0ft', 'sbi-kyc', 'sbi-portal', 'hdfc-auth', 'hdfc-card', 'netflix-account', 'apple-id-verify', 'account-recovery'];
  const INSECURE_SENSITIVE_PATHS = ['/login', '/auth', '/signin', '/kyc', '/verify', '/password', '/otp', '/banking', '/claim'];

  const detectedThreats = [];

  function evaluateLink(href) {
    const lower = href.toLowerCase();
    
    // Check raw IP
    if (/https?:\/\/\d+\.\d+\.\d+\.\d+/.test(lower)) {
      return { isThreat: true, reason: 'Raw IP address host' };
    }
    // Check brand typosquatting
    const matchedTypo = TYPOSQUAT_PATTERNS.find(t => lower.includes(t));
    if (matchedTypo) {
      return { isThreat: true, reason: `Brand lookalike typosquatting (${matchedTypo})` };
    }
    // Check high abuse TLD
    const matchedTld = HIGH_ABUSE_TLDS.find(tld => lower.includes(tld + '/') || lower.endsWith(tld));
    if (matchedTld) {
      return { isThreat: true, reason: `High-abuse generic TLD (${matchedTld})` };
    }
    // Check deceptive shortener
    const matchedShort = SHORTENERS.find(s => lower.includes(s));
    if (matchedShort) {
      return { isThreat: true, reason: `Obfuscated URL shortener (${matchedShort})` };
    }
    // Check insecure sensitive endpoints
    if (lower.startsWith('http://') && INSECURE_SENSITIVE_PATHS.some(p => lower.includes(p))) {
      return { isThreat: true, reason: 'Insecure HTTP password/credential portal' };
    }

    return { isThreat: false, reason: '' };
  }

  function interceptClick(e, href, reason) {
    e.preventDefault();
    e.stopPropagation();

    // Show Intercept Modal
    const existing = document.getElementById('scamshield-intercept-modal');
    if (existing) existing.remove();

    const modal = document.createElement('div');
    modal.id = 'scamshield-intercept-modal';
    modal.innerHTML = `
      <div class="scamshield-intercept-card">
        <div style="width:48px; height:48px; background:#FEE2E2; color:#DC2626; border-radius:12px; display:flex; align-items:center; justify-content:center; margin:0 auto 12px; font-size:24px;">
          ⚠️
        </div>
        <h3 style="font-size:16px; font-weight:800; color:#172033; margin-bottom:6px;">
          ScamShield Phishing Interception
        </h3>
        <p style="font-size:12px; color:#64748B; margin-bottom:12px;">
          You clicked a link identified as <strong>HIGH RISK</strong>. Navigating to this page may expose you to credential theft or malware.
        </p>

        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:10px; font-size:11px; text-align:left; margin-bottom:12px;">
          <div style="font-weight:700; color:#334155; margin-bottom:4px;">Target URL:</div>
          <div style="font-family:monospace; color:#DC2626; word-break:break-all;">${href}</div>
          <div style="margin-top:6px; color:#475569;"><strong>Reason:</strong> ${reason}</div>
        </div>

        <div style="display:flex; gap:8px;">
          <button id="scamshield-stay-safe-btn" style="flex:1; padding:10px; background:#0F766E; color:white; border:none; border-radius:10px; font-size:12px; font-weight:700; cursor:pointer;">
            🛡️ Stay Safe (Cancel)
          </button>
          <button id="scamshield-proceed-btn" style="padding:10px 14px; background:white; color:#94A3B8; border:1px solid #CBD5E1; border-radius:10px; font-size:11px; font-weight:600; cursor:pointer;">
            Proceed Anyway
          </button>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    document.getElementById('scamshield-stay-safe-btn').onclick = () => modal.remove();
    document.getElementById('scamshield-proceed-btn').onclick = () => {
      modal.remove();
      window.open(href, '_blank', 'noopener,noreferrer');
    };
  }

  function updatePageAlertPill() {
    let pill = document.getElementById('scamshield-page-alert-pill');
    if (detectedThreats.length === 0) {
      if (pill) pill.remove();
      return;
    }

    if (!pill) {
      pill = document.createElement('div');
      pill.id = 'scamshield-page-alert-pill';
      document.body.appendChild(pill);
    }

    pill.innerHTML = `
      <div class="scamshield-pill-header">
        <span class="scamshield-pulsing-dot"></span>
        <strong style="color:#991B1B">🛡️ ScamShield Alert:</strong>
        <span style="font-weight:600; color:#7F1D1D">${detectedThreats.length} Suspicious Link${detectedThreats.length > 1 ? 's' : ''} Detected</span>
        <button class="scamshield-pill-btn" id="scamshield-toggle-details">Details ▾</button>
        <button class="scamshield-pill-close" id="scamshield-close-pill">✕</button>
      </div>
      <div class="scamshield-pill-content" id="scamshield-pill-dropdown" style="display:none;">
        <div style="font-size:10px; font-weight:700; color:#64748B; margin-bottom:6px; text-transform:uppercase;">
          Flagged on this page:
        </div>
        ${detectedThreats.map((t, idx) => `
          <div class="scamshield-threat-item">
            <div style="font-weight:700; color:#DC2626; font-size:10px;">⚠️ ${t.reason}</div>
            <div style="color:#475569; font-size:10px; margin-top:2px;">${t.href}</div>
            <a href="#" data-threat-idx="${idx}" class="scamshield-scroll-to" style="color:#0F766E; font-size:10px; font-weight:700; text-decoration:none; display:inline-block; margin-top:4px;">
              🔍 Scroll & Highlight on page →
            </a>
          </div>
        `).join('')}
      </div>
    `;

    document.getElementById('scamshield-close-pill').onclick = () => pill.remove();
    const dropdown = document.getElementById('scamshield-pill-dropdown');
    document.getElementById('scamshield-toggle-details').onclick = () => {
      const isHidden = dropdown.style.display === 'none';
      dropdown.style.display = isHidden ? 'block' : 'none';
      document.getElementById('scamshield-toggle-details').textContent = isHidden ? 'Hide ▴' : 'Details ▾';
    };

    // Scroll to link handler
    pill.querySelectorAll('.scamshield-scroll-to').forEach(btn => {
      btn.onclick = (e) => {
        e.preventDefault();
        const idx = parseInt(btn.getAttribute('data-threat-idx'), 10);
        const item = detectedThreats[idx];
        if (item && item.element) {
          item.element.scrollIntoView({ behavior: 'smooth', block: 'center' });
          item.element.style.outline = '4px solid #DC2626';
          item.element.style.outlineOffset = '4px';
          setTimeout(() => { item.element.style.outline = ''; }, 3000);
        }
      };
    });
  }

  function scanLinks() {
    const links = document.querySelectorAll('a[href]:not([data-scamshield-checked])');
    let newThreatsFound = false;

    links.forEach(link => {
      link.setAttribute('data-scamshield-checked', 'true');
      const href = link.href;
      if (!href || href.startsWith('javascript:') || href.startsWith('#')) return;

      const assessment = evaluateLink(href);
      if (assessment.isThreat) {
        newThreatsFound = true;
        detectedThreats.push({
          href: href,
          reason: assessment.reason,
          element: link
        });

        // Add visual link highlight
        link.classList.add('scamshield-warning-link');

        // Add warning badge
        const badge = document.createElement('span');
        badge.className = 'scamshield-warning-badge';
        badge.title = `🛡️ ScamShield Alert: Flagged as ${assessment.reason}`;
        badge.innerText = ` ⚠️ [ScamShield Flag: ${assessment.reason}]`;
        link.parentNode.insertBefore(badge, link.nextSibling);

        // Attach click interception protection
        link.addEventListener('click', (e) => interceptClick(e, href, assessment.reason), true);
      }
    });

    if (newThreatsFound) {
      updatePageAlertPill();
      try {
        chrome.runtime.sendMessage({
          action: "UPDATE_PAGE_THREATS",
          count: detectedThreats.length
        });
      } catch (e) {}
    }
  }

  // Right-Click Context Menu Modal Renderer
  function renderAuditModal(data) {
    const existing = document.getElementById('scamshield-audit-overlay');
    if (existing) existing.remove();

    const isHigh = data.risk_level === 'HIGH';
    const modal = document.createElement('div');
    modal.id = 'scamshield-audit-overlay';

    modal.innerHTML = `
      <div class="scamshield-header">
        <div class="scamshield-brand">
          <span>🛡️ ScamShield Audit</span>
        </div>
        <button class="scamshield-close-btn" id="scamshield-close-overlay">✕</button>
      </div>

      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
        <span style="font-size:11px; font-weight:600; color:#64748B;">Assessed Target:</span>
        <span class="${isHigh ? 'scamshield-badge-high' : 'scamshield-badge-low'}">
          ${data.risk_level} (${data.risk_score}/100)
        </span>
      </div>

      <div class="scamshield-target">
        ${data.inspected_item}
      </div>

      <div style="font-size:11px; font-weight:700; color:#334155; margin-bottom:4px;">Forensic Indicators:</div>
      <ul class="scamshield-indicators">
        ${data.flags.map(f => `<li>${f}</li>`).join('')}
      </ul>

      <div class="scamshield-rec">
        ${data.recommendation}
      </div>

      <button id="scamshield-dismiss-btn" style="width:100%; margin-top:12px; padding:7px; background:#0F766E; color:white; border:none; border-radius:8px; font-size:11px; font-weight:700; cursor:pointer;">
        Dismiss Audit
      </button>
    `;

    document.body.appendChild(modal);
    document.getElementById('scamshield-close-overlay').onclick = () => modal.remove();
    document.getElementById('scamshield-dismiss-btn').onclick = () => modal.remove();

    setTimeout(() => {
      if (document.getElementById('scamshield-audit-overlay')) {
        modal.remove();
      }
    }, 15000);
  }

  // Listen for messages from background.js
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'SHOW_SCAMSHIELD_MODAL' && request.data) {
      renderAuditModal(request.data);
      sendResponse({ status: 'modal_displayed' });
    }
  });

  // Initial live scan and observer
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', scanLinks);
  } else {
    scanLinks();
  }

  const observer = new MutationObserver(() => scanLinks());
  observer.observe(document.body || document.documentElement, { childList: true, subtree: true });
})();
