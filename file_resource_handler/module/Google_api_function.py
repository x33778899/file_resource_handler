import csv
import logging
import shutil
import time
import os
import pandas as pd
import pyautogui
import pyperclip
from Commons_function import Commons_function
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from Google_api_function import Google_api_function
import asyncio
import log
from pynput import mouse
from collections import deque

# 設定日誌
logger = log.setup_logger()


# 功能參數調整
def function_parameter():
    # 判斷遊戲點選功能是否正常
    game_feature_check = 'game_string_check.csv'
    # 翻譯對照表
    game_translation_reference_table = "game_translation_reference_table.csv"
    # 沒有得到前端圖片間距用猜的
    image_size = 285
    # y軸截圖座標
    image_height = 410
    # y軸截圖範圍
    image_height_range = 120
    # x軸等於13的原因是沒拖曳x=0可以點到你要的東西,拖曳後點選x會有上一次拖曳前的最後一個
    x = 13
    # y軸
    y = 300
    # drag_along_the_x_axis =image_size*6 代表我只點6張圖
    drag_along_the_x_axis = image_size * 6 + x
    # 遊戲名稱計算
    game_name_count = 0
    # 單純判斷因為count=0 要額外截圖,理論上只有0跟0以上的判斷
    count = 0
    # 截圖x軸範圍
    screenshot_range = 0
    # 拖曳次數
    drag_count = 0
    # 從右點到左
    reverse_calculation = 1
    # 目前點在幾行
    row = 1
    # 網頁
    url = "https://apifront.qaz411.com/lx/S004/8.0.39/index.html?ps=qptest-wss.qaz411.com:8031&gameId=0&companyId=5064&theme=S004&agent=1101285&account=1101285_8888&token=91d70a1a628e77c235fa4afffc578d2f61df20236cfa2d1d4ff70c881c0de296c1e9a53278d005be3057bc07bd9092923a6ee0ea7409bb53f89d792db81130e54e805c3a969525eb34feb505b1d0d4a1372bcf509d3f1c690e890b16177dfd43635f92c59e91abf6e1431e374efcbe036d0bd6a2777f8a988328f3fe551912e3&type=1&platform=1&languageType=zh_cn&sml=0&backgroundUrl=null&title=gfg"

    #     url ="https://apifront.qaz411.com/lx/S004/8.0.32/index.html?ps=qptest-wss.qaz411.com:8032&gameId=0&companyId=5001&theme=S004&agent=1100005&account=1100005_abc&token=5f192b3583c6ef9409cc66cd932a91cd50e7aebfe83ccfe79b3b3cfc5d8371b61ef19e0ff78bd28ba4fa9280886c829c3387e9172cf64885e4fc8a3bcf14a575ce0c2fc5bce67e555f1ef87dad81ddb6bbb08c1c2ac296dd7b426f5a4abb08886bae5373f20dd558503855c69f991d235159d42070bd074ddd20191b5618bae5&type=1&platform=1&languageType=zh_cn&sml=1&backgroundUrl=&title=lx"
    return image_height, image_size, count, drag_along_the_x_axis, drag_count, game_feature_check, \
        game_translation_reference_table, game_name_count, image_height_range, reverse_calculation, row, x, y, url


