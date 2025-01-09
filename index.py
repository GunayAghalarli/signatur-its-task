import sqlite3
import cv2
import numpy as np
import re
import json
import matplotlib.pyplot as plt
import time

db_path = "./signaturits_metadata.db"
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# get camera ids from db and store in an array
camera_details = cursor.execute("SELECT camera_id, width, height FROM camera_config").fetchall()
camera_objects = [{"camera_id": cam[0], "width": cam[1], "height": cam[2]} for cam in camera_details] 

# get camera id and coordinates from db
plate_details = cursor.execute("SELECT reading_id, camera_id, coordinates FROM readings").fetchall()
plate_objects = [{"reading_id":plate[0],"camera_id": plate[1], "coordinates": plate[2]} for plate in plate_details]

# convert coordinates strings to proper lists
for plate in plate_objects:
    coordinates_str = plate['coordinates']

    # remove newline characters and convert spaces to commas
    coordinates_str = re.sub(r'\s+', ',', coordinates_str.replace('\n', ' ').strip())

    # replace [, with just [ to handle cases like [,779]
    coordinates_str = re.sub(r'\[\s*,', '[', coordinates_str)  
    
    try:
        # convert coordinates_str to a list of lists 
        plate['coordinates'] = json.loads(coordinates_str)
        
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON for plate {plate['reading_id']}: {e}")
        plate['coordinates'] = []  # Default to empty list if there's an error
# group plates by camera_id
plates_by_camera = {}
for plate in plate_objects:
    start_time = time.time()
    camera_id = plate['camera_id']
    if camera_id not in plates_by_camera:
        plates_by_camera[camera_id] = []
    plates_by_camera[camera_id].append(plate)

# itearting through camera objects
for camera in camera_objects:

    # extract camera objects id, width and height
    cam_id = camera["camera_id"]
    cam_width = camera["width"]
    cam_height = camera["height"]

    # create an empty "heatmap" for the camera frame
    heatmap = np.zeros((cam_height, cam_width), dtype=np.int32)
    
    # create white canvas for each camera
    camera_frame = np.ones((cam_height, cam_width,3), dtype=np.uint8)*255

    # get plates for this camera
    plates = plates_by_camera.get(cam_id, [])

    # add each plate's coverage to the heatmap
    for plate in plates:
        
        if not plate['coordinates']:
            continue  # skip current plate if coordinates are invalid or empty

        # convert coordinates to numpy array
        plate_coords = np.array(plate['coordinates'], dtype=np.int32)
        # increment heatmap for overlaps
        temp_map = np.zeros_like(heatmap, dtype=np.int32)
        cv2.fillPoly(temp_map, [plate_coords], color=1)
        # add the temporary mask to the heatmap
        heatmap += temp_map  # increment existing values
        # draw on the white canvas
        cv2.polylines(camera_frame, [plate_coords], isClosed=True, color=(0, 0, 255), thickness=2)  # Red lines for plates

    # find the region with the most overlap
    max_visits = np.max(heatmap)
    print(f"Maximum heatmap value for Camera {cam_id}: {max_visits}")
    max_region = np.argwhere(heatmap == max_visits)
    # display results for the current camera
    print(f"Camera {cam_id}: Maximum overlap of {max_visits} plates at regions(height,width): {max_region}")

    # visualize the heatmap
    heatmap_normalized = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
    heatmap_colored = cv2.applyColorMap(heatmap_normalized.astype(np.uint8), cv2.COLORMAP_JET)
    end_time = time.time()
    print(f"Time taken to process camera {cam_id}: {end_time - start_time:.2f} seconds")
  
    # Heatmap of Overlapping Plates
    plt.figure(figsize=(8, 6))
    plt.imshow(cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB))
    plt.colorbar(label="Overlap Intensity")
    plt.title(f"Camera {cam_id} - Heatmap of Overlapping Plates")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.grid(visible=False)  
    plt.show()

    # Individual Plate Locations
    plt.figure(figsize=(8, 6))
    plt.imshow(cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB))  # Convert BGR (OpenCV) to RGB (Matplotlib)
    plt.title(f"Camera {cam_id} - Individual Plate Locations")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.grid(visible=False)  
    plt.show()

# wait for any key press and close all windows
cv2.waitKey(0)
cv2.destroyAllWindows()
connection.close()

