# gpt_4panel_comic_maker

### 環境構築（バージョンは動作確認済みのもの）
- Python 3.10.12
- torch 2.0.1+cu117
- その他のモジュールは requirements.txt に記載
- 環境構築用コマンド：
  ```
  conda create -n 4panelcomic python
  conda activate 4panelcomic
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
  pip install -r requirements.txt
  ```

### 使用方法
- あらかじめルートフォルダに api_key.txt を作り，そこにAPIキーを記入する．
  - .gitignoreで「api_key.txt」および「apikey.txt」というファイルはpush時に無視する（アップロードしない）設定になっている．
  - APIキーの読み込みは my_function.py の generate_text で行っている．
- 実行コマンド: 
  ```
  python start_gui.py
  ```
- test.py で画像生成のみの実験を行える

- test_t2i_comparison.py：プロンプト比較用のスクリプト
  - コード内で指定した複数のスタイル用プロンプトとクオリティ用プロンプトの組み合わせで描画を行う．
  - ```python test_t2i_comparison.py```：
    - コード内で指定したデフォルトテキスト（ピカチュウとミッキーマウスが抱きしめ合う状況）を描画する．
  - ```python test_t2i_comparison.py -s hoge```：
    - 「hoge」という状況を描画する．
  - ```python test_t2i_comparison.py -s hoge++fuga++piyo```：
    - 「hoge」「fuga」「piyo」という状況を順次描画する．

### utils 内の関数等
- run_video_out.py：動画化ファイル化用スクリプト
  - GUI_WINDOWクラスのメソッド update_image 内で呼び出している
  - 個別に実行したい場合は以下のコマンドで動画化可能：
    + ```python run_video_out.py```：out_folder 内の最後のフォルダ内のmp3 & pngを動画化
    + ```python run_video_out.py -f folder_path```：folder_path内のmp3 & pngを動画化

