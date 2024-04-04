import argparse
import glob
import os
from utils import video_out

folder_list = sorted(glob.glob(os.path.join('out_folder', "*")))
defpath = folder_list[-1]

# コマンドライン引数の設定
parser = argparse.ArgumentParser(description='Create a video from images and audio files in a folder.')
parser.add_argument('-f', '--folder_path', default=defpath, type=str, help='The path to the folder containing the images and audio files.')
args = parser.parse_args()

# 動画の作成
video_out.make_video(args.folder_path, "4panel_comic_video.mp4")
