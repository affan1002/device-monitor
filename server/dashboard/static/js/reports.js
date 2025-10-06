// ========================================
// Reports Page JavaScript
// ========================================

const API_BASE_URL = '/api/v1';

// Load initial stats when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadQuickStats();
    
    // Refresh every minute
    setInterval(loadQuickStats, 60000);
});

/**
 * Load quick statistics
 */
async function loadQuickStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/devices`);
        const data = await response.json();
        
        if (!data.devices || data.devices.length === 0) {
            document.getElementById('total-uptime').textContent = 'No data';
            document.getElementById('avg-session').textContent = 'No data';
            document.getElementById('most-active').textContent = 'No devices';
            document.getElementById('power-events').textContent = '0';
            return;
        }
        
        // Calculate total uptime across all devices
        let totalUptime = 0;
        let totalEvents = 0;
        let mostActiveDevice = null;
        let maxUptime = 0;
        
        for (const device of data.devices) {
            // Get stats for each device
            const statsResponse = await fetch(`${API_BASE_URL}/devices/${device.device_id}/stats?limit=1`);
            const statsData = await statsResponse.json();
            
            if (statsData.stats && statsData.stats.length > 0) {
                const uptime = statsData.stats[0].uptime || 0;
                totalUptime += uptime;
                
                if (uptime > maxUptime) {
                    maxUptime = uptime;
                    mostActiveDevice = device.hostname;
                }
            }
            
            // Get events count
            const eventsResponse = await fetch(`${API_BASE_URL}/devices/${device.device_id}/power_events?limit=1000`);
            const eventsData = await eventsResponse.json();
            totalEvents += eventsData.total || 0;
        }
        
        // Update display
        document.getElementById('total-uptime').textContent = formatUptime(totalUptime);
        document.getElementById('avg-session').textContent = formatUptime(totalUptime / data.devices.length);
        document.getElementById('most-active').textContent = mostActiveDevice || 'N/A';
        document.getElementById('power-events').textContent = totalEvents;
        
    } catch (error) {
        console.error('Error loading quick stats:', error);
    }
}

/**
 * Generate report based on selected options
 */
async function generateReport() {
    const reportType = document.getElementById('report-type').value;
    const dateRange = document.getElementById('date-range').value;
    
    const reportDisplay = document.getElementById('report-display');
    reportDisplay.innerHTML = '<div class="loading"><p>Generating report...</p></div>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/devices`);
        const data = await response.json();
        
        if (!data.devices || data.devices.length === 0) {
            reportDisplay.innerHTML = `
                <div class="empty-state">
                    <p>📭 No devices found. Cannot generate report.</p>
                </div>
            `;
            return;
        }
        
        let reportHtml = '';
        
        switch(reportType) {
            case 'usage':
                reportHtml = await generateUsageReport(data.devices, dateRange);
                break;
            case 'uptime':
                reportHtml = await generateUptimeReport(data.devices, dateRange);
                break;
            case 'events':
                reportHtml = await generateEventsReport(data.devices, dateRange);
                break;
            case 'performance':
                reportHtml = await generatePerformanceReport(data.devices, dateRange);
                break;
        }
        
        reportDisplay.innerHTML = reportHtml;
        
    } catch (error) {
        console.error('Error generating report:', error);
        reportDisplay.innerHTML = `
            <div class="error-card">
                <p>❌ Error generating report. Please try again.</p>
            </div>
        `;
    }
}

/**
 * Generate usage summary report
 */
async function generateUsageReport(devices, dateRange) {
    let html = `
        <div class="report-content">
            <div class="report-header">
                <h2>📊 Usage Summary Report</h2>
                <p>Date Range: ${formatDateRange(dateRange)}</p>
                <p>Generated: ${new Date().toLocaleString()}</p>
            </div>
            <table class="report-table">
                <thead>
                    <tr>
                        <th>Device</th>
                        <th>Platform</th>
                        <th>Status</th>
                        <th>Avg CPU</th>
                        <th>Avg Memory</th>
                        <th>Last Seen</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    for (const device of devices) {
        const statsResponse = await fetch(`${API_BASE_URL}/devices/${device.device_id}/stats?limit=50`);
        const statsData = await statsResponse.json();
        
        let avgCpu = 0, avgMemory = 0;
        if (statsData.stats && statsData.stats.length > 0) {
            avgCpu = statsData.stats.reduce((sum, s) => sum + s.cpu_percent, 0) / statsData.stats.length;
            avgMemory = statsData.stats.reduce((sum, s) => sum + s.memory_percent, 0) / statsData.stats.length;
        }
        
        html += `
            <tr>
                <td><strong>${escapeHtml(device.hostname)}</strong></td>
                <td>${escapeHtml(device.platform || 'Unknown')}</td>
                <td>
                    <span class="badge ${device.is_active ? 'badge-success' : 'badge-danger'}">
                        ${device.is_active ? 'Active' : 'Inactive'}
                    </span>
                </td>
                <td>${avgCpu.toFixed(1)}%</td>
                <td>${avgMemory.toFixed(1)}%</td>
                <td>${formatDateTime(device.last_seen)}</td>
            </tr>
        `;
    }
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    return html;
}

/**
 * Generate uptime report
 */
async function generateUptimeReport(devices, dateRange) {
    let html = `
        <div class="report-content">
            <div class="report-header">
                <h2>⏱️ Uptime Report</h2>
                <p>Date Range: ${formatDateRange(dateRange)}</p>
            </div>
            <table class="report-table">
                <thead>
                    <tr>
                        <th>Device</th>
                        <th>Current Uptime</th>
                        <th>Status</th>
                        <th>Last Boot</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    for (const device of devices) {
        const statsResponse = await fetch(`${API_BASE_URL}/devices/${device.device_id}/stats?limit=1`);
        const statsData = await statsResponse.json();
        
        let uptime = 'N/A';
        if (statsData.stats && statsData.stats.length > 0) {
            uptime = formatUptime(statsData.stats[0].uptime);
        }
        
        html += `
            <tr>
                <td><strong>${escapeHtml(device.hostname)}</strong></td>
                <td>${uptime}</td>
                <td>
                    <span class="badge ${device.is_active ? 'badge-success' : 'badge-danger'}">
                        ${device.is_active ? 'Online' : 'Offline'}
                    </span>
                </td>
                <td>${formatDateTime(device.created_at)}</td>
            </tr>
        `;
    }
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    return html;
}

