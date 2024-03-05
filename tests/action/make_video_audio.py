import cv2
from moviepy.editor import VideoFileClip, AudioFileClip

# 定义音频和图片文件路径
audio_file = 'audio/0001.mp3'
image_file = 'images/011.png'

# 输出视频文件路径
output_file = 'output_audio.mp4'

# 读取音频文件
audio_clip = AudioFileClip(audio_file)
audio_duration = audio_clip.duration  # 音频时长

# 初始化视频写入器
frame_rate = 30  # 视频帧率
frame_size = (768, 512)  # 视频分辨率
output_video = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'mp4v'), frame_rate, frame_size)

# 计算视频帧数
num_frames = int(audio_duration * frame_rate)
print(f"Generating {num_frames} frames")

# 读取图片文件
img = cv2.imread(image_file)

# 将图片写入每个视频帧
for i in range(num_frames):
    output_video.write(img)

# 释放OpenCV视频写入器
output_video.release()

# 使用MoviePy来将音频和视频合并
video_clip = VideoFileClip(output_file)
final_clip = video_clip.set_audio(audio_clip)
final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')

print("Output video saved to:", output_file)