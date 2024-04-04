# from diffusers import StableDiffusionPipeline    
# from torch import autocast
# model_id = "CompVis/stable-diffusion-v1-2"
# device = "cuda"
# pipe = StableDiffusionPipeline.from_pretrained(model_id)
# pipe = pipe.to(device)


# # 文章を設定し、画像を生成
# prompt = 'dog manga style'
# with autocast("cuda"):
#     image = pipe(prompt)[0][0]

# 画像を表示し保存

# for num in range(4):
#     sharpe_txt = '#' * int((25 + num*25)/2)
#     log_txt = f'[{25 + num*25}%]：'+ sharpe_txt
#     print(log_txt)

import os
from gtts import gTTS
import datetime
from playsound import playsound
# out_dir = os.path.join('out_folder', datetime.datetime.now().strftime("%Y-%m-%d_%H-%M"))

# if not os.path.exists(out_dir):
#     os.makedirs(out_dir)

# for i in range(4):

#     text = 'おはようございます'

#     # gTTSオブジェクトを作成
#     tts = gTTS(text=text, lang='ja')

#     # 音声ファイルを保存
#     out_name = os.path.join(out_dir, 'audio0'+str(i+1) +'.mp3')
#     tts.save(out_name)

# for i in range(4):
#     audio = os.path.join(out_dir,  'audio0'+str(i+1) +'.mp3')
#     playsound((audio.replace('\\', '/'))) # pathが\だとダメっぽい

from torch import autocast
from diffusers import StableDiffusionPipeline
from googletrans import Translator  # pip install googletrans==4.0.0-rc1

style0 = 'コッミクスタイル'
style1 = '漫画スタイル'
style2 = 'ピカソ風'
style3 = 'モノクロ線画'
style4 = '透明感があるモノクロ線画風'
style5 = '浮世絵'

text = "The robot is sitting on the CEO's chair."
# text = 'old man, laundry in the river.'


translator = Translator()

model_id = "CompVis/stable-diffusion-v1-2"
model_id2 = 'stabilityai/stable-diffusion-2-1'
model_id3 = 'Lykon/DreamShaper'
device = "cuda"
pipe = StableDiffusionPipeline.from_pretrained(model_id3)
pipe = pipe.to(device)

english_style = translator.translate(style4, src='ja', dest='en')
print(english_style.text)

#((best quality)) ((masterpiece)) ((highres)) ((intricate details)) 
positive_prompt ='((intricate details)) ' +'an ' + english_style.text +\
' depicting the situation of ' + text
positive_prompt1 = text + english_style.text

positive_prompt2 = 'a ' + english_style.text+  ' illustration depicting the situation of' + text +\
', (highres), (intricate details)'

p = 'One day, an old man was doing laundry by the river.'

negative_prompt = '((NSFW))'

print(negative_prompt)
with autocast("cuda"):
    ## ここに戻りたい
    while True:
        image = pipe(positive_prompt, negative_prompt= negative_prompt, width=512, height=512)[0][0]

        pixels = image.load()

        brightness_sum = 0
        for y in range(512):
            for x in range(512):
                # ピクセルのRGB値を取得
                r, g, b = pixels[x, y]

                # 輝度値の計算（グレースケールの場合）
                brightness = (r + g + b) // 3

                # 輝度値の合計を計算
                brightness_sum += brightness
     
        
        if brightness_sum != 0:
            break


image.show()

