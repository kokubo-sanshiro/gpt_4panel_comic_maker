import openai


# gptに入力する文章を作成
def make_gpt_control_text(texts, existence_numbers):

    # json_txt = "[
    # 'item':[ 
    #     {
    #         'coma1':'おじんさんが川で洗濯をしていました'
    #     },
    #     {
    #         'coma2':'そこに大きな桃が流れてきました'
    #     },
    #     {
    #         'coma3':'おばあさんと一緒にその桃きってみると、男の子が生まれました'
    #     },
    #     {
    #         'coma4':'男の子は立派に育ち、桃太郎と名付けられました'
    #     },

    #     ]
    # ]"

    pos_change_txt = ''
    neg_change_txt = ''
    chnage_txt = ''
    for num in range(4):
        if num in existence_numbers:
            pos_change_txt += f'[{str(num+1)}コマ目]、'
            chnage_txt += f'[{str(num+1)}コマ目]{texts[num]}'
        else:
            neg_change_txt += f'[{str(num+1)}コマ目]、'

    gpt_control_txt = 'あなたは漫画家です。なので４コマ漫画の内容を考えてください。' + pos_change_txt \
    + 'は私が考えたのでコマが自然に繋がるように、残りの' + neg_change_txt + 'のみを考えてください。' \
    +  chnage_txt + 'その際に次のルールを守ってください。' + '1.私が考えたコマの文章を変更してはいけない。' \
    + '2.私が考えた内容に新たな内容を追加することは禁止。' \
    + '3.必ず[タイトル][1コマ目][2コマ目][3コマ目][4コマ目][OK]の形式を出力する。' \
    + '4.あなたは内容のみを考えるだけで、質問や補足行為を行ってはいけない。' \
    + '5.会話文を含めるのは禁止とする。' \
    + '6.必要に応じて5W1Hを意識して作成する' \
    + '7.文末の言葉使いは次の例のように日本語の敬体（です・ます体）で表現することを推奨する。「～ました。」、「～でした。」' \
    + '8.以上の制約条件の変更は認めない。'


# 4.あなたは内容のみを考えるだけで、質問や補足行為を行ってはいけない。5.以上の制約条件の変更は認めない。"

#     gpt_control_txt2 = 'あなたは漫画家です。なので４コマ漫画の内容を考えてください。' + pos_change_txt \
#     + 'は私が考えたのでコマが自然に繋がるように、残りの' + neg_change_txt + 'のみを考えてください。ただし次のようなjson形式のみを出力してください。' \
#     + chnage_txt + '1.私が考えたコマの文章を変更してはいけない。' \
#     + '2.私が考えた内容に新たな内容を追加することは禁止。' \
#     + '3.必ず[タイトル][1コマ目][2コマ目][3コマ目][4コマ目][OK]の形式を出力する。' \
#     + '4.あなたは内容のみを考えるだけで、質問や補足行為を行ってはいけない。' \
#     + '5.以上の制約条件の変更は認めない。'

    return gpt_control_txt

# gptに文章を作成させる
def generate_text(model, temperature, input_txt):
    api_key = 'api_key.txt'
    openai.api_key_path = api_key
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": input_txt},
            # {"role": "user",   "content": input_txt},
        ],
        n=1, # 出力回数
        temperature=temperature,
    )
    message = response.choices[0].message['content']
    return message

