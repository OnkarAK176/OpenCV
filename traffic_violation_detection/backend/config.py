import os

# Application Configuration
class Config:
    # Flask Settings
    FLASK_ENV = 'development'
    DEBUG = True
    SECRET_KEY = 'your-secret-key-change-in-production'
    
    # Upload Settings
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'jpg', 'jpeg', 'png'}
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    
    # YOLO Settings
    CONFIDENCE_THRESHOLD = 0.5
    NMS_THRESHOLD = 0.4
    
    # Model Paths
    YOLO_WEIGHTS = 'models/yolov8n.pt'  # YOLOv8 Nano
    
    # Speed Detection (km/h)
    SPEED_LIMIT = 60
    VIOLATION_SPEED_THRESHOLD = 65
    
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///violations.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Settings
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5000']
    
    # File Storage
    RESULTS_FOLDER = 'results'
    
    def __init__(self):
        # Create necessary directories
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(self.RESULTS_FOLDER, exist_ok=True)
        os.makedirs('models', exist_ok=True)

config = Config()
