// ============================================
// Focus OS Browser Monitor
// ============================================

// Get the browser name
function getBrowserName() {

    const userAgent = navigator.userAgent.toLowerCase();

    if (userAgent.includes("edg")) {
        return "edge";
    }

    if (userAgent.includes("chrome")) {
        return "chrome";
    }

    return "browser";
}


// Extract only the domain from the URL
function getDomain(url) {

    try {

        const parsedURL = new URL(url);

        return parsedURL.hostname
            .replace(/^www\./, "");

    } catch (error) {

        return "unknown";
    }
}


// Send the currently active tab to Focus OS
function sendCurrentTabToFocusOS() {

    chrome.tabs.query(
        {
            active: true,
            lastFocusedWindow: true
        },

        function(tabs) {

            // No active tab
            if (!tabs || tabs.length === 0) {

                console.log(
                    "Focus OS: No active tab."
                );

                return;
            }


            const tab = tabs[0];


            // No URL available
            if (!tab.url) {

                console.log(
                    "Focus OS: No URL available."
                );

                return;
            }


            // Get browser and domain
            const browser = getBrowserName();

            const domain = getDomain(
                tab.url
            );


            console.log(
                "Focus OS sending:",
                browser,
                domain
            );


            // Build local Focus OS URL
            const focusOSUrl =
                "http://127.0.0.1:8765/update?" +
                "browser=" +
                encodeURIComponent(browser) +
                "&domain=" +
                encodeURIComponent(domain);


            // Send information to Focus OS
            fetch(
                focusOSUrl,
                {
                    method: "GET",
                    cache: "no-store"
                }
            )

            .then(function(response) {

                if (!response.ok) {

                    throw new Error(
                        "HTTP error: " +
                        response.status
                    );
                }

                return response.json();

            })

            .then(function(data) {

                console.log(
                    "Focus OS server response:",
                    data
                );

            })

            .catch(function(error) {

                console.error(
                    "Focus OS connection error:",
                    error
                );

            });

        }
    );
}



// ============================================
// TAB CHANGED
// ============================================

chrome.tabs.onActivated.addListener(
    function(activeInfo) {

        console.log(
            "Focus OS: Active tab changed."
        );

        sendCurrentTabToFocusOS();

    }
);



// ============================================
// BROWSER WINDOW CHANGED
// ============================================

chrome.windows.onFocusChanged.addListener(
    function(windowId) {

        console.log(
            "Focus OS: Browser window changed."
        );

        sendCurrentTabToFocusOS();

    }
);



// ============================================
// PAGE NAVIGATION
// ============================================

chrome.tabs.onUpdated.addListener(
    function(tabId, changeInfo, tab) {

        // Only monitor the active tab
        if (!tab.active) {
            return;
        }


        // Wait until the page has finished loading
        if (changeInfo.status === "complete") {

            console.log(
                "Focus OS: Active page loaded."
            );

            sendCurrentTabToFocusOS();

        }

    }
);



// ============================================
// EXTENSION STARTUP
// ============================================

sendCurrentTabToFocusOS();


console.log(
    "Focus OS browser monitor started."
);