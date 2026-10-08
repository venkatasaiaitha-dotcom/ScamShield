// ScamShield Content Script - Proactive In-Page Link Inspector & Modal Handler
(function() {
  const SUSPICIOUS_INDICATORS = ['.xyz', '.top', '.tk', '.site', '.club', 'kyc-verify', 'paypa1', 'amaz0n', 'sbi-kyc', '192.168.', 'account-recovery'];

  function scanLinks() {
    const links = document.querySelectorAll('a[href]:not([data-scamshield-checked])');
    links.forEach(link => {
      link.setAttribute('data-scamshield-checked', 'true');
      const href = link.href.toLowerCase();

      const matched = SUSPICIOUS_INDICATORS.find(ind => href.includes(ind));
      if (matched) {
        link.classList.add('scamshield-warning-link');
        
        // Add warning badge icon next to link
        const badge = document.createElement('span');
        badge.className = 'scamshield-warning-badge';
        badge.title = '🛡️ ScamShield Alert: Suspicious link detected (' + matched + ')';
        badge.innerText = ' ⚠️ [ScamShield Flag]';
        link.parentNode.insertBefore(badge, link.nextSibling);
      }
    });
  }

  // Floating Audit Modal Renderer
  function renderAuditModal(data) {
    // Remove existing if any
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

    // Auto-dismiss after 15 seconds if not interacted
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

  // Initial scan and observer for dynamically loaded webmail / messaging items
  scanLinks();
  const observer = new MutationObserver(() => scanLinks());
  observer.observe(document.body, { childList: true, subtree: true });
})();
