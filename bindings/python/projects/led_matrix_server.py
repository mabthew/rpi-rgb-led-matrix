#!/usr/bin/env python3
"""
LED Matrix Server - Web API for controlling LED matrix projects
Provides REST endpoints for configuring and controlling various LED matrix displays.
"""

import sys
import os
import json
import threading
import time
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import subprocess
import signal

# Add shared components to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

app = Flask(__name__)
CORS(app)  # Enable CORS for web interface

class LEDMatrixController:
    """Central controller for all LED matrix projects."""
    
    def __init__(self):
        self.current_project = None
        self.current_process = None
        self.project_configs = {
            'retro-clock': {
                'name': 'Retro Clock',
                'script': 'retro-clock/retro-clock.py',
                'config': {
                    'color_theme': 'orange',
                    'animation_mode': 'scroll_down',
                    'show_ampm': True,
                    'brightness': 80
                }
            },
            'simple-clock': {
                'name': 'Simple Clock',
                'script': 'simple-clock/simple-clock.py',
                'config': {}
            },
            'weather-display': {
                'name': 'Weather Display', 
                'script': 'weather-display/weather-display.py',
                'config': {}
            }
        }
        
        # Load saved configuration
        self.load_config()
        
        print("🚀 LED Matrix Controller initialized")
        print(f"📊 Available projects: {list(self.project_configs.keys())}")
    
    def load_config(self):
        """Load configuration from file."""
        config_file = os.path.join(os.path.dirname(__file__), 'matrix_config.json')
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    saved_config = json.load(f)
                    # Update project configs with saved values
                    for project, config in saved_config.get('projects', {}).items():
                        if project in self.project_configs:
                            self.project_configs[project]['config'].update(config)
                    
                    # Set default project if specified
                    self.default_project = saved_config.get('default_project', 'retro-clock')
                    print(f"📁 Configuration loaded. Default project: {self.default_project}")
            else:
                self.default_project = 'retro-clock'
        except Exception as e:
            print(f"⚠️ Error loading config: {e}")
            self.default_project = 'retro-clock'
    
    def save_config(self):
        """Save current configuration to file."""
        config_file = os.path.join(os.path.dirname(__file__), 'matrix_config.json')
        try:
            config_data = {
                'default_project': self.default_project,
                'projects': {project: data['config'] for project, data in self.project_configs.items()}
            }
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            print("💾 Configuration saved")
        except Exception as e:
            print(f"⚠️ Error saving config: {e}")
    
    def start_project(self, project_name):
        """Start a specific LED matrix project."""
        if project_name not in self.project_configs:
            return False, f"Unknown project: {project_name}"
        
        # Stop current project if running
        self.stop_current_project()
        
        try:
            project_info = self.project_configs[project_name]
            script_path = os.path.join(os.path.dirname(__file__), project_info['script'])
            
            # Build command with configuration
            cmd = ['sudo', 'python3', script_path]
            
            # Add configuration parameters (this will be project-specific)
            if project_name == 'retro-clock':
                config = project_info['config']
                if 'brightness' in config:
                    cmd.extend(['--led-brightness', str(config['brightness'])])
            
            # Start the process
            self.current_process = subprocess.Popen(
                cmd,
                cwd=os.path.dirname(script_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.current_project = project_name
            print(f"▶️ Started project: {project_info['name']}")
            return True, f"Started {project_info['name']}"
            
        except Exception as e:
            print(f"❌ Error starting project {project_name}: {e}")
            return False, str(e)
    
    def stop_current_project(self):
        """Stop the currently running project."""
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=5)
                print(f"⏹️ Stopped project: {self.current_project}")
            except subprocess.TimeoutExpired:
                self.current_process.kill()
                print(f"🔪 Force killed project: {self.current_project}")
            except Exception as e:
                print(f"⚠️ Error stopping project: {e}")
            finally:
                self.current_process = None
                self.current_project = None
    
    def update_project_config(self, project_name, config_updates):
        """Update configuration for a specific project."""
        if project_name not in self.project_configs:
            return False, f"Unknown project: {project_name}"
        
        # Update the configuration
        self.project_configs[project_name]['config'].update(config_updates)
        
        # Save to disk
        self.save_config()
        
        # If this project is currently running, restart it with new config
        if self.current_project == project_name:
            self.start_project(project_name)
        
        return True, "Configuration updated"
    
    def get_status(self):
        """Get current status of the matrix controller."""
        return {
            'current_project': self.current_project,
            'current_project_name': self.project_configs[self.current_project]['name'] if self.current_project else None,
            'running': self.current_process is not None and self.current_process.poll() is None,
            'available_projects': {k: v['name'] for k, v in self.project_configs.items()},
            'default_project': self.default_project
        }
    
    def send_clock_api_request(self, endpoint, data=None):
        """Send API request to running retro clock."""
        if self.current_project != 'retro-clock':
            return False
        
        try:
            import urllib.request
            import urllib.parse
            
            url = f'http://localhost:8080{endpoint}'
            
            if data:
                data_encoded = json.dumps(data).encode('utf-8')
                req = urllib.request.Request(url, data=data_encoded, 
                                           headers={'Content-Type': 'application/json'})
                req.get_method = lambda: 'POST'
            else:
                req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=5) as response:
                return True
        except Exception as e:
            print(f"⚠️ Error communicating with retro clock: {e}")
            return False
    
    def get_clock_api_request(self, endpoint):
        """Get data from running retro clock API."""
        if self.current_project != 'retro-clock':
            return None
        
        try:
            import urllib.request
            
            url = f'http://localhost:8080{endpoint}'
            req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=5) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"⚠️ Error getting data from retro clock: {e}")
            return None

