import sqlite3
import cv2
import numpy as np
import re
import ast

db_path = "./signaturits_metadata.db"
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# create the camera frame and making all pixels white
width, height = 1280, 720
# get camera ids from db and store in an array
camera_details = cursor.execute("SELECT camera_id, width, height FROM camera_config").fetchall()
camera_objects = [{"camera_id": cam[0], "width": cam[1], "height": cam[2]} for cam in camera_details] 

# get camera id and coordinates from db
plate_details = cursor.execute("SELECT camera_id, coordinates FROM readings").fetchall()
# an array to store plate details as objects
plates_objects = [] 

for plate in plate_details:
    camera_id = plate[0]
    coordinates_str = plate[1]
     

    # store each camera id and coordinates as asn object and add into array
    plate_obj = {"camera_id": camera_id, "coordinates": coordinates_str}
    plates_objects.append(plate_obj)

for obj in plates_objects[:10]:
    print("plates_objects", obj)





# itearting through camera objects
for camera in camera_objects:
    # extract camera objects id, width and height
    cam_id = camera["camera_id"]
    cam_width = camera["width"]
    cam_height = camera["height"]
    # create white canvas for each camera
    camera_frame = np.ones((cam_height, cam_width), dtype=np.uint8)*255
# set border tickness and color
# border_thickness = 5
# color = (0, 0, 0)
# cv2.rectangle(camera1, (0, 0), (width, border_thickness), color, -1)
# cv2.rectangle(camera1, (0, height - border_thickness), (width, height), color, -1)
# cv2.rectangle(camera1, (0, 0), (border_thickness, height), color, -1)
# cv2.rectangle(camera1, (width - border_thickness, 0), (width, height), color, -1)

# Define the coordinates of the plate (as a 4-point polygon)
# plate_coords = np.array([[508, 578], [760, 578], [760, 635], [508, 635]])
# # Draw the plate as a polygon (quadrilateral) with a blue border
# cv2.polylines(camera1, [plate_coords], isClosed=True, color=(255, 0, 0), thickness=2)
    # displas canvas for each camera
    cv2.imshow("Camera " + str(cam_id) + " Canvas ", camera_frame)

# wait for any key press and close all windows
cv2.waitKey(0)
cv2.destroyAllWindows()
connection.close()
