import cv2
import numpy as np
from ultralytics import YOLO
import easyocr
from typing import Tuple, List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VehicleDetector:
    """Detects vehicles and their license plates using YOLOv8"""
    
    def __init__(self, model_path: str = 'models/yolov8n.pt', conf_threshold: float = 0.5):
        """Initialize YOLO model for vehicle detection"""
        try:
            self.model = YOLO(model_path)
            self.conf_threshold = conf_threshold
            logger.info(f"✓ YOLO model loaded from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            self.model = None
    
    def detect_vehicles(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect vehicles in frame
        Returns: List of detections with bounding boxes and confidence
        """
        if self.model is None:
            return []
        
        try:
            results = self.model(frame, conf=self.conf_threshold, verbose=False)
            detections = []
            
            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0])
                        cls = int(box.cls[0])
                        
                        # COCO class 2 = car, 5 = bus, 7 = truck
                        if cls in [2, 5, 7]:
                            detections.append({
                                'bbox': (int(x1), int(y1), int(x2), int(y2)),
                                'confidence': conf,
                                'class': cls,
                                'area': (x2 - x1) * (y2 - y1)
                            })
            
            return detections
        except Exception as e:
            logger.error(f"Error in vehicle detection: {e}")
            return []
    
    def detect_license_plates(self, frame: np.ndarray, vehicle_bbox: Tuple) -> List[Dict]:
        """
        Detect license plates in vehicle region
        Returns: List of cropped license plate regions
        """
        x1, y1, x2, y2 = vehicle_bbox
        vehicle_region = frame[y1:y2, x1:x2]
        
        if vehicle_region.size == 0:
            return []
        
        # Use YOLO to detect license plates in vehicle region
        try:
            results = self.model(vehicle_region, conf=0.5, verbose=False)
            plates = []
            
            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        px1, py1, px2, py2 = box.xyxy[0].cpu().numpy()
                        conf = float(box.conf[0])
                        
                        # Adjust coordinates to original frame
                        plates.append({
                            'bbox': (int(x1 + px1), int(y1 + py1), int(x1 + px2), int(y1 + py2)),
                            'confidence': conf,
                            'crop': vehicle_region[int(py1):int(py2), int(px1):int(px2)]
                        })
            
            return plates
        except Exception as e:
            logger.error(f"Error detecting license plates: {e}")
            return []


class OCRRecognizer:
    """Performs OCR on license plates using EasyOCR"""
    
    def __init__(self, languages: List[str] = ['en']):
        """Initialize EasyOCR reader"""
        try:
            self.reader = easyocr.Reader(languages, gpu=False)
            logger.info(f"✓ OCR model initialized with languages: {languages}")
        except Exception as e:
            logger.error(f"Failed to initialize OCR: {e}")
            self.reader = None
    
    def recognize_plate(self, plate_image: np.ndarray) -> Dict:
        """
        Recognize text on license plate
        Returns: OCR results with text and confidence
        """
        if self.reader is None or plate_image is None or plate_image.size == 0:
            return {'text': '', 'confidence': 0.0, 'success': False}
        
        try:
            # Preprocess image for better OCR
            gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            
            # Run OCR
            results = self.reader.readtext(thresh, detail=1)
            
            if not results:
                return {'text': '', 'confidence': 0.0, 'success': False}
            
            # Combine text and calculate average confidence
            text = ''.join([result[1] for result in results])
            avg_confidence = np.mean([result[2] for result in results])
            
            return {
                'text': text.strip(),
                'confidence': float(avg_confidence),
                'success': True,
                'raw_results': results
            }
        except Exception as e:
            logger.error(f"Error in OCR recognition: {e}")
            return {'text': '', 'confidence': 0.0, 'success': False}


class ViolationDetector:
    """Detects traffic violations"""
    
    def __init__(self, speed_limit: float = 60.0):
        self.speed_limit = speed_limit
        self.violation_threshold = speed_limit + 5  # 5 km/h margin
    
    def detect_speed_violation(self, estimated_speed: float) -> Dict:
        """Detect if vehicle exceeded speed limit"""
        return {
            'is_violation': estimated_speed > self.violation_threshold,
            'estimated_speed': estimated_speed,
            'speed_limit': self.speed_limit,
            'excess_speed': max(0, estimated_speed - self.speed_limit),
            'violation_type': 'SPEEDING' if estimated_speed > self.violation_threshold else 'NORMAL'
        }
    
    def estimate_speed(self, bbox1: Tuple, bbox2: Tuple, fps: float, time_interval: float) -> float:
        """
        Rough estimate of vehicle speed based on movement
        In real implementation, would use optical flow and calibration
        """
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Calculate center displacement
        center1 = ((x1_1 + x2_1) / 2, (y1_1 + y2_1) / 2)
        center2 = ((x1_2 + x2_2) / 2, (y1_2 + y2_2) / 2)
        
        distance_pixels = np.sqrt((center2[0] - center1[0])**2 + (center2[1] - center1[1])**2)
        
        # Rough conversion (needs camera calibration for accuracy)
        pixels_per_meter = 10  # This should be calibrated with actual camera
        distance_meters = distance_pixels / pixels_per_meter
        time_seconds = time_interval
        
        if time_seconds > 0:
            speed_ms = distance_meters / time_seconds
            speed_kmh = speed_ms * 3.6
            return max(0, speed_kmh)
        
        return 0.0
