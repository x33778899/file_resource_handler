import csv
import logging
import time
from PIL import Image
import pyautogui
import io
from io import BytesIO
from airtest_selenium.proxy import WebChrome
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from PIL import ImageChops
import pandas as pd
import numpy as np
from skimage.metrics import structural_similarity as ssim
import Levenshtein
import codecs
from Google_api_function import Google_api_function


# 功能參數調整
def function_parameter():
    # 判斷遊戲點選功能是否正常
    filename = 'game_feature_check.csv'
    # 沒有得到前端圖片間距用猜的
    canvas_size = 292
    # y軸截圖座標
    canvas_height = 410
    # y軸截圖範圍
    image_height_cut = 110
    # x軸等於13的原因是沒拖曳x=0可以點到你要的東西,拖曳後點選x會有上一次拖曳前的最後一個
    x = 13
    # y軸
    y = 300
    # drag_along_the_x_axis =canvas_size*6 代表我只點6張圖
    drag_along_the_x_axis = canvas_size * 6 + x
    # 遊戲名稱計算
    game_name_count = 0
    # 單純判斷因為點第一個位置的邊界不一樣,基本上只會判斷0跟0以上
    count = 0
    # 截圖x軸移動
    screenshot_range = 0
    # 拖曳次數
    drag_count = 3

    # 從右點到左
    reverse_calculation = 1
    # 目前點在幾行
    which_row = 1
    return canvas_height, canvas_size, count, drag_along_the_x_axis, drag_count, filename, game_name_count, \
        image_height_cut, reverse_calculation, which_row, x, y


