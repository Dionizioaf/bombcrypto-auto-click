"""
coding: utf-8
Fork of https://github.com/mpcabete/bombcrypto-bot
"""

import os
import platform
OSWin = True if platform.system() == "Windows" else False

from cv2 import cv2
from colorama import Fore
import datetime as dt
import requests
from captcha.solveCaptcha import solveCaptcha

from os import listdir
from random import random

if OSWin == True:
    import pygetwindow
import numpy as np
import mss
import pyautogui
import time
import sys

import yaml

import logging
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

welcome = """
-------------------------------------------------------------------
Fork of https://github.com/mpcabete/bombcrypto-bot

>>---> Press ctrl + c to kill the bot.
>>---> Some configs can be fount in the config.yaml file.
-------------------------------------------------------------------
"""

print(welcome)

# Load config file
stream = open("config.yaml", 'r')
config = yaml.safe_load(stream)

# Config headers
config_threshold = config['threshold']
multiaccount_config = config['multiaccount']

# HELPER
current_account = 'brave'

# First config of pyautohui
pyautogui.PAUSE = config['time_intervals']['interval_between_moviments']
pyautogui.FAILSAFE = False

# Initial definitions
send_to_work_clicks = 0
login_attempts = 0
new_map_available = False

#connection
connectionConfig = config['connection']
proxyEnabled = connectionConfig['proxyEnabled']
proxyServer = {
    'http': connectionConfig['proxyServer'],
    'https': connectionConfig['proxyServer']
}

# Wallet Ids
config_accounts = config['accounts']
Walleturl = config_accounts['Walleturl']
WalletStatus = config_accounts['WalletEnable']
MultiAccount = config_accounts['multiAccount'] if OSWin == True else False
Accounts = config_accounts['Account']



""" 
=================================
Colored print functions
=================================
"""


def inform(msg: str, msg_type: str):
    # Select color
    colors = {
        "log": Fore.LIGHTWHITE_EX,
        "warn": Fore.LIGHTYELLOW_EX,
        "error": Fore.LIGHTRED_EX,
        "info": Fore.LIGHTBLUE_EX,
        "success": Fore.LIGHTGREEN_EX,
        "emphasis": Fore.LIGHTMAGENTA_EX,
    }
    # print
    print(colors[msg_type] + '(' + dt.datetime.now().strftime('%H:%M:%S') + ') ' + msg)
    if msg_type != "log" and msg_type !=  "info":
        send_wallet_info(current_account,'log',msg, msg_type)
    # forces to ???flush??? terminal buffer
    sys.stdout.flush()


"""
---------------------
App sync Data
---------------------
"""

def send_wallet_info(browser,module,content,extra = ''):
    try:
        AccountIndex = -1
        for index, element in enumerate(Accounts):
            if element["Browser"] == browser:
                AccountIndex = index
        
        contentPut = {
            "metodo": module,
            "valor": content,
            "kind": extra
        }

        
        if (proxyEnabled == True):
            requests.put(Walleturl + "api/bombbot", proxies=proxyServer, auth=(Accounts[AccountIndex]['name'], Accounts[AccountIndex]['id']), data = contentPut)
        else:
            requests.put(Walleturl + "api/bombbot", auth=(Accounts[AccountIndex]['name'], Accounts[AccountIndex]['id']), data = contentPut)
    except Exception as e:
	    print("ERROR : "+str(e))

def send_wallet_image(browser,module,content):
    try:
        AccountIndex = -1
        for index, element in enumerate(Accounts):
            if element["Browser"] == browser:
                AccountIndex = index
        payload={}
        files=[
        ('multipleFiles',(module + '.png',open(content,'rb'),'image/png'))
        ]
        if (proxyEnabled == True):
            requests.put(Walleturl + "api/" + module + "_image", proxies=proxyServer, auth=(Accounts[AccountIndex]['name'], Accounts[AccountIndex]['id']),  data=payload, files=files)
        else :
            requests.put(Walleturl + "api/" + module + "_image", auth=(Accounts[AccountIndex]['name'], Accounts[AccountIndex]['id']),  data=payload, files=files)
    except:
        inform('Falha ao enviar imagem para o servidor','error');
    
