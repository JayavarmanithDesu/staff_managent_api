/**
 * Core Frontend Logic (app.js)
 * Handles JWT authentication, state management via LocalStorage, 
 * and API interactions for Check-in/Check-out functionality.
 */

// --- Constants ---
// Define your API base URL here. Assumes Django is running on localhost port 8000.
const API_BASE_URL = 'http://127.0.0.1:8000/api/'; 
const LOCAL_STORAGE_KEY = 'staffToken';

// Utility function to get the current date in YYYY-MM-DD format
const getTodayDate = () => {
    return new Date().toISOString().split('T')[0];
};

// --- Token Management ---

/**
 * Stores the received access token in LocalStorage.
 * @param {string} token - The JWT access token.
 */
const saveToken = (token) => {
    localStorage.setItem(LOCAL_STORAGE_KEY, token);
};

/**
 * Retrieves the JWT token from LocalStorage.
 * @returns {string | null} The stored token or null.
 */
const getToken = () => {
    return localStorage.getItem(LOCAL_STORAGE_KEY);
};

/**
 * Removes the JWT token from LocalStorage.
 */
const removeToken = () => {
    localStorage.removeItem(LOCAL_STORAGE_KEY);
};

// --- API Utility ---

/**
 * Helper function to make authenticated API requests.
 * @param {string} url - The full API endpoint URL.
 * @param {object} options - Fetch options (method, headers, body, etc.).
 * @returns {Promise<Response>} The fetch Response object.
 */
const apiFetch = async (endpoint, options = {}) => {
    const token = getToken();
    const headers = options.headers || {};

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    headers['Content-Type'] = 'application/json';

    return fetch(API_BASE_URL + endpoint, {
        ...options,
        headers,
    });
};

// --- Authentication and Navigation ---

/**
 * Handles the login process: POSTs credentials, saves token, redirects.
 */
const loginUser = async () => {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const messageEl = document.getElementById('message');
    
    // Clear previous messages
    messageEl.textContent = '';
    messageEl.classList.add('hidden');

    try {
        const response = await fetch(API_BASE_URL + 'token/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            saveToken(data.access);
            window.location.href = 'dashboard.html';
        } else {
            // Handle API errors (e.g., Invalid credentials)
            messageEl.textContent = data.detail || 'Login failed. Check username and password.';
            messageEl.classList.remove('hidden');
        }
    } catch (error) {
        console.error('Network Error:', error);
        messageEl.textContent = 'A network error occurred. Check server connection.';
        messageEl.classList.remove('hidden');
    }
};

/**
 * Logs out the user and redirects to the login page.
 */
const logoutUser = () => {
    removeToken();
    window.location.href = 'login.html';
};

/**
 * Checks if the user is authenticated; if not, redirects to login.
 */
const checkAuthentication = () => {
    if (!getToken()) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
};

// --- Dashboard Logic ---

/**
 * Initializes the dashboard: fetches user info and checks attendance status.
 */
const initializeDashboard = async () => {
    if (!checkAuthentication()) return;

    // Display current date
    document.getElementById('dateDisplay').textContent = getTodayDate();
    
    try {
        // Fetch current user details (using a dedicated endpoint like /users/me/ is better, 
        // but for simplicity, we assume the first user is the logged in user for this demo fetch)
        // In a real app, you'd decode the JWT to get the user ID or use a /users/me/ endpoint.
        const userResponse = await apiFetch('v1/users/'); 
        const users = await userResponse.json();
        
        if (userResponse.ok && users.length > 0) {
            // Find the current user - this is a temporary workaround for a missing /me endpoint
            // In a real app, the API would return the current user's details directly.
            const currentUser = users.find(u => u.username === sessionStorage.getItem('username')) || users[0];

            if (currentUser) {
                document.getElementById('userName').textContent = currentUser.first_name || currentUser.username;
                sessionStorage.setItem('userId', currentUser.id); // Store ID for potential use
            }
        }
    } catch (error) {
        console.error('Error fetching user info:', error);
        // If user fetching fails, still allow attendance check
    }
    
    // Proceed to check attendance status
    checkAttendanceStatus();
};


/**
 * Checks the current attendance status and updates the button/UI state.
 */
