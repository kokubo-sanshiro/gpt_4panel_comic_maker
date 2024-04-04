from gtts import gTTS
from playsound import playsound
import os
import datetime


def make_audio(texts, savedir, mode = 5):
    if mode != 5:

        # 音声ファイルを保存
        old_name = os.path.join(savedir, 'audio0'+str(mode) +'.mp3')
        new_name = os.path.join(savedir, 'befor_audio0'+str(mode) + datetime.datetime.now().strftime("_%m_%d_%H_%M") +'.mp3')
        os.rename(old_name, new_name)

        # gTTSオブジェクトを作成
        tts = gTTS(text=texts, lang='ja')
        tts.save(old_name)
    else:
        for i in range(4):

            text = texts[i+1]

            # gTTSオブジェクトを作成
            tts = gTTS(text=text, lang='ja')

            # 音声ファイルを保存
            out_name = os.path.join(savedir, 'audio0'+str(i+1) +'.mp3')
            tts.save(out_name)
    
        

# oudio = os.path.join('out_folder/2023-07-09_14-18', 'audio0'+str(0+1) +'.mp3')

# save = os.path.join('out_folder', '2023-07-09_14-48')
# for i in range(4):
#     audio = os.path.join(save,'audio0'+str(i+1) +'.mp3')
#     playsound(audio.replace('\\', '/'))

