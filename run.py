import csv
import requests
from bs4 import BeautifulSoup
import time ,os
import difflib
import pprint
        
class NTUSTBulletin:
    def __init__(self, page):
        self.page = page
        self.url = (
            f"https://bulletin.ntust.edu.tw/p/403-1045-1391-{self.page}.php?Lang=zh-tw"
        )
        self.header  = [] 
        self.data = [] 
    # 由request取得html資料
    def get_html_pages(self):
        response = requests.get(self.url)
        return response
    # 取得設定的網址
    def get_url(self):
        return self.url
    # 取得表格的文字檔案
    def get_table_str(self):
        content = self.get_html_pages()
        soup = BeautifulSoup(content.text,"html.parser")
        table = soup.find("table")
        return table.prettify().encode("utf-8")
    
    # you need to run parsehtml first ! 
    def convert_table_into_list(self):
        data = self.header[::]
        data.append(self.data)
        return data    
        
        
    # 解析表格並回傳表格抬頭，表格內容
    def parse_html(self, content):
        soup = BeautifulSoup(content, "html.parser")
        table = soup.find("table")
        thead = table.find("thead")
        thead_tr = thead.find("tr")
        thead_th_list = thead_tr.find_all("th")
        header = [th.text for th in thead_th_list]
        header.append("url")
        tbody = table.find("tbody")
        rows = tbody.find_all("tr")
        data = []
        for row in rows:
            # format: [date , unit , title , url ]
            row_data = []
            url = ""
            # search for url in each row data
            tds = row.find_all("td")
            for td in tds:
                temp = td.text.strip().replace(" ", "").replace("\t", "").replace("\n", "").replace(",","").replace('"',"").replace('|','').replace(",","").replace('“',"")
                row_data.append(
                    temp
                )
                
                a_element = td.find("a")
                # is not empty
                if a_element:
                    href = a_element.get("href")
                    # url 移除結尾/
                    if href.endswith("/"):
                        print(href)
                        href = href [:-1]
                    row_data.append(href)
            data.append(row_data)
        # 設定存在內部
        self.header = header
        self.data = data 
    def save_to_csv(self, filename="output.csv"):
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f,delimiter=',', quotechar='',quoting=csv.QUOTE_NONE,escapechar='\\')
            writer.writerow(self.header)
            writer.writerows(self.data)
        print(f"Saved table data to {filename}")
    def get_table_list_string(self):
        temp = [] 
        header  = self.header[::]
        data = self.data[::]
        temp.append(['日期,發佈單位,標題,url\n'])
        temp.append([",".join(i) for i in data])
        print(temp)
    def run(self,save=False):
        response = self.get_html_pages()
        self.parse_html(response.text)
        if save:
            self.save_to_csv()



class TableWatcher:
    def __init__(self, url, hash_file):
        self.url = url
        self.hash_file = hash_file

    def get_table_hash(self,content):
        return hash(content)
    # 如果需要更改則回傳true 
    def check_table(self, content):
        current_hash = self.get_table_hash(content)
        if not os.path.exists(self.hash_file):
            with open(self.hash_file, 'w') as f:
                f.write(str(current_hash))
            return False
        #確保檔案存在！
        with open(self.hash_file, 'r+') as f:
            try:
                previous_hash = int(f.read())
            except ValueError:
                previous_hash = None
                f.seek(0)
                f.write(str(current_hash))#寫入當前的哈希值
                f.truncate()
            if current_hash != previous_hash:
                print('Table content changed')
                # 在这里可以添加发送通知、保存数据等操作
                f.seek(0)
                f.write(str(current_hash))
                f.truncate()
                return True
        return False
    #比較output.csv與當前的list差異 
    # []- > str ["row1\n","row2\n","row3"]
    # data [[header],[row1],[row2]]
    def show_difference(self,old_file_path,list_table):
        # read from file 
        with open(old_file_path,"r+") as f :
            try:
                old_list_table =  f.read().splitlines(keepends=True)
                # print(old_file_path)               
            except:
                raise FileNotFoundError
        # print(old_list_table)
        # for i in range(len(old_list_table)):
        #     for j in range(len(i)):
        #         old_list_table[i][j].replace("\n","")
        # print(old_list_table)
        
page = NTUSTBulletin(1) 
# page.run(save=True)
# print(page.get_table_list_string())
watcher = TableWatcher(page.get_url(),'table_hash.txt')
watcher.show_difference("output.csv",page.get_table_list_string())
# while True:    
#data = page.load_from_csv()
#print(data)



    
    
    
    # if watcher.check_table(page.get_table_str()):
    #     print("CHANGED")
    #     #下載資料 
    #     # page.run()
    #     #儲存
    #     # page.save_to_csv()
    #     # 上傳到數據庫 sql 
        
    #     # 發送通知 
        
    # time.sleep(5)
# # # 使用类获取网页表格数据
# all_data = []
# for page in range(1, 9):
#     print(f"page :{page}...")
#     ntust_bulletin = NTUSTBulletin(page)
#     header, data = ntust_bulletin.run()
#     all_data += data
# # 儲存
# filename = "ouput.csv"
# with open(filename, "w", newline="", encoding="utf-8") as f:
#     writer = csv.writer(f,delimiter=',', quotechar='',quoting=csv.QUOTE_NONE,escapechar='\\')
#     writer.writerow(header)
#     writer.writerows(all_data)
