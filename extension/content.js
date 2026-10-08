// ScamShield Content Script - Proactive In-Page Link Inspector
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

  // Initial scan and observer for dynamically loaded webmail / messaging items
  scanLinks();
  const observer = new MutationObserver(() => scanLinks());
  observer.observe(document.body, { childList: true, subtree: true });
})();
