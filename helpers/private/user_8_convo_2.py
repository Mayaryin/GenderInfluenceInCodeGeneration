from helpers.Message import Message

CONVERSATION_ID = 2
USER_ID = 8
MODEL_VERSION = "ChatGPT-4o-mini-high"

message_0 = Message(
    conversation_id=CONVERSATION_ID,
    role="user",
    message_text="""
    I am working on the problem of reconstruction trajectory of drone out of map of an interest through frames.  the task itself is "Classic CV - Drone navigation
If you ever thought of flying drones that can be resistant to electronic warfare, this task can give you an idea how to build an autonomous navigation system for UAV.
Description of the task: 
Given a satellite panoramic image of an area where an unknown good UAV should have flown and a series of photos taken from the UAV during its flight, you should reconstruct and visualise its route.
Requirements:
The code should read a region map and series of “frames” from specified paths
The output should be either a single image with a trajectory or a video with a trajectory and real-time moving position of the UAV. 
Input data [link]:
Panoramic satellite map of the area of interest
50 consecutive “photos” from the UAV  (we imitate it with satellite image taken at a proper angle and at another scale)

Deliverables:
Well organized and commented code
Requirements.txt or environment.yml
README.md with basic description of your solution
An image with a map and visualized route with information about start/finish and order of route points
Notes:
Use trajectory interpolation and smoothing (if needed)
Optionally for final results visualization you can make a video with zoomed in map region and per-frame trajectory visualization
Optionally for ideal visualization on the image you can show bounding boxes of “photos” taken from the drone with preservation of their size and rotation.
"
    """,
    model_version="",
    message_order=0,
    conversational="""
    I am working on the problem of reconstruction trajectory of drone out of map of an interest through frames.  the task itself is
    """,
    code="",
    other="""Classic CV - Drone navigation
If you ever thought of flying drones that can be resistant to electronic warfare, this task can give you an idea how to build an autonomous navigation system for UAV.
Description of the task: 
Given a satellite panoramic image of an area where an unknown good UAV should have flown and a series of photos taken from the UAV during its flight, you should reconstruct and visualise its route.
Requirements:
The code should read a region map and series of “frames” from specified paths
The output should be either a single image with a trajectory or a video with a trajectory and real-time moving position of the UAV. 
Input data [link]:
Panoramic satellite map of the area of interest
50 consecutive “photos” from the UAV  (we imitate it with satellite image taken at a proper angle and at another scale)

Deliverables:
Well organized and commented code
Requirements.txt or environment.yml
README.md with basic description of your solution
An image with a map and visualized route with information about start/finish and order of route points
Notes:
Use trajectory interpolation and smoothing (if needed)
Optionally for final results visualization you can make a video with zoomed in map region and per-frame trajectory visualization
Optionally for ideal visualization on the image you can show bounding boxes of “photos” taken from the drone with preservation of their size and rotation.""",
    code_blocks=None
)