# 開始執行程式
def start(function):
    # 創建 Google_api_function 的對象
    google_api = Google_api_function()

    # 使用對象調用 google_api_read 方法
    client = google_api.google_api_read()
    # 設定參數
    image_height, image_size, count, drag_along_the_x_axis, drag_count, game_feature_check, game_translation_reference_table, \
        game_name_count, image_height_cut, reverse_calculation, row, x, y, url = function_parameter()

    Commons = Commons_function()

    #         迴圈開始執行前先清乾淨csv
    Commons.clear_csv(game_feature_check, ['Click Before', 'Click After', 'Comparison Result'])

    #     迴圈開始執行前先清乾淨csv
    Commons.clear_csv(game_translation_reference_table, ['game_directory', "string1", "string2", "string3", "string4"
        , "string5", "string6", "string7", "string8", "string9", "string10", "string11", "string12", "string13",
                                                         "string14"])
    # 切割字串獲取language_type
    language_type = get_language_type(url)

    # 建立網頁驅動
    driver = Commons.createwd(url)

    # 獲取螢幕尺寸
    screen_width, screen_height = pyautogui.size()

    print(f"螢幕尺寸：{screen_width} x {screen_height}")
    loop = asyncio.get_event_loop()

    while True:
        #         x = pyautogui.position().x
        #         time.sleep(1)
        #         print("x座標：", x)
        try:
            loop.run_until_complete(Commons.check_url_loading_status_main(driver, loop))
        except KeyboardInterrupt:
            break

        time.sleep(2)
        canvas = driver.find_element(By.TAG_NAME, "canvas")
        actions = ActionChains(driver)

        location = canvas.location
        # 從右點到左不進入判斷
        if x >= drag_along_the_x_axis and not reverse_calculation > 1:
            drag_count += 1
            x = 13
            count = 0

        # 判斷拖曳次數
        for i in range(drag_count):
            Commons.window_dragging_logic(actions, canvas, drag_along_the_x_axis, i, drag_count)
        # 第一張圖開始的位子計算方式不同
        if count == 0 or reverse_calculation >= 2:
            # 解析截圖的文字
            #                 drag_comparison = Google_api_function().google_api_Image_text_analysis(client, 'drag_comparison' + str(
            #                     drag_count) + '.png')
            #                 # 寫入csv
            #                 test_write_csv(drag_comparison, 'drag_comparison' + str(drag_count) + '.csv', 'Click Before')

            if drag_count > 0:
                # 用來判斷視窗拖曳是否拉到底
                Commons.crop_image("drag_comparison" + str(drag_count) + ".png", 1700, 400, 220, 150)

                drag_comparison = Google_api_function().google_api_Image_text_analysis(client, 'drag_comparison' + str(
                    drag_count) + '.png')
                # original_image_text = Google_api_function().google_api_Image_text_analysis(client,
                #                                                                            'drag_comparison' + str(
                #                                                                                drag_count) + '.png')

                # 三重保險比對一字串相似度比較
                # text_similarity = calculate_text_similarity(
                #     read_csv_compare_similarity('drag_comparison' + str(drag_count) + '.csv', "Click Before"),
                #     read_csv_compare_similarity('drag_comparison' + str(drag_count - 1) + '.csv', "Click Before"))
                #                 # 三重保險比對二字串交集比對,預防有辨識不清楚,google辨識文字並非100%會用空格分割字串
                #                 intersection_set = (
                #                         read_csv_compare_intersection('drag_comparison' + str(drag_count) + '.csv', "Click Before") &
                #                         read_csv_compare_intersection('drag_comparison' + str(drag_count - 1) + '.csv', "Click Before"))
                # 三重保險比對三保險圖片相似度比對
                #                 image_similarity = Commons.image_comparison('drag_comparison' + str(drag_count) + '.png',
                #                                                             'drag_comparison' + str(drag_count - 1) + '.png')
                #                 logger.debug(image_similarity)
                # text_similarity 跟image_similarity判斷值可以更多資料調整相似度可以在多試幾次後修正
                if drag_comparison == "":
                    #                 if text_similarity > 0.5 or len(intersection_set) > 0 or image_similarity > 0.3:
                    # 判斷是不是拖曳到底了
                    # 拉到底從左邊開始點不準確從右邊開始點到左邊
                    # 相似度可以在多試幾次後修正
                    # 點選前截圖
                    Commons.screenshot_image(image_height, image_height_cut, image_size,
                                             screen_width - reverse_calculation * 275 - 20, 'original_image' + str
                                             (game_name_count) + ".png")

                    time.sleep(1)

                    # 解析文字
                    original_image_text = Google_api_function().google_api_Image_text_analysis(client,
                                                                                               'original_image' + str
                                                                                               (game_name_count) + ".png")

                    time.sleep(1)
                    search_set = set([original_image_text])

                    # 交集比對計算如果有一樣的代表可以換第二行了
                    game_set = read_csv_compare_similarity(game_feature_check, "Click Before")

                    intersection_set = game_set.intersection(search_set)

                    if len(intersection_set) != 0:  # 如果集合不為空
                        y += 330
                        drag_count = 0
                        image_height += 330
                        reverse_calculation = 1
                        # 本來就點在第二行了可以中斷了
                        if row == 2:
                            print("自動化測試結束")
                            break
                        else:
                            print("開始點選第二行")
                            row = 2
                            Commons.refresh(driver)
                            continue

                    else:
                        print("集合為空")
                        time.sleep(1)

                        # 模仿ai點擊功能
                        Commons.click_coordinates(screen_width - reverse_calculation * 275, y)

                        loop.run_until_complete(Commons.check_url_loading_status_main(driver, loop))
                        time.sleep(5)
                        # 點擊選項後的截圖
                        Commons.screenshot_image(image_height, image_height_cut, image_size,
                                                 screen_width - reverse_calculation * 275 - 20,
                                                 'compare_image' + str(game_name_count) + ".png")

                        time.sleep(3)

                        #                     # 寫入csv 用來判斷是不是重複了可以換行了
                        #                     test_write_csv(original_image_text, 'identify_duplicate_data.csv', 'data')

                        logging.info(intersection_set)

                        # 解析文字
                        compare_image_text = Google_api_function().google_api_Image_text_analysis(client,
                                                                                                  'compare_image' + str(
                                                                                                      game_name_count) + '.png')

                        # csv 判斷 功能是否正常
                        check_game_clicking_to_csv(compare_image_text, game_feature_check, original_image_text)

                        # 自動化測試的模式選擇
                        automated_test_mode(Commons, client, driver, function, game_name_count,
                                            game_translation_reference_table, language_type, original_image_text)

                        game_name_count += 1

                        reverse_calculation += 1

                        Commons.refresh(driver)
                else:
                    # 網頁截圖流程的邏輯
                    count, game_name_count, x = _web_page_screenshot_evaluation_process(actions, image_height,
                                                                                        image_size,
                                                                                        client, count, driver,
                                                                                        game_feature_check,
                                                                                        game_translation_reference_table,
                                                                                        game_name_count,
                                                                                        image_height_cut,
                                                                                        x, y, Commons,
                                                                                        language_type, loop, function)
            else:
                # 網頁截圖流程的邏輯
                count, game_name_count, x = _web_page_screenshot_evaluation_process(actions, image_height,
                                                                                    image_size,
                                                                                    client, count, driver,
                                                                                    game_feature_check,
                                                                                    game_translation_reference_table,
                                                                                    game_name_count,
                                                                                    image_height_cut,
                                                                                    x, y, Commons,
                                                                                    language_type, loop, function)

        else:
            # 網頁截圖流程的邏輯
            count, game_name_count, x = _web_page_screenshot_evaluation_process(actions, image_height,
                                                                                image_size,
                                                                                client, count, driver,
                                                                                game_feature_check,
                                                                                game_translation_reference_table,
                                                                                game_name_count,
                                                                                image_height_cut,
                                                                                x, y, Commons,
                                                                                language_type, loop, function)
    loop.close()


