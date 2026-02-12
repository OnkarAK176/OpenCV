# Installation & Setup Guide

Complete step-by-step guide to install and run the Traffic Violation Detection System.

---

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **RAM**: 4GB minimum (8GB+ recommended)
- **Disk Space**: 3GB+ (for models and data)
- **Internet**: Required for first-time model downloads
- **GPU** (Optional): NVIDIA GPU with CUDA 11.8+ for faster processing

---

## 🪟 Windows Installation

### Step 1: Install Python

1. Download Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **IMPORTANT**: Check "Add Python to PATH"
4. Click "Install Now"
5. Verify installation:
   ```bash
   python --version
   ```

### Step 2: Clone Repository

```bash
cd Desktop
git clone <repository-url>
cd traffic_violation_detection
```

or simply extract the project folder.

### Step 3: Quick Start (Automatic)

Run the automated setup script:

```bash
start-windows.bat
```

This will:
- Create virtual environment
- Install dependencies
- Download models
- Start both servers
- Open browser automatically

**That's it!** Skip to [Usage](#usage) section.

### Step 4: Manual Setup (If Automatic Fails)

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Run the optional setup script
python setup.py

# Start backend server
python app.py
```

In a new PowerShell/CMD window:

```bash
cd frontend
python -m http.server 3000
```

---

## 🐧 Linux/macOS Installation

### Step 1: Install Python & Git

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3 python3-venv git
```

**macOS:**
```bash
brew install python3 git
```

### Step 2: Clone Repository

```bash
cd ~
git clone <repository-url>
cd traffic_violation_detection
```

### Step 3: Quick Start (Automatic)

Make the script executable and run it:

```bash
chmod +x start.sh
./start.sh
```

### Step 4: Manual Setup (If Automatic Fails)

```bash
# Create virtual environment
python3 -m venv backend/venv
source backend/venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Optional setup
python setup.py

# Start backend
python app.py
```

In another terminal:

```bash
cd frontend
python3 -m http.server 3000
```

---

## 🐳 Docker Installation

### System Requirements

- Docker: 20.10+
- Docker Compose: 2.0+
- 4GB available disk space

### Installation Steps

```bash
# Clone repository
cd traffic_violation_detection

# Build and start containers
docker-compose up --build

# On first run, this may take 10-15 minutes
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

**Stop containers:**
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

## ✅ Verification Checklist

After installation, verify everything is working:

- [ ] Python version is 3.8+
- [ ] Virtual environment is activated
- [ ] All dependencies installed without errors
- [ ] Backend server running on http://localhost:5000
- [ ] Frontend accessible on http://localhost:3000
- [ ] Backend health check returns 200:
  ```bash
  curl http://localhost:5000/api/health
  ```

---

## 🔧 Configuration

### Backend Configuration

Edit `backend/config.py` to customize:

```python
# Speed violation settings
SPEED_LIMIT = 60              # km/h
VIOLATION_SPEED_THRESHOLD = 65  # km/h

# Detection confidence
CONFIDENCE_THRESHOLD = 0.5    # 0-1 scale
NMS_THRESHOLD = 0.4          # Non-max suppression

# File upload limits
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'jpg', 'jpeg', 'png'}

# Flask settings
DEBUG = True                   # Set False for production
SECRET_KEY = 'change-this-in-production'
```

### Frontend Configuration

Edit `frontend/script.js` to change API base URL:

```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

---

## 🚀 First Time Setup Guide

### What Happens on First Run

1. **Model Downloads** (~2GB)
   - YOLOv8 Nano model (~6.3 MB)
   - EasyOCR models (~1.5 GB)
   - Time: 5-15 minutes depending on internet speed

2. **Directory Creation**
   - `uploads/` - Stores uploaded files
   - `results/` - Stores processed videos
   - `models/` - Caches pre-trained models
   - `logs/` - Application logs

3. **Cache Building**
   - Models are cached locally
   - Subsequent runs are faster

---

## 🐛 Troubleshooting

### Common Issues & Solutions

**Problem: "ModuleNotFoundError: No module named 'cv2'"**
```bash
# Solution: Reinstall OpenCV
pip install --upgrade opencv-python
```

**Problem: "CUDA out of memory"**
```bash
# Solution: Use CPU-only mode in detection.py
# Change gpu=False in EasyOCR initialization
```

**Problem: Port 5000 already in use**
```bash
# Find process using port 5000
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Change port in app.py
app.run(port=5001)
```

**Problem: "No module named 'uvloop'"** (Windows)
```bash
# Solution: Remove uvloop requirement (Windows-specific issue)
pip uninstall uvloop
```

**Problem: Models download is very slow**
```bash
# Download models manually
from ultralytics import YOLO
model = YOLO('yolov8n.pt')  # Downloads to ~/.cache/huggingface
```

**Problem: "TypeError: 'NoneType' object is not subscriptable"**
```bash
# Solution: Update EasyOCR and dependencies
pip install --upgrade easyocr torch
```

---

## 📊 System Performance

### Expected Performance

| Component | Time | Specs |
|-----------|------|-------|
| First Start | 5-15 min | Model downloads |
| Subsequent Starts | <30 sec | Cold start |
| 30-sec Video Process | 2-5 min | CPU-based |
| 30-sec Video Process | 30-60 sec | GPU-based (RTX 3060) |
| Image Process | 10-30 sec | Depends on size |

### Optimization Tips

1. **GPU Acceleration**
   - Install CUDA 11.8+
   - Install cuDNN
   - Enable GPU in config

2. **Memory Management**
   - Close other applications
   - Process smaller videos first
   - Monitor with `nvidia-smi`

3. **Network Optimization**
   - Use wired connection for uploads
   - Place server geographically close
   - Enable HTTP/2 in production

---

## 🔐 Production Deployment

### Before Going Live

1. **Security**
   ```python
   DEBUG = False
   SECRET_KEY = os.environ.get('SECRET_KEY', 'generate-new-key')
   ALLOWED_HOSTS = ['your-domain.com']
   ```

2. **Database**
   - Switch from SQLite to PostgreSQL
   - Set up regular backups
   - Use connection pooling

3. **Reverse Proxy**
   ```nginx
   upstream tvds_backend {
       server 127.0.0.1:5000;
   }
   
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://tvds_backend;
       }
   }
   ```

4. **SSL/HTTPS**
   - Use Let's Encrypt for free SSL
   - Configure HSTS headers
   - Enable CORS selectively

5. **Monitoring**
   - Set up logging
   - Monitor disk space
   - Track processing times
   - Alert on errors

---

## 📞 Support & Help

### Getting Help

1. Check the [README.md](README.md) for general information
2. Review troubleshooting section above
3. Check logs: `backend/logs/`
4. Open an issue with full error message

### Useful Commands

```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (Linux/macOS)
source venv/bin/activate

# Deactivate virtual environment
deactivate

# Check Python packages
pip list

# Clear pip cache
pip cache purge

# Test API
curl http://localhost:5000/api/health

# Monitor process (Linux/macOS)
top -p $(pgrep -f "python app.py")

# Kill process on port 5000 (Linux/macOS)
kill -9 $(lsof -t -i:5000)
```

---

## ✨ Next Steps

After successful installation:

1. Read [README.md](README.md) for features overview
2. Check [Usage Guide](README.md#-usage) for how to use the system
3. Review [API Documentation](README.md#-api-endpoints)
4. Upload a test video/image to verify operation
5. Configure settings for your use case

---

**Version**: 1.0.0  
**Last Updated**: February 2026  
**Status**: Fully Documented
