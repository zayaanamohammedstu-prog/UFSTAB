/**
 * OratorHub API Client
 * Handles all communication with the backend API
 */

// API Configuration
const API_BASE_URL = window.location.origin + '/api';
let authToken = localStorage.getItem('authToken') || null;
let currentUser = null;

// API Helper Functions
const api = {
    /**
     * Make an API request
     */
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        // Add auth token if available
        if (authToken) {
            headers['Authorization'] = `Bearer ${authToken}`;
        }

        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'API request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    /**
     * GET request
     */
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },

    /**
     * POST request
     */
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    /**
     * PUT request
     */
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    },

    /**
     * Upload file
     */
    async upload(endpoint, formData) {
        const url = `${API_BASE_URL}${endpoint}`;
        const headers = {};

        if (authToken) {
            headers['Authorization'] = `Bearer ${authToken}`;
        }

        const response = await fetch(url, {
            method: 'POST',
            headers,
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Upload failed');
        }

        return data;
    }
};

// Authentication Functions
const auth = {
    /**
     * Register new user
     */
    async register(userData) {
        try {
            const response = await api.post('/auth/register', userData);
            authToken = response.access_token;
            currentUser = response.user;
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            showNotification('Registration successful!', 'success');
            return response;
        } catch (error) {
            showNotification(error.message, 'error');
            throw error;
        }
    },

    /**
     * Login user
     */
    async login(credentials) {
        try {
            const response = await api.post('/auth/login', credentials);
            authToken = response.access_token;
            currentUser = response.user;
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            showNotification('Login successful!', 'success');
            return response;
        } catch (error) {
            showNotification(error.message, 'error');
            throw error;
        }
    },

    /**
     * Logout user
     */
    logout() {
        authToken = null;
        currentUser = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('currentUser');
        showNotification('Logged out successfully', 'success');
        window.location.reload();
    },

    /**
     * Get current user
     */
    async getCurrentUser() {
        if (!authToken) return null;

        try {
            const response = await api.get('/auth/me');
            currentUser = response;
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            return currentUser;
        } catch (error) {
            // Token might be invalid
            this.logout();
            return null;
        }
    },

    /**
     * Check if user is logged in
     */
    isLoggedIn() {
        return authToken !== null;
    },

    /**
     * Update user profile
     */
    async updateProfile(userData) {
        try {
            const response = await api.put('/auth/me', userData);
            currentUser = response.user;
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            showNotification('Profile updated successfully!', 'success');
            return response;
        } catch (error) {
            showNotification(error.message, 'error');
            throw error;
        }
    }
};

// Tournament API Functions
const tournaments = {
    /**
     * Get all tournaments
     */
    async getAll() {
        try {
            return await api.get('/tournaments');
        } catch (error) {
            showNotification('Error loading tournaments', 'error');
            throw error;
        }
    },

    /**
     * Get tournament by ID
     */
    async getById(id) {
        try {
            return await api.get(`/tournaments/${id}`);
        } catch (error) {
            showNotification('Error loading tournament', 'error');
            throw error;
        }
    },

    /**
     * Create tournament
     */
    async create(tournamentData) {
        try {
            const response = await api.post('/tournaments', tournamentData);
            showNotification('Tournament created successfully!', 'success');
            return response;
        } catch (error) {
            showNotification(error.message, 'error');
            throw error;
        }
    },

    /**
     * Update tournament
     */
    async update(id, tournamentData) {
        try {
            const response = await api.put(`/tournaments/${id}`, tournamentData);
            showNotification('Tournament updated successfully!', 'success');
            return response;
        } catch (error) {
            showNotification(error.message, 'error');
            throw error;
        }
    },

    /**
     * Delete tournament
     */
    async delete(id) {
        try {
            const response = await api.delete(`/tournaments/${id}`);
            showNotification('Tournament deleted successfully!', 'success');
            return response;
        } catch (error) {
            showNotification(error.message, 'error');
            throw error;
        }
    },

    /**
     * Get tournament standings
     */
    async getStandings(id) {
        try {
            return await api.get(`/tournaments/${id}/standings`);
        } catch (error) {
            showNotification('Error loading standings', 'error');
            throw error;
        }
    }
};

// Real-time Updates with SSE
class EventStream {
    constructor() {
        this.eventSource = null;
        this.listeners = {};
    }

    /**
     * Connect to event stream
     */
    connect() {
        if (this.eventSource) {
            return;
        }

        this.eventSource = new EventSource(`${API_BASE_URL}/stream/events`);

        this.eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleEvent(data);
            } catch (error) {
                console.error('Error parsing event:', error);
            }
        };

        this.eventSource.onerror = (error) => {
            console.error('SSE Error:', error);
            // Reconnect after 5 seconds
            setTimeout(() => {
                this.eventSource.close();
                this.eventSource = null;
                this.connect();
            }, 5000);
        };

        console.log('Connected to event stream');
    },

    /**
     * Disconnect from event stream
     */
    disconnect() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
            console.log('Disconnected from event stream');
        }
    },

    /**
     * Handle incoming event
     */
    handleEvent(data) {
        const { type, data: eventData } = data;

        // Call registered listeners
        if (this.listeners[type]) {
            this.listeners[type].forEach(callback => callback(eventData));
        }

        // Call global listeners
        if (this.listeners['*']) {
            this.listeners['*'].forEach(callback => callback(data));
        }
    },

    /**
     * Register event listener
     */
    on(eventType, callback) {
        if (!this.listeners[eventType]) {
            this.listeners[eventType] = [];
        }
        this.listeners[eventType].push(callback);
    },

    /**
     * Unregister event listener
     */
    off(eventType, callback) {
        if (!this.listeners[eventType]) {
            return;
        }
        this.listeners[eventType] = this.listeners[eventType].filter(
            cb => cb !== callback
        );
    }
}

// Initialize event stream
const eventStream = new EventStream();

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Load auth token from storage
    const storedToken = localStorage.getItem('authToken');
    if (storedToken) {
        authToken = storedToken;
        const storedUser = localStorage.getItem('currentUser');
        if (storedUser) {
            currentUser = JSON.parse(storedUser);
        }
    }

    // Connect to event stream if logged in
    if (auth.isLoggedIn()) {
        eventStream.connect();
        
        // Listen for real-time updates
        eventStream.on('pairing_update', (data) => {
            showNotification('New pairings available!', 'info');
            // Refresh pairings if on draw page
            if (document.querySelector('#draw.tab-content.active')) {
                // Reload draw
            }
        });

        eventStream.on('result_update', (data) => {
            showNotification('Results updated!', 'info');
            // Refresh results if on results page
        });
    }
});

// Export for use in other scripts
window.OratorHub = {
    api,
    auth,
    tournaments,
    eventStream,
    getAuthToken: () => authToken,
    getCurrentUser: () => currentUser
};