def automated_test_mode(Commons, client, driver, function, game_name_count, game_translation_reference_table,
                        language_type, original_image_text):
    if function == 2:
        game_mode_item = Commons.read_json_config(original_image_text, language_type,
                                                  'original_image' + str(game_name_count) + ".png",
                                                  client)
        logging.info(game_mode_item)

        game_mode = game_mode_item["mode"]

        game_name = game_mode_item["game_name"]

        game_directory = game_mode_item["game_directory"]

        time.sleep(2)

        _select_mode(Commons, client, driver, game_mode, game_directory, game_name_count,
                     game_translation_reference_table, game_name)


# 獲取languageType
def get_language_type(url):
    language_type_prefix = url.split("languageType=")[1]
    language_type = language_type_prefix.split("&")[0]
    return language_type


# 網頁截圖遊戲流程的邏輯
def _web_page_screenshot_evaluation_process(actions, image_height, image_size, client, count, driver,
                                            game_feature_check, game_translation_reference_table, game_name_count,
                                            image_height_range, x, y, Commons, language_type, loop
                                            , function):
    # 點選前截圖
    Commons.screenshot_image(image_height, image_height_range, image_size, x - 13,
                             'original_image' + str(game_name_count) + ".png")

    # 圖片文字解析
    original_image_text = Google_api_function().google_api_Image_text_analysis(client, 'original_image' + str(
        game_name_count) + ".png")
    # 預防字串間隔過長輩辨識出換行符號,把換行符號清掉
    original_image_text_replace = original_image_text.replace("\n", "")  # 清除換行符號

    if original_image_text_replace == "":
        x += image_size
        count += 1
        game_name_count += 1
        Commons.refresh(driver)
        time.sleep(2)

    else:

        time.sleep(3)
        # 模仿ai點擊功能
        Commons.click_coordinates(x, y)

        loop.run_until_complete(Commons.check_url_loading_status_main(driver, loop))
        time.sleep(3)
        # 點擊選項後的截圖
        Commons.screenshot_image(image_height, image_height_range, image_size, x - 13,
                                 'compare_image' + str(game_name_count) + ".png")

        time.sleep(2)

        compare_image_text = Google_api_function().google_api_Image_text_analysis(client, 'compare_image' + str(
            game_name_count) + '.png')
        # csv 判斷 功能是否正常
        check_game_clicking_to_csv(compare_image_text, game_feature_check, original_image_text_replace)

        #     test_csv = read_csv(game_name_count)
        #     logging.info(test_csv)
        # 自動化測試的模式選擇
        automated_test_mode(Commons, client, driver, function, game_name_count, game_translation_reference_table,
                            language_type, original_image_text)

        x += image_size
        count += 1
        game_name_count += 1
        # 畫面從新整理
        Commons.refresh(driver)

    return count, game_name_count, x


