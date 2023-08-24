import csv
import requests
from bs4 import BeautifulSoup
import time ,os
import difflib
import pprint
# [[標題,.....,url]轉成[["標題,...,url"]]
def list_row_to_str(list_data):
    temp = list_data[::]
    for i in range(len(temp)):
        temp[i] = ",".join(temp[i])
    return temp
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
            writer = csv.writer(f,delimiter=';', quotechar='',quoting=csv.QUOTE_NONE,escapechar='\\')
            writer.writerow(self.header)
            writer.writerows(self.data)
        print(f"Saved table data to {filename}")
    def get_table_list_string(self):
        temp = self.data[::]
        temp.insert(0,self.header)
        # print(temp)
        return temp 
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
    # 如果需要資料更改或是檔案不存在 則回傳true 
    def table_changed(self, content):
        current_hash = self.get_table_hash(content)
        #第一次執行時檔案不一定存在 
        if not os.path.exists(self.hash_file):
            with open(self.hash_file, 'w') as f:
                f.write(str(current_hash))
            return True
        #確保檔案存在！
        with open(self.hash_file, 'r+') as f:
            try:
                previous_hash = int(f.read())
            except ValueError:
                previous_hash = None
                f.seek(0)
                f.write(str(current_hash))#寫入當前的哈希值
                f.truncate()
                return True
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
    def show_difference(self,save_data_csv_file,netword_new_data):
        # save_data：從csv檔案中存取的資料
        with open(save_data_csv_file) as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            save_data = list_row_to_str(list(reader))
        # netword_new_data :從網頁抓下來的新資料
        netword_new_data = list_row_to_str(netword_new_data)
        count = 0 
        diff = []
        for i in netword_new_data:
            if i not in save_data:
                count += 1 
                diff.append(f"新增：{i}")
        print(f"共計：新增{count}筆資料")                
        pprint.pprint(diff)
        return count 

while(1):
    page = NTUSTBulletin(1) 
    page.run(save=True)
    watcher = TableWatcher(page.get_url(),'table_hash.txt')
    # todo : bug 不要邊爬邊存 ，有改變在存檔 
    # 若是資料更新！
    if watcher.table_changed(page.get_table_str()):
        # 顯示不同之處
        watcher.show_difference("output.csv",page.get_table_list_string())
        # 新增到SQL內 

    time.sleep(10)