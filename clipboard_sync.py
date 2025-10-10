import pyperclip
import time
import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv
import os

load_dotenv()

FIREBASE_DB_URL = os.getenv("FIREBASE_DB_URL")
FIREBASE_CRED_PATH = "firebase-key.json" 

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(FIREBASE_CRED_PATH)
        firebase_admin.initialize_app(cred, {
            'databaseURL': FIREBASE_DB_URL
        })
    except Exception as e:
        print(f" Firebase init error: {e}")
        exit(1)

clipboard_ref = db.reference('clipboard')

def update_clipboard_to_firebase(text):
    try:
        clipboard_ref.set(text)
        print(f"  Uploaded to Firebase: {text}")
    except Exception as e:
        print(f" Failed to upload to Firebase: {e}")

def main():
    print(" Universal Clipboard Sync started...")

    last_clipboard = pyperclip.paste()
    print(f"  Initial clipboard: {last_clipboard}")
    update_clipboard_to_firebase(last_clipboard)

    def listener(event):
        new_data = event.data
        if new_data != pyperclip.paste():
            print(f"  Firebase updated - setting laptop clipboard: {new_data}")
            pyperclip.copy(new_data)

    clipboard_ref.listen(listener)

    while True:
        try:
            time.sleep(1)
            current_clipboard = pyperclip.paste()
            if current_clipboard != last_clipboard:
                print(f"  Synced clipboard to Firebase: {current_clipboard}")
                update_clipboard_to_firebase(current_clipboard)
                last_clipboard = current_clipboard
        except Exception as e:
            print(f" Error in main loop: {e}")


if __name__ == "__main__":
    main()
