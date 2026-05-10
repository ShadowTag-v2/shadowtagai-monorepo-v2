// Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

function saveSettings(settings) {
  const storageArea = settings.useLocalStorage ? chrome.storage.local : chrome.storage.sync;
  storageArea.set(settings, function() {
    console.log('Settings saved');
  });
}

function loadSettings(callback) {
  // We first check sync to see if the preference is stored there, 
  // then fallback to local if sync is empty or specifically set to local.
  chrome.storage.sync.get(['useLocalStorage'], function(syncResult) {
    const storageArea = syncResult.useLocalStorage ? chrome.storage.local : chrome.storage.sync;
    storageArea.get(null, function(items) {
      callback(items);
    });
  });
}