def send_print_screen_to_app():
    generate_printscreen()
    time.sleep(5)
    send_wallet_image(current_account,'printscreen',os.path.dirname(os.path.realpath(__file__)) + r'\tmp\printscreen.png')
    time.sleep(5)


"""
---------------------
Add randomness (mouse position) function
---------------------
"""


def add_randomness(n, random_factor_size=None):
    if random_factor_size is None:
        randomness_percentage = 0.1
        random_factor_size = randomness_percentage * n

    random_factor = 2 * random() * random_factor_size
    if random_factor > 5:
        random_factor = 5
    without_average_random_factor = n - random_factor_size
    randomized_n = int(without_average_random_factor + random_factor)
    # logger('{} with randomness -> {}'.format(int(n), randomized_n))
    return int(randomized_n)


"""
---------------------
moveTo (mouse) with randomness function
---------------------
"""


def move_to_with_randomness(x, y, t=0.5):
    pyautogui.moveTo(add_randomness(x, 10), add_randomness(y, 10), t)


"""
---------------------
remove sulfix function
---------------------
"""


def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string


"""
---------------------
Load images function
---------------------
"""


def load_images():
    file_names = listdir('./targets/')
    targets = {}
    for file in file_names:
        path = 'targets/' + file
        targets[remove_suffix(file, '.png')] = cv2.imread(path)

    return targets


images = load_images()


def generate_printscreen():

    # take screenshot of game area
    back_button = positions(images['corner'], threshold=config_threshold['default'])

    # from the bcoin image calculates the area of the square for print
    xx, yy, aa, bb = back_button[0]
    x_init = xx + 10
    y_init = yy - 20
    img_lenght = 1030
    img_height = 690

    # take screenshot
    my_screen = pyautogui.screenshot(region=(x_init, y_init, img_lenght, img_height))
    # save image
    img_dir = os.path.dirname(os.path.realpath(__file__)) + r'\tmp\printscreen.png'
    my_screen.save(img_dir)
    # delau
    time.sleep(2)
    
"""
---------------------
Show function
---------------------
"""


def show(rectangles, img=None):
    if img is None:
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            img = np.array(sct.grab(monitor))

    for (x, y, w, h) in rectangles:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255, 255), 2)

    # cv2.rectangle(img, (result[0], result[1]), (result[0] + result[2], result[1] + result[3]), (255,50,255), 2)
    cv2.imshow('img', img)
    cv2.waitKey(0)


"""
---------------------
Click button function
---------------------
"""


def click_btn(img, name=None, timeout=3, threshold=config_threshold['default']):
    # forces to ???flush??? terminal buffer
    sys.stdout.flush()

    if not name is None:
        pass
        # print('waiting for "{}" button, timeout of {}s'.format(name, timeout))
    start = time.time()
    clicked = False
    while not clicked:
        matches = positions(img, threshold=threshold)
        if len(matches) == 0:
            hast_timed_out = time.time() - start > timeout
            if hast_timed_out:
                if not name is None:
                    pass
                    # print('timed out')
                return False
            # print('button not found yet')
            continue

        x, y, w, h = matches[0]
        pos_click_x = x + w / 2
        pos_click_y = y + h / 2

        # change "moveto" to w randomness
        move_to_with_randomness(pos_click_x, pos_click_y, 0.5)
        pyautogui.click()

        return True


"""
---------------------
Print screen function
---------------------
"""


def print_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))
        # The screen part to capture
        # monitor = {"top": 160, "left": 160, "width": 1000, "height": 135}

        # Grab the data
        return sct_img[:, :, :3]


"""
---------------------
Get positions of an target
---------------------
"""