message_1 = Message(
    conversation_id=CONVERSATION_ID,
    role='assistant',
    message_text="""
    Here is a proposed hybrid approach leveraging the discussed techniques:
Coarse Localization per Frame (Deep + Classic): For each UAV frame, perform a coarse localization on the panoramic map. This could be done by a deep visual place recognition network to get an approximate region (e.g., the network suggests a likely 100×100 pixel area in the map where the frame might belong). If a deep model is not available, one could take a simpler approach: downscale the map and do a rough feature match or correlation to find an initial guess. The coarse localization narrows down the search area drastically.
Fine Alignment per Frame (Feature Matching + Homography): Given the candidate region, use feature-based matching to precisely align the frame. For example, run SIFT (or SuperPoint) on the UAV frame and the candidate map patch, match descriptors, and then use cv2.findHomography with RANSAC to compute the exact placement​
docs.opencv.org
. If not enough features match (perhaps due to viewpoint), use a learned matcher like LoFTR to get dense correspondences and estimate the homography. This step provides the frame’s homography or at least the center location on the map with better accuracy. By combining deep and classic, we take advantage of deep learning’s ability to handle large viewpoint changes and the precision of geometric methods to finalize the pose.
Sequential Consistency Check: As we process frames 1 through 50, we can enforce temporal consistency. After obtaining the homography for frame i, we know its approximate position. For frame i+1, we might initialize the search for matches around the previous position (since the UAV likely didn’t jump far). This can be implemented by cropping the map to a neighborhood of frame i’s location before doing the coarse match for frame i+1. If frame i+1’s independent match result differs greatly from where a motion model would predict (e.g., Kalman prediction), we can flag it and perhaps retry matching with different methods. This makes the system more robust by not treating each frame in isolation. Essentially, we fuse the localization with a motion prior on the fly (which is what a Kalman filter would mathematically do).
Apply Kalman Filter for Smoothing: As we get a stream of positions (and perhaps velocities estimated from differences), we feed them into a Kalman filter. The filter will output a smoothed estimate for each frame’s position. This handles any frame where the matching was slightly off and ensures the trajectory is physically smooth. It also allows interpolation if, say, one frame was completely unmatchable – the filter would interpolate between frame i and i+2 for the missing i+1. By the end of frame 50, we have a filtered trajectory in map pixel coordinates.
Refine with Spline (if needed): Depending on the quality needed, we can take the Kalman-filtered discrete trajectory and fit a continuous spline through all points. This can iron out any minor jitters remaining. If the Kalman filter already produced a satisfactory smooth path, this step might be optional. Alternatively, instead of a spline, one could simply output the piecewise linear path (connecting the dots) – since 50 frames is not that many, a slight jaggedness might be visible, so a spline gives a visually pleasing curve through those waypoints.
Visualization: Finally, use the chosen Python tools to plot the trajectory on the satellite image. Mark the start and end. Perhaps draw an arrow indicating direction (or color the line from blue at start to red at end, creating a gradient indicating progression). Include any additional info desired: for example, small thumbnails of certain UAV frames at their locations (one can paste a scaled-down version of the frame onto the map for illustration). Ensure to save the output in the required format (high-resolution image or a video file). Throughout this process, we rely on well-established libraries: OpenCV for image processing and feature matching, PyTorch for running deep models (if used), SciPy for filters/splines, and Matplotlib or OpenCV for the plotting.
     """,
    model_version=MODEL_VERSION,
    message_order=1,
    conversational="",
    code="",
    other="",
    code_blocks=[]
)

message_2 = Message(
    conversation_id=CONVERSATION_ID,
    role="user",
    message_text="""
        Focus on one step at the time. Write what is the expected outcome.
        """,
    model_version="",
    message_order=2,
    conversational="Focus on one step at the time. Write what is the expected outcome.",
    code="",
    other="",
    code_blocks=None
)


