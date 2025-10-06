// ========================================
// Device Details Page JavaScript
// ========================================

const API_BASE_URL = '/api/v1';
let deviceId = null;
let cpuChart, memoryChart, diskChart;

// Get device ID from URL
document.addEventListener('DOMContentLoaded', function() {
    // Extract device ID from URL path (/devices/device-001)
    const pathParts = window.location.pathname.split('/');
    deviceId = pathParts[pathParts.length - 1];
    
    if (deviceId) {
        loadDeviceDetails();
        
        // Refresh data every 30 seconds
        setInterval(() => {
            loadDeviceDetails();
            updateCharts();
        }, 30000);
    } else {
        showError();
    }
});

/**
 * Load all device details
 */
async function loadDeviceDetails() {
    try {
        // Load device info
        await loadDeviceInfo();
        
        // Load device stats
        await loadDeviceStats();
        
        // Load power events
        await loadPowerEvents();
        
        // Load system stats history
        await loadStatsHistory();
        
        // Initialize charts
        if (!cpuChart) {
            initCharts();
        } else {
            updateCharts();
        }
        
        // Hide loading, show content
        document.getElementById('loading-state').style.display = 'none';
        document.getElementById('device-content').style.display = 'block';
        
    } catch (error) {
        console.error('Error loading device details:', error);
        showError();
    }
}

/**
 * Load device basic information
 */
async function loadDeviceInfo() {
    const response = await fetch(`${API_BASE_URL}/devices/${deviceId}`);
    
    if (!response.ok) {
        throw new Error('Device not found');
    }
    
    const data = await response.json();
    const device = data.device;
    
    // Update page title and header
    document.getElementById('device-hostname').textContent = device.hostname;
    document.title = `${device.hostname} - Device Monitor`;
    
    // Update status badge
    const statusBadge = document.getElementById('device-status-badge');
    statusBadge.textContent = device.is_active ? '● Online' : '○ Offline';
    statusBadge.className = `badge ${device.is_active ? 'badge-success' : 'badge-danger'}`;
    
    // Update basic info
    document.getElementById('device-id').textContent = device.device_id;
    document.getElementById('hostname').textContent = device.hostname;
    document.getElementById('platform').textContent = device.platform || 'Unknown';
    document.getElementById('platform-version').textContent = device.platform_version || 'Unknown';
    
    // Update timing info
    document.getElementById('last-seen').textContent = formatDateTime(device.last_seen);
    document.getElementById('registered').textContent = formatDateTime(device.created_at);
    document.getElementById('is-active').textContent = device.is_active ? 'Active' : 'Inactive';
}

/**
 * Load current device statistics
 */
async function loadDeviceStats() {
    const response = await fetch(`${API_BASE_URL}/devices/${deviceId}/stats?limit=1`);
    const data = await response.json();
    
    if (data.stats && data.stats.length > 0) {
        const stat = data.stats[0];
        
        // Update current stats
        document.getElementById('current-cpu').textContent = `${stat.cpu_percent.toFixed(1)}%`;
        document.getElementById('current-memory').textContent = `${stat.memory_percent.toFixed(1)}%`;
        document.getElementById('current-disk').textContent = `${stat.disk_percent.toFixed(1)}%`;
        document.getElementById('uptime').textContent = formatUptime(stat.uptime);
        document.getElementById('stats-timestamp').textContent = formatDateTime(stat.timestamp);
    } else {
        document.getElementById('current-cpu').textContent = 'No data';
        document.getElementById('current-memory').textContent = 'No data';
        document.getElementById('current-disk').textContent = 'No data';
        document.getElementById('uptime').textContent = 'No data';
        document.getElementById('stats-timestamp').textContent = 'No data';
    }
}

/**
 * Load power events
 */
async function loadPowerEvents() {
    const response = await fetch(`${API_BASE_URL}/devices/${deviceId}/power_events?limit=20`);
    const data = await response.json();
    
    const tbody = document.getElementById('events-tbody');
    
    if (!data.events || data.events.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted">No events recorded</td></tr>';
        return;
    }
    
    // Build table rows
    tbody.innerHTML = data.events.map(event => {
        const eventBadge = getEventBadge(event.event_type);
        return `
            <tr>
                <td>${eventBadge}</td>
                <td>${formatDateTime(event.timestamp)}</td>
                <td>${escapeHtml(event.details || '-')}</td>
            </tr>
        `;
    }).join('');
}

/**
 * Load system statistics history
 */