def positions(target, threshold=config_threshold['default'], img=None):
    if img is None:
        img = print_screen()
    result = cv2.matchTemplate(img, target, cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles


"""
---------------------
Scroll function
---------------------
"""


def scroll():
    commoms = positions(images['commom-text'], threshold=config_threshold['commom'])
    if len(commoms) == 0:
        return
    x, y, w, h = commoms[len(commoms) - 1]
    #
    move_to_with_randomness(x, y, 0.5)

    if not config['use_click_and_drag_instead_of_scroll']:
        pyautogui.scroll(-config['scroll_size'])
    else:
        pyautogui.dragRel(0, -config['click_and_drag_amount'], duration=1, button='left')


"""
---------------------
Click buttons function
---------------------
"""


def click_buttons():
    buttons = positions(images['go-work'], threshold=config_threshold['go_to_work_btn'])
    # print('buttons: {}'.format(len(buttons)))
    for (x, y, w, h) in buttons:

        # Determine center of target
        x_center = x + (w / 2)
        y_center = y + (h / 2)

        move_to_with_randomness(x_center, y_center, 0.5)
        pyautogui.click()

        global send_to_work_clicks
        send_to_work_clicks = send_to_work_clicks + 1
        # cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
        if send_to_work_clicks > 20:
            inform('??????Too many hero clicks, try to increase the go_to_work_btn threshold.', msg_type='warn')
            return
    return len(buttons)


"""
---------------------
Is Working function
---------------------
"""


def is_working(bar, buttons):
    y = bar[1]

    for (_, button_y, _, button_h) in buttons:
        is_below = y < (button_y + button_h)
        is_above = y > (button_y - button_h)
        if is_below and is_above:
            return False
    return True


"""
---------------------
Click greenbar buttons
---------------------
"""


def click_green_bar_buttons():
    offset = 130

    green_bars = positions(images['green-bar'], threshold=config_threshold['green_bar'])
    inform('%d green bars detected' % len(green_bars), msg_type='log')
    buttons = positions(images['go-work'], threshold=config_threshold['go_to_work_btn'])
    inform('%d buttons detected' % len(buttons), msg_type='log')
    send_wallet_info(current_account,'stamina','%d buttons detected' % len(buttons))

    not_working_green_bars = []
    for bar in green_bars:
        if not is_working(bar, buttons):
            not_working_green_bars.append(bar)
    if len(not_working_green_bars) > 0:
        inform('%d buttons with green bar detected' % len(not_working_green_bars), msg_type='log')
        inform('Clicking in %d heroes' % len(not_working_green_bars), msg_type='log')

    # se tiver botao com y maior que bar y-10 e menor que y+10
    for (x, y, w, h) in not_working_green_bars:
        # isWorking(y, buttons)

        # Determine center of target
        x_center = x + offset + (w / 2)
        y_center = y + (h / 2)

        move_to_with_randomness(x_center, y_center, 0.5)
        pyautogui.click()
        global send_to_work_clicks
        send_to_work_clicks = send_to_work_clicks + 1
        if send_to_work_clicks > 20:
            inform('??????Too many hero clicks, try to increase the go_to_work_btn threshold.', msg_type='warn')
            return
        # cv2.rectangle(sct_img, (x, y) , (x + w, y + h), (0,255,255),2)
    return len(not_working_green_bars)


"""
---------------------
Click fullbar buttons
---------------------
"""


def click_fullbar_buttons():
    offset = 100
    full_bars = positions(images['full-stamina'], threshold=config_threshold['default'])
    buttons = positions(images['go-work'], threshold=config_threshold['go_to_work_btn'])

    not_working_full_bars = []
    for bar in full_bars:
        if not is_working(bar, buttons):
            not_working_full_bars.append(bar)

    if len(not_working_full_bars) > 0:
        inform('Clicking in %d heroes' % len(not_working_full_bars), msg_type='log')

    for (x, y, w, h) in not_working_full_bars:
        # Determine center of target
        x_center = x + offset + (w / 2)
        y_center = y + (h / 2)

        move_to_with_randomness(x_center, y_center, 0.5)
        pyautogui.click()
        global send_to_work_clicks
        send_to_work_clicks = send_to_work_clicks + 1

    return len(not_working_full_bars)


"""
---------------------
Go to heroes function
---------------------
"""


def go_to_heroes():
    if click_btn(images['go-back-arrow']):
        global login_attempts
        login_attempts = 0

    # TODO tirar o sleep quando colocar o pulling
    time.sleep(1)
    click_btn(images['hero-icon'])
    time.sleep(1)


"""
----------------------
Check BCoin quantity
----------------------
"""


def get_total_bcoins():
    global saldo_atual

    # inform
    inform("Trying to look BCoins in chest.", msg_type='log')

    # click on chest button
    click_btn(images['chest'])

    # wait until "coin-icon" apears
    i = 10
    coins_pos = positions(images['coin-icon'], threshold=config_threshold['default'])
    while len(coins_pos) == 0:
        if i <= 0:
            break
        i = i - 1
        coins_pos = positions(images['coin-icon'], threshold=config_threshold['default'])
        time.sleep(5)

    if len(coins_pos) == 0:
        # inform error in "coin-icon" dont apears
        inform("???? Error fetching Bcoins from chest.", msg_type='error')
        # close window
        click_btn(images['x'])

        return

    # after "coin-icon" apears wait until receive BCoin value from server
    time.sleep(30)

    # from the bcoin image calculates the area of the square for print
    k, l, m, n = coins_pos[0]
    k = k + 200
    #l = l + 130
    m = 200
    n = 50

    # take screenshot
    my_screen = pyautogui.screenshot(region=(k, l, m, n))
    img_dir = os.path.dirname(os.path.realpath(__file__)) + r'\tmp\bcoins.png'
    my_screen.save(img_dir)
    send_wallet_image(current_account,'bcoin',img_dir)   

    # Delay
    time.sleep(2)
    # inform BCoins
    inform("???? BCoins in chest - screen printed.", msg_type='log')
    # close window
    click_btn(images['x'])


"""
---------------------
Go to game function
---------------------
"""


def go_to_game():
    # in case of server overload popup
    click_btn(images['x'])
    # time.sleep(3)
    click_btn(images['x'])

    click_btn(images['treasure-hunt-icon'])


"""
---------------------
Refres Heroes Positions function
---------------------
"""


def go_to_main_page():
    click_btn(images['go-back-arrow'])


"""
---------------------
connect wallet function
---------------------
"""


def connect_wallet():
    inform('??? Game has disconnected. Refreshing.', msg_type='error')

    # Send CTRL+F5 to update page
    pyautogui.hotkey('ctrl', 'f5')

    time.sleep(30)

    # Click in wallet button
    if click_btn(images['connect-wallet'], name='connectWalletBtn', timeout=10):
        inform('Connect wallet button detected, logging in!', msg_type='log')
        send_wallet_info(current_account,'login','')

    time.sleep(1)

def continue_metamask():
    inform('Select metamask as Login.', msg_type='info')

    # Click in wallet button
    if click_btn(images['connect-metamask'], name='connect-metamask', timeout=10):
        inform('Continue login as metamask, logging in!', msg_type='log')
        send_wallet_info(current_account,'login','')

    time.sleep(1)

"""
---------------------
Metamask sign in function
---------------------
"""


def metamask_sign_in():
    # English button text
    if click_btn(images['select-wallet-2-en'], name='select-wallet-2-en', timeout=10, threshold=config_threshold['select_wallet_buttons']):
        inform('Metamask button found [EN]. Sign in.', msg_type='log')

    # Portuguese button text
    elif click_btn(images['select-wallet-2-pt'], name='select-wallet-2-pt', timeout=10, threshold=config_threshold['select_wallet_buttons']):
        inform('Metamask button found [PT]. Sign in.', msg_type='log')
    
    elif click_btn(images['select-wallet-3-pt'], name='select-wallet-3-pt', timeout=10, threshold=config_threshold['select_wallet_buttons']):
        inform('Metamask button found [PT]. Sign in.', msg_type='log')


"""
---------------------
Metamask login function
---------------------
"""


def metamask_login():

    # Send password to metamask page
    pyautogui.write(config["metamask_password"])

    time.sleep(1)

    # English button text
    if click_btn(images['metamask-unlock-en'], name='select-wallet-2-en', timeout=10, threshold=config_threshold['select_wallet_buttons']):
        inform('Metamask login button found [EN]. Send password.', msg_type='log')

    # Portuguese button text
    elif click_btn(images['metamask-unlock-pt'], name='select-wallet-2-pt', timeout=10, threshold=config_threshold['select_wallet_buttons']):
        inform('Metamask login button found [PT]. Send password.', msg_type='log')


"""
---------------------
Close Metamask Windows when it is behind the browser
---------------------
"""

def closeMetaMaskWindows():
    send_print_screen_to_app()
    if OSWin == True:
        Metamask = []
        CountMMWindow = 1;
        while CountMMWindow > 0:
            for w in pygetwindow.getWindowsWithTitle('MetaMask'):
                Metamask.append({
                    "Metamask": w
                })
            CountMMWindow = len(Metamask)
            for last in Metamask:
                last["Metamask"].activate()
                time.sleep(3)
                metamask_login()
    else:
        #Alert possible Metamask Window
        inform('Verify if there is not any metamask window behin browser', 'warn')




"""
---------------------
Refresh Heroes function: Send heroes to work
---------------------
"""


def refresh_heroes():

    # restart send to work clicks
    global send_to_work_clicks
    send_to_work_clicks = 0

    inform('Finding heroes to work...', msg_type='log')

    go_to_heroes()

    if config['select_heroes_mode'] == "full":
        inform('Sending heroes with FULL stamina bar to work', msg_type='log')
    elif config['select_heroes_mode'] == "green":
        inform('Sending heroes with GREEN stamina bar to work', msg_type='log')
    else:
        inform('Sending ALL heroes to work', msg_type='log')

    empty_scrolls_attempts = config['scroll_attemps']

    while empty_scrolls_attempts > 0:
        if config['select_heroes_mode'] == 'full':
            buttons_clicked = click_fullbar_buttons()
        elif config['select_heroes_mode'] == 'green':
            buttons_clicked = click_green_bar_buttons()
        else:
            buttons_clicked = click_buttons()

        if buttons_clicked == 0:
            empty_scrolls_attempts = empty_scrolls_attempts - 1
        scroll()
        time.sleep(2)
    inform('{} heroes sent to work'.format(send_to_work_clicks), msg_type='log')
    send_wallet_info(current_account,'work','{} heroes sent to work'.format(send_to_work_clicks))
    go_to_game()



"""
---------------------
Find screen function

Return:
    0 = no screen defined
    1 = connect_wallet
    2 = captcha
    3 = metamask
    4 = main page
    5 = page heroes
    6 = page work (map)
    7 = error popup
    8 = new map
---------------------
"""


def find_screen():
    # DO NOT CHANGE THE ORDER ABOVE (PRIORITY).
    
    # 9 = matamask login
    if (len(positions(images['metamask-unlock-en'], threshold=0.90)) > 0) or \
            (len(positions(images['metamask-unlock-pt'], threshold=0.90)) > 0):
        return 9

    # 3 = metamask wallet
    if (len(positions(images['select-wallet-2-en'], threshold=0.90)) > 0) or \
            (len(positions(images['select-wallet-2-pt'], threshold=0.90)) > 0):
        return 3

    # 7 = error popup
    elif (len(positions(images['ok'], threshold=config_threshold['default'])) > 0) or \
            (len(positions(images['ok-firefox'], threshold=config_threshold['default'])) > 0):
        return 7

    # 1 = connect_wallet or tab crash
    if (len(positions(images['connect-wallet'], threshold=config_threshold['default'])) > 0) or \
            (len(positions(images['tab-crash'], threshold=config_threshold['default'])) > 0):
        return 1

    # 2 = captcha
    if len(positions(images['robot'], threshold=config_threshold['default'])) > 0:
        return 2

    # 4 = main page
    if len(positions(images['hero-icon'], threshold=config_threshold['default'])) > 0:
        return 4

    # 5 = page heroes
    if len(positions(images['go-work'], threshold=config_threshold['default'])) > 0:
        return 5

    # 8 = new map
    elif len(positions(images['new-map'], threshold=config_threshold['default'])) > 0:
        return 8

    # 6 = page work (map)
    if len(positions(images['go-back-arrow'], threshold=config_threshold['default'])) > 0:
        return 6

    # 10 = page work (map)
    if len(positions(images['connect-metamask'], threshold=config_threshold['default'])) > 0:
        return 10
        
    # 0 = no screen defined
    return 0


"""
---------------------
MAIN function
---------------------
"""

def main():
    global current_account, new_map_available
    time.sleep(5)
    windows = []
    if OSWin == True:
        for w in pygetwindow.getWindowsWithTitle('Bombcrypto'):
            windows.append({
                "window": w,
                "login" : 0,
                "heroes" : 0,
                "new_map" : 0,
                "check_for_captcha" : 0,
                "refresh_heroes" : 0,
                "BCoins_in_chest": 0
                })
    else:
        windows.append({
            "window": [{
                "title": Accounts[0]['Browser']
            }],
            "login" : 0,
            "heroes" : 0,
            "new_map" : 0,
            "check_for_captcha" : 0,
            "refresh_heroes" : 0,
            "BCoins_in_chest": 0
        })

    while True:
        for last in windows:
            try:
                last["window"].activate()
            except:
                inform('***  Encontramos problemas para trocar as janelas.','info')
            
            last_screen_found = 0

            if OSWin == True:
                if 'Brave' in last["window"].title:
                    current_account = 'brave'
                    inform('========================','info')
                    inform('Changing account - NFT02 [Navegador Brave]','info')
                if 'Firefox' in last["window"].title:
                    current_account = 'firefox'
                    inform('========================','info')
                    inform('Changing account - NFT00 [Navegador Firefox]','info')
                if 'Chrome' in last["window"].title:
                    current_account = 'chrome'
                    inform('========================','info')
                    inform('Changing account - NFT01 [Navegador Chrome]','info')
                if 'Chromium' in last["window"].title:
                    current_account = 'chromium'
                    inform('========================','info')
            else:
                current_account = Accounts[0]['Browser']
            time.sleep(5)
            
            intervals = config['time_intervals']
            inform("???? TRAPA-TRADE STARTED! It's time to earn some BCoins ????!!!", msg_type='info')

            ProcessingAccount= True
            SendToWorkOnce = False
            PrintGainOne = False
            SleepCounter = 0
            MetaMaskStuck = 0

            while ProcessingAccount == True:
                # get now time
                now = time.time()

                # Find screen number
                screen = find_screen()
                inform('Current screen: '+ str(screen),"info")

                if MetaMaskStuck >= 2:
                    #Limpa Metamask
                    closeMetaMaskWindows()

                # 0 = no screen defined
                if screen == 0:
                    
                    # Check if freezes
                    if now - last_screen_found >= add_randomness(intervals['check_freeze'] * 60):
                        # Update last found screen
                        last_screen_found = now
                        # Call connect_wallet function
                        connect_wallet()
                        
                    elif last_screen_found == 0:
                        # Update last found screen
                        last_screen_found = now
                        # Call connect_wallet function
                        connect_wallet()
                        
                    else:
                        # Nothing found and in freeze time wait
                        time.sleep(1)
                        continue

                # 1 = connect_wallet or no action after X min
                elif screen == 1:
                    if now - last["login"] >= add_randomness(intervals['check_for_login'] * 60):
                        last["login"] = now
                        # Call connect_wallet function
                        connect_wallet()
                        

                # 2 = captcha
                elif screen == 2:
                    # Call solve_captcha function
                    inform("Captcha found. Trying to solve.", msg_type='emphasis')
                    # Call solve captcha class
                    solveCaptcha(pyautogui.PAUSE)

                # 3 = metamask
                elif screen == 3:
                    metamask_sign_in()
                    MetaMaskStuck = MetaMaskStuck + 1

                # 4 = main page
                elif screen == 4:
                    MetaMaskStuck = 0
                    send_wallet_info(current_account,'heroes','')
                    if now - last["heroes"] >= add_randomness(intervals['send_heroes_for_work'] * 60):
                        last["heroes"] = now
                        # open heroes page
                        inform('???? Opening hero pages.', msg_type='log')
                        click_btn(images['hero-icon'])
                    else:
                        # open work map (refresh hero positions)
                        inform('???? Refreshing heroes positions.', msg_type='log')
                        click_btn(images['treasure-hunt-icon'])

                # 5 = page heroes
                elif screen == 5:
                    # Call refresh_heroes function
                    refresh_heroes()
                    SendToWorkOnce= True

                # 6 = page work (map)
                elif screen == 6:
                    # if is a new map, send printscreen to telegram bot
                    if new_map_available:
                        # inform
                        inform('??????? New map opened! Printing screen.', msg_type='success')
                        # Send print to telegram
                        try:
                            send_print_screen_to_app()
                        except:
                            inform('Error generating print screen.','info')
                        # unset
                        new_map_available = False

                    inform('Map screen.', msg_type='log')
                    if last["heroes"] == 0:
                        last["heroes"] = now
                    if last["refresh_heroes"] == 0:
                        last["refresh_heroes"] = last["heroes"]

                    # Call refresh_heroes_positions function
                    if now - last["refresh_heroes"] > add_randomness(intervals['refresh_heroes_positions'] * 60):
                        last["refresh_heroes"] = now
                        inform('Go to main page.', msg_type='log')
                        go_to_main_page()
                    else:
                        # if the heroes have to work,
                        # Try to show BCoins first
                        if now - last["BCoins_in_chest"] > add_randomness(intervals['interval_between_bcoins_chest'] * 60):
                            last["BCoins_in_chest"] = now
                            get_total_bcoins()
                            PrintGainOne= True
                            if SleepCounter==multiaccount_config['waitcycles']:
                                last["refresh_heroes"]=0

                        # sleep for the heroes refresh time to save processing
                        t = 60  # seconds of delay
                        inform('Nothing to do. Delay of ' + str(t) + 's to keep proccessing.', msg_type='success')
                        time.sleep(t)
                    if SendToWorkOnce == True and PrintGainOne == True:
                        ProcessingAccount= False
                    else:
                        if SleepCounter==multiaccount_config['waitcycles']:
                            last["refresh_heroes"]=0
                        SleepCounter=SleepCounter+1

                # 7 = error popup
                elif screen == 7:
                    # inform
                    inform('??? Some error occurred. Clicking ok.', msg_type='error')
                    # Send print to telegram
                    try:
                        send_print_screen_to_app()
                    except:
                        inform('Error generating print screen.','info')
                    # Click OK button (game error)
                    if not click_btn(images['ok'], name='ok_btn', timeout=5):
                        # click OK button (firefox error)
                        click_btn(images['ok-firefox'], name='ok_btn_firefox', timeout=5)

                # 8 = new map
                elif screen == 8:
                    # mark global variable pointer
                    new_map_available = True
                    # inform
                    inform('???? Map completed! Open the new one.', msg_type='success')
                    # Click NEW MAP button
                    click_btn(images['new-map'])

                # 3 = metamask login
                elif screen == 9:
                    metamask_login()

                # 3 = metamask login
                elif screen == 10:
                    continue_metamask()
                # if screen != 0, update last_screen_found
                last_screen_found = now

                # Delay before start again...
                time.sleep(1)

# Call main function
main()