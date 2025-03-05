#
#                    _ooOoo_
#                   o8888888o
#                   88" . "88
#                   (| -_- |)
#                   O\  =  /O
#                ____/`---'\____
#              .'  \\|     |//  `.
#             /  \\|||  :  |||//  \
#            /  _||||| -:- |||||-  \
#            |   | \\\  -  /// |   |
#            | \_|  ''\---/''  |   |
#            \  .-\__  `-`  ___/-. /
#          ___`. .'  /--.--\  `. . __
#       ."" '<  `.___\_<|>_/___.'  >'"".
#      | | :  `- \`.;`\ _ /`;.`/ - ` : | |
#      \  \ `-.   \_ __\ /__ _/   .-` /  /
# ======`-.____`-.___\_____/___.-`____.-'======
#                    `=---='
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#             佛祖保佑       永无BUG
import logging
import random
import re
import threading
import traceback
from threading import Thread
import time
from typing import List

import numpy
import requests
import texts
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

import random

import schedule

"""
原作者推荐，原作者地址:https://github.com/Zemelee/wjx
获取代理ip，这里要使用到一个叫“品赞ip”的第三方服务: https://www.ipzan.com?pid=ggj6roo98
注册，需要实名认证（这是为了防止你用代理干违法的事，相当于网站的免责声明，属于正常步骤，所有代理网站都会有这一步）
将自己电脑的公网ip添加到网站的白名单中，然后选择地区，时长为1分钟，数据格式为txt，提取数量选1
然后点击生成api，将链接复制到放在zanip函数里
设置完成后，不要问为什么和视频教程有点不一样，因为与时俱进！(其实是因为懒，毕竟代码改起来容易，视频录起来不容易嘿嘿2023.10.29)
如果不需要ip可不设置，也不影响此程序直接运行（悄悄提醒，品赞ip每周可以领3块钱）
"""



# 定义运行时间段
RUN_TIME_SLOTS = [
    {"start": "08:00", "end": "09:00"},  # 早上 8:00 到 9:00
    {"start": "10:30", "end": "10:42"},  # 早上 10:30 到 10:42
    {"start": "11:10", "end": "11:22"},  # 早上 11:10 到 11:22
    {"start": "12:17", "end": "12:32"},  # 早上 12:17 到 12:32
    {"start": "13:47", "end": "13:55"},  # 早上 12:17 到 12:32
    {"start": "14:00", "end": "15:00"},  # 下午 14:00 到 15:00
    {"start": "15:40", "end": "15:50"},  # 下午 15:40 到 15:50
    {"start": "17:20", "end": "17:50"},  # 下午 17:20 到 17:50
    {"start": "20:00", "end": "21:00"},  # 晚上 20:00 到 21:00
    {"start": "23:30", "end": "23:40"},  # 晚上 23:30 到 23:40
    {"start": "00:10", "end": "00:15"},  # 晚上 00:10 到 00:15
]


# 模拟手机、Ipad运行
MOBILE_USER_AGENTS = [
    # iPhone
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    # Android
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
    # iPad
    "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
]

# 检查当前时间是否在运行时间段内
def is_in_running_time():
    current_time = time.strftime("%H:%M")
    for slot in RUN_TIME_SLOTS:
        if slot["start"] <= current_time <= slot["end"]:
            return True
    return False

def zanip():
    # 这里放你的ip链接，选择你想要的地区，1分钟，ip池无所谓，数据格式txt，提取数量1，数量一定是1!其余默认即可
    api = "https://service.ipzan.com/"
    ip = requests.get(api).text
    return ip

# 问卷星问卷的地址（自行修改）
url = "https://www.wjx.cn/xxx.aspx"

# 单选题
# -1代表随机数，[]内代表被选中的概率
single_prob = {
    "1": -1,
    "3": -1,
    "4": -1,
    "5": -1,
    "6": -1,
    "7": -1,
    "8": -1,
    "9": -1,
    "78":[0,0,0,0,0,1]
}

# 下拉框参数，具体含义参考单选题，如果没有下拉框题也不要删，就让他躺在这儿吧，其他题也是哦，没有就不动他，别删，只改你有的题型的参数就好啦
droplist_prob = {"1": [2, 1, 1]}

# 多选题
# 表示每个选项选择的概率，100表示必选，30表示选择B的概率为30；不能写[1,1,1,1]这种比例了，不然含义为选ABCD的概率均为1%
# 最好保证概率和加起来大于100
multiple_prob = {"77": [0, 0, 0, 0, 0, 100]}

