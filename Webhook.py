import os
import ctypes
import requests
import pyautogui
import time
from PIL import Image
import win32gui
import win32ui


class LogBot:
    def capture_window_and_save(self, output_file=None):
        hwnd = win32gui.FindWindow(None, "ArkAscended")

        if hwnd == 0:
            print(f"Window 'ArkAscended' not found.")
            return
        
        pyautogui.press('l')
        time.sleep(2)

        left, top, right, bot = win32gui.GetWindowRect(hwnd)
        w = right - left
        h = bot - top

        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

        saveDC.SelectObject(saveBitMap)

        result = ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)

        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)

        im = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)

        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)

        if result == 1:
            if output_file is not None:
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                im.save(output_file, format="PNG")
            else:
                print("Output file not provided.")
        else:
            print("PrintWindow failed.")

    def post_to_discord(self, image_path, content, webhook_url):
        with open(image_path, 'rb') as file:
            image_data = file.read()

        payload = {
            'content': content,
            'username': "Tribe Logs",
            #'avatar_url': 'https://example.com/avatar.png', - not needed but available.
        }

        files = {'file': (os.path.basename(image_path), image_data)}
        response = requests.post(webhook_url, data=payload, files=files)

        if response.status_code == 200:
            print("Logs successfully sent via Webhook")
        else:
            print(f"Failed to send logs: {response.status_code} - {response.text}")

    def send_logs(self):
        log_webhook = "https://your-webhook"
        image_path = "logs/screenshots/logs_only.png"
        self.capture_window_and_save(output_file=image_path)

        try:
            logs = Image.open(image_path)
            if logs:
                left = 757
                top = 188
                right = 1162
                bottom = 828
                cropped_image = logs.crop((left, top, right, bottom))
                cropped_image.save(image_path)

                self.post_to_discord(image_path, "", log_webhook)
                pyautogui.press('escape')

        except Exception as e:
            print(f"Error processing logs: {e}")

if __name__ == "__main__":
    bot = LogBot()
    bot.send_logs()