# 點選樣式
def _select_mode(Commons, client, driver, game_mode, game_directory, game_name_count, game_translation_reference_table,
                 game_name):
    if game_mode == "1":
        # 點擊模式 1
        _click_mode_one(Commons, client, driver, game_directory, game_name_count, game_translation_reference_table,
                        game_name)
    elif game_mode == "2":
        # 點擊模式 2
        _click_mode_two(Commons, client, driver, game_directory, game_name_count, game_translation_reference_table,
                        game_name)
    elif game_mode == "3":
        # 點擊模式 3
        _click_mode_three(Commons, client, driver, game_directory, game_name_count, game_translation_reference_table,
                          game_name)


# 點選模式1
def _click_mode_one(Commons, client, driver, game_directory, game_name_count, game_translation_reference_table,
                    game_name):
    # 模仿ai點擊功能,隨便一個位子都可以,點掉教學
    Commons.click_coordinates(300, 300)

    time.sleep(3)

    #     # 遊戲名稱位置
    #     Commons.screenshot_image(100, 140, 420,
    #                              750, 'string_title' + str(game_name_count) + ".png")

    #     截圖全螢幕
    click = False
    # 遊戲按鈕檢查,預防加載速度影響檢查兩遍
    for i in range(2):
        best_image_path, check_judgment = game_button_check(Commons, driver, game_directory,
                                                            game_name_count, i, click, "mode_1/options_language/")
        if check_judgment:
            break
    # 獲取xy軸
    x_diff, y_diff = Commons.get_coordinates(best_image_path,
                                             "screenshot_full_screen" + str(game_name_count) + ".png")
    time.sleep(2)
    # 點選項
    Commons.click_coordinates(x_diff + 50, y_diff + 150)

    time.sleep(3)
    click = False
    # 遊戲按鈕檢查,預防加載速度影響檢查兩遍
    for i in range(2):
        best_image_path, check_judgment = game_button_check(Commons, driver, game_directory,
                                                            game_name_count, i, click, "mode_1/information/")
        if check_judgment:
            break
    # 獲取xy軸
    x_diff, y_diff = Commons.get_coordinates(best_image_path,
                                             "screenshot_full_screen" + str(game_name_count) + ".png")
    # 點選項
    Commons.click_coordinates(x_diff + 50, y_diff + 150)

    # 等待出現?選單
    time.sleep(3)
    # 遊戲說明位置
    Commons.screenshot_image(180, 90, 420,
                             750, 'string_check_a' + str(game_name_count) + ".png")
    # 賠率表位置遊戲規則位置
    Commons.screenshot_image(270, 270, 300,
                             200, 'string_check_b' + str(game_name_count) + ".png")

    #     Commons.screenshot_image(380, 90, 300,
    #                              200, 'string_check_c' + str(game_name_count) + ".png")
    # 點選項
    Commons.click_coordinates(230 + 50, 380 + 50)
    time.sleep(3)

    #     # 遊戲規則翻譯位置
    #     Commons.screenshot_image(340, 580, 850,
    #                              560, 'string_check_c' + str(game_name_count) + ".png")

    result = deque()
    result.append(game_directory)
    result.append(game_name)

    time.sleep(3)

    #     string_title = Google_api_function().google_api_Image_text_analysis(client, 'string_title' + str(
    #         game_name_count) + '.png')
    column_two = Google_api_function().google_api_Image_text_analysis(client, 'string_check_a' + str(
        game_name_count) + '.png')
    column_three = Google_api_function().google_api_Image_text_analysis(client, 'string_check_b' + str(
        game_name_count) + '.png')
    #     column_four = Google_api_function().google_api_Image_text_analysis(client, 'string_check_c' + str(
    #         game_name_count) + '.png')
    #     result.append(string_title)
    result.append(column_two)
    result.append(column_three)

    drag_select_text(580, 350, 1000, 1000, result)

    result_list = list(result)
    write_csv(game_translation_reference_table, [result_list])