# 矩阵题概率参数,-1表示随机，其他含义参考单选题；同样的，题号不重要，保证第几个参数对应第几个矩阵小题就可以了；
# 在示例问卷中矩阵题是第10题，每个小题都要设置概率值才行！！以下参数表示第二题随机，其余题全选A
matrix_prob = {
    "1": -1,
    "2": -1,
    "3": -1,
    "4": -1,
    "5": -1,
    "6": -1,
}

# 量表题概率参数，参考单选题
scale_prob = {"78":[0, 0, 0, 0, 0, 1]}


# 年级与年龄对应（题号对应）
# 1，2为题号
grade_question_number = "1"  # 年级题
age_question_number = "2"  # 年龄题

# 年级对应的年龄范围
grade_to_age = {
    "1": ["18", "19","20"],  # 大一
    "2": ["19", "20", "21"],  # 大二
    "3": ["20","21", "22"],  # 大三
    "4": ["22", "23","24"]  # 大四
}

# 填空题参数
texts = {
    "2": []  # 自动填充年龄
}

# 填空题概率
texts_prob={
    "2": [] # 自动填充
}

# 自动匹配年龄
def fill_age_texts():
    global texts, texts_prob
    # 确保选中的年级是有效值
    selected_grade = single_prob.get(grade_question_number, -1)
    if selected_grade == -1 or str(selected_grade) not in grade_to_age:
        selected_grade = str(random.choice(["1", "2", "3", "4"]))  # 随机选择一个年级
        print(f"⚠️  `single_prob[1]` 未设定，随机选择年级 {selected_grade}")
    # 获取对应的年龄范围
    possible_ages = grade_to_age.get(str(selected_grade), ["18", "25"])
    # 兜底：如果 `possible_ages` 为空，防止崩溃
    if not possible_ages:
        possible_ages = ["18", "25"]
    # 填充 texts["2"]
    texts[age_question_number] = possible_ages
    # 生成均匀分布的概率
    texts_prob[age_question_number] = [1 / len(possible_ages)] * len(possible_ages)
    print(f"✅ 选择年级 {selected_grade}，可选年龄 {possible_ages}，生成概率 {texts_prob[age_question_number]}")

# 调用年龄填充
fill_age_texts()

# 参数归一化，把概率值按比例缩放到概率值和为1，比如某个单选题[1,2,3,4]会被转化成[0.1,0.2,0.3,0.4],[1,1]会转化成[0.5,0.5]
for prob in [single_prob, matrix_prob, droplist_prob, scale_prob, texts_prob]:
    for key in prob:
        if isinstance(prob[key], list):
            prob_sum = sum(prob[key])
            prob[key] = [x / prob_sum for x in prob[key]]

# 转化为列表,去除题号
single_prob = list(single_prob.values())
droplist_prob = list(droplist_prob.values())
multiple_prob = list(multiple_prob.values())
matrix_prob = list(matrix_prob.values())
scale_prob = list(scale_prob.values())

# 搞笑一下
print("佛曰：bug泛滥，我已瘫痪!")

# 校验IP地址合法性
def validate(ip):
    pattern = r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?):(\d{1,5})$"
    if re.match(pattern, ip):
        return True
    return False


# 检测题量
def detect(driver: WebDriver) -> List[int]:
    q_list: List[int] = []
    page_num = len(driver.find_elements(By.XPATH, '//*[@id="divQuestion"]/fieldset'))
    for i in range(1, page_num + 1):
        questions = driver.find_elements(By.XPATH, f'//*[@id="fieldset{i}"]/div')
        valid_count = sum(
            1 for question in questions if question.get_attribute("topic").isdigit()
        )
        q_list.append(valid_count)
    return q_list


# 填空题处理函数
def vacant(driver: WebDriver, current, index):
    # 根据题号 current 获取填空题内容
    if str(current) in texts:
        content = texts[str(current)]  # 获取填空题内容
        p = texts_prob[str(current)]  # 获取填空题概率
        if content and p:  # 确保内容和概率不为空
            text_index = numpy.random.choice(a=numpy.arange(0, len(p)), p=p)
            driver.find_element(By.CSS_SELECTOR, f"#q{current}").send_keys(content[text_index])
        else:
            print(f"⚠️ 第 {current} 题填空题内容或概率为空！")
    else:
        print(f"⚠️ 第 {current} 题不是填空题或未定义！")

