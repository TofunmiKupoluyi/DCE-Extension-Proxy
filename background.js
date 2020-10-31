/*
 * --------------------------------------------------
 * Keep list of tabs outside of request callback
 * --------------------------------------------------
 */
var tabs = {};

// Get all existing tabs
chrome.tabs.query({}, function(results) {
    results.forEach(function(tab) {
        tabs[tab.id] = tab.url;
    });
});

// Create tab event listeners
function onUpdatedListener(tabId, changeInfo, tab) {
    tabs[tab.id] = tab.url;
}
function onRemovedListener(tabId) {
    delete tabs[tabId];
}

// Subscribe to tab events
chrome.tabs.onUpdated.addListener(onUpdatedListener);
chrome.tabs.onRemoved.addListener(onRemovedListener);

var callback = function(details) {
    chrome.extension.getBackgroundPage().console.log(details.requestHeaders);
    let initiatingUrl = (tabs[details.tabId] != null) ? tabs[details.tabId] : details.initiator;
    details.requestHeaders.push({name: "initiating-url", value: initiatingUrl});
    return {
        requestHeaders: details.requestHeaders
    };
}
    


// var filter = {urls:["http://*/*.js*", "https://*/*.js*", "http://*/proxy_return_capstone", "https://*/proxy_return_capstone"]};
var filter = {urls:["http://*/*.*", "https://*/*.*"], types: ["script"]};
var opt_extraInfoSpec = ["blocking", "requestHeaders", "extraHeaders"];


chrome.webRequest.onBeforeSendHeaders.addListener(callback, filter, opt_extraInfoSpec);
