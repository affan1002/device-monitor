# 🖥️ Device Monitor System

An open-source, cross-platform device monitoring system built for enterprise environments to track employee device usage, power states, and system statistics.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow.svg)

## 🌟 Features

### Current Features (Agent)
- ✅ **Power State Monitoring** - Track device startup, shutdown, sleep, and wake events
- ✅ **System Statistics** - Monitor CPU, memory, and disk usage
- ✅ **Local Database Storage** - SQLite database for offline data collection
- ✅ **Cross-Platform Support** - Works on Windows, Linux, and macOS
- ✅ **Detailed Logging** - Comprehensive activity logs
- ✅ **Background Service** - Runs silently in the background

### Upcoming Features (Server & Dashboard)
- 🔄 **Centralized Management** - Monitor multiple devices from one dashboard
- 🔄 **Web Dashboard** - Beautiful, interactive web interface
- 🔄 **Real-time Analytics** - Charts and graphs for usage patterns
- 🔄 **Report Generation** - Automated usage reports
- 🔄 **Alerts & Notifications** - Get notified of unusual activity
- 🔄 **REST API** - Full API for data access and integration

## 🏗️ Architecture

```
device-monitor/
├── agent/              # Client-side monitoring agent
│   ├── monitors/       # Power and system monitoring modules
│   ├── database/       # Local SQLite database management
│   ├── config/         # Configuration settings
│   └── utils/          # Helper functions and logging
├── server/            # Central management server (coming soon)
├── scripts/           # Utility scripts
└── docs/              # Documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR-USERNAME/device-monitor.git
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

5. **Run the agent**
```bash
python agent/main.py
```

## 📊 Usage

### Running the Agent

Start monitoring your device:
```bash
python agent/main.py
```

The agent will:
- Log system startup event
- Monitor power state changes
- Collect system statistics every 5 minutes
- Store data in local SQLite database

### Viewing Collected Data

View the database contents:
```bash
python scripts/view_database.py
```

Generate a formatted report:
```bash
python scripts/view_report.py
```

### Stopping the Agent

Press `Ctrl+C` to gracefully shutdown the agent.

## 🗄️ Database Schema

### Power Events
- Event type (startup, shutdown, sleep, wake)
- Timestamp
- Event details
- Sync status

### System Statistics
- Timestamp
- CPU usage percentage
- Memory usage percentage
- Disk usage percentage
- System uptime
- Sync status

### Session Events
- Session type (login, logout)
- Start/end time
- Duration
- Username

## 🛠️ Technology Stack

**Agent:**
- Python 3.7+
- psutil - System monitoring
- SQLite - Local database
- python-dotenv - Configuration management

**Server (Coming Soon):**
- Flask - Web framework
- PostgreSQL/MySQL - Database
- Docker - Containerization

## 📋 Roadmap

- [x] Phase 1: Core agent development
  - [x] Power state monitoring
  - [x] System statistics collection
  - [x] Local database storage
  - [x] Cross-platform support
- [ ] Phase 2: Server & Dashboard
  - [ ] REST API development
  - [ ] Web dashboard interface
  - [ ] Multi-device management
  - [ ] Data visualization
- [ ] Phase 3: Advanced Features
  - [ ] Real-time notifications
  - [ ] Advanced analytics
  - [ ] Mobile app
  - [ ] Cloud deployment

## 🔐 Privacy & Ethics

This system is designed for legitimate IT management purposes. Please ensure:
- ✅ Transparent employee notification
- ✅ Compliance with local privacy laws (GDPR, etc.)
- ✅ Proper data retention policies
- ✅ Secure data handling

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Your Name**
- Cybersecurity Student
- GitHub: [@your-username](https://github.com/your-username)

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

⭐ If you find this project useful, please consider giving it a star!