# Global controller instance
controller = LEDMatrixController()

# REST API Endpoints

@app.route('/api/status', methods=['GET'])
def api_status():
    """Get current status."""
    return jsonify(controller.get_status())

@app.route('/api/projects', methods=['GET'])
def api_projects():
    """Get list of available projects and their configurations."""
    projects = {}
    for name, data in controller.project_configs.items():
        projects[name] = {
            'name': data['name'],
            'config': data['config'],
            'running': controller.current_project == name
        }
    return jsonify(projects)

@app.route('/api/projects/<project_name>/start', methods=['POST'])
def api_start_project(project_name):
    """Start a specific project."""
    success, message = controller.start_project(project_name)
    return jsonify({'success': success, 'message': message})

@app.route('/api/projects/<project_name>/stop', methods=['POST'])
def api_stop_project(project_name):
    """Stop a specific project (if it's currently running)."""
    if controller.current_project == project_name:
        controller.stop_current_project()
        return jsonify({'success': True, 'message': f'Stopped {project_name}'})
    else:
        return jsonify({'success': False, 'message': 'Project not currently running'})

@app.route('/api/projects/<project_name>/config', methods=['GET'])
def api_get_project_config(project_name):
    """Get configuration for a specific project."""
    if project_name not in controller.project_configs:
        return jsonify({'error': 'Project not found'}), 404
    
    return jsonify(controller.project_configs[project_name]['config'])

@app.route('/api/projects/<project_name>/config', methods=['POST'])
def api_update_project_config(project_name):
    """Update configuration for a specific project."""
    config_updates = request.json
    success, message = controller.update_project_config(project_name, config_updates)
    return jsonify({'success': success, 'message': message})

# Enhanced Retro Clock Endpoints
@app.route('/api/retro-clock/theme', methods=['POST'])
def api_retro_clock_theme():
    """Change retro clock color theme."""
    data = request.json
    theme = data.get('theme')
    
    if not theme:
        return jsonify({'success': False, 'message': 'Theme parameter required'}), 400
    
    # Update via direct API call to running clock (if available)
    success = controller.send_clock_api_request('/theme', {'theme': theme})
    if success:
        # Also update stored config
        controller.update_project_config('retro-clock', {'color_theme': theme})
        return jsonify({'success': True, 'message': f'Theme changed to {theme}'})
    else:
        return jsonify({'success': False, 'message': 'Could not update running clock'}), 500