async function loadStatsHistory() {
    const response = await fetch(`${API_BASE_URL}/devices/${deviceId}/stats?limit=20`);
    const data = await response.json();
    
    const tbody = document.getElementById('stats-tbody');
    
    if (!data.stats || data.stats.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No statistics recorded</td></tr>';
        return;
    }
    
    // Build table rows (reverse to show newest first)
    tbody.innerHTML = data.stats.map(stat => `
        <tr>
            <td>${formatDateTime(stat.timestamp)}</td>
            <td>${stat.cpu_percent.toFixed(1)}%</td>
            <td>${stat.memory_percent.toFixed(1)}%</td>
            <td>${stat.disk_percent.toFixed(1)}%</td>
            <td>${formatUptime(stat.uptime)}</td>
        </tr>
    `).join('');
}

/**
 * Initialize performance charts
 */
function initCharts() {
    // CPU Chart
    const cpuCtx = document.getElementById('device-cpu-chart');
    cpuChart = new Chart(cpuCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'CPU Usage (%)',
                data: [],
                borderColor: 'rgb(37, 99, 235)',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
    
    // Memory Chart
    const memoryCtx = document.getElementById('device-memory-chart');
    memoryChart = new Chart(memoryCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Memory Usage (%)',
                data: [],
                borderColor: 'rgb(124, 58, 237)',
                backgroundColor: 'rgba(124, 58, 237, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
    
    // Disk Chart
    const diskCtx = document.getElementById('device-disk-chart');
    diskChart = new Chart(diskCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Disk Usage (%)',
                data: [],
                borderColor: 'rgb(16, 185, 129)',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
    
    // Load initial chart data
    updateCharts();
}

/**
 * Update charts with latest data
 */
async function updateCharts() {
    try {
        const response = await fetch(`${API_BASE_URL}/devices/${deviceId}/stats?limit=50`);
        const data = await response.json();
        
        if (!data.stats || data.stats.length === 0) {
            return;
        }
        
        // Reverse to show oldest to newest
        const stats = data.stats.reverse();
        
        const labels = stats.map(s => formatTime(s.timestamp));
        const cpuData = stats.map(s => s.cpu_percent);
        const memoryData = stats.map(s => s.memory_percent);
        const diskData = stats.map(s => s.disk_percent);
        
        // Update CPU chart
        if (cpuChart) {
            cpuChart.data.labels = labels;
            cpuChart.data.datasets[0].data = cpuData;
            cpuChart.update();
        }
        
        // Update Memory chart
        if (memoryChart) {
            memoryChart.data.labels = labels;
            memoryChart.data.datasets[0].data = memoryData;
            memoryChart.update();
        }
        
        // Update Disk chart
        if (diskChart) {
            diskChart.data.labels = labels;
            diskChart.data.datasets[0].data = diskData;
            diskChart.update();
        }
        
    } catch (error) {
        console.error('Error updating charts:', error);
    }
}

/**
 * Get badge HTML for event type
 */
function getEventBadge(eventType) {
    const badges = {
        'STARTUP': '<span class="badge badge-success">🟢 STARTUP</span>',
        'SHUTDOWN': '<span class="badge badge-danger">🔴 SHUTDOWN</span>',
        'SLEEP': '<span class="badge badge-info">😴 SLEEP</span>',
        'WAKE': '<span class="badge badge-warning">⏰ WAKE</span>',
        'BATTERY_CHARGING': '<span class="badge badge-success">🔌 CHARGING</span>',
        'BATTERY_UNPLUGGED': '<span class="badge badge-warning">🔋 UNPLUGGED</span>',
        'BATTERY_FULL': '<span class="badge badge-success">✅ BATTERY FULL</span>',
        'BATTERY_LOW': '<span class="badge badge-warning">⚠️ BATTERY LOW</span>',
        'BATTERY_CRITICAL': '<span class="badge badge-danger">🚨 BATTERY CRITICAL</span>'
    };
    
    return badges[eventType] || `<span class="badge badge-info">${escapeHtml(eventType)}</span>`;
}

/**
 * Show error state
 */
function showError() {
    document.getElementById('loading-state').style.display = 'none';
    document.getElementById('error-state').style.display = 'block';
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

function formatTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-IN', {
        timeZone: 'Asia/Kolkata',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });
}

function formatUptime(seconds) {
    if (!seconds) return '0s';
    
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    let result = '';
    if (days > 0) result += `${days}d `;
    if (hours > 0) result += `${hours}h `;
    if (minutes > 0) result += `${minutes}m`;
    
    return result || '0m';
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
