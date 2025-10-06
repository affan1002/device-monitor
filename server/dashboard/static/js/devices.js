// ========================================
// Devices Page JavaScript
// ========================================

const API_BASE_URL = '/api/v1';
let allDevices = [];

// Load devices when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadAllDevices();
    
    // Refresh every 30 seconds
    setInterval(loadAllDevices, 30000);
    
    // Search functionality
    document.getElementById('search-input').addEventListener('input', function(e) {
        searchDevices(e.target.value);
    });
});

/**
 * Load all devices from API
 */
async function loadAllDevices() {
    try {
        const response = await fetch(`${API_BASE_URL}/devices`);
        const data = await response.json();
        
        allDevices = data.devices || [];
        displayDevices(allDevices);
        
    } catch (error) {
        console.error('Error loading devices:', error);
        document.getElementById('devices-grid').innerHTML = `
            <div class="error-card">
                <p>❌ Failed to load devices. Make sure the server is running!</p>
            </div>
        `;
    }
}

/**
 * Display devices in grid
 */
function displayDevices(devices) {
    const grid = document.getElementById('devices-grid');
    
    if (!devices || devices.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <p>📭 No devices found. Start the agent to register a device!</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = devices.map(device => `
        <div class="device-card ${device.is_active ? 'active' : 'inactive'}">
            <div class="device-header">
                <h3>🖥️ ${escapeHtml(device.hostname)}</h3>
                <span class="badge ${device.is_active ? 'badge-success' : 'badge-danger'}">
                    ${device.is_active ? '● Online' : '○ Offline'}
                </span>
            </div>
            <div class="device-body">
                <p><strong>Device ID:</strong> ${escapeHtml(device.device_id)}</p>
                <p><strong>Platform:</strong> ${escapeHtml(device.platform || 'Unknown')}</p>
                <p><strong>Last Seen:</strong> ${formatDateTime(device.last_seen)}</p>
                <p><strong>Registered:</strong> ${formatDateTime(device.created_at)}</p>
            </div>
            <div class="device-footer">
                <button class="btn btn-primary btn-sm" onclick="viewDeviceDetails('${device.device_id}')">
                    View Details
                </button>
            </div>
        </div>
    `).join('');
}

/**
 * Filter devices by status
 */
function filterDevices(filter) {
    let filtered = allDevices;
    
    if (filter === 'active') {
        filtered = allDevices.filter(d => d.is_active);
    } else if (filter === 'inactive') {
        filtered = allDevices.filter(d => !d.is_active);
    }
    
    displayDevices(filtered);
}

/**
 * Search devices
 */
function searchDevices(query) {
    if (!query) {
        displayDevices(allDevices);
        return;
    }
    
    const filtered = allDevices.filter(device => 
        device.hostname.toLowerCase().includes(query.toLowerCase()) ||
        device.device_id.toLowerCase().includes(query.toLowerCase()) ||
        (device.platform && device.platform.toLowerCase().includes(query.toLowerCase()))
    );
    
    displayDevices(filtered);
}

/**
 * View device details
 */
function viewDeviceDetails(deviceId) {
    // Navigate to device details page
    window.location.href = `/devices/${deviceId}`;
}

/**
 * Utility functions
 */
function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    // Convert to IST (UTC+5:30)
    return date.toLocaleString('en-IN', {
        timeZone: 'Asia/Kolkata',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
    });
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
