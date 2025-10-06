// ========================================
// Device Monitor Dashboard - Main JavaScript
// ========================================

// API Base URL
const API_BASE_URL = '/api/v1';
const DASHBOARD_API_URL = '/dashboard/api';

// Initialize Chart.js charts
let cpuChart, memoryChart;

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initDashboard();
    loadDashboardStats();
    loadDevices();
    initCharts();
    
    // Refresh data every 30 seconds
    setInterval(() => {
        loadDashboardStats();
        loadDevices();
        updateCharts();
    }, 30000);
});

/**
 * Initialize the dashboard
 */
function initDashboard() {
    console.log('🚀 Dashboard initialized');
}

/**
 * Load dashboard statistics
 */
async function loadDashboardStats() {
    try {
        const response = await fetch(`${DASHBOARD_API_URL}/stats`);
        const data = await response.json();
        
        // Update stat cards
        document.getElementById('total-devices').textContent = data.total_devices || 0;
        document.getElementById('active-devices').textContent = data.active_devices || 0;
        document.getElementById('total-events').textContent = data.total_events || 0;
        document.getElementById('avg-cpu').textContent = `${data.avg_cpu || 0}%`;
        
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
        showError('Failed to load dashboard statistics');
    }
}

/**
 * Load devices list
 */
async function loadDevices() {
    try {
        const response = await fetch(`${API_BASE_URL}/devices`);
        const data = await response.json();
        
        const tbody = document.getElementById('devices-tbody');
        
        if (!data.devices || data.devices.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No devices found</td></tr>';
            return;
        }
        
        // Build table rows
        tbody.innerHTML = data.devices.map(device => `
            <tr>
                <td><strong>${escapeHtml(device.device_id)}</strong></td>
                <td>${escapeHtml(device.hostname)}</td>
                <td>
                    <span class="badge badge-info">${escapeHtml(device.platform || 'Unknown')}</span>
                </td>
                <td>
                    <span class="badge ${device.is_active ? 'badge-success' : 'badge-danger'}">
                        ${device.is_active ? '● Active' : '○ Inactive'}
                    </span>
                </td>
                <td>${formatDateTime(device.last_seen)}</td>
            </tr>
        `).join('');
        
    } catch (error) {
        console.error('Error loading devices:', error);
        showError('Failed to load devices');
    }
}

/**
 * Initialize Chart.js charts
 */
function initCharts() {
    // CPU Chart
    const cpuCtx = document.getElementById('cpuChart');
    if (cpuCtx) {
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
                    legend: {
                        display: false
                    }
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
    }
    
    // Memory Chart
    const memoryCtx = document.getElementById('memoryChart');
    if (memoryCtx) {
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
                    legend: {
                        display: false
                    }
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
    }
    
    // Load initial chart data
    updateCharts();
}

/**
 * Update charts with latest data
 */
async function updateCharts() {
    try {
        // Get all devices
        const devicesResponse = await fetch(`${API_BASE_URL}/devices`);
        const devicesData = await devicesResponse.json();
        
        if (!devicesData.devices || devicesData.devices.length === 0) {
            return;
        }
        
        // Get stats for the first device (you can modify this to aggregate all devices)
        const firstDevice = devicesData.devices[0];
        const statsResponse = await fetch(`${API_BASE_URL}/devices/${firstDevice.device_id}/stats?limit=20`);
        const statsData = await statsResponse.json();
        
        if (!statsData.stats || statsData.stats.length === 0) {
            return;
        }
        
        // Reverse to show oldest to newest
        const stats = statsData.stats.reverse();
        
        // Update CPU chart
        if (cpuChart) {
            cpuChart.data.labels = stats.map(s => formatTime(s.timestamp));
            cpuChart.data.datasets[0].data = stats.map(s => s.cpu_percent);
            cpuChart.update();
        }
        
        // Update Memory chart
        if (memoryChart) {
            memoryChart.data.labels = stats.map(s => formatTime(s.timestamp));
            memoryChart.data.datasets[0].data = stats.map(s => s.memory_percent);
            memoryChart.update();
        }
        
    } catch (error) {
        console.error('Error updating charts:', error);
    }
}

/**
 * Utility Functions
 */

// Format datetime to readable string in IST
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

// Format time only in IST
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

// Escape HTML to prevent XSS
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Show error message
function showError(message) {
    console.error(message);
    // You can implement a toast notification here
}

// Show success message
function showSuccess(message) {
    console.log(message);
    // You can implement a toast notification here
}
