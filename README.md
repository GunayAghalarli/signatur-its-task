
# License Plate Heatmap Generator

This script generates a heatmap visualization showing areas of high overlap from multiple camera frames, based on license plate coordinates. It reads camera and plate data from an SQLite database and uses OpenCV to create and display the heatmaps for each camera.

## Requirements

To run this script, you'll need the following Python libraries:

- `sqlite3` (for SQLite database interaction)
- `cv2` (OpenCV for image processing and visualization)
- `numpy` (for numerical operations)
- `re` (for regex operations)
- `json` (for parsing JSON data)
- `time` (for performance measurement)

You can install the required packages via `pip` if you don't already have them:

```bash
pip install opencv-python numpy
```

## File Structure

Ensure the following files exist:

- The SQLite database file (`signaturits_metadata.db`) containing the required camera and plate data.
- The Python script file (`index.py`).

## How It Works

1. **Database Connection:**
   - The script connects to the SQLite database (`signaturits_metadata.db`) and retrieves two sets of data:
     - **Camera Configuration**: Camera ID, width, and height.
     - **Plate Readings**: Reading ID, camera ID, and coordinates of the license plate(s).

2. **Data Processing:**
   - The script cleans and processes the coordinates from the database. Each plate's coordinates are stored in a list.
   - Plates are grouped by their associated camera ID to efficiently process each camera's data.

3. **Heatmap Generation:**
   - A blank "heatmap" is created for each camera using a white canvas (all pixel values initialized to 0).
   - For each plate, the coordinates are drawn on the heatmap, and the pixel count is incremented to indicate the number of plates that overlap at a specific pixel.
   - The script identifies the region with the maximum overlap, where plates frequently appear.

4. **Visualization:**
   - For each camera, a colorized heatmap is generated. The heatmap highlights regions with more plate overlaps with blue color and unused parts of the canvas is white color.

5. **Performance Tracking:**
   - The script tracks and prints the time taken for different stages (fetching data, processing coordinates, generating the heatmap).

6. **Display:**
   - The script uses OpenCV to display the heatmap for each camera, using a colorized view (using the JET color map). The visualization remains open until a key is pressed.

## Output

- The script displays heatmaps of the camera frames, where the colors represent the number of plates observed in those regions.
- For each camera, the script prints the regions with the most plate overlaps and the count of plates in those regions.

## How to Run

1. Make sure the `signaturits_metadata.db` database exists and is properly structured (i.e., contains `camera_config` and `readings` tables).
2. Place the Python script in the same directory or adjust paths as necessary.
3. Run the script:

```bash
python index.py
```

4. Press any key to close the heatmap windows after they're displayed.