# 預防加載問題影響到尋找按鈕,最多檢查兩遍
def game_button_check(Commons, driver, game_directory, game_name_count, i, click, parent_directory):
    # 截圖全螢幕
    driver.save_screenshot("screenshot_full_screen" + str(game_name_count) + ".png")
    time.sleep(2)
    # 自己找按鈕點擊,尋找?按鈕
    best_image_path = Commons.find_best_match("screenshot_full_screen" + str(game_name_count) + ".png",
                                              parent_directory)
    if game_directory in best_image_path:
        print("圖片正確")
    else:
        if i == 0:
            print("圖片有問題")
        else:
            click = True
            logger.warning(parent_directory + "    " + game_directory + ":   圖片有問題")
    return best_image_path, click


# 點選模式2
def _click_mode_two(Commons, client, driver, game_directory, game_name_count, game_translation_reference_table,
                    game_name):
    x_diff, y_diff = _check_read_status(Commons, driver,
                                        "screenshot_full_screen" + str(game_name_count) + ".png", "mode_2"
                                                                                                  "/game/")

    #     # 為了預防加載速度過慢,重複判點選按鈕,
    #     while True:
    #         time.sleep(1)
    #         if similarity < 0.01:
    #             similarity, x_diff, y_diff = _check_read_status(Commons, driver,
    #                                                             "screenshot_full_screen" + str(game_name_count) + ".png",
    #                                                             "mode_2"
    #                                                             "/game/")
    #         else:
    #             break

    # 遊戲名稱位置
    Commons.screenshot_image(100, 140, 420,
                             750, 'string_title' + str(game_name_count) + ".png")
    click = False
    # 遊戲按鈕檢查,預防加載速度影響檢查兩遍
    for i in range(2):
        best_image_path, check_judgment = game_button_check(Commons, driver, game_directory,
                                                            game_name_count, i, click, "mode_2/information/")
        if check_judgment:
            break
    # # 截圖全螢幕
    # driver.save_screenshot("screenshot_full_screen" + str(game_name_count) + ".png")
    #
    # time.sleep(3)
    # # 自己找按鈕點擊,尋找?按鈕
    # best_image_path = Commons.find_best_match("screenshot_full_screen" + str(game_name_count) + ".png", "mode_2"
    #                                                                                                     "/information/")
    #
    # if game_directory in best_image_path:
    #     print("圖片正確")
    # elif "common" in best_image_path:
    #     print("圖片正確")
    # else:
    #     logger.warning("mode_2/information/    " + game_directory + ":   圖片有問題")
    # 獲取xy軸
    x_diff, y_diff = Commons.get_coordinates(best_image_path,
                                             "screenshot_full_screen" + str(game_name_count) + ".png")
    # 點選項
    Commons.click_coordinates(x_diff + 50, y_diff + 150)

    # 等待出現?選單
    time.sleep(3)
    # 玩法規則位置
    Commons.screenshot_image(220, 90, 420,
                             750, 'string_check_a' + str(game_name_count) + ".png")
    # 所有標頭位置 的圖片寬度
    header_length = 1290
    # 所有標頭位置
    Commons.screenshot_image(320, 90, header_length,
                             310, 'string_check_b' + str(game_name_count) + ".png")
    # 解析所有標頭文字
    text = Google_api_function().google_api_Image_text_analysis(client,
                                                                "string_check_b" + str(game_name_count) + ".png")
    # 根據標頭裡的換行符號切割
    lines = text.split("\n")
    # 得到標頭總長度/字串切割長度從而得到點選次數跟要點的座標
    length_from_click = header_length / len(lines)

    #     # 排行說明位置
    #     Commons.screenshot_image(320, 90, 250,
    #                              650, 'string_check_c' + str(game_name_count) + ".png")
    #     # 牌型大小位置
    #     Commons.screenshot_image(320, 90, 250,
    #                              990, 'string_check_d' + str(game_name_count) + ".png")
    #     # 牌型倍數位置
    #     Commons.screenshot_image(320, 90, 250,
    #                              1330, 'string_check_e' + str(game_name_count) + ".png")
    result = deque()
    result.append(game_directory)
    result.append(game_name)
    # 邏輯為依靠google 解析圖片的功能,google解析圖片文字有空格會自動補上換行符號
    # 我有我切割換行符號可以得到長度,再用截圖的寬度去除長度我可以得到要點幾次以及間距
    # 因為不確定是另存圖片還是複製文字,所以兩件事都做,判斷邏輯未如果圖片存在解析圖片文字寫入
    for i in range(len(lines)):
        Commons.click_coordinates(length_from_click * (i + 1) + 50, 320 + 50)
        drag_select_text(290, 450, 1300, 1200, result)
        time.sleep(4)
        tilte_image = save_image_by_coordinates(350, 500,
                                                "string_check_" + str(game_name_count) + "_" + str(i) + ".png")
        # 如果圖片才在解析圖片寫入文字
        if check_image_exists(tilte_image):
            image_text = Google_api_function().google_api_Image_text_analysis(client,
                                                                              "string_check_" + str(game_name_count)
                                                                              + "_" + str(i) + ".png")
            result.append(image_text)
        time.sleep(4)
        # 點掉x不然點選座標會改變
        Commons.click_coordinates(1900, 999)
        time.sleep(4)

    time.sleep(5)

    result_list = list(result)
    write_csv(game_translation_reference_table, [result_list])

    #     string_title = Google_api_function().google_api_Image_text_analysis(client, 'string_check_title' + str(
    #         game_name_count) + '.png')
    #     column_two = Google_api_function().google_api_Image_text_analysis(client, 'string_check_a' + str(
    #         game_name_count) + '.png')
    #     column_three = Google_api_function().google_api_Image_text_analysis(client, 'string_check_b' + str(
    #         game_name_count) + '.png')
    #     column_four = Google_api_function().google_api_Image_text_analysis(client, 'string_check_c' + str(
    #         game_name_count) + '.png')
    #     column_five = Google_api_function().google_api_Image_text_analysis(client, 'string_check_d' + str(
    #         game_name_count) + '.png')
    #     column_six = Google_api_function().google_api_Image_text_analysis(client, 'string_check_e' + str(
    #         game_name_count) + '.png')
    #     column_seven = Google_api_function().google_api_Image_text_analysis(client, 'string_check_e' + str(
    #         game_name_count) + '.png')
    #     write_csv(game_translation_reference_table, string_title, column_two,   column_three,column_four,column_five,column_six,column_seven)


