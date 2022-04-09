"""
SMMO API NOTIFICATIONS
Author:      HugTed
Date:        3/25/2022
"""
import sys
import time
from threading import Thread
from tkinter import *
from tkinter import ttk

import requests
from discord_webhook import DiscordWebhook
from win10toast import ToastNotifier


class MyWindow:
    def __init__(self, win):
        self.next_run = None
        self.running = False
        self.toaster = ToastNotifier()

        self.s = ttk.Style()
        self.s.theme_use('alt')
        self.s.configure("blue.Horizontal.TProgressbar", foreground='cornflower blue', background='cornflower blue')
        self.s.configure('W.TButton', font=('calibri', 10, 'bold', 'underline'))

        self.pb = ttk.Progressbar(
            win,
            orient='horizontal',
            mode='indeterminate',
            length=450
        )
        self.pb.place(x=25, y=174)

        self.frame = Frame(win)
        self.frame.place(x=25, y=75)

        self.lbl1 = Label(win, text='API Key:')
        self.t1 = Entry(bd=3, width=65, show="*")
        self.lbl1.place(x=25, y=25)
        self.t1.place(x=75, y=25)

        self.lbl2 = Label(win, text='Discord:')
        self.t2 = Entry(bd=3, width=65)
        self.lbl2.place(x=25, y=50)
        self.t2.place(x=75, y=50)

        self.lbl3 = Label(win, text='Disc ID:')
        self.t3 = Entry(bd=3, width=20)
        self.lbl3.place(x=25, y=75)
        self.t3.place(x=75, y=75)

        self.lbl4 = Label(win, text='Delay:')
        self.t4 = Entry(bd=3, width=5)
        self.t4.insert(0, "300")
        self.lbl4.place(x=215, y=75)
        self.t4.place(x=265, y=75)

        self.notificationOptions = ["Windows", "Discord"]
        self.notificationType = StringVar()
        self.notificationType.set("Windows")
        self.lbl4 = Label(win, text='Type:')
        self.t5 = ttk.OptionMenu(win, self.notificationType, self.notificationOptions[0], *self.notificationOptions)
        self.lbl4.place(x=335, y=75)
        self.t5.place(x=375, y=73)

        self.energyCheck = BooleanVar()
        self.questCheck = BooleanVar()
        self.energyCheck.set(True)
        self.questCheck.set(True)
        self.c1 = ttk.Checkbutton(win, text='Energy Notifications', variable=self.energyCheck, onvalue=True,
                                  offvalue=False)
        self.c2 = ttk.Checkbutton(win, text='Quest Notifications', variable=self.questCheck, onvalue=True,
                                  offvalue=False)
        self.c1.place(x=25, y=125)
        self.c2.place(x=25, y=150)

        self.errorMessage = StringVar()
        self.errorMessage.set('')
        self.lbl6 = Label(win, textvariable=self.errorMessage, fg='#f00')
        self.lbl6.place(x=215, y=125)

        self.dataMessage = StringVar()
        self.dataMessage.set('?/? Energy   ?/? Quests')
        self.lbl7 = Label(win, textvariable=self.dataMessage, fg='#00008b')
        self.lbl7.place(x=215, y=100)

        self.b1 = Button(win, text='Run Checks', command=lambda: self.startChecks())
        self.b1.place(x=320, y=145)
        self.b2 = Button(win, text='Stop Checks', command=lambda: self.stopChecks())
        self.b2.place(x=397, y=145)

        self.lbl8 = Label(win, text='Gold:')
        self.t6 = Entry(bd=3, width=20)
        self.lbl8.place(x=25, y=100)
        self.t6.place(x=75, y=100)
        self.t6.insert(0, -1)

    def readKey(self, k):
        self.t1.insert(0, k)

    def readHook(self, h):
        self.t2.insert(0, h)

    def sendNoti(self, ntype, value, gval=0):
        if gval != 0:
            message = f"You are out of safe mode with {gval:,} gold on you!"
        else:
            message = f"Your {value} is FULL"

        if ntype == "Windows":
            try:
                self.toaster.show_toast("SimpleMMO Notification", f"{message}", icon_path="./data/logo.ico")
                self.errorMessage.set(f'Sending Quest Notification')
            except Exception as e:
                self.errorMessage.set(f'Error: {e}')
        else:
            try:
                if self.t3.get() != "":
                    webhook = DiscordWebhook(url=self.t2.get(), content=f"[<@{self.t3.get()}>] {message}")
                else:
                    webhook = DiscordWebhook(url=self.t2.get(), content=f"{message}")
                webhook.execute()
                self.errorMessage.set(f'Sending Quest Notification')
            except Exception as e:
                self.errorMessage.set(f'Error: {e}')

    def stopChecks(self):
        self.errorMessage.set('')
        self.running = False
        self.pb.stop()

    def startChecks(self):
        api_key = self.t1.get()
        delay = self.t4.get()
        if api_key == "":
            self.errorMessage.set('Error Missing API Key')
            return

        if self.notificationType.get() == "Discord" and self.t2.get() == "":
            self.errorMessage.set('Missing Discord Hook/ID')
            return

        if not delay.isdigit():
            self.errorMessage.set('Missing Check Delay In Seconds')
            return
        elif int(delay) < 2:
            self.errorMessage.set('Minimum Delay is 2 Seconds')
            return
        elif int(delay) < 60:
            self.errorMessage.set('Note: Max API 40 Calls/Min')

        self.pb.start()
        self.running = True
        self.next_run = Thread(target=self.runCheck, args=(api_key, delay))
        self.next_run.daemon = True
        self.next_run.start()

    def runCheck(self, api_key, delay):
        while self.running:
            try:
                endpoint = f'https://api.simple-mmo.com/v1/player/me'
                payload = {'api_key': api_key}
                r = requests.post(url=endpoint, data=payload)
                if str(r.status_code) != "200":
                    self.errorMessage.set(f'API ERROR: {r.status_code}')
                    self.running = False
                    self.pb.stop()
                    return
                res = r.json()
            except:
                self.errorMessage.set(f'API ERROR: Unknown Code')
                self.running = False
                self.pb.stop()
                return

            self.dataMessage.set(
                f'{res["energy"]:,}/{res["maximum_energy"]:,} Energy   {res["quest_points"]:,}/{res["maximum_quest_points"]:,} Quests')

            goldcheck = self.t6.get()
            if goldcheck != -1 and res["safeMode"] == 0 and res["gold"] > int(goldcheck):
                if self.notificationType.get() == "Windows":
                    self.sendNoti("Windows", "Money", res["gold"])
                else:
                    self.sendNoti("Discord", "Money", res["gold"])
            time.sleep(10)
            if self.questCheck.get() and res["quest_points"] >= res["maximum_quest_points"]:
                if self.notificationType.get() == "Windows":
                    self.sendNoti("Windows", "QP")
                else:
                    self.sendNoti("Discord", "QP")
            time.sleep(10)
            if self.energyCheck.get() and res["energy"] >= res["maximum_energy"]:
                if self.notificationType.get() == "Windows":
                    self.sendNoti("Windows", "EP")
                else:
                    self.sendNoti("Discord", "EP")
            time.sleep(int(delay))


sys.setrecursionlimit(5000)
window = Tk()
mywin = MyWindow(window)

with open(f'./data/key.txt', 'r') as f:
    key = f.read()
if key != "":
    mywin.readKey(key)

with open(f'./data/hook.txt', 'r') as f:
    key = f.read()
if key != "":
    mywin.readHook(key)

window.title(f'SimpleMMO Notifications Tool')
window.iconbitmap('./data/logo.ico')
window.geometry("500x200")
window.mainloop()
