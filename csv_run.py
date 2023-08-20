import mysql.connector  # 載入套件
import csv  # 引入 csv
import requests  # 引入 request
from bs4 import BeautifulSoup as bs  # 從bs4 引入 BeautifulSoup 並取名 bs
import re

try:
    connection = mysql.connector.connect(  # 建立MySQL連線
        host="localhost",  # 連線主機名稱
        user="root",  # 登入帳號
        password="123456",  # 登入密碼
        database="test",  # 資料庫名
    )

    with connection.cursor() as cursor:  # 建立資料庫連接的游標
        sql = """
        CREATE TABLE IF NOT EXISTS csv_run (
            ID int NOT NULL AUTO_INCREMENT PRIMARY KEY,
            DATE varchar(12), 
            DEPARTMENT varchar(30),
            TITLE varchar(255),
            URL varchar(255),
            UNIQUE KEY unique_name_height_weight (TITLE, URL)
        )
        """
        cursor.execute(sql)  # 執行SQL指令
        connection.commit()  # 提交至SQL

        with open("ouput.csv", "r") as csvfile:  # 打開 CSV 檔案
            csvreader = csv.reader(csvfile)  # 建立 CSV 讀取器
            next(csvreader)  # 忽略第一行（標題行）

            for row in csvreader:  # 讀取並處理每一列資料
                date = row[0]
                department = row[1]
                title = row[2]
                url = row[3]

                # print(f"URL: {url}, TITLE: {title}")  # 處理資料, f 字串內可以包含變數，用{} 來插入變數

                sql = "INSERT IGNORE INTO csv_run (DATE, DEPARTMENT, TITLE, URL) VALUES (%s, %s, %s, %s)"  # 插入資料表內容, %s 參數的佔位符
                values = (date, department, title, url)
                cursor.execute(
                    sql, values
                )  # 執行SQL指令, 需將變數sql、URL和TITLE傳遞給cursor.execute()
                connection.commit()  # 提交至SQL

    connection.close()  # 關閉SQL連線

except mysql.connector.Error as e:
    print("Error: Could not make connection to the MySQL database")
    print(e)  # 印出連線資料庫時的任何錯誤錯誤訊息
