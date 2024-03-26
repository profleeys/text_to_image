import pandas as pd
import re
from PIL import Image
import sqlite3
from hashlib import sha256
import streamlit as st

# 初始化數據庫連接
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()

# 創建用戶表
def create_users_table():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT)')

# 添加新用戶
def add_userdata(username, password):
    c.execute('INSERT INTO userstable(username, password) VALUES (?,?)', (username, password))
    conn.commit()

# 登入驗證
def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?', (username, password))
    data = c.fetchall()
    return data

# 生成密碼的哈希值
def make_hashes(password):
    return sha256(str.encode(password)).hexdigest()

# 驗證Hash值
def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# 首頁介面
def home_page():
    st.title(":blue[文字轉圖片系統]")
    st.subheader(":orange[Text to Image System]")

    menu = ["首頁", "登入", "註冊"]
    choice = st.sidebar.selectbox("選單", menu, index=0)
    
    if choice == "首頁":
        st.write('''文字轉圖片系統，可以幫助使用者快速地將文字轉換成高品質的圖片。\
同時可以自由地輸入想要轉換成圖片的文字內容，並選擇合適的顏色與背景圖片，\
根據個人喜好來製作出獨特的圖片。''')
        st.image("demo.gif")

    elif choice == "登入":
        username = st.text_input("用戶名")
        password = st.text_input("密碼", type='password')
        
        if st.button("登入"):
            #create_users_table()
            hashed_pswd = make_hashes(password)

            result = login_user(username, hashed_pswd)
            
            if result:
                st.session_state['user_name'] = username
                st.session_state['current_page'] = "用戶頁面"
                st.rerun()
            else:
                st.warning("用戶名或密碼錯誤")

    elif choice == "註冊":
        new_user = st.text_input("新用戶名")
        new_password = st.text_input("新密碼", type='password')

        if st.button("註冊"):
            #create_users_table()
            add_userdata(new_user, make_hashes(new_password))
            st.success("您已成功註冊, 可選擇登入以進行圖片選擇!")

# 瀏覽圖片
def browsing():
    n_o_img = 50

    # 假设你的图片存放在一个列表中，这里我们用URL表示。根据实际情况替换为你的图片路径或URL。
    images = [f"./car/{i}.jpg" for i in range(n_o_img)]

    desc = pd.read_csv('all_data.csv')
    tag = desc['label']

    if 'br_stage' not in st.session_state:
        st.session_state['br_stage'] = 0

    if st.session_state['br_stage'] == 0:
        st.title(":blue[瀏覽熱門圖片]")
        st.subheader(":orange[請選擇幾張預選圖片]")
        
        # 每页显示的图片数
        images_per_page = 12

        # 计算总页数
        total_pages = len(images) // images_per_page + (1 if len(images) % images_per_page > 0 else 0)

        # 用于分页的选择框
        page = st.sidebar.selectbox('選擇分頁', range(1, total_pages+1))

        # 当前页的图片
        start = (page-1) * images_per_page
        end = start + images_per_page
        if end > n_o_img: 
            end = n_o_img
        current_page_images = images[start:end]

        # 用于存储每张图片选中状态的字典
        if 'selected_images' not in st.session_state:
            st.session_state['selected_images'] = {}
            for image in images:
                st.session_state['selected_images'][image] = False

        # 显示当前页的图片和复选框
        for i, image in enumerate(current_page_images, start=1):
            col1, col2 = st.columns([1, 4])
            with col1:
                # 每张图片的复选框
                st.session_state['selected_images'][image] = st.checkbox(f"選擇圖片 {start + i}", key=f"select_{start+i}", value=st.session_state['selected_images'][image])
            with col2:
                img_name = image
                # 載入圖片
                image = Image.open(image)

                # 計算等比例縮放後的大小
                max_width = 500
                max_height = 400
                width, height = image.size

                # 計算縮放比例
                scale = min(max_width / width, max_height / height)

                # 計算新的寬度和高度
                new_width = int(width * scale)
                new_height = int(height * scale)

                # 調整圖片大小
                resized_image = image.resize((new_width, new_height))

                # 顯示圖片
                #st.image(resized_image, caption=f"圖片 {start + i}")
                numbers = re.findall(r'\d+', img_name)
                st.image(resized_image, caption=tag[int(numbers[0])])
                
                # 显示图片，这里使用markdown来显示，也可以根据需要使用st.image
                #st.image(image, caption=f"Image {start + i}")

        # 当按下按钮时，显示用户选中的图片
        if st.sidebar.button('顯示預選的圖片'):
            st.session_state['br_stage'] = 1
            st.rerun()
    elif st.session_state['br_stage'] == 1:
        st.title(":blue[選擇圖片]")
        st.subheader(":orange[請選擇其中的一張圖片]")
        
        #if 'final_choice' not in st.session_state:
        st.session_state['final_choice'] = None
            
        selected = [image for image, selected in st.session_state['selected_images'].items() if selected]
        
        if selected:
            # 只显示选中的图片
            k = 0
            for i, image in enumerate(selected, start=1):
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.checkbox(f"預選圖片 {i}", key=f"final_select_{i}", value=False):
                        # 用户最终选择的图片
                        st.session_state['final_choice'] = image
                        k = k + 1
                with col2:    
                    img_name = image
                    # 載入圖片
                    image = Image.open(image)

                    # 計算等比例縮放後的大小
                    max_width = 500
                    max_height = 400
                    width, height = image.size

                    # 計算縮放比例
                    scale = min(max_width / width, max_height / height)

                    # 計算新的寬度和高度
                    new_width = int(width * scale)
                    new_height = int(height * scale)

                    # 調整圖片大小
                    resized_image = image.resize((new_width, new_height))

                    # 顯示圖片
                    numbers = re.findall(r'\d+', img_name)
                    st.image(resized_image, caption=tag[int(numbers[0])])
                    #st.image(resized_image, caption=f"圖片 {i}")
            if st.button('顯示最終選擇的圖片'):
                # 如果用户做出了最终选择
                if k == 1:
                    st.session_state['br_stage'] = 2
                    st.rerun()
                else:
                    st.error('需選一張最終選擇的圖片!')
        else:
            # No images selected.
            st.session_state['br_stage'] = 0
            st.rerun()
    elif st.session_state['br_stage'] == 2:
        st.title(":blue[最終選擇的圖片]")
        
        # 載入圖片
        image = Image.open(st.session_state['final_choice'])

        # 計算等比例縮放後的大小
        max_width = 700
        max_height = 600
        width, height = image.size

        # 計算縮放比例
        scale = min(max_width / width, max_height / height)

        # 計算新的寬度和高度
        new_width = int(width * scale)
        new_height = int(height * scale)

        # 調整圖片大小
        resized_image = image.resize((new_width, new_height))

        # 顯示圖片
        st.image(resized_image, caption="你的最終選擇")
        
        col1, col2, col3 = st.columns([1, 1, 5])
        
        if col1.button('送出選擇'):
            st.success('圖片已送出進行處理!')
        
        if col2.button('重新選擇'):
            for image in images:
                st.session_state['selected_images'][image] = False
            st.session_state['br_stage'] = 0
            st.rerun()