# 单选题处理函数
def single(driver: WebDriver, current, index):
    xpath = f'//*[@id="div{current}"]/div[2]/div'
    a = driver.find_elements(By.XPATH, xpath)
    p = single_prob[index]
    # 调试信息：打印当前题号和选项数量
    print(f"第 {current} 题，选项数量: {len(a)}")
    # 特殊处理第 78 题
    if current == 78:
        if len(a) < 6:
            print(f"⚠️ 第 78 题选项数量不足 6 个，无法选择第 6 个选项！")
            return
        print(f"✅ 第 78 题选择“非常符合”（第 6 个选项）")
        r = 6  # 直接选择第 6 个选项
    elif p == -1:
        r = random.randint(1, len(a))
    else:
        assert len(p) == len(
            a
        ), f"第{current}题参数长度：{len(p)},选项长度{len(a)},不一致！"
        r = numpy.random.choice(a=numpy.arange(1, len(a) + 1), p=p)
    # 调试信息：打印选择的选项
    print(f"第 {current} 题选择第 {r} 个选项")
    # 点击选项
    driver.find_element(
        By.CSS_SELECTOR, f"#div{current} > div.ui-controlgroup > div:nth-child({r})"
    ).click()
    # 如果是年级选择题，记录选中的年级，并更新年龄填空题的内容
    if str(current) == grade_question_number:
        selected_grade = str(r)  # 记录选择的年级
        print(f"📌 已选择年级：{selected_grade}")
        # 更新对应的年龄范围
        possible_ages = grade_to_age.get(selected_grade, ["18", "25"])
        texts[age_question_number] = possible_ages
        texts_prob[age_question_number] = [1 / len(possible_ages)] * len(possible_ages)
        print(f"✅ 更新年级 {selected_grade} 对应的年龄范围为: {possible_ages}")

# 下拉框处理函数
def droplist(driver: WebDriver, current, index):
    # 先点击“请选择”
    driver.find_element(By.CSS_SELECTOR, f"#select2-q{current}-container").click()
    time.sleep(0.5)
    # 选项数量
    options = driver.find_elements(
        By.XPATH, f"//*[@id='select2-q{current}-results']/li"
    )
    p = droplist_prob[index]  # 对应概率
    r = numpy.random.choice(a=numpy.arange(1, len(options)), p=p)
    driver.find_element(
        By.XPATH, f"//*[@id='select2-q{current}-results']/li[{r + 1}]"
    ).click()


# 多选题处理函数（这里出现了第78题的特别设置是因为一开始我将题目类型搞混了，后来发现不会有什么影响所以没有删除，其实是本身没有多选）
# 如果各位在运行代码时候发现78题选择第6项的概率特别高，可以将IF的部分删除
def multiple(driver: WebDriver, current, index):
    if current == 78:
        css = f"#div{current} > div.ui-controlgroup > div:nth-child(6)"
        driver.find_element(By.CSS_SELECTOR, css).click()
        return
    xpath = f'//*[@id="div{current}"]/div[2]/div'
    options = driver.find_elements(By.XPATH, xpath)
    mul_list = []
    p = multiple_prob[index]
    assert len(options) == len(p), f"第{current}题概率值和选项值不一致"
    # 生成序列,同时保证至少有一个1
    while sum(mul_list) <= 1:
        mul_list = []
        for item in p:
            a = numpy.random.choice(
                a=numpy.arange(0, 2), p=[1 - (item / 100), item / 100]
            )
            mul_list.append(a)
    # 依次点击
    for index, item in enumerate(mul_list):
        if item == 1:
            css = f"#div{current} > div.ui-controlgroup > div:nth-child({index + 1})"
            driver.find_element(By.CSS_SELECTOR, css).click()


# 矩阵题处理函数
def matrix(driver: WebDriver, current, index):
    xpath1 = f'//*[@id="divRefTab{current}"]/tbody/tr'
    a = driver.find_elements(By.XPATH, xpath1)
    q_num = 0  # 矩阵的题数量
    for tr in a:
        if tr.get_attribute("rowindex") is not None:
            q_num += 1
    # 选项数量
    xpath2 = f'//*[@id="drv{current}_1"]/td'
    b = driver.find_elements(By.XPATH, xpath2)  # 题的选项数量+1 = 6
    # 遍历每一道小题
    for i in range(1, q_num + 1):
        p = matrix_prob[index]
        index += 1
        if p == -1:
            opt = random.randint(2, len(b))
        else:
            opt = numpy.random.choice(a=numpy.arange(2, len(b) + 1), p=p)
        driver.find_element(
            By.CSS_SELECTOR, f"#drv{current}_{i} > td:nth-child({opt})"
        ).click()
    return index


# 排序题处理函数，排序暂时只能随机
def reorder(driver: WebDriver, current):
    xpath = f'//*[@id="div{current}"]/ul/li'
    a = driver.find_elements(By.XPATH, xpath)
    for j in range(1, len(a) + 1):
        b = random.randint(j, len(a))
        driver.find_element(
            By.CSS_SELECTOR, f"#div{current} > ul > li:nth-child({b})"
        ).click()
        time.sleep(0.4)


