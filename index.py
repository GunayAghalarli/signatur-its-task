import sqlite3
import cv2
import numpy as np
import re
import json
import matplotlib.pyplot as plt
import time

# Database connection
db_path = "./signaturits_metadata.db"
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# Fetch camera and plate details from the database
camera_details = cursor.execute("SELECT camera_id, width, height FROM camera_config").fetchall()
camera_objects = [{"camera_id": cam[0], "width": cam[1], "height": cam[2]} for cam in camera_details]
plate_details = cursor.execute("SELECT camera_id, coordinates FROM readings").fetchall()
plate_objects = [{"camera_id": plate[0], "coordinates": plate[1]} for plate in plate_details]

for plate in plate_objects:
    coordinates_str = plate['coordinates']
    # Clean '\n' add ',' between coordinates and arrays in the coordinates_str
    coordinates_str = re.sub(r'\s+', ',', coordinates_str.replace('\n', ' ').strip())
    coordinates_str = re.sub(r'\[\s*,', '[', coordinates_str)  # Handle cases like [,779]
    try:
        plate['coordinates'] = json.loads(coordinates_str)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON for plate {plate['reading_id']}: {e}")
        plate['coordinates'] = []  # Default to empty list if there's an error

# Group plates by camera_id
plates_by_camera = {} # empty dictionary to store plates grouped by camera ids
for plate in plate_objects:
    camera_id = plate['camera_id']
    if camera_id not in plates_by_camera:
        plates_by_camera[camera_id] = []
    plates_by_camera[camera_id].append(plate)

# Process each camera
for camera in camera_objects:
    cam_id = camera["camera_id"]
    cam_width = camera["width"]
    cam_height = camera["height"]

    # Initialize the heatmap and camera frame
    composite_heatmap = np.zeros((cam_height, cam_width), dtype=np.float32)
    camera_frame = np.ones((cam_height, cam_width, 3), dtype=np.uint8) * 255

    # Get plates associated with this camera
    plates = plates_by_camera.get(cam_id, [])

    # Process each plate
    for plate in plates:
        if not plate['coordinates']:
            continue  # Skip plates with invalid or empty coordinates

        # Convert coordinates to numpy array
        plate_coords = np.array(plate['coordinates'], dtype=np.int32)
        # Reshape coordinates to the correct format for OpenCV
        plate_coords = plate_coords.reshape((-1, 1, 2))  # Reshaping to (-1, 1, 2)

        # Create a mask for the current plate
        plate_mask = np.zeros((cam_height, cam_width), dtype=np.float32)
        cv2.fillPoly(plate_mask, [plate_coords], color=1)
    

        # Accumulate the plate mask into the heatmap
        cv2.add(composite_heatmap, plate_mask, composite_heatmap)
    
        # Draw plate outlines on the camera frame
        cv2.polylines(camera_frame, [plate_coords], isClosed=True, color=(0, 0, 255), thickness=2)
    # Find the maximum overlap in the heatmap
    max_visits = np.max(composite_heatmap)
    max_region = np.argwhere(composite_heatmap == max_visits)
    print(f"Camera {cam_id}: Maximum overlap of {max_visits} plates(pixels) at {len(max_region)} regions (height, width): {max_region}")

    # Normalize the heatmap for visualization
    composite_heatmap_normalized = cv2.normalize(composite_heatmap, None, 0, 255, cv2.NORM_MINMAX)
    composite_heatmap_uint8 = composite_heatmap_normalized.astype(np.uint8)

    # Apply a color map for better visualization
    composite_heatmap_colored = cv2.applyColorMap(composite_heatmap_uint8, cv2.COLORMAP_JET)

    # Display results
    plt.figure(figsize=(8, 6))
    plt.imshow(cv2.cvtColor(composite_heatmap_colored, cv2.COLOR_BGR2RGB))
    plt.colorbar(label="Overlap Intensity")
    plt.title(f"Camera {cam_id} - Heatmap of Overlapping Plates")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.grid(visible=False)
    plt.show()

    plt.figure(figsize=(8, 6))
    plt.imshow(cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB))
    plt.title(f"Camera {cam_id} - Individual Plate Locations")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.grid(visible=False)
    plt.show()

# Clean up
cv2.destroyAllWindows()
connection.close()
