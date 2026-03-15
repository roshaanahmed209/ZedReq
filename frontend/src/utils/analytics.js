/**
 * Analytics tracking utility for ZedReq frontend
 * Tracks page views, link clicks, and user interactions
 */

const COLLECTOR_URL = import.meta.env.VITE_BACKOFFICE_COLLECTOR_URL || 'http://localhost:5001/api/collect';
const COLLECTOR_API_KEY = import.meta.env.VITE_COLLECTOR_API_KEY || '';

// Generate or retrieve session ID
function getSessionId() {
    let sessionId = sessionStorage.getItem('analytics_session_id');
    if (!sessionId) {
        sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        sessionStorage.setItem('analytics_session_id', sessionId);
    }
    return sessionId;
}

// Get user ID from localStorage or context
function getUserId() {
    // Try to get from localStorage (set by auth system)
    const userStr = localStorage.getItem('user');
    if (userStr) {
        try {
            const user = JSON.parse(userStr);
            return user.uid || user.id || null;
        } catch (e) {
            return null;
        }
    }
    return null;
}

// Get device/browser info
function getDeviceInfo() {
    const ua = navigator.userAgent;
    let deviceType = 'desktop';
    let browser = 'unknown';
    let os = 'unknown';
    
    // Device type
    if (/mobile|android|iphone|ipad/i.test(ua)) {
        deviceType = 'mobile';
    } else if (/tablet|ipad/i.test(ua)) {
        deviceType = 'tablet';
    }
    
    // Browser
    if (ua.includes('Chrome')) browser = 'Chrome';
    else if (ua.includes('Firefox')) browser = 'Firefox';
    else if (ua.includes('Safari')) browser = 'Safari';
    else if (ua.includes('Edge')) browser = 'Edge';
    
    // OS
    if (ua.includes('Windows')) os = 'Windows';
    else if (ua.includes('Mac')) os = 'macOS';
    else if (ua.includes('Linux')) os = 'Linux';
    else if (ua.includes('Android')) os = 'Android';
    else if (ua.includes('iOS')) os = 'iOS';
    
    return { deviceType, browser, os };
}

// Send events to collector
async function sendEvents(events) {
    // Skip if API key is not configured (analytics disabled)
    if (!COLLECTOR_API_KEY) {
        return;
    }
    
    try {
        const headers = {
            'Content-Type': 'application/json',
            'X-API-Key': COLLECTOR_API_KEY,
        };
        
        await fetch(`${COLLECTOR_URL}/events`, {
            method: 'POST',
            headers,
            body: JSON.stringify(events),
        });
    } catch (error) {
        console.debug('Analytics: Failed to send events', error);
    }
}

// Track page view
export function trackPageView(pagePath, pageTitle = null) {
    const event = {
        type: 'page_view',
        user_id: getUserId(),
        session_id: getSessionId(),
        page_path: pagePath,
        page_title: pageTitle || document.title,
        referrer: document.referrer,
        load_time_ms: performance.now(),
    };
    
    sendEvents([event]);
    
    // Update session activity
    updateSessionActivity();
}

// Track link click
export function trackLinkClick(linkUrl, linkText = null, isExternal = false) {
    const event = {
        type: 'link_click',
        user_id: getUserId(),
        session_id: getSessionId(),
        link_url: linkUrl,
        link_text: linkText,
        page_path: window.location.pathname,
        is_external: isExternal,
    };
    
    sendEvents([event]);
}

// Track user interaction (button click, etc.)
export function trackInteraction(interactionType, elementId = null, elementType = null, metadata = null) {
    const event = {
        type: 'interaction',
        user_id: getUserId(),
        session_id: getSessionId(),
        interaction_type: interactionType,
        element_id: elementId,
        element_type: elementType,
        page_path: window.location.pathname,
        metadata: metadata,
    };
    
    sendEvents([event]);
}

// Update session activity
async function updateSessionActivity() {
    // Skip if API key is not configured (analytics disabled)
    if (!COLLECTOR_API_KEY) {
        return;
    }
    
    try {
        const headers = {
            'Content-Type': 'application/json',
            'X-API-Key': COLLECTOR_API_KEY,
        };
        
        await fetch(`${COLLECTOR_URL}/session/update?session_id=${getSessionId()}`, {
            method: 'POST',
            headers,
        });
    } catch (error) {
        console.debug('Analytics: Failed to update session', error);
    }
}

// Start session
export async function startSession() {
    // Skip if API key is not configured (analytics disabled)
    if (!COLLECTOR_API_KEY) {
        return;
    }
    
    const deviceInfo = getDeviceInfo();
    
    try {
        const headers = {
            'Content-Type': 'application/json',
            'X-API-Key': COLLECTOR_API_KEY,
        };
        
        await fetch(`${COLLECTOR_URL}/session/start`, {
            method: 'POST',
            headers,
            body: JSON.stringify({
                user_id: getUserId(),
                session_id: getSessionId(),
                device_type: deviceInfo.deviceType,
                browser: deviceInfo.browser,
                os: deviceInfo.os,
            }),
        });
    } catch (error) {
        console.debug('Analytics: Failed to start session', error);
    }
}

// End session
export async function endSession() {
    // Skip if API key is not configured (analytics disabled)
    if (!COLLECTOR_API_KEY) {
        sessionStorage.removeItem('analytics_session_id');
        return;
    }
    
    try {
        const headers = {
            'Content-Type': 'application/json',
            'X-API-Key': COLLECTOR_API_KEY,
        };
        
        await fetch(`${COLLECTOR_URL}/session/end?session_id=${getSessionId()}`, {
            method: 'POST',
            headers,
        });
        
        sessionStorage.removeItem('analytics_session_id');
    } catch (error) {
        console.debug('Analytics: Failed to end session', error);
    }
}

// Initialize analytics - set up automatic tracking
export function initAnalytics() {
    // Start session
    startSession();
    
    // Track initial page view
    trackPageView(window.location.pathname);
    
    // Track all link clicks automatically
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (link && link.href) {
            const isExternal = link.hostname !== window.location.hostname;
            trackLinkClick(link.href, link.textContent?.trim() || null, isExternal);
        }
    }, true);
    
    // Track page visibility changes (for session tracking)
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
            updateSessionActivity();
        }
    });
    
    // Track before unload (end session)
    window.addEventListener('beforeunload', () => {
        endSession();
    });
}