# 量表处理函数
def scale(driver: WebDriver, current, index):
    xpath = f'//*[@id="div{current}"]/div[2]/div/ul/li'
    a = driver.find_elements(By.XPATH, xpath)  # 获取所有选项
    # 调试信息：打印当前题号和选项数量
    print(f"第 {current} 题，选项数量: {len(a)}")
    # 特殊处理第 78 题
    if current == 78:
        print(f"✅ 第 78 题选择“非常符合”（第 6 个选项）")
        r = 6  # 直接选择第 6 个选项
    else:
        # 如果 `scale_prob` 没有该题目，则生成默认均匀分布概率
        if str(current) not in scale_prob:
            print(f"⚠️ 警告：题号 {current} 缺少概率列表，自动生成均匀概率！")
            p = [1 / len(a)] * len(a)
        else:
            p = scale_prob[str(current)]
        # 如果 `p` 长度与 `a` 长度不匹配，自动修正
        if len(p) != len(a):
            print(f"⚠️ 警告：题号 {current} 选项数 {len(a)} 和概率数 {len(p)} 不匹配！自动调整")
            p = [1 / len(a)] * len(a)  # 让所有选项概率均等
        # 调试信息：打印概率列表
        print(f"第 {current} 题的概率列表: {p}")
        # 选择一个随机选项
        r = numpy.random.choice(a=numpy.arange(1, len(a) + 1), p=p)
    # 调试信息：打印选择的选项
    print(f"第 {current} 题选择第 {r} 个选项")
    # 点击对应的选项
    driver.find_element(
        By.CSS_SELECTOR, f"#div{current} > div.scale-div > div > ul > li:nth-child({r})"
    ).click()

# 刷题逻辑函数
def brush(driver: WebDriver):
    # 这里的填空题是被我指定的所以没有用到自动检测
    q_list = detect(driver)  # 检测页数和每一页的题量
    single_num = 0  # 第num个单选题
    # vacant_num = 1  # 第num个填空题
    droplist_num = 0  # 第num个下拉框题
    multiple_num = 0  # 第num个多选题
    matrix_num = 0  # 第num个矩阵小题
    scale_num = 0  # 第num个量表题
    current = 0  # 题号
    total_questions = sum(q_list)
    total_time = random.randint(210, 380)  # 模拟人类作答时间，让答题时间稳定在200-300秒
    avg_time_per_question = total_time / total_questions

    for j in q_list:  # 遍历每一页
        for k in range(1, j + 1):  # 遍历该页的每一题
            current += 1
            time.sleep(random.uniform(avg_time_per_question * 0.8, avg_time_per_question * 1.2))  # 模拟时间
            # 判断题型 md, python没有switch-case语法
            q_type = driver.find_element(
                By.CSS_SELECTOR, f"#div{current}"
            ).get_attribute("type")
            # 调试信息：打印当前题号和题型
            print(f"第 {current} 题，题型: {q_type}")
            if current == 78:
                print(f"✔ 第78题题型：{q_type}")
                if q_type == "5":
                   scale(driver, current, single_num)
                else:
                    print(f"⚠ 第78题不是量表题，无法处理")
            elif q_type == "1" or q_type == "2":  # 填空题
                vacant(driver, current, current)  # 直接使用题号 current
            elif q_type == "3":  # 单选
                single(driver, current, single_num)
                single_num += 1
            elif q_type == "4":  # 多选
                multiple(driver, current, multiple_num)
                multiple_num += 1
            elif q_type == "5":  # 量表题
                scale(driver, current, scale_num)
                scale_num += 1
            elif q_type == "6":  # 矩阵题
                matrix_num = matrix(driver, current, matrix_num)
            elif q_type == "7":  # 下拉框
                droplist(driver, current, droplist_num)
                droplist_num += 1
            elif q_type == "8":  # 滑块题
                score = random.randint(1, 100)
                driver.find_element(By.CSS_SELECTOR, f"#q{current}").send_keys(score)
            elif q_type == "11":  # 排序题
                reorder(driver, current)
            else:
                print(f"第{k}题为不支持题型！")
        time.sleep(0.5)
        #  一页结束过后点击下一页，或点击提交
        try:
            driver.find_element(By.CSS_SELECTOR, "#divNext").click()  # 点击下一页
            time.sleep(0.5)
        except:
            # 点击提交
            driver.find_element(By.XPATH, '//*[@id="ctlNext"]').click()
    submit(driver)



