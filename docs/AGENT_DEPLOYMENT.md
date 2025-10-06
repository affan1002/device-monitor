# Device Monitor Agent - Deployment Guide

## Quick Setup on New Computer

### Prerequisites
- Python 3.7 or higher
- Network connection to the server

### Files Needed
Copy these to the new computer:
```
agent/
requirements.txt
.env.example
scripts/setup_agent_windows.bat (for Windows)
scripts/setup_agent_linux.sh (for Linux/Mac)
```

### Windows Setup

1. **Copy the agent folder** to the new computer

2. **Get server IP address** (on server computer):
   ```
   ipconfig
   ```
   Note the IPv4 address (e.g., 192.168.1.5)

3. **Run setup script**:
   ```
   cd agent-folder
   scripts\setup_agent_windows.bat
   ```

4. **Configure .env file**:
   ```env
   SERVER_HOST=192.168.1.5  # Your server's IP
   AGENT_ID=device-002      # Unique ID for this device
   API_KEY=dev-key-123
   ```

5. **Run the agent**:
   ```
   .venv\Scripts\activate
   python agent/main.py
   ```

### Linux/Mac Setup

1. **Copy the agent folder** to the new computer

2. **Get server IP address** (on server computer):
   ```
   ip addr show
   ```
   Or on Mac:
   ```
   ifconfig
   ```

3. **Make setup script executable**:
   ```bash
   chmod +x scripts/setup_agent_linux.sh
   ```

4. **Run setup script**:
   ```bash
   cd agent-folder
   ./scripts/setup_agent_linux.sh
   ```

5. **Configure .env file**:
   ```bash
   nano .env
   # Or use any text editor
   ```
   Set:
   ```env
   SERVER_HOST=192.168.1.5  # Your server's IP
   AGENT_ID=device-002      # Unique ID for this device
   API_KEY=dev-key-123
   ```

6. **Run the agent**:
   ```bash
   source .venv/bin/activate
   python agent/main.py
   ```

### Verification

When agent starts successfully, you'll see:
```
INFO: Starting Device Monitor Agent...
✅ Server connection successful: http://192.168.1.5:5000
✅ Device registered successfully: device-002
INFO: Power monitor started...
INFO: System monitor started...
```

The device will appear on the dashboard within 30 seconds.

### Troubleshooting

**Connection Failed:**
- Check if server is running
- Verify SERVER_HOST IP is correct
- Check firewall (port 5000 must be open)
- Ensure both computers are on same network

**Module Not Found:**
- Activate virtual environment first
- Reinstall: `pip install -r requirements.txt`

**Device Not Appearing on Dashboard:**
- Check agent terminal for errors
- Verify AGENT_ID is unique
- Check API_KEY matches server configuration

### Network Requirements

**For Local Network:**
- Server and agents must be on same network
- Server firewall must allow port 5000

**For Internet Deployment:**
- Use server's public IP or domain name
- Configure port forwarding on router
- Consider using HTTPS and proper authentication