const checkAttendanceStatus = async () => {
    const btn = document.getElementById('attendanceBtn');
    const statusMsg = document.getElementById('attendanceStatusMsg');
    const today = getTodayDate();

    statusMsg.textContent = 'Checking status...';
    btn.disabled = true;
    
    try {
        // Fetch today's records for the current user
        // We filter the list to only show today's records (backend filter would be more efficient)
        // Since the staff can only see their own, we just fetch all their records and filter client-side for today.
        const response = await apiFetch(`v1/attendance/?date=${today}`, { method: 'GET' });
        const records = await response.json();
        
        if (!response.ok) {
            throw new Error(records.detail || 'Failed to fetch attendance records.');
        }

        // Find the record for today
        const todayRecord = records.find(r => r.date === today);

        if (!todayRecord) {
            // State 1: No check-in record for today
            btn.textContent = 'CHECK IN';
            btn.className = 'w-full py-4 px-6 bg-green-600 text-white font-bold text-xl rounded-xl shadow-lg transition duration-300 transform hover:scale-[1.01] focus:outline-none focus:ring-4 focus:ring-opacity-50 focus:ring-green-500';
            statusMsg.textContent = 'Ready to start your shift.';
            btn.disabled = false;
        } else if (todayRecord && todayRecord.check_out_time === null) {
            // State 2: Check-in recorded, but no check-out
            btn.textContent = 'CHECK OUT';
            btn.className = 'w-full py-4 px-6 bg-yellow-600 text-white font-bold text-xl rounded-xl shadow-lg transition duration-300 transform hover:scale-[1.01] focus:outline-none focus:ring-4 focus:ring-opacity-50 focus:ring-yellow-500';
            statusMsg.textContent = `Checked in at ${new Date(todayRecord.check_in_time).toLocaleTimeString()}. Ready to check out.`;
            btn.disabled = false;
        } else {
            // State 3: Both check-in and check-out recorded
            btn.textContent = 'DONE FOR TODAY';
            btn.className = 'w-full py-4 px-6 bg-gray-500 text-white font-bold text-xl rounded-xl shadow-lg cursor-not-allowed';
            statusMsg.textContent = 'Attendance recorded for today.';
            btn.disabled = true;
        }

    } catch (error) {
        console.error('Error checking attendance status:', error);
        statusMsg.textContent = 'Error loading status.';
        btn.textContent = 'Retry';
        btn.className = 'w-full py-4 px-6 bg-red-600 text-white font-bold text-xl rounded-xl shadow-lg transition duration-300';
        btn.disabled = false;
        // Optionally, make the button retry the status check
        btn.onclick = checkAttendanceStatus; 
    }
};


/**
 * Sends a POST request to the appropriate check-in or check-out endpoint.
 */
const handleCheckAction = async () => {
    const btn = document.getElementById('attendanceBtn');
    const statusMsg = document.getElementById('attendanceStatusMsg');
    const confirmMsgEl = document.getElementById('confirmationMessage');
    
    const action = btn.textContent;
    let endpoint = '';
    let successMessage = '';
    
    // Determine the action based on the current button text
    if (action === 'CHECK IN') {
        endpoint = 'v1/attendance/check-in/';
        successMessage = 'Successfully Checked In!';
    } else if (action === 'CHECK OUT') {
        endpoint = 'v1/attendance/check-out/';
        successMessage = 'Successfully Checked Out!';
    } else {
        return; // Do nothing if button is disabled or in a final state
    }

    // Disable button and show loading state
    btn.disabled = true;
    btn.textContent = `Processing ${action}...`;
    statusMsg.textContent = 'Processing request...';
    confirmMsgEl.classList.add('hidden');

    try {
        const response = await apiFetch(endpoint, { method: 'POST' });

        if (response.ok || response.status === 201) { // 200 for checkout, 201 for checkin
            // Show confirmation message
            confirmMsgEl.textContent = successMessage;
            confirmMsgEl.className = 'mt-6 text-center text-sm font-semibold text-green-600';
            confirmMsgEl.classList.remove('hidden');

            // Wait a moment and then refresh status
            setTimeout(checkAttendanceStatus, 1500);
        } else {
            const errorData = await response.json();
            statusMsg.textContent = errorData.detail || `Failed to ${action}.`;
            btn.disabled = false;
            btn.textContent = action; // Revert button text
        }
    } catch (error) {
        console.error('Check action failed:', error);
        statusMsg.textContent = `A network error occurred during ${action}.`;
        btn.disabled = false;
        btn.textContent = action; // Revert button text
    }
};

// --- Initialization Logic ---

// Run initialization functions based on the current page
document.addEventListener('DOMContentLoaded', () => {
    // Check which page we are on
    const pathname = window.location.pathname;

    if (pathname.includes('dashboard.html')) {
        initializeDashboard();
    } else if (pathname.includes('login.html')) {
        // You might want to automatically redirect authenticated users here, 
        // but for now, we just ensure the login form is ready.
    }
});