/**
 * Generate events report
 */
async function generateEventsReport(devices, dateRange) {
    let html = `
        <div class="report-content">
            <div class="report-header">
                <h2>⚡ Power Events Report</h2>
                <p>Date Range: ${formatDateRange(dateRange)}</p>
            </div>
            <table class="report-table">
                <thead>
                    <tr>
                        <th>Device</th>
                        <th>Total Events</th>
                        <th>🟢 Startups</th>
                        <th>🔴 Shutdowns</th>
                        <th>😴 Sleep</th>
                        <th>⏰ Wake</th>
                        <th>🔋 Battery</th>
                        <th>Last Event</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    for (const device of devices) {
        const eventsResponse = await fetch(`${API_BASE_URL}/devices/${device.device_id}/power_events?limit=1000`);
        const eventsData = await eventsResponse.json();
        
        const events = eventsData.events || [];
        const startups = events.filter(e => e.event_type === 'STARTUP').length;
        const shutdowns = events.filter(e => e.event_type === 'SHUTDOWN').length;
        const sleep = events.filter(e => e.event_type === 'SLEEP').length;
        const wake = events.filter(e => e.event_type === 'WAKE').length;
        const battery = events.filter(e => e.event_type === 'BATTERY_LOW' || e.event_type === 'BATTERY_CRITICAL' || e.event_type === 'BATTERY_CHARGING' || e.event_type === 'BATTERY_FULL').length;
        const lastEvent = events[0]?.timestamp || 'N/A';
        const lastEventType = events[0]?.event_type || 'N/A';
        
        html += `
            <tr>
                <td><strong>${escapeHtml(device.hostname)}</strong></td>
                <td>${events.length}</td>
                <td>${startups}</td>
                <td>${shutdowns}</td>
                <td>${sleep}</td>
                <td>${wake}</td>
                <td>${battery}</td>
                <td>
                    ${formatDateTime(lastEvent)}<br>
                    <span class="badge badge-info">${lastEventType}</span>
                </td>
            </tr>
        `;
    }
    
    html += `
                </tbody>
            </table>
            <div class="event-legend" style="margin-top: 2rem; padding: 1rem; background: #f8fafc; border-radius: 0.5rem;">
                <h4 style="margin-bottom: 0.5rem;">Event Types:</h4>
                <p style="margin: 0.25rem 0; color: var(--text-secondary); font-size: 0.875rem;">
                    <strong>🟢 Startup:</strong> Device powered on or booted up<br>
                    <strong>🔴 Shutdown:</strong> Device powered off gracefully<br>
                    <strong>😴 Sleep:</strong> Device entered sleep/hibernate mode<br>
                    <strong>⏰ Wake:</strong> Device woke from sleep/hibernate<br>
                    <strong>🔋 Battery:</strong> Battery-related events (low, charging, full, critical)
                </p>
            </div>
        </div>
    `;
    
    return html;
}

/**
 * Generate performance report
 */
async function generatePerformanceReport(devices, dateRange) {
    let html = `
        <div class="report-content">
            <div class="report-header">
                <h2>📈 Performance Report</h2>
                <p>Date Range: ${formatDateRange(dateRange)}</p>
            </div>
            <table class="report-table">
                <thead>
                    <tr>
                        <th>Device</th>
                        <th>Avg CPU</th>
                        <th>Max CPU</th>
                        <th>Avg Memory</th>
                        <th>Max Memory</th>
                        <th>Disk Usage</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    for (const device of devices) {
        const statsResponse = await fetch(`${API_BASE_URL}/devices/${device.device_id}/stats?limit=100`);
        const statsData = await statsResponse.json();
        
        let avgCpu = 0, maxCpu = 0, avgMemory = 0, maxMemory = 0, diskUsage = 0;
        
        if (statsData.stats && statsData.stats.length > 0) {
            const stats = statsData.stats;
            avgCpu = stats.reduce((sum, s) => sum + s.cpu_percent, 0) / stats.length;
            avgMemory = stats.reduce((sum, s) => sum + s.memory_percent, 0) / stats.length;
            maxCpu = Math.max(...stats.map(s => s.cpu_percent));
            maxMemory = Math.max(...stats.map(s => s.memory_percent));
            diskUsage = stats[0].disk_percent;
        }
        
        html += `
            <tr>
                <td><strong>${escapeHtml(device.hostname)}</strong></td>
                <td>${avgCpu.toFixed(1)}%</td>
                <td>${maxCpu.toFixed(1)}%</td>
                <td>${avgMemory.toFixed(1)}%</td>
                <td>${maxMemory.toFixed(1)}%</td>
                <td>${diskUsage.toFixed(1)}%</td>
            </tr>
        `;
    }
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    return html;
}

/**
 * Utility functions
 */
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

function formatDateRange(range) {
    switch(range) {
        case 'today': return 'Today';
        case 'week': return 'Last 7 Days';
        case 'month': return 'Last 30 Days';
        case 'all': return 'All Time';
        default: return 'Custom';
    }
}

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
