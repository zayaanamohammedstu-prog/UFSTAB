/**
 * OratorHub Enhanced Application
 * Additional features and API integration
 */

// Authentication UI Functions
function showLoginModal() {
    document.getElementById('authModal').style.display = 'flex';
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('registerForm').style.display = 'none';
}

function showRegisterForm() {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'block';
}

function showLoginForm() {
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('registerForm').style.display = 'none';
}

function closeAuthModal() {
    document.getElementById('authModal').style.display = 'none';
}

async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        await OratorHub.auth.login({ email, password });
        closeAuthModal();
        updateUIForLoggedInUser();
    } catch (error) {
        console.error('Login error:', error);
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const userData = {
        email: document.getElementById('regEmail').value,
        username: document.getElementById('regUsername').value,
        password: document.getElementById('regPassword').value,
        full_name: document.getElementById('regFullName').value,
        institution: document.getElementById('regInstitution').value,
        role: document.getElementById('regRole').value
    };
    
    try {
        await OratorHub.auth.register(userData);
        closeAuthModal();
        updateUIForLoggedInUser();
    } catch (error) {
        console.error('Registration error:', error);
    }
}

function updateUIForLoggedInUser() {
    const user = OratorHub.getCurrentUser();
    
    if (user) {
        document.getElementById('loginBtn').style.display = 'none';
        document.getElementById('userMenu').style.display = 'flex';
        document.getElementById('userName').textContent = user.full_name || user.username;
    } else {
        document.getElementById('loginBtn').style.display = 'block';
        document.getElementById('userMenu').style.display = 'none';
    }
}

// PWA Service Worker Registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/service-worker.js')
            .then(registration => {
                console.log('Service Worker registered:', registration);
            })
            .catch(error => {
                console.log('Service Worker registration failed:', error);
            });
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    updateUIForLoggedInUser();
    
    // Check for updates every 30 seconds
    if (OratorHub.auth.isLoggedIn()) {
        setInterval(() => {
            OratorHub.auth.getCurrentUser().catch(() => {
                // Token expired, logout
                OratorHub.auth.logout();
            });
        }, 30000);
    }
});

// Enhanced Notification System
let notificationQueue = [];
let isShowingNotification = false;

function showNotificationEnhanced(message, type = 'info', duration = 3000) {
    notificationQueue.push({ message, type, duration });
    
    if (!isShowingNotification) {
        displayNextNotification();
    }
}

function displayNextNotification() {
    if (notificationQueue.length === 0) {
        isShowingNotification = false;
        return;
    }
    
    isShowingNotification = true;
    const { message, type, duration } = notificationQueue.shift();
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove(); displayNextNotification();" style="background: transparent; border: none; color: white; cursor: pointer; font-size: 1.2rem; margin-left: 1rem;">&times;</button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('fadeOut');
        setTimeout(() => {
            notification.remove();
            displayNextNotification();
        }, 300);
    }, duration);
}

// Real-time Event Handlers
OratorHub.eventStream.on('tournament_created', (data) => {
    showNotificationEnhanced(`New tournament: ${data.name}`, 'info');
});

OratorHub.eventStream.on('pairing_update', (data) => {
    showNotificationEnhanced('Pairings updated!', 'info');
    // Auto-refresh if on draw page
    if (document.querySelector('#draw.tab-content.active')) {
        loadCurrentDraw();
    }
});

OratorHub.eventStream.on('result_update', (data) => {
    showNotificationEnhanced('Results updated!', 'success');
    // Auto-refresh if on results/standings page
    if (document.querySelector('#tab.tab-content.active')) {
        displayTeamTab();
        displaySpeakerTab();
    }
});

OratorHub.eventStream.on('motion_released', (data) => {
    showNotificationEnhanced(`Motion released: ${data.motion}`, 'info');
});

// Offline Support
window.addEventListener('online', () => {
    showNotificationEnhanced('Connection restored', 'success');
});

window.addEventListener('offline', () => {
    showNotificationEnhanced('You are offline. Changes will sync when connection is restored.', 'warning', 5000);
});

// Export Data with API Integration
async function exportAllDataEnhanced() {
    try {
        const data = {
            timestamp: new Date().toISOString(),
            user: OratorHub.getCurrentUser(),
            localData: {
                tournament: tournamentData,
                publicSpeaking: publicSpeakingData
            }
        };
        
        const json = JSON.stringify(data, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `oratorhub_backup_${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        showNotificationEnhanced('Data exported successfully!', 'success');
    } catch (error) {
        console.error('Export error:', error);
        showNotificationEnhanced('Error exporting data', 'error');
    }
}

// Load function placeholder for draw
async function loadCurrentDraw() {
    // Implementation depends on current tournament context
    console.log('Loading current draw...');
}

// Check browser compatibility
function checkBrowserCompatibility() {
    const features = {
        serviceWorker: 'serviceWorker' in navigator,
        localStorage: typeof localStorage !== 'undefined',
        fetch: typeof fetch !== 'undefined',
        eventSource: typeof EventSource !== 'undefined'
    };
    
    const unsupported = Object.keys(features).filter(key => !features[key]);
    
    if (unsupported.length > 0) {
        showNotificationEnhanced(
            `Your browser doesn't support: ${unsupported.join(', ')}. Some features may not work.`,
            'warning',
            10000
        );
    }
}

checkBrowserCompatibility();
