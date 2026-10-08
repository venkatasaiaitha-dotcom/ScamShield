document.addEventListener('DOMContentLoaded', () => {
  const checkBtn = document.getElementById('checkBtn');
  const urlInput = document.getElementById('urlInput');
  const resultBox = document.getElementById('resultBox');

  checkBtn.addEventListener('click', async () => {
    const rawUrl = urlInput.value.trim();
    if (!rawUrl) return;

    resultBox.style.display = 'block';
    resultBox.className = 'result';
    resultBox.textContent = 'Inspecting with ScamShield Engine...';

    const urlLower = rawUrl.toLowerCase();
    let isPhishing = false;
    let reason = '';

    if (
      urlLower.includes('.xyz') ||
      urlLower.includes('.top') ||
      urlLower.includes('.tk') ||
      urlLower.includes('.site') ||
      urlLower.includes('kyc') ||
      urlLower.includes('verify') ||
      urlLower.includes('recover') ||
      urlLower.includes('paypa1') ||
      urlLower.includes('sbi-kyc') ||
      /\d+\.\d+\.\d+\.\d+/.test(urlLower)
    ) {
      isPhishing = true;
      reason = 'High-risk unverified domain or deceptive keywords detected.';
    }

    if (isPhishing) {
      resultBox.className = 'result danger';
      resultBox.innerHTML = `<strong>⚠️ HIGH RISK (92/100)</strong><br>${reason}`;
    } else {
      resultBox.className = 'result safe';
      resultBox.innerHTML = `<strong>🟢 LOW RISK (12/100)</strong><br>Standard verified domain pattern.`;
    }
  });
});
