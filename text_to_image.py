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

# 驗證哈希值
def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# 主界面
def main():
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = "首頁"

    if st.session_state['current_page'] == "首頁":
        st.title(":blue[文字轉圖片系統]")
        st.subheader(":orange[Text to Image System]")

        menu = ["首頁", "登入", "註冊"]
        choice = st.sidebar.selectbox("選單", menu, index=0)
        
        if choice == "首頁":
            st.write('''文字轉圖片系統，可以幫助使用者快速地將文字轉換成高品質的圖片。\
同時可以自由地輸入想要轉換成圖片的文字內容，並選擇合適的顏色與背景圖片，\
根據個人喜好來製作出獨特的圖片。''')

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
                
    elif st.session_state['current_page'] == "用戶頁面":         
        menu = ["選項說明", "瀏覽圖片", "查詢圖片", "生成圖片", "回首頁"]
        choice = st.sidebar.selectbox("圖片選擇", menu, index=0)
        
        if choice == "選項說明":
            st.title(":blue[圖片選擇]")
            st.subheader(":orange[Image Selection]")
            st.write(st.session_state['user_name'] + "你好, 歡迎使用圖片選擇!")
            st.write('''圖片選擇可以幫助使用者快速地選擇適合的圖片。\
使用者可根據左邊的選項來瀏覽、查詢或用AI的方式來生成喜歡的圖片。''')
        elif choice == "瀏覽圖片":
            st.title(":blue[瀏覽圖片]")
        elif choice == "查詢圖片":
            st.title(":blue[查詢圖片]")
        elif choice == "生成圖片":
            st.title(":blue[生成圖片]")
        elif choice == "回首頁":
            st.session_state['current_page'] = "首頁"
            st.rerun()
            
if __name__ == '__main__':
    main()