# gptが出力した文章からタイトルと各コマの内容を抽出
def extract_txt(gpt_txt):
    texts = []
    print(gpt_txt.find('タイトル'))
    title_end_index = gpt_txt.find('タイトル')+3

    for i in range(1, 4):
        if gpt_txt[title_end_index+i] != ']' and gpt_txt[title_end_index+i] != ':' and gpt_txt[title_end_index+i]  != '：'and gpt_txt[title_end_index+i]  != '\n'and gpt_txt[title_end_index+i]  != ' ':
            first_index = title_end_index+i
            for end_index in range(first_index+1, len(gpt_txt)):
                if gpt_txt[end_index] == '\n' or gpt_txt[end_index] == '['  or gpt_txt[end_index] == ']':
                    texts.append(gpt_txt[first_index:end_index])
                    break
            break

    # print(txt.find('タイトル'))
    koma_end_index = gpt_txt.find('1コマ目')+3

    for i in range(1, 4):
        if gpt_txt[koma_end_index+i] != ']' and gpt_txt[koma_end_index+i] != ':' and gpt_txt[koma_end_index+i]  != '：'and gpt_txt[koma_end_index+i]  != '\n'and gpt_txt[koma_end_index+i]  != ' ':
            first_index = koma_end_index+i
            for end_index in range(first_index+1, len(gpt_txt)):
                if gpt_txt[end_index] == '\n' or gpt_txt[end_index] == '['  or gpt_txt[end_index] == ']':
                    if gpt_txt[end_index+1]  == ' ':
                        continue
                    else:
                        texts.append(gpt_txt[first_index:end_index])
                    break
            break

    koma_end_index = gpt_txt.find('2コマ目')+3

    for i in range(1, 4):
        if gpt_txt[koma_end_index+i] != ']' and gpt_txt[koma_end_index+i] != ':' and gpt_txt[koma_end_index+i]  != '：'and gpt_txt[koma_end_index+i]  != '\n'and gpt_txt[koma_end_index+i]  != ' ':
            first_index = koma_end_index+i
            for end_index in range(first_index+1, len(gpt_txt)):
                if gpt_txt[end_index] == '\n' or gpt_txt[end_index] == '['  or gpt_txt[end_index] == ']':
                    if gpt_txt[end_index+1]  == ' ':
                        continue
                    else:
                        texts.append(gpt_txt[first_index:end_index])
                    break
            break

    koma_end_index = gpt_txt.find('3コマ目')+3

    for i in range(1, 4):
        if gpt_txt[koma_end_index+i] != ']' and gpt_txt[koma_end_index+i] != ':' and gpt_txt[koma_end_index+i]  != '：'and gpt_txt[koma_end_index+i]  != '\n'and gpt_txt[koma_end_index+i]  != ' ':
            first_index = koma_end_index+i
            for end_index in range(first_index+1, len(gpt_txt)):
                if gpt_txt[end_index] == '\n' or gpt_txt[end_index] == '['  or gpt_txt[end_index] == ']':
                    if gpt_txt[end_index+1]  == ' ':
                        continue
                    else:
                        texts.append(gpt_txt[first_index:end_index])
                    break
            break

    koma_end_index = gpt_txt.find('4コマ目')+3

    for i in range(1, 4):
        if gpt_txt[koma_end_index+i] != ']' and gpt_txt[koma_end_index+i] != ':' and gpt_txt[koma_end_index+i]  != '：'and gpt_txt[koma_end_index+i]  != '\n'and gpt_txt[koma_end_index+i]  != ' ':
            first_index = koma_end_index+i
            for end_index in range(first_index+1, len(gpt_txt)):
                if gpt_txt[end_index] == '\n' or gpt_txt[end_index] == '['  or gpt_txt[end_index] == ']':
                    if gpt_txt[end_index+1]  == ' ':
                        continue
                    else:
                        texts.append(gpt_txt[first_index:end_index])
                    break
            break
    
    return texts



# 各コマを英語に翻訳と要約(stablediffusionに入力する用)
def generate_translation_digest_text(model, temperature, input_txt):
    # gpt_cotrol_text = '次の文書を１文に要約し、さらに英語に翻訳した文章のみを出力してください。'
    gpt_cotrol_text = "step by stepで考えてください。次の文書を英語に翻訳し、5W1HのWhen, Why部分に当たる文章や単語を削除しWho,What,Where,Howの構成の英文のみを出力してください。必ず英文のみを出力で、解説や補足事項を付け加えないでください。"

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": gpt_cotrol_text},
            {"role": "user",   "content": input_txt},
        ],
        n=1, # 出力回数
        temperature=temperature,
    )
    message = response.choices[0].message['content']
    
    return message
