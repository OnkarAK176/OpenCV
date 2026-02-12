from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import logging
from datetime import datetime
import threading
from config import config
from utils.realtime_detection import RealtimeDetector, StreamingProcessor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config)
CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})

# Initialize detector (loaded once)
logger.info("Initializing real-time detector...")
detector = RealtimeDetector(use_gpu=False)  # Set to True if you have GPU
processor = StreamingProcessor(detector, speed_limit=config.SPEED_LIMIT)

# Global variables for streaming
streaming_data = {
    'current_frame': 0,
    'total_violations': 0,
    'detections_count': 0,
    'timestamp': None,
    'last_violations': []
}
streaming_lock = threading.Lock()

logger.info("✓ Real-time detector initialized!")


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'models_loaded': detector.model is not None
    }), 200


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload video or image for processing"""
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify(
            {'error': f'File type not allowed. Allowed: {config.ALLOWED_EXTENSIONS}'}
        ), 400
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > config.MAX_FILE_SIZE:
        return jsonify({'error': f'File too large. Max: {config.MAX_FILE_SIZE / 1024 / 1024}MB'}), 400
    
    try:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join(config.UPLOAD_FOLDER, filename)
        
        file.save(filepath)
        
        logger.info(f"File uploaded: {filename}")
        
        return jsonify({
            'success': True,
            'file_id': filename,
            'filename': filename
        }), 200
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/process/realtime', methods=['POST'])
def process_realtime():
    """
    Real-time video processing with streaming updates
    Much faster than batch processing
    """
    
    data = request.get_json()
    
    if not data or 'file_id' not in data:
        return jsonify({'error': 'file_id required'}), 400
    
    file_id = data['file_id']
    filepath = os.path.join(config.UPLOAD_FOLDER, file_id)
    
    if not os.path.exists(filepath):
        return jsonify({'error': f'File not found: {file_id}'}), 404
    
    try:
        logger.info(f"Starting real-time processing: {file_id}")
        
        def on_violation(violation_info):
            """Callback when violation is detected"""
            with streaming_lock:
                streaming_data['last_violations'].append(violation_info)
                if len(streaming_data['last_violations']) > 10:
                    streaming_data['last_violations'].pop(0)
                streaming_data['total_violations'] += 1
        
        def on_frame(frame_info):
            """Callback on each frame processed"""
            with streaming_lock:
                streaming_data.update(frame_info)
        
        # Process stream
        result = processor.process_stream(
            filepath,
            output_callback=on_violation,
            frame_callback=on_frame
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        logger.info(f"Real-time processing complete: {result['violations']} violations")
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'total_frames': result['total_frames'],
            'fps': result['fps'],
            'violations_detected': result['violations'],
            'violations': result['violation_list'],
            'processing_type': 'realtime'
        }), 200
    
    except Exception as e:
        logger.error(f"Processing error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stream/status', methods=['GET'])
def stream_status():
    """Get current streaming status"""
    with streaming_lock:
        return jsonify({
            'current_frame': streaming_data['current_frame'],
            'total_violations': streaming_data['total_violations'],
            'detections_count': streaming_data['detections_count'],
            'recent_violations': streaming_data['last_violations']
        }), 200


@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    """Get/update system settings"""
    
    if request.method == 'POST':
        data = request.get_json()
        
        if 'frame_skip' in data:
            detector.frame_skip = int(data['frame_skip'])
        
        if 'confidence' in data:
            detector.conf_threshold = float(data['confidence'])
        
        return jsonify({'success': True, 'message': 'Settings updated'}), 200
    
    return jsonify({
        'frame_skip': detector.frame_skip,
        'confidence': detector.conf_threshold,
        'speed_limit': config.SPEED_LIMIT
    }), 200


@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """Get system statistics"""
    
    with streaming_lock:
        return jsonify({
            'success': True,
            'total_violations': streaming_data['total_violations'],
            'current_frame': streaming_data['current_frame'],
            'processing_fps': streaming_data.get('fps', 0)
        }), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Real-Time Traffic Violation Detection System")
    logger.info("=" * 60)
    logger.info("⚡ Optimized for fast processing with frame skipping")
    logger.info("🚀 Starting on http://0.0.0.0:5000")
    logger.info("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