# 開始執行程式
def start():
    # 創建 Google_api_function 的對象
    google_api = Google_api_function()

    # 使用對象調用 google_api_read 方法
    client = google_api.google_api_read()

    canvas_height, canvas_size, count, drag_along_the_x_axis, drag_count, filename, game_name_count, image_height_cut, \
        reverse_calculation, which_row, x, y = function_parameter()

    # 迴圈開始執行前先清乾淨csv
    clear_csv(filename)

    logging.basicConfig(level=logging.INFO)
    # 建立網頁驅動
    driver = createwd()

    # 獲取螢幕尺寸
    screen_width, screen_height = pyautogui.size()
    logging.info(f"螢幕尺寸：{screen_width} x {screen_height}")

    time.sleep(15)

    while True:
        canvas = driver.find_element(By.TAG_NAME, "canvas")
        actions = ActionChains(driver)

        time.sleep(15)

        location = canvas.location
        size = canvas.size
        # 從右點到左不進入判斷
        if x >= drag_along_the_x_axis and not reverse_calculation > 1:
            drag_count += 1
            x = 13
            count = 0

        # 判斷拖曳次數
        for i in range(drag_count):
            window_dragging_logic(actions, canvas, drag_along_the_x_axis)
        # 第一張圖開始的位子計算方式不同
        if count == 0 or reverse_calculation >= 2:
            screenshot_range = canvas_size
            if count == 0:
                # 用來判斷視窗拖曳是否拉到底
                screenshot_image(420, 120, drag_count, drag_along_the_x_axis, location['x'] - 30, "drag_comparison")
                # 解析截圖的文字
                drag_comparison = Google_api_function.google_api_Image_text_analysis(client, 'drag_comparison' + str(
                    drag_count) + '.png')
                # 寫入csv
                test_write_csv(drag_comparison, 'drag_comparison' + str(drag_count) + '.csv', 'Click Before')

            if drag_count > 0:
                # 雙重保險比對一字串相似對比較
                text_similarity = calculate_text_similarity(
                    read_csv_compare_similarity('drag_comparison' + str(drag_count) + '.csv', "Click Before"),
                    read_csv_compare_similarity('drag_comparison' + str(drag_count - 1) + '.csv', "Click Before"))
                # 雙重保險比對二字串交集比對,預防有辨識不清楚,google辨識文字並非100%會用空格分割字串
                intersection_set = (
                        read_csv_compare_intersection('drag_comparison' + str(drag_count) + '.csv', "Click Before") &
                        read_csv_compare_intersection('drag_comparison' + str(drag_count - 1) + '.csv', "Click Before"))

                # text_similarity 判斷直可以更多資料調整相似度可以在多試幾次後修正
                if text_similarity > 0.5 or len(intersection_set) > 0:
                    # 判斷是不是拖曳到底了
                    # 到底從左邊開始點不準確從右邊開始點到左邊
                    # 相似度可以在多試幾次後修正
                    # 點選前截圖
                    screenshot_image(canvas_height, image_height_cut, game_name_count, screenshot_range,
                                     screen_width - reverse_calculation * 275 - 20, 'original_image')

                    time.sleep(1)
                    # 模仿ai點擊功能
                    click_coordinates(screen_width - reverse_calculation * 275, y)

                    # 執行所有功能
                    actions.perform()

                    time.sleep(10)
                    # 點擊選項後的截圖
                    screenshot_image(canvas_height, image_height_cut, game_name_count, screenshot_range,
                                     screen_width - reverse_calculation * 275 - 20, 'compare_pictures')

                    time.sleep(3)
                    # 解析文字
                    original_image_text = Google_api_function.google_api_Image_text_analysis(client,
                                                                                             'original_image' + str(
                                                                                                 game_name_count) + '.png')

                    time.sleep(1)
                    # 寫入csv 用來判斷是不是重複了可以換行了
                    test_write_csv(original_image_text, 'identify_duplicate_data.csv', 'data')

                    # 交集比對計算如果有一樣的代表可以換第二行了
                    intersection_set = read_csv_compare_similarity(filename,
                                                                   "Click Before") & read_csv_compare_similarity(
                        "identify_duplicate_data.csv", "data")

                    logging.info(intersection_set)

                    if intersection_set:  # 如果集合不为空
                        y += 330
                        drag_count = 0
                        canvas_height += 330
                        reverse_calculation = 1
                        # 本來就點在第二行了可以中斷了
                        if which_row == 2:
                            print("自動化測試結束")
                            break
                        else:
                            print("開始點選第二行")
                            which_row = 2
                            refresh(driver)
                            continue

                    else:
                        print("集合為空")

                        # 解析文字
                        compare_image_text = Google_api_function.google_api_Image_text_analysis(client,
                                                                                                'compare_pictures' + str(
                                                                                                    game_name_count) + '.png')

                        # csv 判斷 功能是否正常
                        check_game_clicking_to_csv(compare_image_text, filename, original_image_text)

                        game_name_count += 1

                        reverse_calculation += 1

                        refresh(driver)
                else:
                    # 網頁截圖流程的邏輯
                    count, game_name_count, x = web_page_screenshot_evaluation_process(actions, canvas_height,
                                                                                       canvas_size,
                                                                                       client, count, driver, filename,
                                                                                       game_name_count,
                                                                                       image_height_cut,
                                                                                       screenshot_range, x, y)
            else:
                # 網頁截圖流程的邏輯
                count, game_name_count, x = web_page_screenshot_evaluation_process(actions, canvas_height, canvas_size,
                                                                                   client, count, driver, filename,
                                                                                   game_name_count, image_height_cut,
                                                                                   screenshot_range, x, y)

        else:
            screenshot_range = 280
            # 網頁截圖流程的邏輯
            count, game_name_count, x = web_page_screenshot_evaluation_process(actions, canvas_height, canvas_size,
                                                                               client, count, driver, filename,
                                                                               game_name_count, image_height_cut,
                                                                               screenshot_range, x, y)


# 建立網頁驅動
def createwd():
    chrome_options = Options()
    chrome_options.binary_location = "C:\Program Files\Google\Chrome\Application\chrome.exe"
    driver = WebChrome(chrome_options=chrome_options)
    driver.implicitly_wait(20)
    driver.get(
        "https://apifront.qaz411.com/lx/S004/8.0.15/index.html?ps=qptest-wss.qaz411.com:8031&gameId=0&companyId=5064&theme=S004&agent=1101285&account=1101285_aaa&token=ad87ea4c079f1fc22f73387ab6a7a4139ca38d6ff430768b2f081b2fb6a7963bc165665ed5ef68b6f268d36b97d48f4aa41a46f4efe5fbdf3030fd42a030a8f6fc4deb7da3f75aa882bbed77d0ed90aacbce3cf25c83348801911e404b7cb501e6292a0fb0786fab2cf7f68b8fcaf9c561451e12be40e9ed833fed6f9ff9851c&type=1&platform=1&languageType=zh_cn&sml=0&backgroundUrl=null&title=gfg")
    driver.maximize_window()
    return driver