# 查詢圖片
def searching():
    n_o_img = 50

    # 假设你的图片存放在一个列表中，这里我们用URL表示。根据实际情况替换为你的图片路径或URL。
    all_images = [f"./car/{i}.jpg" for i in range(n_o_img)]

    if 'images' not in st.session_state:
        st.session_state['images'] = [f"./car/{i}.jpg" for i in range(n_o_img)]

    desc = pd.read_csv('all_data.csv')
    tag = desc['label']

    if 'sr_stage' not in st.session_state:
        st.session_state['sr_stage'] = 0

    if st.session_state['sr_stage'] == 0:
        st.title(":blue[搜尋圖片庫]")
        
        # 創建一個TextBox，用於輸入文字
        text_input = st.text_input('請輸入標籤:')
        
        col1, col2, _ = st.columns([1, 2, 5])
        
        # 創建一個按鈕，當按下時檢查TextBox的內容
        if col1.button('搜尋'):
            # 檢查TextBox的內容是否不為空
            if text_input:  # 如果內容不為空
                # 使用列表推导检查每个元素是否包含子字符串
                contains_substring = [text_input.strip() in s for s in tag]
                st.session_state['images'] = [image for i, image in enumerate(all_images) if contains_substring[i]]
            else:  # 如果內容為空
                st.error('請輸入標籤!')
         
        if col2.button('取消搜尋'):
            st.session_state['images'] = [f"./car/{i}.jpg" for i in range(n_o_img)]
        
        images = st.session_state['images']
        
        if(len(images) > 0):
            # 每页显示的图片数
            images_per_page = 12

            # 计算总页数
            total_pages = len(images) // images_per_page + (1 if len(images) % images_per_page > 0 else 0)

            # 用于分页的选择框
            page = st.sidebar.selectbox('選擇分頁', range(1, total_pages+1))

            # 当前页的图片
            start = (page-1) * images_per_page
            end = start + images_per_page
            if end > n_o_img: 
                end = n_o_img
            current_page_images = images[start:end]

            # 用于存储每张图片选中状态的字典
            if 'selected_images' not in st.session_state:
                st.session_state['selected_images'] = {}
                for image in images:
                    st.session_state['selected_images'][image] = False

            # 显示当前页的图片和复选框
            for i, image in enumerate(current_page_images, start=1):
                col1, col2 = st.columns([1, 4])
                with col1:
                    # 每张图片的复选框
                    st.session_state['selected_images'][image] = st.checkbox(f"選擇圖片 {start + i}", key=f"select_{start+i}", value=st.session_state['selected_images'][image])
                with col2:
                    img_name = image
                    # 載入圖片
                    image = Image.open(image)

                    # 計算等比例縮放後的大小
                    max_width = 500
                    max_height = 400
                    width, height = image.size

                    # 計算縮放比例
                    scale = min(max_width / width, max_height / height)

                    # 計算新的寬度和高度
                    new_width = int(width * scale)
                    new_height = int(height * scale)

                    # 調整圖片大小
                    resized_image = image.resize((new_width, new_height))

                    # 顯示圖片
                    #st.image(resized_image, caption=f"圖片 {start + i}")
                    numbers = re.findall(r'\d+', img_name)
                    st.image(resized_image, caption=tag[int(numbers[0])])
                    
                    # 显示图片，这里使用markdown来显示，也可以根据需要使用st.image
                    #st.image(image, caption=f"Image {start + i}")

        # 当按下按钮时，显示用户选中的图片
        if st.sidebar.button('顯示預選的圖片'):
            st.session_state['sr_stage'] = 1
            st.rerun()      
    elif st.session_state['sr_stage'] == 1:
        st.title(":blue[選擇圖片]")
        st.subheader(":orange[請選擇其中的一張圖片]")
        
        #if 'final_choice' not in st.session_state:
        st.session_state['final_choice'] = None
            
        selected = [image for image, selected in st.session_state['selected_images'].items() if selected]
        
        if selected:
            # 只显示选中的图片
            k = 0
            for i, image in enumerate(selected, start=1):
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.checkbox(f"預選圖片 {i}", key=f"final_select_{i}", value=False):
                        # 用户最终选择的图片
                        st.session_state['final_choice'] = image
                        k = k + 1
                with col2:    
                    img_name = image
                    # 載入圖片
                    image = Image.open(image)

                    # 計算等比例縮放後的大小
                    max_width = 500
                    max_height = 400
                    width, height = image.size

                    # 計算縮放比例
                    scale = min(max_width / width, max_height / height)

                    # 計算新的寬度和高度
                    new_width = int(width * scale)
                    new_height = int(height * scale)

                    # 調整圖片大小
                    resized_image = image.resize((new_width, new_height))

                    # 顯示圖片
                    numbers = re.findall(r'\d+', img_name)
                    st.image(resized_image, caption=tag[int(numbers[0])])
                    #st.image(resized_image, caption=f"圖片 {i}")
            if st.button('顯示最終選擇的圖片'):
                # 如果用户做出了最终选择
                if k == 1:
                    st.session_state['sr_stage'] = 2
                    st.rerun()
                else:
                    st.error('需選一張最終選擇的圖片!')
        else:
            # No images selected.
            st.session_state['sr_stage'] = 0
            st.rerun()
    elif st.session_state['sr_stage'] == 2:
        st.title(":blue[最終選擇的圖片]")
        
        # 載入圖片
        image = Image.open(st.session_state['final_choice'])

        # 計算等比例縮放後的大小
        max_width = 700
        max_height = 600
        width, height = image.size

        # 計算縮放比例
        scale = min(max_width / width, max_height / height)

        # 計算新的寬度和高度
        new_width = int(width * scale)
        new_height = int(height * scale)

        # 調整圖片大小
        resized_image = image.resize((new_width, new_height))

        # 顯示圖片
        st.image(resized_image, caption="你的最終選擇")
        
        col1, col2, col3 = st.columns([1, 1, 5])
        
        if col1.button('送出選擇'):
            st.success('圖片已送出進行處理!')
        
        if col2.button('重新選擇'):
            for image in all_images:
                st.session_state['selected_images'][image] = False
            st.session_state['images'] = [f"./car/{i}.jpg" for i in range(n_o_img)]
            st.session_state['sr_stage'] = 0
            st.rerun()

# 用戶介面
def user_page():
    menu = ["選項說明", "瀏覽圖片", "查詢圖片", "生成圖片", "回首頁"]
    choice = st.sidebar.selectbox("圖片選擇", menu, index=0)
    
    if choice == "選項說明":
        st.title(":blue[圖片選擇]")
        st.subheader(":orange[Image Selection]")
        st.write(st.session_state['user_name'] + "你好, 歡迎使用圖片選擇!")
        st.write('''圖片選擇可以幫助使用者快速地選擇適合的圖片。\
使用者可根據左邊的選項來瀏覽、查詢或用AI的方式來生成喜歡的圖片。''')
    elif choice == "瀏覽圖片":
        browsing()
    elif choice == "查詢圖片":
        searching()
    elif choice == "生成圖片":
        st.title(":blue[生成圖片]")
    elif choice == "回首頁":
        st.session_state['current_page'] = "首頁"
        st.rerun()

# 主界面
def main():
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = "首頁"

    if st.session_state['current_page'] == "首頁":  
        home_page() 
    elif st.session_state['current_page'] == "用戶頁面":         
        user_page()
            
if __name__ == '__main__':
    main()
