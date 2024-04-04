import os
import argparse
from playsound import playsound
import torch
from torch import autocast
from diffusers import StableDiffusionPipeline
from googletrans import Translator  # pip install googletrans==4.0.0-rc1

# コマンドライン引数の設定
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--situation', default="ピカチュウとミッキーマウスが抱きしめ合う状況", type=str, help='2つ以上の状況を指定するときは++区切りで並べる')
args = parser.parse_args()

if '++' in args.situation:
    situation_prompts = args.situation.split('++')
else:
    situation_prompts = [args.situation]

style_prompts = ['カートゥーン風のイラスト']
style_prompts = ['アメリカンコミック風のイラスト']
style_prompts += ['2000年代のアニメ風のイラスト']
style_prompts += ['モノクロ線画のイラスト']
style_prompts += ['究極的に写実的な3D CG']
style_prompts += ['透明感があるアクリル画のイラスト']
style_prompts += ['ピカソ風の絵画']
style_prompts += ['浮世絵風の絵画']

quality_prompts =  ['']
quality_prompts += ['(intricate details) ']
quality_prompts += ['(highres) (intricate details) ']
quality_prompts += ['(masterpiece) (highres) (intricate details) ']
quality_prompts += ['((best quality)) (masterpiece) (highres) (intricate details) ']

translator = Translator()
content_prompts_jpn = []
content_prompts_eng = []
situations_jpn = []
styles_jpn = []
for style in style_prompts:
    for situation in situation_prompts:
        situations_jpn += [situation]
        styles_jpn += [style]

        content_prompts_jpn += [f'「{situation}」を描いた{style}']
        print(content_prompts_jpn[-1])

        eng = translator.translate(content_prompts_jpn[-1], src='ja', dest='en')
        content_prompts_eng += [eng.text]
        print(f'  --> {content_prompts_eng[-1]}\n')

positive_prompts = []
output_subfolder_names = []
output_file_names = []
cnt = 0
for i, content in enumerate(content_prompts_eng):
    for quality in quality_prompts:
        output_subfolder_names += [situations_jpn[i]]
        output_file_names += [f'{styles_jpn[i]}_{quality}']

        cnt += 1
        positive_prompts += [f'{quality}({content})']
        print(f'Positive prompt {cnt}: {positive_prompts[-1]}')

negative_prompt = '((NSFW)) ((worst quality)) ((lowres))'
print(f'Negative prompt: {negative_prompt}')

model_id = "CompVis/stable-diffusion-v1-2"
model_id2 = 'stabilityai/stable-diffusion-2-1'
model_id3 = 'Lykon/DreamShaper'
device = "cuda"
pipe = StableDiffusionPipeline.from_pretrained(model_id3)
pipe = pipe.to(device)

imH, imW = 512, 512
output_root = 'test_output'
for i, positive_prompt in enumerate(positive_prompts):
    output_folder = os.path.join(output_root, output_subfolder_names[i])
    os.makedirs(output_folder, exist_ok=True)

    output_path = f'{output_folder}/{i:04d}_{output_file_names[i]}.png'
    print(len(output_path), output_path)
    with autocast("cuda"):
        ## ここに戻りたい
        while True:
            image = pipe(positive_prompt, negative_prompt=negative_prompt, width=imW, height=imH)[0][0]
            pixels = image.load()

            brightness_sum = 0
            for y in range(imH):
                for x in range(imW):
                    # ピクセルのRGB値を取得
                    r, g, b = pixels[x, y]

                    # 輝度値の計算（グレースケールの場合）
                    brightness = (r + g + b) // 3

                    # 輝度値の合計を計算
                    brightness_sum += brightness
            
            if brightness_sum != 0:
                break

    image.save(output_path)
