
import pyautogui
import time
import keyboard
import win32api, win32con
from datetime import datetime, timedelta
import datetime
import os
import sys
import random
from pyautogui import ImageNotFoundException

pyautogui.FAILSAFE = False



def click(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

time.sleep(3)

path = os.path.abspath('')

size_blum = pyautogui.getActiveWindow()

options_ = open(f'{path}/options.txt', 'r')
options_for_all = options_.read()
number_games = int(list(options_for_all.split(','))[0])
if number_games > 15:
    print("Колл. игр должно быть меньше 15")
    sys.exit(1)



profit_game = int(list(options_for_all.split(','))[1])
if profit_game > 0 and profit_game < 101:
    profit_game_1 = 101-profit_game
    num_point_prof = 0.003
    profit_game_last = profit_game_1 * num_point_prof
else:
    print("Профит дожен быть меньше 100 и больше 0")
    sys.exit(1)

options_ = open(f'{path}/options.txt', 'r')
time_sleep_start = int(list(options_for_all.split(','))[2])
time_sleep_end = int(list(options_for_all.split(','))[3])
if time_sleep_start < 1:
    print("Начальнео время между играми должно быть больше 0")
    sys.exit(1)


played_games = 0

while keyboard.is_pressed('q') == False:
    try:
        click(size_blum.left + int((size_blum.width / 2)), size_blum.top + int(size_blum.height / 2))
        time.sleep(1)
        pyautogui.vscroll(-533)
        time.sleep(1)
        template = pyautogui.locateOnScreen(f'{path}/play_first.jpg', region=(size_blum.left, size_blum.top, size_blum.width, size_blum.height), grayscale=True, confidence=0.8)
        object1 = pyautogui.center(template)
        x, y = object1
        for _ in range(1):
            pyautogui.click(x, y)
        time_start = datetime.datetime.now()
        time_add = 0
        break
    except:
        time.sleep(1)

while keyboard.is_pressed('q') == False:
    try:
        template1 = pyautogui.locateOnScreen(f'{path}/play.jpg', region=(
        size_blum.left, size_blum.top, size_blum.width, size_blum.height), grayscale=True, confidence=0.8)
        object1 = pyautogui.center(template1)
        x, y = object1
        for _ in range(1):
            pyautogui.click(x, y)
        time.sleep(0.05)
        time_start = datetime.datetime.now()
        time_add = 0
    except:
        time.sleep(1)
    while keyboard.is_pressed('q') == False:
        flag = 0
        pic = pyautogui.screenshot(region=(size_blum.left, size_blum.top, size_blum.width, size_blum.height))
        width, height = pic.size
        for x in range(0, width, 4):
            for y in range(0, height, 4):
                r, g, b = pic.getpixel((x, y))
                if (b == 232 and r == 130 and g == 220) or (b == 0 and r == 205 and g == 220) or (
                        b == 186 and r == 226 and g == 255):
                    flag = 1
                    click(x + size_blum.left, y + size_blum.top)
                    time.sleep(profit_game_last)
                    if (b == 232 and r == 130 and g == 220):
                        time_add += 1
            if flag == 1:
                break
        time_start_end = datetime.datetime.now()
        if time_start_end >= (time_start + timedelta(seconds=32 + (time_add * 3))):
            played_games += 1
            time.sleep(random.uniform(time_sleep_start, time_sleep_end))
            break
    if number_games == played_games:
        break





