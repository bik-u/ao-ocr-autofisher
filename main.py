import time
import numpy as np
import keyboard
from mss.windows import MSS as mss
import mouse
from threading import Thread, Lock
import cv2 as cv
import pytesseract
import random


pytesseract.pytesseract.tesseract_cmd = './tesseract/tesseract.exe'


global reeling
global real_lock
reeling = False
real_lock = Lock()


def get_setting() -> tuple:
    v = input()
    is_int = True
    try:
        int(v)
    except ValueError:
        is_int = False 
    return is_int, v 


def caught_fish(rod_slot):
    keyboard.press_and_release(rod_slot)
    time.sleep(0.3)
    keyboard.press_and_release(rod_slot)
    time.sleep(1)
    mouse.click()


def reel(main_loop):
    global reeling
    while main_loop.is_alive():
        with real_lock:
            if reeling:
                mouse.click()
        time.sleep(0.05)



def loop():
    global reeling
    global real_lock
    food_index = 0
    # The 1st slot
    rod_slot = '1'
    # Represents 2-0 in the number bar
    food_slots = [str(x) for x in range(2,10)]
    food_slots.append('0')
    print(f"The rod slot is {rod_slot}, rest of the slots are for food!. Starting in 3..")
    time.sleep(3)
    print("Starting..")
    with mss() as sct:
        prev_time = time.time()
        prev_bait = None
        # Useful time values for checks
        caught_time = None
        reel_time = None
        starved_time = None
        while True:
            diff = time.time() - prev_time
            with real_lock:
                if reeling:
                    if time.time() - reel_time > 15:
                        reeling = False
                        caught_fish(rod_slot)

            img = np.array(sct.grab(sct.monitors[1]))
            img = cv.cvtColor(img, cv.COLOR_RGBA2RGB)
            # Usefull seperations
            h, w = img.shape[:-1]
            w1, h1 = int(w/2), int(h/2)

            with real_lock:
                if reeling:
                    res = cv.inRange(img[h1:,w1:], np.array([0, 250, 250]), np.array([5, 255, 255]))
                    text = pytesseract.image_to_string(res)
                    if text.lower().find("caught") > -1:
                        approve = False
                        if caught_time:
                            if time.time() - caught_time > 15:
                                approve = True 
                        else:
                            approve = True
                        if approve:
                            print(text)
                            caught_time = time.time()
                            reeling = False
                            keyboard.press('w')
                            time.sleep(1)
                            keyboard.release('w')
                            caught_fish(rod_slot)

            if diff > 5:    
                res = cv.inRange(img[h1:,w1:], np.array([0, 0, 250]), np.array([5, 5, 255]))
                text = pytesseract.image_to_string(res)
                if text.lower().find("starving") > -1:
                    approve = False
                    if starved_time:
                        if time.time() - starved_time > 30:
                            approve = True
                        elif time.time() - starved_time > 12:
                            food_index += 1
                            approve = True
                    else:
                        approve = True 
                    if approve:
                        starved_time = time.time()
                        with real_lock:
                            reeling = False
                        if food_index < len(food_slots) + 1:
                            keyboard.press_and_release(food_slots[food_index])
                            time.sleep(0.3)
                            mouse.click()
                            time.sleep(0.3)
                            keyboard.press_and_release(rod_slot)
                            caught_fish(rod_slot)

                prev_time = time.time()

            # Bait part
            w3 = int(w*1/3)
            res = cv.inRange(img[h1:,w3:w3*2], np.array([133, 133, 250]), np.array([143, 143, 255]))
            text = pytesseract.image_to_string(res)
            if text.lower().find('fish bait') > -1:
                b = None
                try:
                    for i in text.split():
                        if len(i) > 1 and i[0].lower() == 'x':
                            b = int(i[1:])
                except ValueError as exp:
                    pass
                except IndexError:
                    pass
                if not prev_bait and b:
                    prev_bait = b
                if prev_bait and b:
                    if prev_bait-1 == b:
                        with real_lock:
                            time.sleep(random.uniform(0.1, 0.5))
                            reeling = True
                        reel_time = time.time()
                    prev_bait = b

            
def main():
    pic_loop = Thread(group=None, target=loop, daemon=True)
    pic_loop.start()
    reel(pic_loop)


if __name__ == "__main__":
    main()