# 提交函数
def submit(driver: WebDriver):
    time.sleep(1)
    # 点击对话框的确认按钮
    try:
        driver.find_element(By.XPATH, '//*[@id="layui-layer1"]/div[3]/a').click()
        time.sleep(1)
    except:
        pass
    # 点击智能检测按钮，因为可能点击提交过后直接提交成功的情况，所以智能检测也要try
    try:
        driver.find_element(By.XPATH, '//*[@id="SM_BTN_1"]').click()
        time.sleep(3)
    except:
        pass
    # 滑块验证
    try:
        slider = driver.find_element(By.XPATH, '//*[@id="nc_1__scale_text"]/span')
        sliderButton = driver.find_element(By.XPATH, '//*[@id="nc_1_n1z"]')
        if str(slider.text).startswith("请按住滑块"):
            width = slider.size.get("width")
            ActionChains(driver).drag_and_drop_by_offset(
                sliderButton, width, 0
            ).perform()
    except:
        pass

# 运行函数
def run(xx, yy, is_mobile=False):
    option = webdriver.ChromeOptions()
    option.add_experimental_option("excludeSwitches", ["enable-automation"])
    option.add_experimental_option("useAutomationExtension", False)

    # 启用无头模式
    option.add_argument("--headless")  # 无头模式
    option.add_argument("--disable-gpu")  # 禁用 GPU 加速
    option.add_argument("--no-sandbox")  # 禁用沙盒模式

    # 移动端访问
    if is_mobile:
        # 随机选择一个手机 User-Agent
        mobile_user_agent = random.choice(MOBILE_USER_AGENTS)
        option.add_argument(f"user-agent={mobile_user_agent}")
        # 设置手机屏幕尺寸
        option.add_argument("--window-size=375,812")  # iPhone X 的屏幕尺寸
        # 启用移动端模拟
        mobile_emulation = {
            "deviceName": "iPhone X"
        }
        option.add_experimental_option("mobileEmulation", mobile_emulation)
    else:
        # PC端访问
        option.add_argument("--window-size=1200,800")

    global cur_num, cur_fail
    while cur_num < target_num:
        if not is_in_running_time():  # 检查是否在运行时间段内
            print("当前非运行时间段，休眠中...")
            time.sleep(60)  # 休眠 1 分钟
            continue
        if use_ip:
            ip = zanip()
            option.add_argument(f"--proxy-server={ip}")
        driver = webdriver.Chrome(options=option)
        driver.set_window_size(375, 812) if is_mobile else driver.set_window_size(1200, 800)
        driver.set_window_position(x=xx, y=yy)
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
            },
        )
        try:
            driver.get(url)
            url1 = driver.current_url
            brush(driver)
            time.sleep(4)
            url2 = driver.current_url
            if url1 != url2:
                cur_num += 1
                print(f"已填写{cur_num}份 - 失败{cur_fail}次 - {time.strftime('%H:%M:%S', time.localtime(time.time()))} ")
                driver.quit()
        except:
            traceback.print_exc()
            lock.acquire()
            cur_fail += 1
            lock.release()
            print("\033[42m", f"已失败{cur_fail}次,失败超过{int(fail_threshold)}次(左右)将强制停止", "\033[0m")
            if cur_fail >= fail_threshold:
                logging.critical("失败次数过多，为防止耗尽ip余额，程序将强制停止，请检查代码是否正确")
                quit()
            driver.quit()
            continue

def main():
    print("定时任务调度器启动...")
    num_threads = 3  # PC窗口数量
    mobile_threads = 5 # 自动窗口数量
    threads: list[Thread] = []
    # 创建并启动PC端线程
    for i in range(num_threads):
        x = 50 + i * 60  # 浏览器弹窗左上角的横坐标
        y = 50  # 纵坐标
        thread = Thread(target=run, args=(x, y))
        threads.append(thread)
        thread.start()
    # 创建并启动移动端线程
    for i in range(mobile_threads):
        x = 50 + (num_threads + i) * 60
        y = 60
        thread = Thread(target=run, args=(x, y, True))
        threads.append(thread)
        thread.start()
    # 等待所有线程完成
    for thread in threads:
        thread.join()


# 多线程执行run函数
if __name__ == "__main__":
    target_num = 50  # 目标份数，自行修改
    # 失败阈值，数值可自行修改为固定整数
    fail_threshold = target_num / 4 + 1
    cur_num = 0
    cur_fail = 0
    lock = threading.Lock()
    use_ip = False
    if validate(zanip()):
        print("IP设置成功, 将使用代理ip填写")
        use_ip = True
    else:
        print("IP设置失败, 将使用本机ip填写")
    main()
