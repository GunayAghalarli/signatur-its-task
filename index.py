import sqlite3
import cv2
import numpy as np

db_path = "./signaturits_metadata.db"
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# create the camera frame and making all pixels white
width, height = 1280, 720
# get camera ids from db and store in an array
cameras = cursor.execute("SELECT camera_id FROM camera_config").fetchall()
camera_ids = [row[0] for row in cameras] 
print("print camera",camera_ids)
# function to create camera frame 
camera1 = np.ones((height, width, 3), dtype=np.uint8) * 255
# set border tickness and color
border_thickness = 5
color = (0, 0, 0)
cv2.rectangle(camera1, (0, 0), (width, border_thickness), color, -1)
cv2.rectangle(camera1, (0, height - border_thickness), (width, height), color, -1)
cv2.rectangle(camera1, (0, 0), (border_thickness, height), color, -1)
cv2.rectangle(camera1, (width - border_thickness, 0), (width, height), color, -1)

# Define the coordinates of the plate (as a 4-point polygon)
plate_coords = np.array([[508, 578], [760, 578], [760, 635], [508, 635]])
# Draw the plate as a polygon (quadrilateral) with a blue border
cv2.polylines(camera1, [plate_coords], isClosed=True, color=(255, 0, 0), thickness=2)

cv2.imshow('Camera1', camera1)
cv2.waitKey(0)
cv2.destroyAllWindows()
connection.close()
