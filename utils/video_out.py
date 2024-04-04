import cv2
import numpy as np
from PIL import Image
from pydub import AudioSegment
from moviepy.editor import *
import os
import glob

def make_video(folder_path, output_name):
    # 画像と音声ファイルのパスを取得
    images = sorted(glob.glob(os.path.join(folder_path, "*.png")))
    audios = sorted(glob.glob(os.path.join(folder_path, "*.mp3")))

    # 出力パスを作成
    output_path = os.path.join(folder_path, output_name)

    # 画像と音声の数
    num_files = len(images)

    # 基準画像サイズを取得
    width, height = Image.open(images[0]).size
    for image in images[1:]:
        w, h = Image.open(image).size
        width = max(width, w)
        height = max(height, h)

    # 空のビデオを作成
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter('temp_video.mp4', fourcc, 30.0, (width, height))

    # 各画像をフレームとして追加
    for i, image in enumerate(images):
        frame = cv2.imread(image)
        frame = cv2.resize(frame, (width, height))

        # mp3の再生時間を取得し、対応するフレーム数を計算
        audio = AudioSegment.from_mp3(audios[i])
        duration = audio.duration_seconds
        num_frames = int(duration * 30)  # 30fpsなので

        # 同じフレームを必要な回数追加
        for _ in range(num_frames):
            video.write(frame)

        # 1秒間の無音区間（0.5秒は現在のフレーム、0.5秒は次のフレーム）
        for _ in range(15):  # 30fpsのため15フレーム
            video.write(frame)
        if i < len(images) - 1:
            frame_next = cv2.imread(images[i+1])
            frame_next = cv2.resize(frame_next, (width, height))
            for _ in range(15):  # 30fpsのため15フレーム
                video.write(frame_next)

    # 一時的なビデオファイルをリリース
    video.release()

    # 音声を結合
    combined_audio = AudioSegment.from_mp3(audios[0]) + AudioSegment.silent(duration=1000)  # 1秒の無音区間
    for audio in audios[1:]:
        combined_audio += (AudioSegment.from_mp3(audio) + AudioSegment.silent(duration=1000))  # 各音声ファイルの後に1秒の無音区間を追加

    # 結合した音声を一時的なファイルとして保存
    combined_audio.export("combined_audio.mp3", format='mp3')

    # 一時的なビデオと音声を結合
    videoclip = VideoFileClip("temp_video.mp4")
    audioclip = AudioFileClip("combined_audio.mp3")

    videoclip = videoclip.set_audio(audioclip)

    # 最終的なビデオを書き出す
    videoclip.write_videofile(output_path, codec='libx264')
    # videoclip.write_videofile(output_name, codec='libx264')

    # 一時的なファイルを削除
    os.remove("temp_video.mp4")
    os.remove("combined_audio.mp3")







# 初期版（単体スクリプト）

# import cv2
# import numpy as np
# from PIL import Image
# from pydub import AudioSegment
# from moviepy.editor import *

# # 画像と音声の数
# num_files = 4

# # 画像と音声ファイルのリストを作成
# images = [f'img{i:02}.png' for i in range(1, num_files+1)]
# audios = [f'audio{i:02}.mp3' for i in range(1, num_files+1)]

# # 基準画像サイズを取得
# width, height = Image.open(images[0]).size
# for image in images[1:]:
#     w, h = Image.open(image).size
#     width = max(width, w)
#     height = max(height, h)

# # 空のビデオを作成
# fourcc = cv2.VideoWriter_fourcc(*'mp4v')
# video = cv2.VideoWriter('temp_video.mp4', fourcc, 30.0, (width, height))

# # 各画像をフレームとして追加
# for i, image in enumerate(images):
#     img = cv2.imread(image)
#     img = cv2.resize(img, (width, height))
#     frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

#     # mp3の再生時間を取得し、対応するフレーム数を計算
#     audio = AudioSegment.from_mp3(audios[i])
#     duration = audio.duration_seconds
#     num_frames = int(duration * 30)  # 30fpsなので

#     # 同じフレームを必要な回数追加
#     for _ in range(num_frames):
#         video.write(frame)

#     # 1秒間の無音区間（0.5秒は現在のフレーム、0.5秒は次のフレーム）
#     for _ in range(15):  # 30fpsのため15フレーム
#         video.write(frame)
#     if i < len(images) - 1:
#         img_next = cv2.imread(images[i+1])
#         img_next = cv2.resize(img_next, (width, height))
#         frame_next = cv2.cvtColor(img_next, cv2.COLOR_BGR2RGB)
#         for _ in range(15):  # 30fpsのため15フレーム
#             video.write(frame_next)

# # 一時的なビデオファイルをリリース
# video.release()

# # 音声を結合
# combined_audio = AudioSegment.from_mp3(audios[0]) + AudioSegment.silent(duration=1000)  # 1秒の無音区間
# for audio in audios[1:]:
#     combined_audio += (AudioSegment.from_mp3(audio) + AudioSegment.silent(duration=1000))  # 各音声ファイルの後に1秒の無音区間を追加

# # 結合した音声を一時的なファイルとして保存
# combined_audio.export("combined_audio.mp3", format='mp3')

# # 一時的なビデオと音声を結合
# videoclip = VideoFileClip("temp_video.mp4")
# audioclip = AudioFileClip("combined_audio.mp3")

# videoclip = videoclip.set_audio(audioclip)

# # 最終的なビデオを書き出す
# videoclip.write_videofile("final_video.mp4", codec='libx264')

# # 一時的なファイルを削除
# os.remove("temp_video.mp4")
# os.remove("combined_audio.mp3")
