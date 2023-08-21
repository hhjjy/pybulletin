import csv
import requests
from bs4 import BeautifulSoup


class NTUSTBulletin:
    def __init__(self, page):
        self.page = page
        self.url = (
            f"https://bulletin.ntust.edu.tw/p/403-1045-1391-{self.page}.php?Lang=zh-tw"
        )

    def get_html_pages(self):
        response = requests.get(self.url)
        return response

    def parse_html(self, content):
        soup = BeautifulSoup(content, "html.parser")
        table = soup.find("table")
        thead = table.find("thead")
        thead_tr = thead.find("tr")
        thead_th_list = thead_tr.find_all("th")
        header = [th.text for th in thead_th_list]
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
                row_data.append(
                    td.text.strip().replace(" ", "").replace("\t", "").replace("\n", "")
                )

                a_element = td.find("a")
                # is not empty
                if a_element:
                    href = a_element.get("href")
                    row_data.append(href)
            data.append(row_data)
        return header, data

    def save_to_csv(self, header, data):
        filename = "table.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data)
        print(f"Saved table data to {filename}")

    def run(self):
        response = self.get_html_pages()
        return self.parse_html(response.text)
        # self.save_to_csv(header, data)


# # 使用类获取网页表格数据
all_data = []
for page in range(1, 160):
    print(f"page :{page}...")
    ntust_bulletin = NTUSTBulletin(page)
    header, data = ntust_bulletin.run()
    all_data += data

# 儲存
filename = "ouput.csv"
with open(filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, quotechar='"', quoting=csv.QUOTE_ALL)
    writer.writerow(header)
    writer.writerows(all_data)
