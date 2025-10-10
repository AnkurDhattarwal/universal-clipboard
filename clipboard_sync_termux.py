import os
import time
import subprocess
import requests
from dotenv import load_dotenv

load_dotenv()
FIREBASE_DB_URL = os.getenv("FIREBASE_DB_URL")
if not FIREBASE_DB_URL:
    print("FIREBASE_DB_URL not set in .env")
    raise SystemExit(1)
FIREBASE_DB_URL = FIREBASE_DB_URL.rstrip('/')

def get_clipboard():
    try:
        p = subprocess.run(['termux-clipboard-get'],
                           capture_output=True, text=True, timeout=5)
        return p.stdout or ""
    except Exception as e:
        print("get_clipboard error:", e)
        return ""

def set_clipboard(text):
    try:
        subprocess.run(['termux-clipboard-set'],
                       input=text, text=True, check=True, timeout=5)
    except Exception as e:
        print("set_clipboard error:", e)

def read_remote():
    try:
        r = requests.get(f"{FIREBASE_DB_URL}/clipboard.json", timeout=10)
        if r.status_code == 200:
            return r.json()  
        else:
            print("Firebase GET status:", r.status_code, r.text)
            return None
    except Exception as e:
        print("Firebase GET error:", e)
        return None

def write_remote(value):
    try:
        r = requests.put(f"{FIREBASE_DB_URL}/clipboard.json", json=value, timeout=10)
        if r.status_code in (200, 204):
            return True
        else:
            print("Firebase PUT status:", r.status_code, r.text)
            return False
    except Exception as e:
        print("Firebase PUT error:", e)
        return False

def main():
    print("Universal Clipboard (Termux) starting...")
    last_local = get_clipboard()
    if last_local is None:
        last_local = ""
    print("Local clipboard:", repr(last_local))
    remote = read_remote()
    if remote is None:
        remote = ""
    print("Remote clipboard:", repr(remote))

    if remote == "" and last_local != "":
        write_remote(last_local)
    elif remote != "" and remote != last_local:
        set_clipboard(remote)
        last_local = remote

    while True:
        try:
            time.sleep(1) 
            remote_now = read_remote()
            if remote_now is not None and remote_now != remote:
                remote = remote_now
                local_now = get_clipboard()
                if local_now != remote:
                    print("Remote changed - setting local clipboard")
                    set_clipboard(remote)
                    last_local = remote

            local_now = get_clipboard()
            if local_now != last_local:
                print("Local changed - uploading to remote")
                write_remote(local_now)
                last_local = local_now
        except Exception as e:
            print("Loop error:", e)
            time.sleep(5)

if __name__ == "__main__":
    main()
