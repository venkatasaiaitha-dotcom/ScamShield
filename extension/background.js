// ScamShield Background Service Worker
function assessItem(rawText) {
  const text = (rawText || '').trim();
  const lower = text.toLowerCase();
  let score = 15;
  const flags = [];

  // URL checks
  if (lower.includes('.xyz') || lower.includes('.top') || lower.includes('.tk') || lower.includes('.site') || lower.includes('.club')) {
    score += 40;
    flags.push('Deceptive or high-abuse generic TLD');
  }
  if (/https?:\/\/\d+\.\d+\.\d+\.\d+/.test(lower)) {
    score += 40;
    flags.push('Raw IP address host instead of registered domain');
  }
  if (lower.includes('bit.ly') || lower.includes('tinyurl') || lower.includes('cutt.ly')) {
    score += 25;
    flags.push('Obfuscated URL shortener masking true destination');
  }
  if (lower.startsWith('http://')) {
    score += 15;
    flags.push('Insecure unencrypted HTTP protocol');
  }

  // Keywords & Phishing Indicators
  if (lower.includes('kyc') || lower.includes('verify') || lower.includes('pan card') || lower.includes('update your kyc') || lower.includes('documents')) {
    score += 35;
    flags.push('KYC / identity document harvesting lure');
  }
  if (lower.includes('blocked') || lower.includes('suspended') || lower.includes('24 hours') || lower.includes('urgent') || lower.includes('immediately')) {
    score += 30;
    flags.push('Artificial psychological urgency & threat pressure');
  }
  if (lower.includes('paypa1') || lower.includes('amaz0n') || lower.includes('sbi-kyc') || lower.includes('hdfc-card') || lower.includes('netflix-account')) {
    score += 40;
    flags.push('Brand impersonation & lookalike typosquatting');
  }
  if (lower.includes('lucky draw') || lower.includes('won ₹') || lower.includes('cash prize') || lower.includes('claim reward')) {
    score += 35;
    flags.push('Lottery / advance-fee prize bait');
  }

  // Safe indicator checks
  if (lower.includes('tracking id') || lower.includes('delivered to') || lower.includes('boarding pass') || lower.includes('flight')) {
    score = 8;
    flags.length = 0;
  }

  score = Math.min(Math.max(score, 8), 96);
  const isHigh = score >= 70;
  const isSuspicious = score >= 30 && score < 70;
  const riskLevel = isHigh ? 'HIGH' : isSuspicious ? 'SUSPICIOUS' : 'LOW';

  return {
    inspected_item: text.length > 80 ? text.substring(0, 80) + '...' : text,
    risk_score: score,
    risk_level: riskLevel,
    flags: flags.length ? flags : ['No malicious heuristics detected in this selection.'],
    summary: isHigh ? 'High probability of phishing or credential theft.' : isSuspicious ? 'Contains unverified or elevated risk patterns.' : 'Item appears legitimate with standard indicators.',
    recommendation: isHigh ? 'Do NOT navigate to this link or share passwords/OTPs.' : isSuspicious ? 'Proceed with caution and verify independently.' : 'Verified clean pattern.'
  };
}

chrome.runtime.onInstalled.addListener(() => {
  // Clear any existing menu items before re-creating
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({
      id: "scamshield-inspect-text",
      title: "🛡️ Inspect selection with ScamShield",
      contexts: ["selection", "link"]
    });
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "scamshield-inspect-text") {
    const textToCheck = info.linkUrl || info.selectionText || "";
    if (!textToCheck) return;

    const result = assessItem(textToCheck);

    // 1. Show native browser notification
    try {
      chrome.notifications.create({
        type: "basic",
        iconUrl: "popup.html",
        title: `🛡️ ScamShield: ${result.risk_level} RISK (${result.risk_score}/100)`,
        message: result.summary,
        priority: 2
      });
    } catch (e) {
      // notifications not supported or denied
    }

    // 2. Send message to content script in the active tab to render floating modal
    if (tab && tab.id) {
      chrome.tabs.sendMessage(tab.id, {
        action: "SHOW_SCAMSHIELD_MODAL",
        data: result
      }).catch(() => {
        // Fallback: If tab was opened before extension loaded, inject dynamically
        chrome.scripting.executeScript({
          target: { tabId: tab.id },
          func: (res) => {
            alert(`🛡️ ScamShield Safety Audit:\n\n[${res.risk_level} RISK - Score: ${res.risk_score}/100]\nTarget: ${res.inspected_item}\n\nIndicators:\n• ${res.flags.join('\n• ')}\n\nRecommendation: ${res.recommendation}`);
          },
          args: [result]
        }).catch(() => {});
      });
    }
  }
});
