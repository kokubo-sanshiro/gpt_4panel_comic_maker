import tkinter as tk
from tkinter import ttk
import openai
from PIL import Image, ImageTk
import datetime
import os
from playsound import playsound # Version: 1.2.2 じゃないと動かないと思う
from text2speech import make_audio
import traceback
from torch import autocast
from diffusers import StableDiffusionPipeline
from googletrans import Translator  # pip install googletrans==4.0.0-rc1

from my_function import make_gpt_control_text, generate_text, extract_txt, generate_translation_digest_text
from utils import video_out

import time
class GUI_WINDOW():

    def __init__(self):
        self.stable = StableDiffusion()
        self.window = tk.Tk()
        self.window.title("4 コマ漫画作成")
        # self.window.config(bg='#ff8c00')
        self.window.config(bg='#4682b4')

        style = ttk.Style()
        style.theme_use('default')  # 使用するテーマ名を指定します

        self.translator = Translator()


        # モニターと同じサイズのフレームを作成
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()
        self.window.geometry(f"{self.screen_width}x{self.screen_height}")

        self.gpt_model="gpt-3.5-turbo"
        self.gpt_temperature  = 0.8

        self.usage_txt = '+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ +\n\
   このアプリは４コマ漫画を作成してくれます.          　           \n\
   【使用方法】   　　　　　　　　　　　　　　　　　　　　          \n\
    + １つ以上３つ以下の内容を下のテキストボックスに入力する   \n\
    + 入力後作成ボタンをクリックする                               \n\
    + 作成後スタートボタンを押す　　　                             \n\
    + リセットボタンでボックスのテキストをすべてクリアする           \n\
   【画像再作成ボタンの仕様】\n\
    + コマ内容の変更または、各コマ画像ボックスにチェックを\n \
      入れることで画像を作成する（複数選択と入力OK）\n \
   【注意】                                                      \n\
    + 作成には時間がかかります(1分程度)                            \n\
    + 入力文章の内容が変更される場合があります                      \n\
    + 難しいワードや文章の場合、絵の内容にずれが生じます　  \n\
    + 絵のスタイルは入力スタイルが優先されます  \n \
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ +'
        # gptに出力させた文章を保存
        self.out_txt = []
        self.copy_out_txt = []
        # gptに出力させた文章gptに要約と翻訳を行わせた文章を保存
        self.trans_dige_txts = []
        # 直近の保存ディレクタ
        self.out_dir = ''

        self.re_make_flg = False
        self.one_make_flg = False # 一回はスタートしているか

    def __call__(self):
        self.make_style()
        self.make_main_panel()
        self.make_sub_panel()
        self.make_parts_left(True)
        self.make_parts_center()
        self.make_parts_right()
        self.add_log('疑似コマンドプロンプト')

        self.window.mainloop()
        # 左上右下
    # main panel 作成

    def make_style(self):
        self.style = ttk.Style()
        self.style.configure("Custom.TFrame",  background="lightskyblue")
        self.style.configure('my.TRadiobutton', font=("Helvetica", 11))
        self.style.configure('Large.TButton', font=('Helvetica', 16))
    
    def make_main_panel(self):
        # 左側の全体フレーム作成
        self.left_frame_width = self.screen_width//5
        self.left_main_frame = ttk.Frame(self.window, width=self.left_frame_width, height=self.screen_height, 
                                        padding=(20 , 20, 20 ,20),
                                          # 修正: Styleの名前を"TFrame"に変更
                                        style="Custom.TFrame",
                                        ) 
        self.left_main_frame.grid(row=0, column=0)
        # 中央の全体フレーム作成
        self.center_frame_width = int((self.screen_width - self.left_frame_width)*0.65)
        self.center_main_frame = ttk.Frame(self.window, width=self.center_frame_width, height=self.screen_height, 
                                           padding=(10 , 10, 10 ,10), 
                                           style="Custom.TFrame"
                                           ) # 左上右下

        self.center_main_frame.grid(row= 0, column=1)

        # 右側の全体フレーム作成
        self.right_frame_width = self.screen_width -self.center_frame_width
        self.right_main_frame = ttk.Frame(self.window,  height=self.screen_height, 
                                          padding=(20 , 20, 20 ,20),
                                          style="Custom.TFrame"
                                          ) # 左上右下
        self.right_main_frame.grid(row= 0, column=2)

        for i in range(3):  # Assuming there are 3 rows
            self.window.grid_rowconfigure(i, weight=1)
        for i in range(3):  # Assuming there are 3 columns
            self.window.grid_columnconfigure(i, weight=1)

    def make_sub_panel(self):
        # - left panl ------------------------------ #
        # 使用方法のフレーム
        h = 165
        self.usage_frame = ttk.Frame(self.left_main_frame, width=self.left_frame_width, height=h,)
        self.usage_frame.grid(row=0)

        # 各コマを入力するフレーム
        h1 = int((self.screen_height - h)*0.55)
        self.coma_frame = ttk.Frame(self.left_main_frame, width=self.left_frame_width+82, height=h1,)
        self.coma_frame.grid(row=1)

        # option選択（モデルと画風選択）フレーム
        h2 = int((self.screen_height-h-h1)*0.3)
        self.option_frame = ttk.Frame(self.left_main_frame, width= self.left_frame_width+82, height= h2, style='Custom.TFrame')
        self.option_frame.grid(row=2)

        # 画風選択フレーム
        # h = int((self.screen_height-h)*0.6)
        # self.paiting_frame = ttk.Frame(self.left_main_frame, width= self.left_frame_width, height= h)
        # self.paiting_frame.grid(row=2)
        # # モデル選択フレーム
        # h = int((self.screen_height-h)*0.3)
        # self.model_frame = ttk.Frame(self.left_main_frame, width= self.left_frame_width, height= h)
        # self.model_frame.grid(row=3)

        # 作成bottonフレーム
        # h = int((self.screen_height-h)*0.5)
        self.button_frame = ttk.Frame(self.left_main_frame, width=self.left_frame_width, height=(self.screen_height-h-h1-h2)*0.25, style='Custom.TFrame')
        self.button_frame.grid(row=3)

        # self.remake_panel = ttk.Frame(self.left_main_frame, width=self.left_frame_width+80, height=90)
        # self.remake_panel.grid(row=5)
        # self.remake_panel.pack_propagate(False)

        # - center panl ----------------------------- #
        self.center_label_frame  = ttk.Frame(self.center_main_frame, width=self.center_frame_width, height=int(self.screen_height*0.05), style="Custom.TFrame")
        self.center_image_frame  = ttk.Frame(self.center_main_frame, width=self.center_frame_width, height=int(self.screen_height*0.6), style="Custom.TFrame")
        self.center_button_frame = ttk.Frame(self.center_main_frame, width=self.center_frame_width, height=int(self.screen_height*0.15), style="Custom.TFrame")
        self.center_log_frame    = ttk.Frame(self.center_main_frame, width=self.center_frame_width, height=int(self.screen_height*0.2), style="Custom.TFrame")

        self.center_label_frame.grid(row=0)
        self.center_image_frame.grid(row=1)
        self.center_button_frame.grid(row=2)
        self.center_log_frame.grid(row=3)
        # - right panl ------------------------------ #
        self.right_img_frame1  = ttk.Frame(self.right_main_frame, width=self.right_frame_width, height=int(self.screen_height*0.25))
        self.right_img_frame2  = ttk.Frame(self.right_main_frame, width=self.right_frame_width, height=int(self.screen_height*0.25))
        self.right_img_frame3  = ttk.Frame(self.right_main_frame, width=self.right_frame_width, height=int(self.screen_height*0.25))
        self.right_img_frame4  = ttk.Frame(self.right_main_frame, width=self.right_frame_width, height=int(self.screen_height*0.25))
        self.right_img_frame1.grid(row=0)
        self.right_img_frame2.grid(row=1)
        self.right_img_frame3.grid(row=2)
        self.right_img_frame4.grid(row=3)

    def make_parts_left(self, first_flg):
        # - left parts ------------------------------------------------------------#
        # 使用方法テキスト
        if first_flg:
            self.frame_label = ttk.Label(self.usage_frame, text=self.usage_txt, font=("Helvetica", 10, "bold"))
            self.frame_label.grid(row=1)

        # first_flg = False
        # コマ入力部分
        if first_flg:
            relwidth = 1
            # rel(x or y): 親の幅に対する(水平or垂直)位置、(height, widht):親に対する長さ
            self.coma1_entry = self.create_text_with_scrollbar(self.coma_frame, '###   1コマ目   ###', rely=0.0, relheight=0.25, relwidth=relwidth)
            self.coma2_entry = self.create_text_with_scrollbar(self.coma_frame, '###   2コマ目   ###', rely=0.25, relheight=0.25, relwidth=relwidth)
            self.coma3_entry = self.create_text_with_scrollbar(self.coma_frame, '###   3コマ目   ###', rely=0.5, relheight=0.25, relwidth=relwidth)
            self.coma4_entry = self.create_text_with_scrollbar(self.coma_frame, '###   4コマ目   ###', rely=0.75, relheight=0.25, relwidth=relwidth)
        else:
            for widget in self.coma_frame.winfo_children():
                widget.destroy()
            relwidth = 0.4
            # rel(x or y): 親の幅に対する(水平or垂直)位置、(height, widht):親に対する長さ
            self.coma1_entry = self.create_text_with_scrollbar(self.coma_frame, '###   1コマ目   ###', rely=0.0, relheight=0.25, relwidth=relwidth)
            self.coma2_entry = self.create_text_with_scrollbar(self.coma_frame, '###   2コマ目   ###', rely=0.25, relheight=0.25, relwidth=relwidth)
            self.coma3_entry = self.create_text_with_scrollbar(self.coma_frame, '###   3コマ目   ###', rely=0.5, relheight=0.25, relwidth=relwidth)
            self.coma4_entry = self.create_text_with_scrollbar(self.coma_frame, '###   4コマ目   ###', rely=0.75, relheight=0.25, relwidth=relwidth)

            self.translation_button1 = self.make_translation_button(self.coma_frame, '翻訳⇒', num=1, rely=0.12, relx=0.4, relheight=0.04, relwidth=0.1)
            self.translation_button2 = self.make_translation_button(self.coma_frame, '翻訳⇒', num=2, rely=0.38, relx=0.4, relheight=0.04, relwidth=0.1)
            self.translation_button3 = self.make_translation_button(self.coma_frame, '翻訳⇒', num=3, rely=0.62, relx=0.4, relheight=0.04, relwidth=0.1)
            self.translation_button4 = self.make_translation_button(self.coma_frame, '翻訳⇒', num=4, rely=0.88, relx=0.4, relheight=0.04, relwidth=0.1)

            self.prompt1_entry = self.create_text_with_scrollbar(self.coma_frame, '###   1コマ目 prompt  ###', relx = 0.5, rely=0.0, relheight=0.25, relwidth=relwidth)
            self.prompt2_entry = self.create_text_with_scrollbar(self.coma_frame, '###   2コマ目 prompt  ###', relx = 0.5, rely=0.25, relheight=0.25, relwidth=relwidth)
            self.prompt3_entry = self.create_text_with_scrollbar(self.coma_frame, '###   3コマ目 prompt  ###', relx = 0.5, rely=0.5, relheight=0.25, relwidth=relwidth)
            self.prompt4_entry = self.create_text_with_scrollbar(self.coma_frame, '###   4コマ目 prompt  ###', relx = 0.5, rely=0.75, relheight=0.25, relwidth=relwidth)

            self.var1 = tk.IntVar()
            self.var2 = tk.IntVar()
            self.var3 = tk.IntVar()
            self.var4 = tk.IntVar()

            self.remake_check_button1 = ttk.Checkbutton(self.coma_frame, text='選\n択', variable=self.var1, onvalue=1, offvalue=0, style= 'my.TRadiobutton')
            self.remake_check_button2 = ttk.Checkbutton(self.coma_frame, text='選\n択', variable=self.var2, onvalue=1, offvalue=0, style= 'my.TRadiobutton')
            self.remake_check_button3 = ttk.Checkbutton(self.coma_frame, text='選\n択', variable=self.var3, onvalue=1, offvalue=0, style= 'my.TRadiobutton')
            self.remake_check_button4 = ttk.Checkbutton(self.coma_frame, text='選\n択', variable=self.var4, onvalue=1, offvalue=0, style= 'my.TRadiobutton')

            self.remake_check_button1.place(relx = 0.9, rely=0.10, relheight=0.1, relwidth=0.1)
            self.remake_check_button2.place(relx = 0.9, rely=0.34, relheight=0.1, relwidth=0.1)
            self.remake_check_button3.place(relx = 0.9, rely=0.6, relheight=0.1, relwidth=0.1)
            self.remake_check_button4.place(relx = 0.9, rely=0.84, relheight=0.1, relwidth=0.1)

        if first_flg:
            # option frame の中身
            self.style.configure('Opution.TFrame', borderwidth=2, relief="solid", background="lightskyblue")
            # model
            self.model_frame = ttk.Frame(self.option_frame, padding=(2,2,2,2),style='Opution.TFrame')
            # 画風
            self.paiting_frame = ttk.Frame(self.option_frame, padding=(2,2,2,2), style='Opution.TFrame')
            self.model_frame.place(  relx = 0.05, rely=0.1)
            self.paiting_frame.place(relx = 0.5, rely=0.1)

            self.model_text = ttk.Label(self.model_frame, text='《 モデル選択 》', font=("Helvetica", 10,), anchor='center')
            self.model_text.grid(row=0, column=0, sticky='nsew')  

            self.model_button_frame = ttk.Frame(self.model_frame,)
            self.model_button_frame.grid(row=1, column=0, sticky='ew') 
            self.model_option = tk.StringVar()
            self.gpt_model3 = ttk.Radiobutton(self.model_button_frame, text='GPT3.5', variable=self.model_option, value='gpt-3.5-turbo', style= 'my.TRadiobutton')
            self.gpt_model3.grid(row=0, column=0)
            self.gpt_model4 = ttk.Radiobutton(self.model_button_frame, text='GPT4.0', variable=self.model_option, value='gpt-4', style= 'my.TRadiobutton')
            self.gpt_model4.grid(row = 0, column=1)

            #
            self.paiting_label = ttk.Label(self.paiting_frame, text="《 画風スタイルを選択 or 入力 》", anchor='center', font=("Helvetica", 10,))
            self.paiting_label.grid(row=0, column=0, sticky='nsew')

            self.pating_button_frame = ttk.Frame(self.paiting_frame, )
            self.pating_button_frame.grid(row=1)

            self.selected_option = tk.StringVar()
            # Create radio buttons
            style1 = '漫画風'
            style2 = 'ピカソ風'
            style3 = 'モノクロ線画風'
            style4 = '3D風'
            self.radio_button1 = ttk.Radiobutton(self.pating_button_frame, text=style1, variable=self.selected_option, value=style1, style= 'my.TRadiobutton')
            self.radio_button1.grid(row=0, column=0, sticky="w")
            self.radio_button2 = ttk.Radiobutton(self.pating_button_frame, text=style2, variable=self.selected_option, value= style2, style= 'my.TRadiobutton')
            self.radio_button2.grid(row=0, column=1, sticky="w")
            self.radio_button3 = ttk.Radiobutton(self.pating_button_frame, text=style3, variable=self.selected_option, value=style3, style= 'my.TRadiobutton')
            self.radio_button3.grid(row=1, column=0, sticky="w")
            self.radio_button4 = ttk.Radiobutton(self.pating_button_frame, text=style4, variable=self.selected_option, value=style4, style= 'my.TRadiobutton')
            self.radio_button4.grid(row=1, column=1, sticky="w")
            # 入力できる部分
            self.text_entry = ttk.Entry(self.paiting_frame) # self.selected_option.get()
            self.text_entry.grid(row=2, sticky='nsew')

        
        if first_flg:
            self.make_img_button = ttk.Button(self.button_frame, text="作成", command = self.get_text, style='Large.TButton')
            self.make_img_button.place(relx = 0.05, rely=0)
            self.remake_img_button = ttk.Button(self.button_frame, text="画像再作成",  command= self.remake_img, style='Large.TButton')
            self.remake_img_button.pack_forget()
        else:
            self.remake_img_button.place(relx = 0.65, rely=0)


        # self.button2 = ttk.Button(self.button_frame, text="textリセット", padding=(10, 5, 10, 5), command=self.clear_text)
        # self.button2.grid(row= 0, column=1)

    def make_parts_center(self):
        # - center parts ------------------------------------------------------------ #
        self.center_label = ttk.Label(self.center_label_frame, text='', background='lightskyblue')
        self.center_label.place(x=0, y=0, width=self.center_frame_width)
        # 画像を表示 
        self.center_img_show('center_default_img', 1)

        self.button3 = ttk.Button(self.center_button_frame, text="スタート", padding=(10, 5, 10, 5), command=self.update_image)
        self.button3.grid(column= 0)
        self.button3.grid_remove()

        # Labelウィジェットをウィンドウの中央に配置
        self.image_label.place(relx=0.5, rely=0.5, anchor='center')

        # ウィンドウの中央下部に配置されたスクロールバー付きのテキストウィジェットの作成
        self.log_display = self.create_log_display(self.center_log_frame)

    def make_parts_right(self):
        # - right parts ------------------------------------------------------------ #
        self.img_show('default_img')


    def create_log_display(self, parent):
        frame = ttk.Frame(parent, style="Custom.TFrame")
        text_widget = tk.Text(frame, state='disabled', bg = '#000000', fg='#ffffff')
        text_widget.place(relx=0, rely=0, relwidth=1.0, relheight=0.9)  # relwidthを1.0に変更

        frame.place(relx=0.52, rely=0.5, anchor='center', relwidth=0.7, relheight=1.0)

        return text_widget


    def create_text_with_scrollbar(self, parent, label_text, **kwargs):
        frame = ttk.Frame(parent)
        
        # ラベルを作成
        label = ttk.Label(frame, text=label_text,)
        label.pack(side=tk.TOP, fill=tk.X)

        text_widget = tk.Text(frame, font=('Helvetica', 12) ) # ここで見た目変更できる　あとでやる
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget['yscrollcommand'] = scrollbar.set

        frame.place(**kwargs)

        return text_widget
    
    def make_translation_button(self, parent, text_label, num, **kwargs):
        frame = ttk.Frame(parent)
        button = tk.Button(frame, text=text_label, command= lambda i=num: self.trans_button_command(i))
        button.pack(fill=tk.BOTH, expand=True)
        # self.translation_button_frame.place(rely=0.0, relx=0.4, relheight=0.25, relwidth=0.1)
        frame.place(**kwargs)

        return button
    
    def trans_button_command(self, i):
        self.add_log('翻訳中...')
        if i == 1:
            text = self.coma1_entry.get('1.0', 'end-1c')
            prompt_text = generate_translation_digest_text(self.gpt_model, 0.3, text)
            self.prompt1_entry.delete('1.0', tk.END)
            self.prompt1_entry.insert(tk.END, prompt_text)
            
        elif i == 2:
            text = self.coma2_entry.get('1.0', 'end-1c')
            prompt_text = generate_translation_digest_text(self.gpt_model, 0.3, text)
            self.prompt2_entry.delete('1.0', tk.END)
            self.prompt2_entry.insert(tk.END, prompt_text)
        elif i == 3:
            text = self.coma3_entry.get('1.0', 'end-1c')
            prompt_text = generate_translation_digest_text(self.gpt_model, 0.3, text)
            self.prompt3_entry.delete('1.0', tk.END)
            self.prompt3_entry.insert(tk.END, prompt_text)
        elif i == 4:
            text = self.coma4_entry.get('1.0', 'end-1c')
            prompt_text = generate_translation_digest_text(self.gpt_model, 0.3, text)
            self.prompt4_entry.delete('1.0', tk.END)
            self.prompt4_entry.insert(tk.END, prompt_text)
        
        # self.out_txt[i] = text
        self.trans_dige_txts[i-1] = prompt_text
        self.add_log('翻訳を行いました')
        self.window.update()
    
        
    def re_frame(self, ):
        self.button3.grid(column=0)
        texts = []
        texts.append(self.coma1_entry.get('1.0', 'end-1c'))
        texts.append(self.coma2_entry.get('1.0', 'end-1c'))
        texts.append(self.coma3_entry.get('1.0', 'end-1c'))
        texts.append(self.coma4_entry.get('1.0', 'end-1c'))

        self.make_parts_left(False)

        self.coma1_entry.insert(tk.END, texts[0])
        self.coma2_entry.insert(tk.END, texts[1])
        self.coma3_entry.insert(tk.END, texts[2])
        self.coma4_entry.insert(tk.END, texts[3])

        self.re_make_flg = True
        self.window.update()
    
    # ログの表示
    def add_log(self, message, end='\n'):
        
        self.log_display.configure(state='normal')
        self.log_display.insert(tk.END, message + end)
        self.log_display.configure(state='disabled')
        self.log_display.yview_moveto(1.0)
        self.log_display.update_idletasks()  # Add this line

    def clear_text(self, mode = 0):
        self.coma1_entry.delete('1.0', tk.END)
        self.coma2_entry.delete('1.0', tk.END)
        self.coma3_entry.delete('1.0', tk.END)
        self.coma4_entry.delete('1.0', tk.END)

        self.prompt1_entry.delete('1.0', tk.END)
        self.prompt2_entry.delete('1.0', tk.END)
        self.prompt3_entry.delete('1.0', tk.END)
        self.prompt4_entry.delete('1.0', tk.END)

        if mode == 0:
            self.add_log('テキストをクリアしました.')


    def center_img_show(self, savedir, number, mode = 0):
        # mode: 0は真ん中に一枚画像表示、elseは真ん中に４枚画像を表示

        for widget in self.center_image_frame.grid_slaves():
            widget.grid_forget()


        if mode == 0:
            image_path = os.path.join(savedir, 'img0' + str(number) + '.png')
            img = Image.open(image_path)
            img = img.resize((512, 512), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
            # Check if the label already exists
            if hasattr(self, 'image_label'):
                # If the label exists, just update the image
                self.image_label.config(image=img)
                self.image_label.image = img  # keep a reference to the image
            else:
                # If the label doesn't exist, create it and pack it
                self.image_label = tk.Label(self.center_image_frame, image=img,)
                self.image_label.image = img  # keep a reference to the image
                self.image_label.pack()

            self.image_label.update_idletasks()  # Add this line
        else:
            self.image_labels = []  # Initialize a list to hold all the labels

            for num in range(4):
                print('ok')
                image_path = os.path.join(savedir, 'img0' + str(num+1) + '.png')
                img = Image.open(image_path)
                img = img.resize((256, 256), Image.LANCZOS)
                img = ImageTk.PhotoImage(img)

                # Always create a new label for each image
                image_label = tk.Label(self.center_image_frame, image=img,)
                image_label.image = img  # keep a reference to the image
                row = 0 if num < 2 else 1
                image_label.grid(row=row, column=num%2)

                # Add the label to our list of labels
                self.image_labels.append(image_label)
        self.window.update()


    def img_show(self, savedir):
        img_paths = [os.path.join(savedir, 'img0' + str(i+1) + '.png') for i in range(4)]
        frames = [self.right_img_frame1, self.right_img_frame2, self.right_img_frame3, self.right_img_frame4]
        imgs = ['img1', 'img2', 'img3', 'img4']
        labels = ['image_label1', 'image_label2', 'image_label3', 'image_label4']

        for i in range(4):
            img = Image.open(img_paths[i])
            
            # 画像を指定のサイズにリサイズ
            img = img.resize((230, 230), Image.LANCZOS)
            
            img = ImageTk.PhotoImage(img)
            setattr(self, imgs[i], img)

            if hasattr(self, labels[i]):
                getattr(self, labels[i]).config(image=img)
                getattr(self, labels[i]).image = img
            else:
                label = tk.Label(frames[i], image=img)
                setattr(self, labels[i], label)
                label.image = img
                label.pack()

    
    def get_text(self):

        texts = []
        texts.append(self.coma1_entry.get('1.0', 'end-1c'))
        texts.append(self.coma2_entry.get('1.0', 'end-1c'))
        texts.append(self.coma3_entry.get('1.0', 'end-1c'))
        texts.append(self.coma4_entry.get('1.0', 'end-1c'))

        existence_numbers = []
        for i in range(4):
            if texts[i] != '':
                existence_numbers.append(i)

        if len(existence_numbers) == 0:
            self.add_log('※１コマ以上はユーザーが考えてください')
        elif  len(existence_numbers) == 4:
            self.add_log('※入力コマ数は３コマまでとしてください')
            # max_com_flg = True
        elif self.selected_option.get() == '' and self.text_entry.get() == '':
            self.add_log('※ スタイルを選択または入力してください')
        elif self.model_option.get() == '':
            self.add_log('※ モデルを選択してください')
        else:
            self.gpt_model = self.model_option.get()
            self.add_log('ユーザーが考えた、')

            image_save_dir = os.path.join('out_folder', datetime.datetime.now().strftime("%Y-%m-%d_%H-%M"))
            if not os.path.exists(image_save_dir):
                os.makedirs(image_save_dir)

            f = open(os.path.join(image_save_dir, 'info.txt'), 'w', encoding='utf-8') 
            for number in existence_numbers:
                self.add_log(' '+f'[{number+1}コマ目]: {texts[number]}')
            if len(existence_numbers) == 4:
                self.add_log('に合うような４コマ漫画の画像を作成します',end='\n\n')
            
            else:
                self.add_log('に合うように残りの')
                for num in range(4):
                    if num not in existence_numbers:
                        self.add_log(' '+f'[{num+1}コマ目]')

            try:
                self.add_log('を作成します.',end='\n\n')

                self.add_log('作成中...')
                self.add_log('  [0%]: [__________________________________________________]')
                gpt_control_txt = make_gpt_control_text(texts, existence_numbers) # gptのロールテキストを作成
                f.write('[gpt_control_txt] ---\n' +  gpt_control_txt)

                # gptにテキストを出力させく
                gpt_out_txt = generate_text(self.gpt_model, self.gpt_temperature, gpt_control_txt) 
                f.write('\n[gpt_out_tetx] ---\n' +  gpt_out_txt)

                
                text_list   = extract_txt(gpt_out_txt) # 文のみを抽出
                f.write('\n[抽出したテキスト] ---' +  '\n '.join(text_list))
                # テキストの音声を作成
                make_audio(text_list, image_save_dir)

                trans_dige_txts = []
                trans_dige_txts.append(generate_translation_digest_text(self.gpt_model, 0.3, text_list[1])) # 各コマを英語に翻訳と要約を
                trans_dige_txts.append(generate_translation_digest_text(self.gpt_model, 0.3, text_list[2]))
                trans_dige_txts.append(generate_translation_digest_text(self.gpt_model, 0.3, text_list[3]))
                trans_dige_txts.append(generate_translation_digest_text(self.gpt_model, 0.3, text_list[4]))
                f.write('\n[テキストの要約と翻訳] ---' + '\n'.join(trans_dige_txts))
                self.add_log(' [10%]: [#####_____________________________________________]')
                self.window.update()  # GUIの更新

                style = self.text_entry.get() if self.text_entry.get() != '' else self.selected_option.get()
                en_style = self.translator.translate(style, src='ja', dest='en')
                check_list = []
                check_list.append(self.stable.generate_image(trans_dige_txts[0], en_style, image_save_dir, 1)) # テキストから画像を作成
                # print('ok');time.sleep(1)
                # f.write(' ')
                self.window.update()  # GUIの更新
                self.add_log(' [25%]: [#############_____________________________________]')
                check_list.append(self.stable.generate_image(trans_dige_txts[1], en_style, image_save_dir, 2)) # テキストから画像を作成
                self.window.update()
                self.add_log(' [50%]: [#########################_________________________]')
                check_list.append(self.stable.generate_image(trans_dige_txts[2], en_style, image_save_dir, 3)) # テキストから画像を作成
                self.window.update()
                self.add_log(' [75%]: [######################################____________]')
                check_list.append(self.stable.generate_image(trans_dige_txts[3], en_style, image_save_dir, 4)) # テキストから画像を作成
                self.add_log('[100%]: [##################################################]')

                if any(x < 1 for x in check_list):
                    self.add_log('エラー：画像生成に失敗したため、もう一度お試しください')
                    print("4回以上画像生成に失敗した")
                    raise Exception("エラー発生")

                self.out_txt = text_list
                self.trans_dige_txts = trans_dige_txts
                self.out_dir = image_save_dir

                self.add_log('$ 作成が完了しました. スタートボタンを押してください')
                if self.re_make_flg == False:
                    self.re_frame()
            except Exception as e:
                self.add_log('エラー：作成に失敗しました. もう一度お試しください')
                traceback.print_exc()



    
    def remake_img(self):
        # 画像変更するコマのボタンの値を取得
        check_list = [self.var1.get(), self.var2.get(), self.var3.get(), self.var4.get()]
 
        if len(self.out_txt) == 0:
            self.add_log('※先に4コマ漫画を作成してください')
            return
        
        try:
            temp_trans_dige_txts = [(self.prompt1_entry.get('1.0', 'end-1c')), (self.prompt2_entry.get('1.0', 'end-1c')), (self.prompt3_entry.get('1.0', 'end-1c')), (self.prompt4_entry.get('1.0', 'end-1c'))]
        except Exception as e:
                self.add_log('エラー：入力されてないpromptがあります')
                traceback.print_exc()
                return
        # コマ文章取得
        new_text_list = [self.out_txt[0], self.coma1_entry.get('1.0', 'end-1c'), self.coma2_entry.get('1.0', 'end-1c'), self.coma3_entry.get('1.0', 'end-1c'), self.coma4_entry.get('1.0', 'end-1c')]
        if all(x == 0 for x in check_list) :
            self.add_log('※再作成するチェックボックス選択してください')
        elif any(v == '' for v in new_text_list):
            self.add_log('エラー：内容が入力さいていないコマがあります')        
        else:
            self.add_log('画像の再作成を開始します')
            style = self.text_entry.get() if self.text_entry.get() != '' else self.selected_option.get()
            en_style = self.translator.translate(style, src='ja', dest='en')
            print(style, en_style)
            for i, num in enumerate(check_list):
                if new_text_list[i] != self.out_txt[i]:
                    # if new_text_list[i+1] == '':
                    #     self.add_log(str(i+1)+'※コマの内容を入力してください')
                    #     return
                    make_audio(new_text_list[i+1], self.out_dir, mode = (i+1))
                    # self.trans_dige_txts[i] = generate_translation_digest_text(self.gpt_model, 0.3, new_text_list[i+1])
                if num == 1 : #or (self.out_txt[i+1] != new_text_list[i+1])
                    self.out_txt[i+1] = new_text_list[i+1]

                    self.add_log(str(i+1)+'コマ目の画像を再作成中...')
                    self.window.update()
                    # 前の画像の名前を変更し再保存
                    image_path = os.path.join(self.out_dir, 'img0' + str(i+1) + '.png')
                    befor_img = Image.open(image_path)
                    befor_img_path = os.path.join(self.out_dir, 'befor_img0' + str(i+1) + datetime.datetime.now().strftime("_%m_%d_%H_%M") +'.png')
                    befor_img.save(befor_img_path)
                    
                    # 新しく画像を再作成
                    if (self.stable.generate_image(self.trans_dige_txts[i], en_style, self.out_dir, i+1)) == 0:
                        self.add_log('エラー：画像の再作成に失敗しました')
                    
            self.add_log('$ 画像の再作成が完了しました\n中央が作成後、右側が元の画像になります')
            self.center_img_show(self.out_dir, 1, 1)
            self.window.update()
 
    def update_image(self, i = 0):
        try:
            if i == 0:
                self.add_log('\n[タイトル]：'+self.out_txt[0])

            self.center_img_show(self.out_dir, i+1)
            time.sleep(2)
            self.add_log(f'[{i+1}コマ目]:' + self.out_txt[i+1])
            audio = os.path.join(self.out_dir,  'audio0'+str(i+1) +'.mp3')
            playsound((audio.replace('\\', '/'))) # pathが\だとダメっぽい
            
            if i < 3:
                self.window.after(2000, self.update_image, i+1)  # Call this function again after 2 seconds
            else:
                self.window.after(2000, self.img_show, self.out_dir)  # Call img_show after 2 seconds
                self.clear_text(mode = 1)
                self.coma1_entry.insert(tk.END, self.out_txt[1])
                self.coma2_entry.insert(tk.END, self.out_txt[2])
                self.coma3_entry.insert(tk.END, self.out_txt[3])
                self.coma4_entry.insert(tk.END, self.out_txt[4])

                self.prompt1_entry.insert(tk.END, self.trans_dige_txts[0])
                self.prompt2_entry.insert(tk.END, self.trans_dige_txts[1])
                self.prompt3_entry.insert(tk.END, self.trans_dige_txts[2])
                self.prompt4_entry.insert(tk.END, self.trans_dige_txts[3])

            video_out.make_video(self.out_dir, "4panel_comic_video.mp4")

        except IndexError as e:
            self.add_log('エラー：先にコマの内容を考え、作成ボタンを押してください.')
        except Exception as e:
            # その他の例外が発生した場合の処理を記述する
            print("予期しないエラーが発生しました:", e)
            traceback.print_exc()
            self.add_log('エラー：予期しないエラーが発生しました.もう一度お試しください.')

class StableDiffusion():
    def __init__(self):

        self.model_id = "Lykon/DreamShaper"
        self.device = "cuda"
        self.pipe = StableDiffusionPipeline.from_pretrained(self.model_id)
        self.pipe = self.pipe.to(self.device)
    
    def generate_image(self, text, style, save_dir, num):
            pos_prompt = '((best quality)) ((masterpiece)) ((highres)) ((intricate details)) '
            pos_prompt += f'{style.text} depicting the situation of "{text}"'

            neg_prompt = '((NSFW)) ((worst quality)) ((lowres))'

            with autocast("cuda"):
                cnt = 0
                while True:
                    image = self.pipe(pos_prompt, negative_prompt= neg_prompt, width=256, height=256)[0][0]

                    pixels = image.load()

                    brightness_sum = 0
                    for y in range(256):
                        for x in range(256):
                            # ピクセルのRGB値を取得
                            r, g, b = pixels[x, y]

                            # 輝度値の計算（グレースケールの場合）
                            brightness = (r + g + b) // 3

                            # 輝度値の合計を計算
                            brightness_sum += brightness
                    if cnt == 3:
                        return 0
                    
                    if brightness_sum != 0:
                        break
                    cnt += 1
                
            image.save(os.path.join(save_dir, 'img0' + str(num) + '.png'))
            return 1

    
if __name__ == "__main__":
    gui = GUI_WINDOW()
    gui()