# 網頁截圖流程的邏輯
def web_page_screenshot_evaluation_process(actions, canvas_height, canvas_size, client, count, driver, filename,
                                           game_name_count, image_height_cut, screenshot_range, x, y):
    # 點選前截圖
    screenshot_image(canvas_height, image_height_cut, game_name_count, screenshot_range, x - 30,
                     'original_image')
    time.sleep(1)
    # 模仿ai點擊功能
    click_coordinates(x, y)
    # 執行所有功能
    actions.perform()
    time.sleep(10)
    # 點擊選項後的截圖
    screenshot_image(canvas_height, image_height_cut, game_name_count, screenshot_range, x - 30,
                     'compare_pictures')
    time.sleep(3)
    # 圖片文字解析
    original_image_text = Google_api_function.google_api_Image_text_analysis \
        (client, 'original_image' + str(game_name_count) + '.png')
    compare_image_text = Google_api_function.google_api_Image_text_analysis \
        (client, 'compare_pictures' + str(game_name_count) + '.png')
    # csv 判斷 功能是否正常
    check_game_clicking_to_csv(compare_image_text, filename, original_image_text)
    x += canvas_size
    count += 1
    game_name_count += 1
    # 畫面從新整理
    refresh(driver)
    return count, game_name_count, x


# 計算兩個集合的字串相似度
def calculate_text_similarity(text_set1, text_set2):
    text1 = ' '.join(text_set1)
    text2 = ' '.join(text_set2)

    similarity = Levenshtein.ratio(text1, text2)

    return similarity


# 畫面從新整理
def refresh(driver):
    driver.refresh()


# 將遊戲功能是否正常寫入csv
def check_game_clicking_to_csv(compare_image_text, filename, original_image_text):
    if original_image_text != compare_image_text:
        write_csv(original_image_text, compare_image_text, "True", filename)
        print("兩個字串不相等")
    else:
        write_csv(original_image_text, compare_image_text, "False", filename)
        print("兩個字串相等")


# 第一層保險讀取csv比對,判斷是否拉到底,辨識文字相似度
def read_csv_compare_similarity(file_path, header):
    result_set = set()
    df = pd.read_csv(file_path, encoding='utf-8-sig', dtype=str)
    title = df[header]

    for data in title:
        result_set.add(data)
    return result_set


# 第二層保險交集比對的寫法
def read_csv_compare_intersection(file_path, header):
    result_set = set()
    df = pd.read_csv(file_path, encoding='utf-8-sig', dtype=str)
    title = df[header]

    for data in title:
        split_data = data.split(" ")
        result_set.update(split_data)

    return result_set


# 寫入csv
# 非必要看到辨識出什麼東西
# 方便修改程式問題
def test_write_csv(png_text, filename, header_name):
    header = [
        [header_name]  # 添加英文標題
    ]
    data = [
        [png_text]
    ]

    with open(filename, 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerows(header)  # 寫入標題
        writer.writerows(data)  # 寫入數據


# 拖曳視窗
def window_dragging_logic(actions, canvas, drag_along_the_x_axis):
    for i in range(3):
        actions.drag_and_drop_by_offset(canvas, -drag_along_the_x_axis / 2, 0).perform()
        time.sleep(1)
    time.sleep(2)


# 進行截圖
def screenshot_image(canvas_height, canvas_height_range, count, screenshot_range, x, image_name):
    im = pyautogui.screenshot(region=(x, canvas_height, screenshot_range, canvas_height_range))
    im.save(image_name + str(count) + '.png')


# 點選座標
def click_coordinates(x, y):
    pyautogui.click(x, y, duration=0.25)


# 寫入csv
def write_csv(original_image_text, compare_image_text, critical_result, filename):
    data = [
        [original_image_text.strip(), compare_image_text.strip(), critical_result],
    ]

    with open(filename, 'a', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerows(data)


# 清除csv檔案
def clear_csv(filename):
    # 標頭
    data = [
        ['Click Before', 'Click After', 'Comparison Result'],  # 添加英文標頭
    ]

    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