# 點選模式3
def _click_mode_three(Commons, client, driver, game_directory, game_name_count, game_translation_reference_table,
                      game_name):
    time.sleep(9)

    x_diff, y_diff = _check_read_status(Commons, driver,
                                        "screenshot_full_screen" + str(game_name_count) + ".png",
                                        "mode_3/game/")

    # 為了預防加載速度過慢,重複判點選按鈕
    #     while True:
    #         time.sleep(1)
    #         if similarity < 0.01:
    #             similarity, x_diff, y_diff = _check_read_status(Commons, driver,
    #                                                             "screenshot_full_screen" + str(game_name_count) + ".png",
    #                                                             "mode_3"
    #                                                             "/game/")
    #         else:
    #             break

    # 點選項
    Commons.click_coordinates(x_diff + 50, y_diff + 150)

    # 等待出現初級場加載結束
    time.sleep(3)
    # 點掉教學
    Commons.click_coordinates(x_diff + 50, y_diff + 150)
    time.sleep(3)

    # driver.save_screenshot("screenshot_full_screen" + str(game_name_count) + ".png")
    #
    # best_image_path = Commons.find_best_match("screenshot_full_screen" + str(game_name_count) + ".png",
    #                                           "mode_3/options_language/")
    #
    # if game_directory in best_image_path:
    #     print("圖片正確")
    # elif "common" in best_image_path:
    #     print("圖片正確")
    # else:
    #     logger.warning("mode_3/options_language/    " + game_directory + ":   圖片有問題")

    click = False
    # 遊戲按鈕檢查,預防加載速度影響檢查兩遍
    for i in range(2):
        best_image_path, check_judgment = game_button_check(Commons, driver, game_directory,
                                                            game_name_count, i, click, "mode_3/options_language/")
        if check_judgment:
            break

    # 獲取xy軸
    x_diff, y_diff = Commons.get_coordinates(best_image_path,
                                             "screenshot_full_screen" + str(game_name_count) + ".png")

    # 點選項
    Commons.click_coordinates(x_diff + 50, y_diff + 150)

    time.sleep(3)

    click = False
    # 遊戲按鈕檢查,預防加載速度影響檢查兩遍
    for i in range(2):
        best_image_path, check_judgment = game_button_check(Commons, driver, game_directory,
                                                            game_name_count, i, click, "mode_3/information/")
        if check_judgment:
            break

    # driver.save_screenshot("screenshot_full_screen" + str(game_name_count) + ".png")
    #
    # best_image_path = Commons.find_best_match("screenshot_full_screen" + str(game_name_count) + ".png",
    #                                           "mode_3/information/")
    #
    # if game_directory in best_image_path:
    #     print("圖片正確")
    # elif "common" in best_image_path:
    #     print("圖片正確")
    # else:
    #     logger.warning("mode_3/information/    " + game_directory + ":   圖片有問題")

    # 獲取xy軸跟相似度
    x_diff, y_diff = Commons.get_coordinates(best_image_path,
                                             "screenshot_full_screen" + str(game_name_count) + ".png")

    # 點選項
    Commons.click_coordinates(x_diff + 50, y_diff + 150)

    time.sleep(4)

    # 魚種賠率位置
    Commons.screenshot_image(220, 600, 250,
                             150, 'string_check_a' + str(game_name_count) + ".png")
    #     # 特色遊戲位置
    #     Commons.screenshot_image(380, 90, 250,
    #                              150, 'string_check_b' + str(game_name_count) + ".png")
    #     # 介面引導位置
    #     Commons.screenshot_image(530, 90, 250,
    #                              150, 'string_check_c' + str(game_name_count) + ".png")

    Commons.click_coordinates(x_diff + 50, y_diff + 150)

    # 點選特色遊戲
    Commons.click_coordinates(150 + 50, 380)

    time.sleep(2)
    # 頁數位置
    Commons.screenshot_image(880, 80, 60,
                             1110, 'string_check_page' + str(game_name_count) + ".png")

    time.sleep(2)

    #     number_click = Google_api_function().google_api_Image_text_analysis(client, 'string_check_page' + str(
    #         game_name_count) + '.png')
    number_click = ""
    if number_click == "" or not number_click.isdigit():
        number_click = 5

    result = deque()
    result.append(game_directory)
    result.append(game_name)
    for i in range(int(number_click)):
        # 特色遊戲翻譯位置
        Commons.screenshot_image(280, 500, 1280,
                                 470, 'string_check_b_' + str(game_name_count) + "_" + str(i) + ".png")

        text = Google_api_function().google_api_Image_text_analysis(client, 'string_check_b_' + str(
            game_name_count) + "_" + str(i) + ".png")

        result.append(text)  # 將 text 的字串添加到集合中
        # 點選下一頁
        Commons.click_coordinates(1280, 900)

        time.sleep(2)

    # # 點選項
    # Commons.click_coordinates(230 + 50, 380 + 50)
    # time.sleep(1)
    # # 遊戲規則翻譯位置
    # Commons.screenshot_image(340, 580, 850,
    #                          560, 'string_check_d'+str(game_name_count)+".png")
    time.sleep(5)

    #     string_title = Google_api_function().google_api_Image_text_analysis(client, 'string_check_title' + str(
    #         game_name_count) + '.png')
    #     column_two = Google_api_function().google_api_Image_text_analysis(client, 'string_check_a' + str(
    #         game_name_count) + '.png')
    #     column_three = Google_api_function().google_api_Image_text_analysis(client, 'string_check_b' + str(
    #         game_name_count) + '.png')
    #     column_four = Google_api_function().google_api_Image_text_analysis(client, 'string_check_c' + str(
    #         game_name_count) + '.png')
    result_list = list(result)
    write_csv(game_translation_reference_table, [result_list])


