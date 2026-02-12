import cv2
import numpy as np
from typing import Tuple, List, Dict, Optional
import logging
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)

class VideoProcessor:
    """Process video files for traffic violation detection"""
    
    def __init__(self, detector, recognizer, violation_detector):
        self.detector = detector
        self.recognizer = recognizer
        self.violation_detector = violation_detector
        self.vehicle_tracks = defaultdict(list)  # Track vehicles across frames
        self.next_vehicle_id = 0
    
    def process_video(self, video_path: str, output_path: Optional[str] = None, 
                     confidence_threshold: float = 0.6) -> Dict:
        """
        Process video and detect traffic violations
        
        Args:
            video_path: Path to input video
            output_path: Optional path to save annotated video
            confidence_threshold: Min confidence for detections
        
        Returns:
            Dictionary with violations found and statistics
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return {'error': f'Failed to open video: {video_path}'}
        
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Setup video writer if output path provided
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        violations = []
        frame_count = 0
        
        logger.info(f"Starting video processing: {fps} fps, {width}x{height}, {total_frames} frames")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Detect vehicles
            detections = self.detector.detect_vehicles(frame)
            
            # Process each detection
            for detection in detections:
                violation_data = self._process_vehicle(
                    frame, detection, frame_count, fps, confidence_threshold
                )
                
                if violation_data and violation_data.get('is_violation'):
                    violations.append(violation_data)
                    
                    # Draw on frame
                    frame = self._draw_violation(frame, violation_data)
            
            # Write to output video
            if writer:
                writer.write(frame)
            
            # Log progress every 100 frames
            if frame_count % 100 == 0:
                logger.info(f"Processed {frame_count}/{total_frames} frames")
        
        cap.release()
        if writer:
            writer.release()
        
        return {
            'success': True,
            'total_frames': frame_count,
            'fps': fps,
            'violations_detected': len(violations),
            'violations': violations,
            'output_path': output_path if output_path else None
        }
    
    def _process_vehicle(self, frame: np.ndarray, detection: Dict, 
                        frame_count: int, fps: float, conf_threshold: float) -> Optional[Dict]:
        """Process individual vehicle detection"""
        
        bbox = detection['bbox']
        confidence = detection['confidence']
        
        if confidence < conf_threshold:
            return None
        
        x1, y1, x2, y2 = bbox
        vehicle_region = frame[y1:y2, x1:x2]
        
        # Try to detect license plate
        plate_detected = False
        plate_text = "UNRECOGNIZED"
        plate_confidence = 0.0
        
        # Simple license plate detection: look in lower portion of vehicle
        plate_height = (y2 - y1) // 3  # Lower third of vehicle
        plate_region = frame[y2 - plate_height:y2, x1:x2]
        
        if plate_region.size > 0:
            ocr_result = self.recognizer.recognize_plate(plate_region)
            if ocr_result['success'] and ocr_result['confidence'] > 0.5:
                plate_text = ocr_result['text']
                plate_confidence = ocr_result['confidence']
                plate_detected = True
        
        # Estimate speed (simplified - would need calibration for real system)
        estimated_speed = np.random.uniform(40, 75)  # Simulated speed for demo
        
        violation_result = self.violation_detector.detect_speed_violation(estimated_speed)
        
        return {
            'frame': frame_count,
            'timestamp': frame_count / fps,
            'vehicle_bbox': bbox,
            'vehicle_confidence': float(confidence),
            'plate_text': plate_text,
            'plate_confidence': float(plate_confidence),
            'plate_detected': plate_detected,
            'estimated_speed': estimated_speed,
            'is_violation': violation_result['is_violation'],
            'violation_type': violation_result['violation_type'],
            'excess_speed': violation_result['excess_speed'],
            'speed_limit': violation_result['speed_limit']
        }
    
    def _draw_violation(self, frame: np.ndarray, violation_data: Dict) -> np.ndarray:
        """Draw violation information on frame"""
        
        x1, y1, x2, y2 = violation_data['vehicle_bbox']
        
        # Draw vehicle bounding box (red for violation, green for normal)
        color = (0, 0, 255) if violation_data['is_violation'] else (0, 255, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Draw plate text
        plate_text = violation_data['plate_text']
        plate_conf = violation_data['plate_confidence']
        cv2.putText(frame, f"Plate: {plate_text} ({plate_conf:.2f})", 
                   (x1, y1 - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw speed and violation info
        speed = violation_data['estimated_speed']
        speed_text = f"Speed: {speed:.1f} km/h"
        cv2.putText(frame, speed_text, (x1, y1 - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        if violation_data['is_violation']:
            excess = violation_data['excess_speed']
            violation_text = f"⚠ VIOLATION +{excess:.1f} km/h"
            cv2.putText(frame, violation_text, (x1, y2 + 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return frame
    
    def process_image(self, image_path: str, confidence_threshold: float = 0.6) -> Dict:
        """Process single image for violations"""
        
        frame = cv2.imread(image_path)
        if frame is None:
            return {'error': f'Failed to load image: {image_path}'}
        
        detections = self.detector.detect_vehicles(frame)
        violations = []
        
        for detection in detections:
            violation_data = self._process_vehicle(frame, detection, 1, 30, confidence_threshold)
            if violation_data:
                violations.append(violation_data)
        
        return {
            'success': True,
            'image_path': image_path,
            'detections_count': len(detections),
            'violations': violations
        }
