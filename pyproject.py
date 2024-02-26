from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from datetime import datetime
import sys


# 将所给货币中英文对照文件转化为字典形式
def load_currency_dictionary(filename):
    currency_dict = {}
    with open(filename, "r") as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) == 2:
                currency_dict[parts[1]] = parts[0]
    return currency_dict


# 查找货币对应的中文
def translate_currency(currency, currency_dict):
    return currency_dict.get(currency, False)


# 判断给定的时间是否准确
def is_valid_date(date_string):
    try:
        datetime.strptime(date_string, "%Y%m%d")
        return True
    except ValueError:
        return False


# 读取日期和简写货币名称
[date_string, currency] = [sys.argv[1], sys.argv[2]]
# 将输入的简写货币名称改为中文
currency_trans = translate_currency(
    currency, load_currency_dictionary("currency_translate.txt")
)

# 如果读入的货币名称和日期不合规，则再次读取
while not currency_trans or not is_valid_date(date_string):
    if not currency_trans:
        print("the currency couldn't be found.")
    if not is_valid_date(date_string):
        print("the date is wrong.")
    [date_string, currency] = input().split()
    currency_trans = translate_currency(
        currency, load_currency_dictionary("currency_translate.txt")
    )
# 将日期改为xxxx-xx-xx形式方便后续处理
date_string = date_string[0:4] + "-" + date_string[4:6] + "-" + date_string[6:]

# 打开网站开始爬取
driver = webdriver.Edge()
driver.get("https://www.boc.cn/sourcedb/whpj/")
search = driver.find_element(By.ID, "historysearchform").find_elements(
    By.CLASS_NAME, "search_ipt"
)
# 输入查找日期
for i in range(2):
    search[i].click()
    search[i].send_keys(Keys.BACK_SPACE)
    search[i].send_keys(date_string)

# 关闭日期选择窗口
close_button = driver.find_element(By.ID, "calendarClose")
close_button.click()
# 选择对应货币
dropdown = driver.find_element(By.ID, "pjname")
dropdown.click()
# 选中对应货币
select = Select(dropdown)
select.select_by_visible_text(currency_trans)
# 查找
search_button = driver.find_element(By.CSS_SELECTOR, ".main .search_btn")
search_button.click()
# 开始爬取数据
result_list = []  # 所有数据
for i in range(10):
    tr_list = driver.find_element(By.CLASS_NAME, "publish").find_elements(
        By.TAG_NAME, "tr"
    )
    for tr in tr_list:
        if tr == tr_list[0]:
            tag = "th"
        else:
            tag = "td"
        table_list = tr.find_elements(By.TAG_NAME, tag)
        row_list = []
        for td in table_list:
            # 把每一行上的元素 按列加入row_list,即得到完整的一行
            row_list.append(td.text)
            # 把每一行加入result_list
        result_list.append(row_list)
        # 下一页
    btn = driver.find_element(By.LINK_TEXT, "下一页")
    btn.click()

# 将爬到的数据写入文件，每个元素之间按空格隔开
f = open("result.txt", "w")
for line in result_list:
    for l in line:
        f.write(l + " ")
    f.write("\n")
f.close()
# 输出结果
if result_list[1][3] != "":
    print("现汇卖出价为:" + result_list[1][3])
else:
    print("无现汇卖出价")
