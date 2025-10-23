#!/bin/bash
"""
LED Matrix Server Setup Script
Installs dependencies and configures the LED Matrix Server for auto-start on Raspberry Pi.
"""

echo "🚀 Setting up LED Matrix Server..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt update
apt upgrade -y

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
apt install -y python3-pip python3-flask python3-flask-cors

# Install Flask and CORS if not available via apt
pip3 install flask flask-cors

# Get the current directory (should be the projects directory)
PROJECT_DIR="$(pwd)"
SERVICE_FILE="$PROJECT_DIR/led-matrix-server.service"
SYSTEMD_SERVICE="/etc/systemd/system/led-matrix-server.service"

# Update the service file with the correct paths
echo "⚙️ Configuring service file..."
sed "s|/home/pi/rpi-rgb-led-matrix/bindings/python/projects|$PROJECT_DIR|g" "$SERVICE_FILE" > "$SYSTEMD_SERVICE"

# Set correct permissions
chmod 644 "$SYSTEMD_SERVICE"

# Reload systemd and enable the service
echo "🔄 Enabling LED Matrix Server service..."
systemctl daemon-reload
systemctl enable led-matrix-server.service

# Start the service
echo "▶️ Starting LED Matrix Server..."
systemctl start led-matrix-server.service

# Check service status
echo "📊 Service Status:"
systemctl status led-matrix-server.service --no-pager -l

# Show network information
echo ""
echo "🌐 LED Matrix Server Setup Complete!"
echo "📱 Access the web interface at:"
echo "   http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "🔧 Useful commands:"
echo "   sudo systemctl status led-matrix-server    # Check status"
echo "   sudo systemctl restart led-matrix-server   # Restart service" 
echo "   sudo systemctl stop led-matrix-server      # Stop service"
echo "   sudo systemctl logs led-matrix-server      # View logs"
echo ""
echo "🎯 The retro-clock will auto-start by default!"
echo "   Use the web interface to change projects and settings."