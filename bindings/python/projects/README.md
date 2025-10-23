# LED Matrix Server 🎮

A web-based controller for managing LED matrix projects on Raspberry Pi. Provides REST API endpoints and a web interface for configuring and controlling various LED matrix displays.

## Features ✨

- **🌐 Web Interface**: Control your LED matrix from any device on your network
- **🔄 Auto-Start**: Configurable default project that starts automatically on boot
- **🎨 Live Configuration**: Change colors, animations, and settings in real-time
- **📊 Project Management**: Start, stop, and switch between different LED matrix projects
- **💾 Persistent Settings**: Configuration is saved and restored across reboots

## Supported Projects 📱

### Retro Clock 🕰️
- **Color Themes**: Orange, Light Gray, Dark Green, Light Blue
- **Animation Modes**: Simple or Scroll-Down transitions
- **Display Options**: Configurable AM/PM indicator
- **Brightness Control**: Adjustable LED brightness

### Coming Soon
- Simple Clock
- Weather Display  
- Stock Tracker
- Music Display

## Quick Setup 🚀

1. **Clone the repository** (if not already done):
   ```bash
   cd /home/pi
   git clone https://github.com/mabthew/rpi-rgb-led-matrix.git
   cd rpi-rgb-led-matrix/bindings/python/projects
   ```

2. **Run the setup script**:
   ```bash
   sudo chmod +x setup_matrix_server.sh
   sudo ./setup_matrix_server.sh
   ```

3. **Access the web interface**:
   Open your browser and go to: `http://[your-pi-ip]:5000`

## Manual Installation 🔧

If you prefer to set up manually:

### Install Dependencies
```bash
sudo apt update
sudo apt install python3-pip python3-flask python3-flask-cors
sudo pip3 install flask flask-cors
```

### Configure Auto-Start Service
```bash
# Copy service file
sudo cp led-matrix-server.service /etc/systemd/system/

# Edit paths in service file if needed
sudo nano /etc/systemd/system/led-matrix-server.service

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable led-matrix-server.service
sudo systemctl start led-matrix-server.service
```

## Usage 📖

### Web Interface
- Navigate to `http://[your-pi-ip]:5000` in any browser
- Start/stop projects with the control buttons
- Configure project settings using the dropdowns and sliders
- Set the default project for auto-start on boot

### REST API Endpoints

#### Get Status
```http
GET /api/status
```

#### List Projects
```http
GET /api/projects
```

#### Start Project
```http
POST /api/projects/{project_name}/start
```

#### Update Project Configuration
```http
POST /api/projects/{project_name}/config
Content-Type: application/json

{
  "color_theme": "light_blue",
  "animation_mode": "scroll_down",
  "brightness": 90
}
```

#### Set Default Project
```http
POST /api/default-project
Content-Type: application/json

{
  "project": "retro-clock"
}
```

## Configuration 🎛️

### Retro Clock Options
- **Color Theme**: `orange`, `light_gray`, `dark_green`, `light_blue`
- **Animation Mode**: `simple`, `scroll_down`
- **Show AM/PM**: `true`, `false`
- **Brightness**: `1-100`

### Command Line Usage
You can also run projects directly:
```bash
# Basic usage
sudo python3 retro-clock/retro-clock.py

# With configuration
sudo python3 retro-clock/retro-clock.py --color-theme light_blue --animation-mode scroll_down --led-brightness 90
```

## Service Management 🛠️

```bash
# Check service status
sudo systemctl status led-matrix-server

# View logs
sudo journalctl -u led-matrix-server -f

# Restart service
sudo systemctl restart led-matrix-server

# Stop service
sudo systemctl stop led-matrix-server

# Disable auto-start
sudo systemctl disable led-matrix-server
```

## File Structure 📁

```
projects/
├── led_matrix_server.py           # Main server application
├── led-matrix-server.service      # Systemd service file
├── setup_matrix_server.sh         # Setup script
├── matrix_config.json            # Saved configuration (created automatically)
├── retro-clock/
│   └── retro-clock.py            # Enhanced with configuration support
├── shared/                       # Shared components
└── README.md                     # This file
```

## Network Access 🌐

The server runs on port `5000` and is accessible from:
- **Local**: `http://localhost:5000`
- **Network**: `http://[raspberry-pi-ip]:5000`
- **Hostname**: `http://raspberrypi.local:5000` (if mDNS is enabled)

## Troubleshooting 🔍

### Service Won't Start
```bash
# Check logs for errors
sudo journalctl -u led-matrix-server -n 50

# Check if port is in use
sudo netstat -tlnp | grep :5000
```

### Web Interface Not Accessible
- Verify the Raspberry Pi's IP address: `hostname -I`
- Check firewall settings: `sudo ufw status`
- Ensure the service is running: `sudo systemctl status led-matrix-server`

### Matrix Hardware Issues
- Verify wiring connections
- Check if running as root (required for GPIO access)
- Test with a simple matrix example first

## Development 💻

### Adding New Projects
1. Create project directory under `projects/`
2. Add project configuration to `LEDMatrixController.project_configs`
3. Update web interface template if custom configuration needed

### API Extensions
The REST API can be extended by adding new routes to `led_matrix_server.py`.

## License 📄

This project follows the same license as the rpi-rgb-led-matrix library.