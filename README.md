# 🖥️ Device Monitor System

An open-source, cross-platform device monitoring system built for enterprise environments to track employee device usage, power states, and system statistics.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

## 🌟 Features

### Current Features
- ✅ **Power State Monitoring** - Track device startup, shutdown, sleep, wake, and battery events
- ✅ **System Statistics** - Monitor CPU, memory, and disk usage in real-time
- ✅ **Centralized Dashboard** - Beautiful web interface to monitor all devices
- ✅ **Local & Cloud Storage** - SQLite for local data, server database for centralized management
- ✅ **Cross-Platform Support** - Works on Windows, Linux, and macOS
- ✅ **Real-time Analytics** - Interactive charts and graphs for usage patterns
- ✅ **Report Generation** - Automated usage, uptime, events, and performance reports
- ✅ **REST API** - Full API for data access and integration
- ✅ **Multi-Device Management** - Monitor unlimited devices from one dashboard

## 🏗️ Architecture

```
device-monitor/
├── agent/              # Client-side monitoring agent
│   ├── monitors/       # Power and system monitoring modules
│   ├── database/       # Local SQLite database management
│   ├── sync/           # Server synchronization
│   ├── config/         # Configuration settings
│   └── utils/          # Helper functions and logging
├── server/             # Central management server
│   ├── api/            # REST API endpoints
│   ├── models/         # Database models
│   ├── dashboard/      # Web dashboard (HTML/CSS/JS)
│   └── config/         # Server configuration
├── scripts/            # Deployment and utility scripts
└── docs/               # Documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/affan1002/device-monitor.git
cd device-monitor
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure settings**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run the server**
```bash
python server/app.py
```

6. **Run the agent (in a new terminal)**
```bash
python agent/main.py
```

7. **Access the dashboard**
```
Open browser: http://localhost:5000
```

## 📊 Usage

### Running the Server

Start the central monitoring server:
```bash
python server/app.py
```

Access the dashboard at: `http://localhost:5000`

**Dashboard Features:**
- 📈 Real-time device statistics
- 🖥️ Device management interface
- 📋 Comprehensive reports
- ⚡ Power event tracking

### Running the Agent

Start monitoring a device:
```bash
python agent/main.py
```

The agent will:
- Register with the server automatically
- Log system startup event
- Monitor power state changes (startup, shutdown, sleep, wake, battery)
- Collect system statistics every 5 minutes
- Sync data to server every 5 minutes
- Store data locally in SQLite database

### Viewing Reports

1. Navigate to **Reports** page on the dashboard
2. Select report type:
   - Usage Summary
   - Uptime Report
   - Events Report
   - Performance Report
3. Choose date range
4. Click "Generate Report"

### Stopping Services

Press `Ctrl+C` to gracefully shutdown the agent or server.

## 🗄️ Database Schema

### Devices
- Device ID, hostname, platform
- Last seen, registration date
- Active status

### Power Events
- Event type (STARTUP, SHUTDOWN, SLEEP, WAKE, BATTERY_*)
- Timestamp, details
- Device reference

### System Statistics
- Timestamp
- CPU, memory, disk usage percentages
- System uptime
- Device reference

### Session Events
- Session type (login, logout)
- Start/end time, duration
- Username, device reference

## 🛠️ Technology Stack

**Agent:**
- Python 3.7+
- psutil - System monitoring
- SQLite - Local database
- requests - Server communication
- pytz - Timezone handling

**Server:**
- Flask - Web framework
- Flask-SQLAlchemy - ORM
- SQLite/PostgreSQL - Database
- Chart.js - Data visualization
- Bootstrap-inspired UI

## 📱 Deployment

### Deploy Agent on Multiple Computers

See [Agent Deployment Guide](docs/AGENT_DEPLOYMENT.md) for detailed instructions.

**Quick steps:**
1. Copy agent files to target computer
2. Configure `.env` with server IP and unique device ID
3. Run setup script
4. Start agent

### Network Configuration

**Local Network:**
- Server and agents on same network
- Use server's local IP address
- Open port 5000 on firewall

**Internet Deployment:**
- Use public IP or domain name
- Configure port forwarding
- Consider HTTPS and authentication

## 📋 Roadmap

- [x] Phase 1: Core agent development
  - [x] Power state monitoring
  - [x] System statistics collection
  - [x] Local database storage
  - [x] Cross-platform support
  - [x] Battery monitoring
  - [x] Sleep/wake detection
- [x] Phase 2: Server & Dashboard
  - [x] REST API development
  - [x] Web dashboard interface
  - [x] Multi-device management
  - [x] Data visualization
  - [x] Report generation
- [ ] Phase 3: Advanced Features
  - [ ] Real-time notifications
  - [ ] Advanced analytics
  - [ ] Mobile app
  - [ ] User authentication
  - [ ] Cloud deployment
  - [ ] Email alerts

## 🔐 Privacy & Ethics

This system is designed for legitimate IT management purposes. Please ensure:
- ✅ Transparent employee notification
- ✅ Compliance with local privacy laws (GDPR, etc.)
- ✅ Proper data retention policies
- ✅ Secure data handling
- ✅ Informed consent from monitored users

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Affan**
- Cybersecurity Student
- GitHub: [@affan1002](https://github.com/affan1002)
- Project: [Device Monitor System](https://github.com/affan1002/device-monitor)

## 📧 Contact

For questions or support, please open an issue on GitHub:
- Issues: [https://github.com/affan1002/device-monitor/issues](https://github.com/affan1002/device-monitor/issues)

## 🙏 Acknowledgments

- Built as a cybersecurity learning project
- Designed for educational and enterprise IT management purposes
- Inspired by the need for transparent device monitoring solutions

---

⭐ If you find this project useful, please consider giving it a star on [GitHub](https://github.com/affan1002/device-monitor)!

**Live Demo:** Run locally with `python server/app.py` and visit `http://localhost:5000`
