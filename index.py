
import cv2
import numpy as np

import matplotlib.pyplot as plt

width, height = 1280, 720

heatmap = np.zeros((height, width), dtype=np.int32)
camera_frame = np.ones((height, width,3), dtype=np.uint8) * 255

plates = [[[508, 578], [760, 578], [760, 635], [508, 635]], [[403, 569],
 [598, 569], [598, 624], [403, 624]], [[518, 579], [758, 589], [756, 635], [516, 625]], 
 [[547, 592], [797, 600], [795, 648], [545, 640]], [[597, 465],
 [780, 476], [777, 511], [594, 500]], [[597, 465],
 [782, 465],
 [782, 511],
 [597, 511]], [[431, 561], [647, 576], [644, 618], [428, 603]], [[462, 570], [634, 570], [634, 610], [462, 610]], [[696, 380], [909, 390], [907, 431],
 [694, 422]], [[425, 561], [651, 561], [651, 618], [425, 618]]]

plate_objects = [{"coordinates": plate} for plate in plates]
print(f"plate objects at {plate_objects}")

for plate in plate_objects:
        if not plate['coordinates']:
            continue  # Skip if coordinates are invalid or empty

        # Convert coordinates to numpy array
        plate_coords = np.array(plate['coordinates'], dtype=np.int32)
        print(f"plate_coords at {plate_coords}")
        # Increment heatmap for overlaps
        temp_mask = np.zeros_like(heatmap, dtype=np.int32)
        cv2.fillPoly(temp_mask, [plate_coords], color=1)
        # Add the temporary mask to the heatmap
        heatmap += temp_mask  # Increment existing values
        # Draw plate outlines on camera frame
        cv2.polylines(camera_frame, [plate_coords], isClosed=True, color=(0, 0, 255), thickness=2)

# Find regions of maximum overlap
max_visits = np.max(heatmap)
max_region = np.argwhere(heatmap == max_visits)
print(f"Camera  Maximum overlap of {max_visits} plates at regions: {max_region}")
heatmap_normalized = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
heatmap_colored = cv2.applyColorMap(heatmap_normalized.astype(np.uint8), cv2.COLORMAP_JET)

plt.figure(figsize=(8, 6))
plt.imshow(cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB))
plt.colorbar(label="Overlap Intensity")
plt.title(f"Camera  - Heatmap of Overlapping Plates")
plt.xlabel("X Coordinate")
plt.ylabel("Y Coordinate")
plt.grid(visible=False)
plt.show()
plt.close('all')

plt.figure(figsize=(8, 6))
plt.imshow(cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB))
plt.title(f"Camera  - Individual Plate Locations")
plt.xlabel("X Coordinate")
plt.ylabel("Y Coordinate")
plt.grid(visible=False)
plt.show()
plt.close('all')

cv2.waitKey(0)
cv2.destroyAllWindows()








# import sqlite3
# import cv2
# import numpy as np
# import re
# import json
# import time
# import matplotlib.pyplot as plt

# start_time = time.time()

# db_path = "./signaturits_metadata.db"
# connection = sqlite3.connect(db_path)
# cursor = connection.cursor()

# # get camera ids from db and store in an array
# step1_start = time.time()
# camera_details = cursor.execute("SELECT camera_id, width, height FROM camera_config").fetchall()
# camera_objects = [{"camera_id": cam[0], "width": cam[1], "height": cam[2]} for cam in camera_details] 
# step1_end = time.time()
# print(f"Fetching camera details took {step1_end - step1_start:.4f} seconds")

# # get camera id and coordinates from db
# step2_start = time.time()
# plate_details = cursor.execute("SELECT reading_id, camera_id, coordinates FROM readings").fetchall()
# plate_objects = [{"reading_id":plate[0],"camera_id": plate[1], "coordinates": plate[2]} for plate in plate_details]
# step2_end = time.time()
# print(f"Fetching plate details took {step2_end - step2_start:.4f} seconds")

# # Convert coordinates strings to proper lists
# step3_start = time.time()
# for plate in plate_objects:
#     coordinates_str = plate['coordinates']

#      # Remove newline characters and convert spaces to commas
#     coordinates_str = re.sub(r'\s+', ',', coordinates_str.replace('\n', ' ').strip())

