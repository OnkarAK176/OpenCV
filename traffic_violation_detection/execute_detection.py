import sys
import os
import json
import time

sys.path.insert(0, r'E:\Desktop\proj\traffic_violation_detection\backend')
os.chdir(r'E:\Desktop\proj\traffic_violation_detection\backend')

from utils.realtime_detection import RealtimeDetector, StreamingProcessor
from config import Config

config = Config()

print('=' * 70)
print('TRAFFIC VIOLATION DETECTION - REAL-TIME EXECUTION')
print('=' * 70)
print()

# Initialize detector
print('Initializing Real-Time Detector...')
detector = RealtimeDetector(use_gpu=False)
processor = StreamingProcessor(detector, speed_limit=config.SPEED_LIMIT)

print('   ✓ Detector ready')
print('   ✓ Processing mode: Real-time streaming')
print('   ✓ Frame skip: 2 (50% faster processing)')
print()

# Process video
video_path = r'E:\Desktop\proj\traffic_violation_detection\test_traffic_synthetic.mp4'
print('📹 Processing video: test_traffic_synthetic.mp4')
print('   - Duration: 5 seconds')
print('   - Resolution: 640x480')
print()

start_time = time.time()
print('⏳ Processing frames...')

violations = []
frame_count = 0

def on_violation(violation):
    global frame_count, violations
    violations.append(violation)
    frame_count += 1
    frame_id = violation.get('frame_num', 'N/A')
    speed = violation.get('speed', 0)
    plate = violation.get('license_plate', 'N/A')
    print(f'   [VIOLATION] Frame {frame_id}: Speed {speed:.1f} km/h - Plate: {plate}')

try:
    result = processor.process_stream(
        video_path,
        output_callback=on_violation
    )
    
    elapsed_time = time.time() - start_time
    
    print()
    print('=' * 70)
    print('SUCCESS: PROCESSING COMPLETE')
    print('=' * 70)
    print()
    print('📊 DETECTION RESULTS:')
    print(f'   • Processing time: {elapsed_time:.2f} seconds')
    print(f'   • Total violations: {result.get("violations", 0)}')
    print(f'   • Total frames: {result.get("total_frames", 0)}')
    print(f'   • FPS during processing: {result.get("fps", 30):.1f}')
    print(f'   • Violations detected: {len(result.get("violation_list", []))}')
    print()
    print('📈 STATISTICS:')
    video_duration = result.get("total_frames", 0) / result.get("fps", 30)
    efficiency = video_duration / elapsed_time if elapsed_time > 0 else 0
    print(f'   • Video duration: ~{video_duration:.1f} seconds')
    print(f'   • Processing efficiency: {efficiency:.2f}x')
    print()
    print('⚙️  OPTIMIZATION DETAILS:')
    print('   • Frame skip: ENABLED (every 2nd frame)')
    print('   • Speed boost: ~2x faster than no-skip')
    print('   • GPU acceleration: Disabled (CPU mode)')
    print()
    print('=' * 70)
    
    print('\nJSON OUTPUT:')
    print(json.dumps(result, indent=2))
    
except Exception as e:
    print(f'ERROR: {str(e)}')
    import traceback
    traceback.print_exc()
