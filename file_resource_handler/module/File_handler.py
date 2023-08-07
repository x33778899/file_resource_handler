import csv
import logging
import time
from PIL import Image
import pyautogui
import io
from io import BytesIO
from PIL import ImageChops
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import pandas as pd
import numpy as np
from skimage.metrics import structural_similarity as ssim
import Levenshtein
import codecs
from Google_api_function import Google_api_function
from Commons_function import Commons_function
import cv2
import os


# 功能參數調整
def function_parameter():
    # 判斷遊戲點選功能是否正常
    filename = 'game_string_check.csv'
    # 沒有得到前端圖片間距用猜的
    image_size = 292
    # y軸截圖座標
    image_height = 410
    # y軸截圖範圍
    image_height_range = 110
    # x軸等於13的原因是沒拖曳x=0可以點到你要的東西,拖曳後點選x會有上一次拖曳前的最後一個
    x = 13
    # y軸
    y = 300
    # drag_along_the_x_axis =image_size*6 代表我只點6張圖
    drag_along_the_x_axis = image_size * 6 + x
    # 遊戲名稱計算
    game_name_count = 0
    # 單純判斷因為點第一個位置的邊界不一樣,基本上只會判斷0跟0以上
    count = 0
    # 截圖x軸範圍
    screenshot_range = 0
    # 拖曳次數
    drag_count = 0
    # 從右點到左
    reverse_calculation = 1
    # 目前點在幾行
    which_row = 1
    return image_height, image_size, count, drag_along_the_x_axis, drag_count, filename, game_name_count, \
        image_height_range, reverse_calculation, which_row, x, y


