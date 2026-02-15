import time
import numpy as np
import keyboard
from mss.windows import MSS as mss
import mouse
import threading
from threading import Thread, Lock
import cv2 as cv2
import random


w, h = 1920, 1080

# Color limits in rgb
lower_white = [230, 230, 230]
upper_white = [255, 255, 255]

lower_red = [230, 0, 0]
upper_red = [255, 0, 0]

lower_yellow = [0, 250, 250]
upper_yellow = [0, 255, 255]


def test_img(img):
    cv2.imshow("img", img)
    cv2.waitKey(1)


def get_middle_numbers(res, p_1, p_2):
    return int(res * p_1), int(res * p_2)


class Fisher:


    def __init__(self):
        self.reel_lock = Lock()
        self.reeling = False
        self.total = 0
        
        self.check_start_time = 0
        self.alert_start_time = 0
        self.times_reeled = 0

    def reel_loop(self):
        while threading.main_thread().is_alive():
            with self.reel_lock:
                if self.reeling and self.times_reeled < 70:
                    self.times_reeled += 1
                    mouse.click()
                elif self.reeling and self.times_reeled > 70:
                    self.reeling = False
                    self.reset_rod()
            time.sleep(0.3)


    def reset_rod(self):
        self.reeling = False
        self.times_reeled = 0
        time.sleep(2)
        self.check_start_time = time.time()
        keyboard.press_and_release('2')
        time.sleep(0.5)
        keyboard.press_and_release('1')
        time.sleep(0.9)
        mouse.click()


    def check_caught(self, img):
        w_m = get_middle_numbers(w, 0.8, 0.2)
        h_m = get_middle_numbers(h, 0.5, 0.5)
        caught_img = img[h_m[0]:h_m[0]+h_m[1], w_m[0]:w_m[0]+w_m[1]]
        caught_mask = cv2.inRange(caught_img, np.array(lower_yellow), np.array(upper_yellow))
        count_white_pixels = np.count_nonzero(caught_mask)
        white_percentage = (count_white_pixels / (caught_mask.shape[0] * caught_mask.shape[1]))
        if white_percentage >= 0.0015:
            self.total +=1
            print(f"Caught something! Total: {self.total}")
            self.reeling = False
            self.reset_rod()


    def check_alert(self, img):
        w_m = get_middle_numbers(w, 0.3, 0.3)
        h_m = get_middle_numbers(h, 0.2, 0.2)
        alert_img = img[h_m[0]:h_m[0]+h_m[1], w_m[0]:w_m[0]+w_m[1]]
        alert_mask = cv2.inRange(alert_img, np.array(lower_white), np.array(upper_white))
        count_white_pixels = np.count_nonzero(alert_mask)
        white_percentage = (count_white_pixels / (alert_mask.shape[0] * alert_mask.shape[1])) 
        if white_percentage >= 0.15:
            print("Reeling!")
            self.alert_start_time = time.time()
            self.reeling = True


    def loop(self):
        print("Make sure character is shift-locked, facing the ocean.\nBest camera position is pressing o twice after going in first person.")
        time.sleep(3)
        print("Starting..")
        self.reset_rod()

        while True:
            with mss() as sct:
                monitor = sct.monitors[1]
                img = np.array(sct.grab(monitor))
                img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
                img = cv2.resize(img, (1920, 1080))
                # Check if is in game

                # If reeling check if caught or check alert
                with self.reel_lock:
                    if self.reeling:
                        self.check_caught(img)
                    else:
                        self.check_alert(img)
                    if time.time() - self.check_start_time > 90:
                        print("Took too long resetting rod")
                        self.reset_rod()
                            
            
def main():
    fisher = Fisher()

    Thread(target=fisher.reel_loop).start()
    fisher.loop()


if __name__ == "__main__":
    main()