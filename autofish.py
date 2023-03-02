import time
import io 
import numpy as np
import keyboard
import math
import mss 
import mouse
from tesserocr import PyTessBaseAPI, image_to_text
from PIL import Image
from threading import Thread
import cv2 as cv 

def get_setting() -> tuple:
    v = input()
    is_int = True
    try:
        int(v)
    except ValueError:
        is_int = False 
    return is_int, v 

def caught_fish():
    time.sleep(0.3)
    mouse.click()

def loop():
    # Main template image
    food_index = 0
    food_slots = [2, 3, 4, 5, 6]
    orc_api = PyTessBaseAPI()
    print("Starting in 3..")
    time.sleep(3)
    print("Starting..")
    with mss.mss() as sct:
        prev_time = time.time()
        prev_bait = 0
        #Useful time values for checks

        while True:
            time.sleep(1/1000 * 100)
            diff = time.time() - prev_time

            # Take screen shot every half a second
            if not diff > 1/60:
                continue
            img = np.array(sct.grab(sct.monitors[1]))
            img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            # Usefull seperations
            w, h = img.shape[::-1]
            w1, h1 = int(w/2), int(h/2)

            # Bait part
            w2, h2 = w1, int(h * 0.84)
            b_sx, bsy = int(0.18*w), int(0.08*h)
            b_img = img[h2:h2-bsy, w1-b_sx:w1+b_sx]
            text = image_to_text(Image.fromarray(b_img))
            print(text)

            # Activity part
            img3 = Image.fromarray(img[h1:,w1:])
            text = image_to_text(img3)
            if text.lower().find("caught") > -1:
                caught_on_screen = time.time()
            if text.lower().find("starved") > -1:
                starved_on_screen = time.time()
            prev_time = time.time()

            
def main():
    loop()


if __name__ == "__main__":
    main()