# 開始執行程式
def start():
    # 創建 Google_api_function 的對象
    google_api = Google_api_function()

    # 使用對象調用 google_api_read 方法
    client = google_api.google_api_read()

    canvas_height, image_size, count, drag_along_the_x_axis, drag_count, filename, game_name_count, image_height_cut, \
        reverse_calculation, which_row, x, y = function_parameter()

    logging.basicConfig(level=logging.INFO)

    Commons = Commons_function()

    # 迴圈開始執行前先清乾淨csv
    Commons.clear_csv(filename, ['String'])

    # 建立網頁驅動
    driver = Commons.createwd(
        "https://apifront.qaz411.com/lx/S004/8.0.28/index.html?ps=qptest-wss.qaz411.com:8032&gameId=0&companyId=5001&theme=S004&agent=1100005&account=1100005_000&token=60710d1e4940453c5d2bafef5e6eb2a731f9958a164a31e35d8f266bd6a9701e8010fae8a484513bf70ec3cca05eff8c89b0c63db3229f05513b7f599d01e15bd06f887cbc69a74f9545d1b98bd596c59884e5656705608601abe8235132cbfe3a620d4395fbebcdb3143a4e6042baa38107a536feecabdf1ccc4b5d3b933d09&type=1&platform=1&languageType=en_us&sml=1&backgroundUrl=&title=lx&ckey=1080613_chessapilixin&lobbyType=0")

    # 獲取螢幕尺寸
    screen_width, screen_height = pyautogui.size()
    logging.info(f"螢幕尺寸：{screen_width} x {screen_height}")

    time.sleep(15)

    while True:
        canvas = driver.find_element(By.TAG_NAME, "canvas")
        actions = ActionChains(driver)

        time.sleep(15)

        location = canvas.location
        # 從右點到左不進入判斷
        if x >= drag_along_the_x_axis and not reverse_calculation > 1:
            drag_count += 1
            x = 13
            count = 0

        # 判斷拖曳次數
        for i in range(drag_count):
            Commons.window_dragging_logic(actions, canvas, drag_along_the_x_axis)
        # 第一張圖開始的位子計算方式不同
        if count == 0 or reverse_calculation >= 2:
            screenshot_range = image_size
            if count == 0:
                # 用來判斷視窗拖曳是否拉到底
                Commons.screenshot_image(420, 120, drag_count, drag_along_the_x_axis, location['x'] - 30,
                                         "drag_comparison")
                # 解析截圖的文字
                drag_comparison = Google_api_function().google_api_Image_text_analysis(client, 'drag_comparison' + str(
                    drag_count) + '.png')
                # 寫入csv
                test_write_csv(drag_comparison, 'drag_comparison' + str(drag_count) + '.csv', 'Click Before')

            if drag_count > 0:
                # 雙重保險比對一字串相似度比較
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
                    Commons.screenshot_image(canvas_height, image_height_cut, game_name_count, screenshot_range,
                                             screen_width - reverse_calculation * 275 - 20, 'original_image')

                    time.sleep(1)
                    # 模仿ai點擊功能
                    Commons.click_coordinates(screen_width - reverse_calculation * 275, y)

                    # 執行所有功能
                    actions.perform()

                    time.sleep(10)
                    # 點擊選項後的截圖
                    Commons.screenshot_image(canvas_height, image_height_cut, game_name_count, screenshot_range,
                                             screen_width - reverse_calculation * 275 - 20, 'compare_pictures')

                    time.sleep(3)
                    # 解析文字
                    original_image_text = Google_api_function().google_api_Image_text_analysis(client,
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
                            Commons.refresh(driver)
                            continue

                    else:
                        print("集合為空")

                        # 解析文字
                        compare_image_text = Google_api_function().google_api_Image_text_analysis(client,
                                                                                                  'compare_pictures' + str(
                                                                                                      game_name_count) + '.png')

                        game_name_count += 1

                        reverse_calculation += 1

                        Commons.refresh(driver)
                else:
                    # 網頁截圖流程的邏輯
                    count, game_name_count, x = _web_page_screenshot_evaluation_process(actions, canvas_height,
                                                                                        image_size,
                                                                                        client, count, driver, filename,
                                                                                        game_name_count,
                                                                                        image_height_cut,
                                                                                        screenshot_range, x, y, Commons)
            else:
                # 網頁截圖流程的邏輯
                count, game_name_count, x = _web_page_screenshot_evaluation_process(actions, canvas_height, image_size,
                                                                                    client, count, driver, filename,
                                                                                    game_name_count, image_height_cut,
                                                                                    screenshot_range, x, y, Commons)

        else:
            screenshot_range = 280
            # 網頁截圖流程的邏輯
            count, game_name_count, x = _web_page_screenshot_evaluation_process(actions, canvas_height, image_size,
                                                                                client, count, driver, filename,
                                                                                game_name_count, image_height_cut,
                                                                                screenshot_range, x, y, Commons)


# 網頁截圖遊戲流程的邏輯
def _web_page_screenshot_evaluation_process(actions, canvas_height, image_size, client, count, driver, filename,
                                            game_name_count, image_height_cut, screenshot_range, x, y, Commons):
    # 點選前截圖
    Commons.screenshot_image(canvas_height, image_height_cut, game_name_count, screenshot_range, x - 30,
                             'original_image')
    time.sleep(1)
    # 模仿ai點擊功能
    Commons.click_coordinates(x, y)
    # 執行所有功能
    actions.perform()
    time.sleep(10)
    # 點擊選項後的截圖
    Commons.screenshot_image(canvas_height, image_height_cut, game_name_count, screenshot_range, x - 30,
                             'compare_pictures')
    time.sleep(3)
    # 圖片文字解析
    original_image_text = Google_api_function().google_api_Image_text_analysis(client, 'original_image' + str(
        game_name_count) + '.png')
    compare_image_text = Google_api_function().google_api_Image_text_analysis(client, 'compare_pictures' + str(
        game_name_count) + '.png')
    # csv 判斷 功能是否正常
    check_game_clicking_to_csv(compare_image_text, filename, original_image_text)

    # 模仿ai點擊功能,隨便一個位子都可以,點掉教學
    Commons.click_coordinates(300, 300)

    time.sleep(1)

    Commons.screenshot_image(160, 100, game_name_count, 400,
                             700, 'string_check_title')

    x += canvas_size
    count += 1
    game_name_count += 1
    # 畫面從新整理
    Commons.refresh(driver)

    return count, game_name_count, x


# 計算兩個集合的字串相似度
def calculate_text_similarity(text_set1, text_set2):
    text1 = ' '.join(text_set1)
    text2 = ' '.join(text_set2)

    similarity = Levenshtein.ratio(text1, text2)

    return similarity


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


# 寫入csv
def write_csv(string, filename):
    data = [
        [string.strip()]
    ]

    with open(filename, 'a', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerows(data)


# 將遊戲功能是否正常寫入csv
def check_game_clicking_to_csv(compare_image_text, filename, original_image_text):
    if original_image_text != compare_image_text:
        write_csv(original_image_text, compare_image_text, "True", filename)
        print("兩個字串不相等")
    else:
        write_csv(original_image_text, compare_image_text, "False", filename)
        print("兩個字串相等")