@app.route('/api/retro-clock/animate', methods=['POST'])
def api_retro_clock_animate():
    """Trigger retro clock animation."""
    data = request.json
    animation_type = data.get('type', 'both')  # hour, minute, simultaneous, both
    
    success = controller.send_clock_api_request('/animate', {'type': animation_type})
    if success:
        return jsonify({'success': True, 'message': f'Animation triggered: {animation_type}'})
    else:
        return jsonify({'success': False, 'message': 'Could not trigger animation'}), 500

@app.route('/api/retro-clock/config', methods=['POST'])
def api_retro_clock_live_config():
    """Update retro clock configuration in real-time."""
    config_updates = request.json
    
    success = controller.send_clock_api_request('/config', config_updates)
    if success:
        # Also update stored config
        controller.update_project_config('retro-clock', config_updates)
        return jsonify({'success': True, 'message': 'Configuration updated'})
    else:
        return jsonify({'success': False, 'message': 'Could not update running clock'}), 500

@app.route('/api/retro-clock/status', methods=['GET'])
def api_retro_clock_status():
    """Get retro clock status."""
    status = controller.get_clock_api_request('/status')
    if status:
        return jsonify(status)
    else:
        return jsonify({'error': 'Could not get clock status'}), 500

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """Stop all projects."""
    controller.stop_current_project()
    return jsonify({'success': True, 'message': 'All projects stopped'})

@app.route('/api/default-project', methods=['POST'])
def api_set_default_project():
    """Set the default project to start on boot."""
    data = request.json
    project_name = data.get('project')
    
    if project_name not in controller.project_configs:
        return jsonify({'success': False, 'message': 'Invalid project name'})
    
    controller.default_project = project_name
    controller.save_config()
    return jsonify({'success': True, 'message': f'Default project set to {project_name}'})

# Web Interface

@app.route('/')
def web_interface():
    """Serve the web interface."""
    return render_template_string(WEB_INTERFACE_TEMPLATE)