#     write_csv(game_translation_reference_table, string_title, column_two, column_three, column_four, result_list)
# 檢查圖片是否存在
def check_image_exists(file_path):
    return os.path.exists(file_path) and os.path.isfile(file_path)


# 檢查讀取狀態,依靠截圖尋找加載好了以後才會出現的文字
def _check_read_status(Commons, driver, compare_image, image_directory):
    driver.save_screenshot(compare_image)
    best_image_path = Commons.find_best_match(compare_image,
                                              image_directory)
    # 獲取xy軸跟相似度
    x_diff, y_diff = Commons.get_coordinates(best_image_path, compare_image)
    time.sleep(2)
    return x_diff, y_diff


# 複製文字的功能
def drag_select_text(start_x_axis, start_y_axis, copy_x_axis, copy_y_axis, result_list):
    # 移動鼠標標記到指定位置
    pyautogui.moveTo(start_x_axis, start_y_axis, duration=0.5)
    time.sleep(1)
    # 模擬滾輪往上滾動
    pyautogui.scroll(1000)

    time.sleep(1)

    # 模擬鼠標點擊並按住左鍵
    pyautogui.mouseDown()

    # 移動鼠標以選擇文本區域
    pyautogui.move(copy_x_axis, 0, duration=0.5)  # 向右移動1000像素
    pyautogui.move(0, copy_y_axis, duration=0.5)  # 向下移動1000像素

    # 釋放鼠標左鍵
    pyautogui.mouseUp()

    # 模擬按下複製快捷鍵
    pyautogui.hotkey('ctrl', 'c')  # 或者使用 pyautogui.hotkey('cmd', 'c')（适用于 macOS）

    # 從剪貼板中獲取複製的數據
    copied_data = pyperclip.paste()
    # 空字串不寫入
    if copied_data != "":
        result_list.append(copied_data)

    return result_list