message_3 = Message(
    conversation_id=CONVERSATION_ID,
    role="assistant",
    message_text="""
    Let's break it down step by step. Before diving into the code, I have a few clarifying questions to ensure I fully understand your setup and requirements:

Dataset Organization:

Do you already have a panoramic satellite map image and a folder with 50 UAV frame images? If so, could you briefly describe how they are organized (e.g., file paths, naming conventions)?

Would you like to start with the image/file loading step to verify that the data is read correctly?

Coarse Localization Details:

For coarse localization, do you have a specific deep model in mind (e.g., a pretrained visual place recognition network) or would you prefer to start with a classical approach such as template matching/correlation (which you can later extend with deep learning methods)?

If you prefer to simulate the deep model (for instance, using a downscaled version of the map and simple correlation), does that align with your current needs?

Environment and Libraries:

Can I assume you have common libraries installed (OpenCV, NumPy, Matplotlib, etc.)? Are there any additional libraries (e.g., for deep learning like PyTorch or TensorFlow) that you’d like to use from the start?

Would you like the initial code to include checks for dependencies or just focus on the core functionality?

Step-by-Step Focus:

Would you like to begin by ensuring that your input images (the map and the UAV frames) are correctly loaded and displayed? This is often a good first step before implementing the coarse localization.

Do you envision the next step as performing coarse localization on each frame to find a candidate region in the map (using either a deep model or a classical method)?

Here’s what I’m proposing for our initial step:

Step 1: Load and Visualize Input Images
Objective:

Read the panoramic map image from a specified path.

Read the series of UAV frame images from a designated folder.

Visualize at least one example (e.g., the map and the first UAV frame) to ensure correct loading.

Expected Outcome:

A printed confirmation that the map image and all UAV frames were successfully loaded.

A couple of display outputs: one for the panoramic map and one for the first UAV frame.
This verifies that our file paths are correct and that the data is accessible.

Below is an example code snippet tailored for a Jupyter Notebook environment:

python
Copy
# Step 1: Load and Visualize the Input Images

import cv2
import os
import matplotlib.pyplot as plt

# Paths (adjust these paths to your local files)
map_image_path = 'path/to/your/panoramic_map.jpg'
frames_folder = 'path/to/your/frames_folder/'

# Load the panoramic map image
map_img = cv2.imread(map_image_path)
if map_img is None:
    raise FileNotFoundError(f"Map image not found at: {map_image_path}")
else:
    # Convert color for correct display in matplotlib (BGR to RGB)
    map_img_rgb = cv2.cvtColor(map_img, cv2.COLOR_BGR2RGB)
    print("Panoramic map image loaded successfully.")

# List and load UAV frame images
frame_files = sorted([os.path.join(frames_folder, f) 
                      for f in os.listdir(frames_folder) 
                      if f.lower().endswith(('.jpg', '.png'))])
if not frame_files:
    raise FileNotFoundError(f"No frame images found in: {frames_folder}")
print(f"Found {len(frame_files)} frame images.")

# Load the first frame image as an example
frame_img = cv2.imread(frame_files[0])
if frame_img is None:
    raise FileNotFoundError(f"Could not load the first frame image from: {frame_files[0]}")
else:
    frame_img_rgb = cv2.cvtColor(frame_img, cv2.COLOR_BGR2RGB)
    print("First UAV frame image loaded successfully.")

# Visualize the map and the first UAV frame
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.imshow(map_img_rgb)
plt.title("Panoramic Map Image")
plt.axis('off')

plt.subplot(1, 2, 2)
plt.imshow(frame_img_rgb)
plt.title("First UAV Frame")
plt.axis('off')

plt.show()
Explanation of the Code:

File Loading:
The code uses OpenCV to load the panoramic map and iterates over the specified frames folder to load all images. It ensures the images exist by checking if they are None.

Visualization:
Using Matplotlib, the code shows both the panoramic map and the first frame. This confirms that your images are being read correctly.

Expected Outcome:

A printed message confirming successful loading of the map image.

A printed message showing how many UAV frame images were found.

Side-by-side display of the panoramic map and the first UAV frame.

Could you please let me know if this matches your setup? Do you have any adjustments or additional requirements? Once confirmed, we can proceed to the next step (e.g., implementing the coarse localization for each UAV frame).

Feel free to ask any questions or clarify any part of the setup!


...
Great! Now that we have robust fine alignment per frame, the next major step is to reconstruct the UAV’s complete trajectory across all frames and then smooth it to enforce temporal consistency. We’ll do this in two parts:

Trajectory Reconstruction:
– Loop over all frames, applying coarse localization and fine alignment.
– Compute a refined position for each frame (for instance, the center of the UAV frame after applying the homography).

Trajectory Smoothing with a Kalman Filter:
– Feed the raw positions into a Kalman filter to produce a smooth, physically plausible trajectory.
– Visualize both the raw (unsmoothed) and the smoothed trajectories on the panoramic map.

Below is a detailed code snippet for these steps. (Make sure that the functions from the previous steps – for coarse localization and fine alignment – are accessible in your notebook.)

python
Copy
import cv2
import numpy as np
import matplotlib.pyplot as plt

# ======= Step 4: Trajectory Reconstruction and Smoothing =======

# Initialize lists to store trajectory positions (raw and smoothed)
raw_positions = []
smoothed_positions = []

# === Kalman Filter Setup ===
# We use a state vector [x, y, vx, vy] and measurements [x, y]
kalman = cv2.KalmanFilter(4, 2)
kalman.measurementMatrix = np.array([[1, 0, 0, 0],
                                     [0, 1, 0, 0]], np.float32)
kalman.transitionMatrix = np.array([[1, 0, 1, 0],
                                    [0, 1, 0, 1],
                                    [0, 0, 1, 0],
                                    [0, 0, 0, 1]], np.float32)
kalman.processNoiseCov = np.eye(4, dtype=np.float32) * 0.03
kalman.measurementNoiseCov = np.eye(2, dtype=np.float32) * 1

# Define a helper function to compute the center from warped corners
def compute_center(warped_corners):
    \"""
    Given warped corners of the UAV frame (a 4x1x2 array), compute the center.
    \"""
    center = np.mean(warped_corners, axis=0).flatten()
    return center

# Number of frames to process
num_frames = len(frames)

# Loop through each frame to compute the refined position
for i in range(num_frames):
    print(f"Processing frame {i+1}/{num_frames}")
    frame_img = frames[i]
    
    # --- Coarse Localization ---
    # Using previously tuned parameters (adjust if needed)
    coarse_x, coarse_y = coarse_localization(pano_map, frame_img, scale_factor=0.1, method=cv2.TM_CCOEFF)
    
    # --- Fine Alignment ---
    # Use the function that employs knn + Lowe's ratio test (adjust padding/threshold as necessary)
    H_full, roi = fine_alignment_knn(pano_map, frame_img, coarse_top_left=(coarse_x, coarse_y),
                                     padding=100, ratio_thresh=0.75)
    if H_full is None:
        print("Alignment failed for frame", i)
        continue  # Skip frames where alignment failed

    # Warp the corners of the UAV frame using the refined homography
    h_frame, w_frame = frame_img.shape[:2]
    frame_corners = np.float32([[0, 0], [w_frame, 0], [w_frame, h_frame], [0, h_frame]]).reshape(-1, 1, 2)
    warped_corners = cv2.perspectiveTransform(frame_corners, H_full)
    
    # Compute the center of the projected frame on the panoramic map
    center = compute_center(warped_corners)
    raw_positions.append(center)
    
    # --- Kalman Filter Smoothing ---
    measurement = np.array([[np.float32(center[0])], [np.float32(center[1])]])
    if i == 0:
        # Initialize the filter's state with the first measurement
        kalman.statePre = np.array([[center[0]], [center[1]], [0.0], [0.0]], dtype=np.float32)
        kalman.statePost = np.array([[center[0]], [center[1]], [0.0], [0.0]], dtype=np.float32)
    
    prediction = kalman.predict()  # Predict the next state (not used here for visualization)
    estimated = kalman.correct(measurement)  # Correct with the measurement
    smoothed_positions.append(estimated[:2].flatten())

# Convert trajectories to NumPy arrays for easier processing
raw_positions = np.array(raw_positions)
smoothed_positions = np.array(smoothed_positions)

# ======= Trajectory Visualization =======

# Create a copy of the panoramic map for visualization
map_vis = pano_map.copy()

# Draw raw positions (blue) and smoothed positions (green)
for pos in raw_positions:
    cv2.circle(map_vis, (int(pos[0]), int(pos[1])), 3, (255, 0, 0), -1)  # Blue: raw positions
for pos in smoothed_positions:
    cv2.circle(map_vis, (int(pos[0]), int(pos[1])), 3, (0, 255, 0), -1)  # Green: smoothed positions

# Optionally, draw lines connecting the positions for clarity
for i in range(1, len(raw_positions)):
    pt1 = (int(raw_positions[i-1][0]), int(raw_positions[i-1][1]))
    pt2 = (int(raw_positions[i][0]), int(raw_positions[i][1]))
    cv2.line(map_vis, pt1, pt2, (255, 0, 0), 2)
for i in range(1, len(smoothed_positions)):
    pt1 = (int(smoothed_positions[i-1][0]), int(smoothed_positions[i-1][1]))
    pt2 = (int(smoothed_positions[i][0]), int(smoothed_positions[i][1]))
    cv2.line(map_vis, pt1, pt2, (0, 255, 0), 2)

plt.figure(figsize=(10, 8))
plt.imshow(cv2.cvtColor(map_vis, cv2.COLOR_BGR2RGB))
plt.title("Trajectory on Panoramic Map (Blue: Raw, Green: Smoothed)")
plt.axis('off')
plt.show()
Code Explanation
Trajectory Extraction:

We loop through each UAV frame and obtain its refined position on the panoramic map.

The refined position is computed by transforming the UAV frame’s corner coordinates using the refined homography and then taking the center.

Kalman Filter Integration:

We initialize a Kalman filter (with a 4-dimensional state: position and velocity) to smooth the noisy raw position measurements.

For every frame, the measurement (center coordinate) is used to correct the predicted state, resulting in a smoothed estimate.

Visualization:

The raw positions (plotted in blue) and smoothed positions (plotted in green) are overlaid on the panoramic map.

Connecting lines are drawn to give you a visual idea of the trajectory flow.

What to Expect
The output is a panoramic map with two overlaid trajectories:

Raw Trajectory (Blue): The unsmoothed, frame-by-frame positions as computed directly from homographies.

Smoothed Trajectory (Green): The output from the Kalman filter, which should exhibit less jitter and be more physically plausible.

This visualization will help you assess whether the temporal consistency is successfully improved.

Please run the above code and check the trajectory visualization. Let me know if the trajectory looks consistent, if you see any misalignments, or if any further adjustments are needed. Once you’re satisfied with the trajectory estimation and smoothing, we can move on to the next step—such as generating a video with real-time map zooming and the trajectory playback if desired.
        """,
    model_version=MODEL_VERSION,
    message_order=3,
    conversational="",
    code="",
    other="",
    code_blocks=[{
            'language':"python",
            'code': """
                    # Step 1: Load and Visualize the Input Images

import cv2
import os
import matplotlib.pyplot as plt

# Paths (adjust these paths to your local files)
map_image_path = 'path/to/your/panoramic_map.jpg'
frames_folder = 'path/to/your/frames_folder/'

# Load the panoramic map image
map_img = cv2.imread(map_image_path)
if map_img is None:
    raise FileNotFoundError(f"Map image not found at: {map_image_path}")
else:
    # Convert color for correct display in matplotlib (BGR to RGB)
    map_img_rgb = cv2.cvtColor(map_img, cv2.COLOR_BGR2RGB)
    print("Panoramic map image loaded successfully.")

# List and load UAV frame images
frame_files = sorted([os.path.join(frames_folder, f) 
                      for f in os.listdir(frames_folder) 
                      if f.lower().endswith(('.jpg', '.png'))])
if not frame_files:
    raise FileNotFoundError(f"No frame images found in: {frames_folder}")
print(f"Found {len(frame_files)} frame images.")

# Load the first frame image as an example
frame_img = cv2.imread(frame_files[0])
if frame_img is None:
    raise FileNotFoundError(f"Could not load the first frame image from: {frame_files[0]}")
else:
    frame_img_rgb = cv2.cvtColor(frame_img, cv2.COLOR_BGR2RGB)
    print("First UAV frame image loaded successfully.")

# Visualize the map and the first UAV frame
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.imshow(map_img_rgb)
plt.title("Panoramic Map Image")
plt.axis('off')

plt.subplot(1, 2, 2)
plt.imshow(frame_img_rgb)
plt.title("First UAV Frame")
plt.axis('off')

plt.show()
                """
            },
        {'language': 'python',
         'code': """
         import cv2
import numpy as np
import matplotlib.pyplot as plt

# ======= Step 4: Trajectory Reconstruction and Smoothing =======

# Initialize lists to store trajectory positions (raw and smoothed)
raw_positions = []
smoothed_positions = []

# === Kalman Filter Setup ===
# We use a state vector [x, y, vx, vy] and measurements [x, y]
kalman = cv2.KalmanFilter(4, 2)
kalman.measurementMatrix = np.array([[1, 0, 0, 0],
                                     [0, 1, 0, 0]], np.float32)
kalman.transitionMatrix = np.array([[1, 0, 1, 0],
                                    [0, 1, 0, 1],
                                    [0, 0, 1, 0],
                                    [0, 0, 0, 1]], np.float32)
kalman.processNoiseCov = np.eye(4, dtype=np.float32) * 0.03
kalman.measurementNoiseCov = np.eye(2, dtype=np.float32) * 1

# Define a helper function to compute the center from warped corners
def compute_center(warped_corners):
    \"""
    Given warped corners of the UAV frame (a 4x1x2 array), compute the center.
    \"""
    center = np.mean(warped_corners, axis=0).flatten()
    return center

# Number of frames to process
num_frames = len(frames)

# Loop through each frame to compute the refined position
for i in range(num_frames):
    print(f"Processing frame {i+1}/{num_frames}")
    frame_img = frames[i]
    
    # --- Coarse Localization ---
    # Using previously tuned parameters (adjust if needed)
    coarse_x, coarse_y = coarse_localization(pano_map, frame_img, scale_factor=0.1, method=cv2.TM_CCOEFF)
    
    # --- Fine Alignment ---
    # Use the function that employs knn + Lowe's ratio test (adjust padding/threshold as necessary)
    H_full, roi = fine_alignment_knn(pano_map, frame_img, coarse_top_left=(coarse_x, coarse_y),
                                     padding=100, ratio_thresh=0.75)
    if H_full is None:
        print("Alignment failed for frame", i)
        continue  # Skip frames where alignment failed

    # Warp the corners of the UAV frame using the refined homography
    h_frame, w_frame = frame_img.shape[:2]
    frame_corners = np.float32([[0, 0], [w_frame, 0], [w_frame, h_frame], [0, h_frame]]).reshape(-1, 1, 2)
    warped_corners = cv2.perspectiveTransform(frame_corners, H_full)
    
    # Compute the center of the projected frame on the panoramic map
    center = compute_center(warped_corners)
    raw_positions.append(center)
    
    # --- Kalman Filter Smoothing ---
    measurement = np.array([[np.float32(center[0])], [np.float32(center[1])]])
    if i == 0:
        # Initialize the filter's state with the first measurement
        kalman.statePre = np.array([[center[0]], [center[1]], [0.0], [0.0]], dtype=np.float32)
        kalman.statePost = np.array([[center[0]], [center[1]], [0.0], [0.0]], dtype=np.float32)
    
    prediction = kalman.predict()  # Predict the next state (not used here for visualization)
    estimated = kalman.correct(measurement)  # Correct with the measurement
    smoothed_positions.append(estimated[:2].flatten())

# Convert trajectories to NumPy arrays for easier processing
raw_positions = np.array(raw_positions)
smoothed_positions = np.array(smoothed_positions)

# ======= Trajectory Visualization =======

# Create a copy of the panoramic map for visualization
map_vis = pano_map.copy()

# Draw raw positions (blue) and smoothed positions (green)
for pos in raw_positions:
    cv2.circle(map_vis, (int(pos[0]), int(pos[1])), 3, (255, 0, 0), -1)  # Blue: raw positions
for pos in smoothed_positions:
    cv2.circle(map_vis, (int(pos[0]), int(pos[1])), 3, (0, 255, 0), -1)  # Green: smoothed positions

# Optionally, draw lines connecting the positions for clarity
for i in range(1, len(raw_positions)):
    pt1 = (int(raw_positions[i-1][0]), int(raw_positions[i-1][1]))
    pt2 = (int(raw_positions[i][0]), int(raw_positions[i][1]))
    cv2.line(map_vis, pt1, pt2, (255, 0, 0), 2)
for i in range(1, len(smoothed_positions)):
    pt1 = (int(smoothed_positions[i-1][0]), int(smoothed_positions[i-1][1]))
    pt2 = (int(smoothed_positions[i][0]), int(smoothed_positions[i][1]))
    cv2.line(map_vis, pt1, pt2, (0, 255, 0), 2)

plt.figure(figsize=(10, 8))
plt.imshow(cv2.cvtColor(map_vis, cv2.COLOR_BGR2RGB))
plt.title("Trajectory on Panoramic Map (Blue: Raw, Green: Smoothed)")
plt.axis('off')
plt.show()"""}]
)



user_8_convo_2 = [message_0, message_1, message_2, message_3]








