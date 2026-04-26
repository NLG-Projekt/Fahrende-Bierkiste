import time
import pyautogui
import pyperclip

time.sleep(3)  # Zeit, um ins richtige Fenster zu klicken
text = pyperclip.paste()
pyautogui.write(text, interval=0.01)