# 右鍵另存圖片的功能
def save_image_by_coordinates(start_x_axis, start_y_axis, file_name):
    # 模擬滾輪往上滾動
    pyautogui.scroll(2000)
    # 移動鼠標到指定的坐標位置
    pyautogui.moveTo(start_x_axis, start_y_axis, duration=0.5)

    # 模擬鼠標右鍵點擊
    pyautogui.click(button='right')

    # 假設在右鍵菜單中的"另存圖片"選項位置為相對於右鍵點擊位置的偏移量
    save_image_x_offset = 100
    save_image_y_offset = 50

    # 移動鼠標到另存圖片選項的位置
    pyautogui.move(save_image_x_offset, save_image_y_offset, duration=0.5)

    # 模擬鼠標左鍵點擊
    pyautogui.click()

    # 構建保存路徑
    save_path = "D:\\work_space\\python_ws\\Airtest_automated_testing\\" + file_name

    # 刪除同名檔案預防圖片已存在（如果存在）
    if os.path.exists(save_path):
        os.remove(save_path)

    # 將保存路徑複製到剪貼板
    pyperclip.copy(save_path)

    # 等待保存圖片窗口打開（根據實際情況調整等待時間）
    pyautogui.sleep(1)

    # 模擬按下快捷鍵Ctrl+V（黏貼路徑）
    pyautogui.hotkey('ctrl', 'v')

    # 模擬按下回車鍵（確認保存)
    pyautogui.press('enter')

    # 預防複製文字的時候複製不到字串把它清掉
    pyperclip.copy('')

    return file_name


# 計算兩個集合的字串相似度
def calculate_text_similarity(text_set1, text_set2):
    text1 = ' '.join(text_set1)
    text2 = ' '.join(text_set2)

    similarity = Levenshtein.ratio(text1, text2)

    return similarity


# 測試讀取資料
def read_csv(number):
    df = pd.read_csv("image.csv", encoding='utf-8-sig', dtype=str)
    click_before_column = df["Click Before"]
    data = click_before_column.iloc[number]
    return data


# 第一層保險讀取csv比對,判斷是否拉到底,辨識文字相似度
def read_csv_compare_similarity(file_path, header):
    result_set = set()
    df = pd.read_csv(file_path, encoding='utf-8-sig', dtype=str)
    title = df[header].astype(str)  # 将列数据转换为字符串类型

    for data in title:
        if pd.notnull(data):  # 确保数据不为空
            result_set.add(data.strip())  # 去除字符串前后空格并添加到集合中
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


# def write_csv(filename, *data_list):
#     data = [
#         [s1, s2, s3, s4, s5, s6, s7, s8],
#     ]
# 寫入csv
def write_csv(filename, data_list):
    # 计算集合中最长的长度
    max_length = max(len(data) for data in data_list)

    # 创建一个嵌套列表，每个子列表对应一个集合的数据
    nested_data = []
    for data in data_list:
        nested_data.append(data + [''] * (max_length - len(data)))

    with open(filename, 'a', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerows(nested_data)


# 將遊戲功能是否正常寫入csv
def check_game_clicking_to_csv(compare_image_text, filename, original_image_text):
    if original_image_text != compare_image_text:
        result = [original_image_text, compare_image_text, "True"]  # 創建一個空的集合
        result_list = list(result)
        write_csv(filename, [result_list])
        print("兩個字串不相等")
    else:
        result = [original_image_text, compare_image_text, "False"]  # 創建一個空的集合
        result_list = list(result)
        write_csv(filename, [result_list])
        print("兩個字串相等")
