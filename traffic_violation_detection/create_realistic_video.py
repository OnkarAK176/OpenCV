"""
Generate realistic test video with features YOLO can detect
"""
import sys
import os
sys.path.insert(0, r'E:\Desktop\proj\traffic_violation_detection\backend')
os.chdir(r'E:\Desktop\proj\traffic_violation_detection')

import cv2
import numpy as np

print('=' * 80)
print('🎬 GENERATING REALISTIC TRAFFIC VIDEO FOR DETECTION')
print('=' * 80)

# Create video with actual detectible objects
output_path = 'test_traffic_realistic.mp4'
fps = 30
duration = 8  # 8 seconds
frame_count = fps * duration
width, height = 1280, 720

print(f'\nGenerating: {output_path}')
print(f'Duration: {duration} seconds ({frame_count} frames)')
print(f'Resolution: {width}x{height}')

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

def draw_car(frame, x, y, size=80, color=(0, 0, 255)):
    """Draw a simple car shape that YOLO can detect"""
    x, y = int(x), int(y)
    # Body
    cv2.rectangle(frame, (x, y), (x + size, y + size // 2), color, -1)
    # Top
    cv2.rectangle(frame, (x + 10, y - 20), (x + size - 10, y), color, -1)
    # Windows
    cv2.rectangle(frame, (x + 15, y - 15), (x + 30, y - 5), (100, 100, 100), -1)
    cv2.rectangle(frame, (x + size - 30, y - 15), (x + size - 15, y - 5), (100, 100, 100), -1)
    # Wheels
    cv2.circle(frame, (x + 20, y + size // 2), 10, (0, 0, 0), -1)
    cv2.circle(frame, (x + size - 20, y + size // 2), 10, (0, 0, 0), -1)

def draw_truck(frame, x, y, size=120, color=(0, 100, 200)):
    """Draw a truck"""
    x, y = int(x), int(y)
    # Cab
    cv2.rectangle(frame, (x, y + 20), (x + 50, y + size), color, -1)
    # Cargo
    cv2.rectangle(frame, (x + 50, y), (x + size, y + size), color, -1)
    # Wheels
    cv2.circle(frame, (x + 20, y + size), 12, (0, 0, 0), -1)
    cv2.circle(frame, (x + size - 20, y + size), 12, (0, 0, 0), -1)

def draw_bus(frame, x, y, size=100, color=(0, 150, 0)):
    """Draw a bus"""
    x, y = int(x), int(y)
    cv2.rectangle(frame, (x, y), (x + size, y + size), color, -1)
    # Windows
    for i in range(3):
        cv2.rectangle(frame, (x + 10 + i * 25, y + 10), (x + 20 + i * 25, y + 30), (100, 100, 100), -1)

print('\nRendering frames...')
for frame_num in range(frame_count):
    # Road background
    frame = np.ones((height, width, 3), dtype=np.uint8) * 100
    
    # Road
    cv2.rectangle(frame, (0, 200), (width, 600), (80, 80, 80), -1)
    
    # Lane markings
    for i in range(0, width, 150):
        cv2.line(frame, (i + int(frame_num % 150), 350), 
                       (i + 80 + int(frame_num % 150), 350), 
                       (255, 255, 0), 3)
    
    # Car 1 (bottom lane)
    car1_x = (frame_num * 3) % (width + 100)
    draw_car(frame, car1_x - 80, 320, 80, (0, 0, 255))
    
    # Car 2 (middle lane)
    car2_x = ((frame_num + 50) * 2.5) % (width + 100)
    draw_car(frame, car2_x - 80, 220, 80, (0, 0, 200))
    
    # Truck (top lane)
    truck_x = ((frame_num + 100) * 2) % (width + 100)
    draw_truck(frame, truck_x - 120, 100, 120, (0, 100, 200))
    
    # Bus (occasional)
    if frame_num % 60 == 0:
        bus_x = (frame_num // 30 * 250) % (width + 200)
        draw_bus(frame, bus_x - 100, 400, 100, (0, 150, 0))
    
    # Info text
    cv2.putText(frame, f'Frame: {frame_num}/{frame_count}', (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, f'Speed: {60 + (frame_num % 40):.0f} km/h', (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Speed limit sign
    cv2.rectangle(frame, (width - 150, 20), (width - 20, 120), (255, 0, 0), -1)
    cv2.putText(frame, '60', (width - 135, 95), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    
    out.write(frame)
    
    if frame_num % 30 == 0:
        print(f'  Frame {frame_num}/{frame_count} ✓')

out.release()

import os
file_size = os.path.getsize(output_path) / (1024 * 1024)
print(f'\n✅ Video created: {output_path}')
print(f'📊 File size: {file_size:.2f} MB')
print(f'🎥 Video ready for detection!')
print('=' * 80)