#     # replace [, with just [ to handle cases like [,779]
#     coordinates_str = re.sub(r'\[\s*,', '[', coordinates_str)  
    
#     try:
#         # Convert coordinates_str to a list of lists 
#         plate['coordinates'] = json.loads(coordinates_str)
        
#     except json.JSONDecodeError as e:
#         print(f"Error decoding JSON for plate {plate['reading_id']}: {e}")
#         plate['coordinates'] = []  # Default to empty list if there's an error
# step3_end = time.time()
# print(f"Processing and cleaning coordinates took {step3_end - step3_start:.4f} seconds")

# # Group plates by camera_id
# step4_start = time.time()
# plates_by_camera = {}
# for plate in plate_objects:
#     camera_id = plate['camera_id']
#     if camera_id not in plates_by_camera:
#         plates_by_camera[camera_id] = []
#     plates_by_camera[camera_id].append(plate)
# step4_end = time.time()
# print(f"Grouping plates by camera_id took {step4_end - step4_start:.4f} seconds")


# # itearting through camera objects
# step5_start = time.time()
# for camera in camera_objects:
#     # extract camera objects id, width and height
#     cam_id = camera["camera_id"]
#     cam_width = camera["width"]
#     cam_height = camera["height"]

#     # Create an empty "heatmap" for the camera frame
#     heatmap = np.zeros((cam_height, cam_width), dtype=np.int32)
    
#     # create white canvas for each camera
#     camera_frame = np.ones((cam_height, cam_width), dtype=np.uint8)*255

#     # Get plates for this camera
#     plates = plates_by_camera.get(cam_id, [])

#     # Add each plate's coverage to the heatmap
#     for plate in plates:
#         if not plate['coordinates']:
#             continue  # Skip if coordinates are invalid or empty

#         # Convert coordinates to numpy array
#         plate_coords = np.array(plate['coordinates'], dtype=np.int32)
        
#         cv2.fillPoly(heatmap, [plate_coords], color=10)
     

#         # Plot the plate location on the white canvas
#         cv2.polylines(camera_frame, [plate_coords], isClosed=True, color=(0, 0, 255), thickness=2)  # Red lines for plates



#     # Find the region with the most overlap
#     max_visits = np.max(heatmap)
#     print(f"Maximum heatmap value for Camera {cam_id}: {max_visits}")

#     max_region = np.argwhere(heatmap == max_visits)

#     # Display results for the current camera
#     print(f"Camera {cam_id}: Maximum overlap of {max_visits} plates at regions: {max_region}")

#     # visualize the heatmap
#     normalized_heatmap = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
#     heatmap_colored = cv2.applyColorMap(normalized_heatmap, cv2.COLORMAP_JET)
#     # Convert BGR to RGB for displaying with Matplotlib
#     heatmap_colored_rgb = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)



 

#     # Heatmap of Overlapping Plates
#     plt.figure(figsize=(8, 6))
#     plt.imshow(heatmap_colored_rgb, cmap='jet', origin='upper')
#     plt.colorbar(label="Overlap Intensity")
#     plt.title(f"Camera {cam_id} - Heatmap of Overlapping Plates")
#     plt.xlabel("X Coordinate")
#     plt.ylabel("Y Coordinate")
#     plt.grid(visible=False)  
#     plt.show()
#     plt.close('all')

#     # Individual Plate Locations
#     plt.figure(figsize=(8, 6))
#     plt.imshow(cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB))  # Convert BGR (OpenCV) to RGB (Matplotlib)
#     plt.title(f"Camera {cam_id} - Individual Plate Locations")
#     plt.xlabel("X Coordinate")
#     plt.ylabel("Y Coordinate")
#     plt.grid(visible=False)  # Optional: Turn off grid lines if not needed
#     plt.show()
#     plt.close('all')

# step5_end = time.time()
# print(f"Drawing and displaying frames took {step5_end - step5_start:.4f} seconds")

# # wait for any key press and close all windows
# cv2.waitKey(0)
# cv2.destroyAllWindows()
# connection.close()
# end_time = time.time()
# print(f"Total script execution time: {end_time - start_time:.4f} seconds")
