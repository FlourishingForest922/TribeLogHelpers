import os
import ctypes
from PIL import Image
import pyautogui
import time
import win32gui
import win32ui
import discord

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

TARGET_CHANNEL_ID = 12345 #YOUR Channel ID

class LogBot:
    def capture_window_and_save(self, output_file=None):
        hwnd = win32gui.FindWindow(None, "ArkAscended")

        if hwnd == 0:
            print(f"Window with title 'ArkAscended' not found.")
            return False
        
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
                return True
            else:
                print("Output file not provided.")
                return False
        else:
            print("PrintWindow failed.")
            return False

    def process_logs(self, image_path):
        """Process and crop the logs screenshot."""
        try:
            logs = Image.open(image_path)
            if logs:
                left = 757
                top = 188
                right = 1162
                bottom = 828
                cropped_image = logs.crop((left, top, right, bottom))
                cropped_image.save(image_path)
                return True
        except Exception as e:
            print(f"Error processing logs: {e}")
            return False

    async def send_logs(self):
        """Function to send logs as a bot message to a specific channel."""
        image_path = "logs/screenshots/logs_only.png"

        if not self.capture_window_and_save(output_file=image_path):
            print("Failed to capture the ArkAscended window. Make sure the game is running.")
            return

        if not self.process_logs(image_path):
            print("Failed to process the logs.")
            return

        target_channel = bot.get_channel(TARGET_CHANNEL_ID)
        if target_channel is None:
            print("Target channel not found.")
            return

        try:
            message_content = f""
            await target_channel.send(message_content, file=discord.File(image_path))
            print(f"Tribe Log sent successfully to specified channel.")
            pyautogui.press('escape')
        except Exception as e:
            print(f"Failed to send logs: {e}")


log_bot = LogBot()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    
    await log_bot.send_logs()

TOKEN = "your-token" 
bot.run(TOKEN)
