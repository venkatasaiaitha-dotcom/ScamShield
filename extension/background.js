// ScamShield Background Service Worker
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "scamshield-inspect-text",
    title: "🛡️ Inspect selection with ScamShield",
    contexts: ["selection", "link"]
  });
});

chrome.contextMenus.onClicked.addListener((info) => {
  if (info.menuItemId === "scamshield-inspect-text") {
    const textToCheck = info.selectionText || info.linkUrl;
    console.log("ScamShield checking selected item:", textToCheck);
    // In production, opens analysis modal or notifies user
  }
});
