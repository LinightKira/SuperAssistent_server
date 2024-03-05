import cv2
import os

# Folder containing images
image_folder = 'images'

# Video output file
video_name = 'output_video.mp4'

# Get the list of image files
images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
images.sort()  # Sort the images if necessary

# Define the video frame size
frame = cv2.imread(os.path.join(image_folder, images[0]))
height, width, layers = frame.shape

frame_width = 768
frame_height = 512
# Initialize the video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter(video_name, fourcc, 1, (frame_width, frame_height), True)

# Write each image to the video
for image in images:
    video.write(cv2.imread(os.path.join(image_folder, image)))

# Release the video writer
video.release()

print(f"Video {video_name} created successfully.")