# HTML Template for web interface
WEB_INTERFACE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>LED Matrix Controller</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .status { padding: 15px; margin: 10px 0; border-radius: 5px; }
        .running { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .stopped { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .project { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
        .project h3 { margin-top: 0; }
        button { padding: 8px 16px; margin: 5px; border: none; border-radius: 3px; cursor: pointer; }
        button:hover { opacity: 0.8; }
        .btn-primary { background: #007bff; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        input, select { padding: 5px; margin: 5px; border: 1px solid #ddd; border-radius: 3px; }
        input[type="range"] { width: 150px; }
        .config-section { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border: 1px solid #e9ecef; }
        .config-section h4 { margin-top: 0; color: #495057; }
        .control-group { margin: 10px 0; }
        .inline-controls { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 LED Matrix Controller</h1>
        
        <div id="status" class="status"></div>
        
        <div id="projects"></div>
        
        <div class="project">
            <h3>⚙️ Global Settings</h3>
            <button class="btn-danger" onclick="stopAll()">Stop All Projects</button>
            <div class="config-section">
                <label>Default Project (Auto-start on boot):</label>
                <select id="defaultProject">
                    <option value="">Select project...</option>
                </select>
                <button class="btn-primary" onclick="setDefaultProject()">Set Default</button>
            </div>
        </div>
    </div>

    <script>
        let projects = {};
        let status = {};

        async function fetchStatus() {
            try {
                const response = await fetch('/api/status');
                status = await response.json();
                updateStatusDisplay();
            } catch (error) {
                console.error('Error fetching status:', error);
            }
        }

        async function fetchProjects() {
            try {
                const response = await fetch('/api/projects');
                projects = await response.json();
                updateProjectsDisplay();
                updateDefaultProjectSelect();
            } catch (error) {
                console.error('Error fetching projects:', error);
            }
        }

        function updateStatusDisplay() {
            const statusDiv = document.getElementById('status');
            if (status.running && status.current_project) {
                statusDiv.className = 'status running';
                statusDiv.innerHTML = `✅ Running: ${status.current_project_name}`;
            } else {
                statusDiv.className = 'status stopped';
                statusDiv.innerHTML = '⏹️ No project running';
            }
        }

        function updateProjectsDisplay() {
            const projectsDiv = document.getElementById('projects');
            projectsDiv.innerHTML = '';

            for (const [key, project] of Object.entries(projects)) {
                const projectDiv = document.createElement('div');
                projectDiv.className = 'project';
                
                let configHtml = '';
                if (key === 'retro-clock') {
                    configHtml = `
                        <div class="config-section">
                            <h4>⚙️ Configuration</h4>
                            <label>Color Theme:</label>
                            <select id="theme_${key}" onchange="updateRealtimeConfig('${key}', 'color_theme', this.value)">
                                <option value="orange" ${project.config.color_theme === 'orange' ? 'selected' : ''}>Classic Orange</option>
                                <option value="light_gray" ${project.config.color_theme === 'light_gray' ? 'selected' : ''}>Light Gray</option>
                                <option value="dark_green" ${project.config.color_theme === 'dark_green' ? 'selected' : ''}>Dark Green</option>
                                <option value="light_blue" ${project.config.color_theme === 'light_blue' ? 'selected' : ''}>Light Blue</option>
                            </select>
                            <button class="btn-secondary" onclick="quickChangeTheme('${key}', document.getElementById('theme_${key}').value)">🎨 Apply Theme</button>
                            <br>
                            <label>Animation Mode:</label>
                            <select id="animation_${key}" onchange="updateRealtimeConfig('${key}', 'animation_mode', this.value)">
                                <option value="simple" ${project.config.animation_mode === 'simple' ? 'selected' : ''}>Simple</option>
                                <option value="scroll_down" ${project.config.animation_mode === 'scroll_down' ? 'selected' : ''}>Scroll Down</option>
                            </select>
                            <br>
                            <label>Brightness:</label>
                            <input type="range" min="1" max="100" value="${project.config.brightness || 80}" 
                                   onchange="updateRealtimeConfig('${key}', 'brightness', parseInt(this.value))" 
                                   oninput="document.getElementById('brightness_display_${key}').textContent = this.value + '%'">
                            <span id="brightness_display_${key}">${project.config.brightness || 80}%</span>
                            <br>
                            <label>Show AM/PM:</label>
                            <input type="checkbox" ${project.config.show_ampm ? 'checked' : ''} 
                                   onchange="updateRealtimeConfig('${key}', 'show_ampm', this.checked)">
                            <br><br>
                            <h4>🎬 Manual Animations</h4>
                            <button class="btn-primary" onclick="triggerAnimation('hour')">Hour Animation</button>
                            <button class="btn-primary" onclick="triggerAnimation('minute')">Minute Animation</button>
                            <button class="btn-primary" onclick="triggerAnimation('simultaneous')">Simultaneous</button>
                            <button class="btn-primary" onclick="triggerAnimation('both')">Both Sequential</button>
                        </div>
                    `;
                }
                
                projectDiv.innerHTML = `
                    <h3>${project.running ? '▶️' : '⏸️'} ${project.name}</h3>
                    <button class="btn-success" onclick="startProject('${key}')">Start</button>
                    <button class="btn-danger" onclick="stopProject('${key}')">Stop</button>
                    ${configHtml}
                `;
                
                projectsDiv.appendChild(projectDiv);
            }
        }

        function updateDefaultProjectSelect() {
            const select = document.getElementById('defaultProject');
            select.innerHTML = '<option value="">Select project...</option>';
            
            for (const [key, project] of Object.entries(projects)) {
                const option = document.createElement('option');
                option.value = key;
                option.textContent = project.name;
                if (status.default_project === key) {
                    option.selected = true;
                }
                select.appendChild(option);
            }
        }

        async function startProject(projectName) {
            try {
                const response = await fetch(`/api/projects/${projectName}/start`, {
                    method: 'POST'
                });
                const result = await response.json();
                alert(result.message);
                fetchStatus();
                fetchProjects();
            } catch (error) {
                alert('Error starting project: ' + error);
            }
        }

        async function stopProject(projectName) {
            try {
                const response = await fetch(`/api/projects/${projectName}/stop`, {
                    method: 'POST'
                });
                const result = await response.json();
                alert(result.message);
                fetchStatus();
                fetchProjects();
            } catch (error) {
                alert('Error stopping project: ' + error);
            }
        }

        async function stopAll() {
            try {
                const response = await fetch('/api/stop', {
                    method: 'POST'
                });
                const result = await response.json();
                alert(result.message);
                fetchStatus();
                fetchProjects();
            } catch (error) {
                alert('Error stopping projects: ' + error);
            }
        }

        async function updateConfig(projectName, key, value) {
            try {
                const response = await fetch(`/api/projects/${projectName}/config`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({[key]: value})
                });
                const result = await response.json();
                console.log('Config updated:', result.message);
                fetchProjects();
            } catch (error) {
                alert('Error updating config: ' + error);
            }
        }

        async function setDefaultProject() {
            const select = document.getElementById('defaultProject');
            const projectName = select.value;
            
            if (!projectName) {
                alert('Please select a project first');
                return;
            }

            try {
                const response = await fetch('/api/default-project', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({project: projectName})
                });
                const result = await response.json();
                alert(result.message);
                fetchStatus();
            } catch (error) {
                alert('Error setting default project: ' + error);
            }
        }

        // Enhanced Retro Clock Functions
        async function updateRealtimeConfig(projectName, key, value) {
            try {
                const response = await fetch(`/api/${projectName}/config`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({[key]: value})
                });
                const result = await response.json();
                console.log('Real-time config updated:', result.message);
                
                // Also update via direct clock API for immediate effect
                if (projectName === 'retro-clock') {
                    fetch('/api/retro-clock/config', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({[key]: value})
                    });
                }
            } catch (error) {
                console.error('Error updating real-time config:', error);
            }
        }

        async function quickChangeTheme(projectName, theme) {
            try {
                const response = await fetch('/api/retro-clock/theme', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({theme: theme})
                });
                const result = await response.json();
                if (result.success) {
                    console.log('Theme changed immediately:', result.message);
                } else {
                    alert('Error changing theme: ' + result.message);
                }
                fetchProjects();
            } catch (error) {
                alert('Error changing theme: ' + error);
            }
        }

        async function triggerAnimation(type) {
            try {
                const response = await fetch('/api/retro-clock/animate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({type: type})
                });
                const result = await response.json();
                if (result.success) {
                    console.log('Animation triggered:', result.message);
                } else {
                    alert('Error triggering animation: ' + result.message);
                }
            } catch (error) {
                alert('Error triggering animation: ' + error);
            }
        }

        // Initial load and periodic refresh
        fetchStatus();
        fetchProjects();
        setInterval(() => {
            fetchStatus();
            fetchProjects();
        }, 5000);
    </script>
</body>
</html>
'''

def signal_handler(sig, frame):
    """Handle shutdown signals."""
    print("\n🛑 Shutting down LED Matrix Server...")
    controller.stop_current_project()
    sys.exit(0)

if __name__ == '__main__':
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Auto-start default project
    if controller.default_project:
        print(f"🚀 Auto-starting default project: {controller.default_project}")
        controller.start_project(controller.default_project)
    
    # Start the web server
    print("🌐 Starting web server on http://0.0.0.0:5000")
    print("📱 Access the web interface from any device on your network")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)