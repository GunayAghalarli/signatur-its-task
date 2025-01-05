import sqlite3
import cv2
import numpy as np
import re
import json
import time

start_time = time.time()

db_path = "./signaturits_metadata.db"
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# create the camera frame and making all pixels white
width, height = 1280, 720
# get camera ids from db and store in an array
# Fetch camera details
step1_start = time.time()
camera_details = cursor.execute("SELECT camera_id, width, height FROM camera_config").fetchall()
camera_objects = [{"camera_id": cam[0], "width": cam[1], "height": cam[2]} for cam in camera_details] 
step1_end = time.time()
print(f"Fetching camera details took {step1_end - step1_start:.4f} seconds")

# get camera id and coordinates from db
# Fetch plate details
step2_start = time.time()
plate_details = cursor.execute("SELECT reading_id, camera_id, coordinates FROM readings").fetchall()
plate_objects = [{"reading_id":plate[0],"camera_id": plate[1], "coordinates": plate[2]} for plate in plate_details]
step2_end = time.time()
print(f"Fetching plate details took {step2_end - step2_start:.4f} seconds")

# Convert coordinates strings to proper lists
step3_start = time.time()
for plate in plate_objects:
    coordinates_str = plate['coordinates']

     # Remove newline characters and convert spaces to commas
    coordinates_str = re.sub(r'\s+', ',', coordinates_str.replace('\n', ' ').strip())

    # replace [, with just [ to handle cases like [,779]
    coordinates_str = re.sub(r'\[\s*,', '[', coordinates_str)  
    
    try:
        # Convert coordinates_str to a list of lists 
        plate['coordinates'] = json.loads(coordinates_str)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON for plate {plate['reading_id']}: {e}")
        plate['coordinates'] = []  # Default to empty list if there's an error
step3_end = time.time()
print(f"Processing and cleaning coordinates took {step3_end - step3_start:.4f} seconds")

# Group plates by camera_id
step4_start = time.time()
plates_by_camera = {}
for plate in plate_objects:
    camera_id = plate['camera_id']
    if camera_id not in plates_by_camera:
        plates_by_camera[camera_id] = []
    plates_by_camera[camera_id].append(plate)
step4_end = time.time()
print(f"Grouping plates by camera_id took {step4_end - step4_start:.4f} seconds")

# itearting through camera objects
step5_start = time.time()
for camera in camera_objects:
    # extract camera objects id, width and height
    cam_id = camera["camera_id"]
    cam_width = camera["width"]
    cam_height = camera["height"]
    # create white canvas for each camera
    camera_frame = np.ones((cam_height, cam_width), dtype=np.uint8)*255

    # Get plates for this camera
    plates = plates_by_camera.get(cam_id, [])

     # Draw each plate as a polygon
    for plate in plates:
        if not plate['coordinates']:
            continue  # Skip if coordinates are invalid or empty

        # Convert coordinates to numpy array
        plate_coords = np.array(plate['coordinates'], dtype=np.int32)

        cv2.polylines(camera_frame, [plate_coords], isClosed=True, color=(0, 0, 255), thickness=2)

    # displays canvas for each camera
    cv2.imshow("Camera " + str(cam_id) + " Canvas ", camera_frame)
step5_end = time.time()
print(f"Drawing and displaying frames took {step5_end - step5_start:.4f} seconds")

# wait for any key press and close all windows
cv2.waitKey(0)
cv2.destroyAllWindows()
connection.close()

