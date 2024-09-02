import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import sqlite3
import pyaudio
import soundfile as sf
import wave
from six_Module import ASR_ZH,ASR_EN
from text1 import Chinese_to_English
from text2 import dialog
from text3 import English_to_Chinese
from tqdm import tqdm
from PIL import Image, ImageTk
import time
import os
import pygame
from tkinter.messagebox import askyesno

class microphone_button(tk.Button):
    def __init__(self, master=None, chunk=3024, frmat=pyaudio.paInt16, channels=1, rate=16000, py=pyaudio.PyAudio()):
        super().__init__(master)
        self.put_placeholder()
        self['relief'] = "flat"
        self['bg'] = '#63493C'
        self['width'] = 45
        self['height'] = 35
        self['command'] = lambda: self.foc_in()
        self['highlightbackground']='#63493C'
        self.place(x=32, y=35)
        self.CHUNK = chunk
        self.FORMAT = frmat
        self.CHANNELS = channels
        self.RATE = rate
        self.p = py
        self.frames = []
        self.st = 1
        self.stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        
    def put_placeholder(self):
        self.filename = "tkimage/aotbt-h86b0n.png"
        self.img = Image.open(self.filename)
        self.resized_img = self.img.resize((60, 40))
        self.photoimg = ImageTk.PhotoImage(self.resized_img)
        self['image'] = self.photoimg
        global transmit
        transmit = True

    def foc_in(self, *args):
        if  fname.get():
            if self.filename == "tkimage/aotbt-h86b0n.png":
                self.filename = "tkimage/ah21l-um7he.png"
                self.img = Image.open(self.filename)
                self.resized_img = self.img.resize((33, 40))
                self.photoimg = ImageTk.PhotoImage(self.resized_img)
                self['image'] = self.photoimg
                global transmit
                transmit = False
                self.start_record()
            else:
                self.put_placeholder()
                self.stop()
        else:
            messagebox.showerror('persona','請選擇人物')      
            
    def start_record(self):
        self.st = 1
        self.frames = []
        
        stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        while self.st == 1:
            data = stream.read(self.CHUNK)
            self.frames.append(data)
            print("* recording")
            root.update()
        stream.close()
        
        wf = wave.open('tkaudio/remote/mic_input.wav', 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        if radioValue.get() == 1:
            remote_zh_text = ASR_ZH('tkaudio/remote/mic_input.wav')
            Choose_Chinese(remote_zh_text)
        else:
            remote_zh_text = ASR_EN('tkaudio/remote/mic_input.wav')
            Choose_English(remote_zh_text)
    def stop(self):
        self.st = 0
        print("stop")


# def closeWindow():
#     ans = askyesno(title='Warning',message='Close the window?')
#     if ans:
#         root.destroy()
#     else:
#         return
def create_setting_window():
    #參數設定畫面
    window1 = tk.Toplevel(root)
    window1.title('參數設定')
    window1.wm_attributes("-topmost", 1) #讓子放窗保持在上面
    #window1.protocol('WM_DELETE_WINDOW', closeWindow)
    div1 = tk.Frame(window1)
    div2 = tk.Frame(window1, borderwidth=2, relief="ridge")
    div3 = tk.Frame(window1, borderwidth=2, relief="ridge")
    
    div1.grid(column=0, row=0, padx=20, pady=10)
    div2.grid(column=0, row=1, pady=10)
    div3.grid(column=0, row=2, pady=10)
    
    #div1選擇人物-----------------------------
    tk.Label(div1, text="選擇人物：", font=('', 12)).grid(column=0, row=0)
    
    cbox_person = ttk.Combobox(div1)
    cbox_person.grid(column=1, row=0, pady=10)
    name = [i[0] for i in cur.execute("SELECT pName FROM person")]
    cbox_person['values'] = name
    cbox_person.bind('<<ComboboxSelected>>', lambda event:combobox_selected(event,cbox_person.current(),cbox_person.get()))
    
    #div2(不會說模組)--------------------------
    tk.Checkbutton(div2, text='顯示中文語音辨識文字', font=('', 12), variable=chkValue1, command=Use_zhtextbox, selectcolor="LightGray").grid(column=0, row=0, sticky="w", padx=25)
    tk.Checkbutton(div2, text='顯示中文-英文文字翻譯', font=('', 12), variable=chkValue2, command=Use_zhtextbox, selectcolor="LightGray").grid(column=0, row=1, sticky="w", padx=25)
    tk.Checkbutton(div2, text='輸出中文-英文語音翻譯', font=('', 12), variable=chkValue3, command=zhplay_sound, selectcolor="LightGray").grid(column=0, row=2, sticky="w", padx=25)
    
    #div3(聽不懂、看不懂模組)--------------------
    tk.Checkbutton(div3, text='顯示英文-中文文字翻譯', font=('', 12), variable=chkValue4, command=Use_entextbox, selectcolor="LightGray").grid(column=0, row=0, sticky="w", padx=25)
    tk.Checkbutton(div3, text='輸出英文-中文語音翻譯', font=('', 12), variable=chkValue5, command=enplay_sound, selectcolor="LightGray").grid(column=0, row=1, sticky="w", padx=25)
    tk.Checkbutton(div3, text='顯示英文難字查詢', font=('', 12), variable=chkValue6, command=Use_entextbox, selectcolor="LightGray").grid(column=0, row=2, sticky="w", padx=25)

def combobox_selected(event,x1,x2):
    fname.set(str(x2))
    xx = 'p'+str(x1+1).zfill(4)
    global persona, number_sentence
    persona = [item[0] for item in cur.execute("SELECT persona FROM persona where pId='%s'" % xx)]
    for i in range(3):
        zh_use[i] = ''
        en_use[i] = ''
    Use_entextbox()
    while number_sentence > 0:
        globals()['frame2_'+str(number_sentence)].destroy()
        number_sentence -= 1
def Use_zhtextbox():
    mssage = ""
    if chkValue1.get() and zh_use[0] != '':
        mssage += zh_use[0]
    if chkValue2.get() and zh_use[1] != '':
        mssage += zh_use[1]

    zh_text.delete(1.0,tk.END)
    zh_text.insert(tk.INSERT,mssage)

def Use_entextbox():
    mssage = ""
    if chkValue4.get() and en_use[0] != '':
        mssage += en_use[0]
    if chkValue6.get() and en_use[1] != '':
        mssage += en_use[1]

    zh_text.delete(1.0,tk.END)
    zh_text.insert(tk.INSERT,mssage)

def zhplay_sound():
    if chkValue3.get() and zh_use[2] != '':
        pygame.mixer.init()
        pygame.mixer.music.load(zh_use[2])
        pygame.mixer.music.play()
    
def enplay_sound():
    if chkValue5.get() and en_use[2] != '':
        pygame.mixer.music.load(en_use[2])
        pygame.mixer.music.play()

class EntryWithPlaceholder(tk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey'):
        super().__init__(master)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['bg']
        self['relief'] = "flat"
        self['font'] = ('', 14)
        self['width'] = 28
        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)
        self.bind("<Return>", self.callback)
        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['bg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['bg'] == self.placeholder_color:
            self.delete('0', 'end')

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()
    
    def callback(self, *args):
        text_transfer()
        self.delete('0', 'end')

def text_transfer():
    if fname.get():
        if transmit:
            if remote_text.get():
                if radioValue.get() == 1:
                    #選擇中文
                    Choose_Chinese(remote_text.get())
                else:
                    #選擇英文
                    Choose_English(remote_text.get())
    else:
        messagebox.showerror('persona','請選擇人物')

def Choose_Chinese(x):
    value1, value2, value3 = Chinese_to_English(x)
    zh_use[0] = value1+"\n"
    zh_use[1] = value2+"\n"
    sf.write("tkaudio/remote/zh/en_audio.wav", value3.to('cpu').detach().numpy()[0], 22050)
    zh_use[2] = 'tkaudio/remote/zh/en_audio.wav'
    Use_zhtextbox()
    zhplay_sound()

def Choose_English(x):
    global number_sentence
    try:
        #使用者輸入
        number_sentence += 1
        remote_dialog(x)
        Use_zhtextbox()
        

        #系統輸出
        number_sentence += 1
        history.append(x)
        value2, value3 = dialog(persona, history)
        history.append(value2)
        local_dialog(value2)
        filepath = "tkaudio/local/en/en_audio"+str(number_sentence)+".wav"
        sf.write(filepath, value3.to('cpu').detach().numpy()[0], 22050)
        

        if os.path.isfile(filepath):
            pygame.mixer.init()
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
        else:
            print("檔案不存在。")
        
        #系統輸出翻譯
        a, b, c = English_to_Chinese(value2)
        sf.write("tkaudio/local/zh/zhaudio.wav", c.to('cpu').detach().numpy()[0], 22050)
        en_use[0] = a+"\n"
        en_use[1] = b+"\n"
        en_use[2] = 'tkaudio/local/zh/zhaudio.wav'
        Use_entextbox()
        enplay_sound()
        
    except:
            print("...")
    

def remote_dialog(x):
    #對話框架(撥放按鈕+文字框+三角形)
    globals()['frame2_'+str(number_sentence)] = tk.Frame(frame,  bg="#c4b3ab")
    globals()['frame2_'+str(number_sentence)].pack(side='top',anchor='e',padx=10,pady=10)
    #文字框
    globals()['message_'+str(number_sentence)]= tk.Message(globals()['frame2_'+str(number_sentence)],text=x,font=("",14),bg="#e1d4c4",width=300,borderwidth = 3)
    globals()['message_'+str(number_sentence)].pack(side='right')

    #播放按鈕
    # globals()['message_'+str(number_sentence)]= tk.Canvas(globals()['frame2_'+str(number_sentence)], width=35, height=35, bg="#c4b3ab", highlightbackground="#c4b3ab")
    # globals()['message_'+str(number_sentence)].create_oval(5, 5, 30, 35, fill='#c4b3ab', outline='#63493C',width=3) # 圓形
    # points = [15, 15, 21, 20, 15, 25]
    # globals()['message_'+str(number_sentence)].create_polygon(points, outline='#63493C', fill='#63493C')
    # globals()['message_'+str(number_sentence)].pack(side='right')
    
def local_dialog(x):
    #對話框架(撥放按鈕+文字框+三角形)
    globals()['frame2_'+str(number_sentence)] = tk.Frame(frame,  bg="#c4b3ab",width=450,height=50)
    globals()['frame2_'+str(number_sentence)].pack(side='top',anchor='w',padx=15,pady=10)
    globals()['frame2_'+str(number_sentence)].propagate(0)
    #文字框
    globals()['message_text'+str(number_sentence)]= tk.Message(globals()['frame2_'+str(number_sentence)],text=x,font=("",14),bg="#ffffff",width=300,borderwidth = 3)
    globals()['message_text'+str(number_sentence)].pack(side='left')

    #播放按鈕
    globals()['message_voice'+str(number_sentence)]= tk.Canvas(globals()['frame2_'+str(number_sentence)], width=35, height=35, bg="#c4b3ab", highlightbackground="#c4b3ab")
    globals()['message_voice'+str(number_sentence)].create_oval(5, 5, 30, 35, fill='#c4b3ab', outline='#63493C',width=3) # 圓形
    points = [15, 15, 21, 20, 15, 25]
    globals()['message_voice'+str(number_sentence)].create_polygon(points, outline='#63493C', fill='#63493C')
    globals()['message_voice'+str(number_sentence)].pack(side='left')
    globals()['message_voice'+str(number_sentence)].bind('<Button-1>', print('~!~!!!'))
if __name__ == "__main__":
    con = sqlite3.connect('dialog.db')      # 連線到資料庫檔案
    cur = con.cursor()                      # 建立cursoe物件

    #主畫面-------------------------------------------------------------------------------------
    root = tk.Tk()
    root.title('英語會話輔助學習系統')
    frame1 = tk.Frame(root, width=500, height=50,  bg="#63493C", borderwidth=2)
    frame2 = tk.Frame(root, width=500, height=350, bg="#c4b3ab", borderwidth=2, relief="ridge")
    frame3 = tk.Frame(root, width=500, height=100, bg="#c4b3ab", borderwidth=2)
    frame4 = tk.Frame(root, width=500, height=100, bg="#EBE4DC", borderwidth=2)

    canvas=tk.Canvas(frame2,bg="#c4b3ab")
    frame=tk.Frame(canvas,bg="#c4b3ab",width=500, height=300)
    myscrollbar=tk.Scrollbar(frame2,orient="vertical",command=canvas.yview)
    canvas.configure(yscrollcommand=myscrollbar.set)
    myscrollbar.pack(side="right",fill="y")
    canvas.pack(side="left")
    canvas.create_window((0,0),window=frame,anchor='nw')
    frame.bind("<Configure>",lambda event:[canvas.configure(scrollregion=canvas.bbox("all"),width=500,height=350),canvas.yview_moveto(1)])
    
    frame1.grid(column=0, row=0)
    frame2.grid(column=0, row=1)
    frame3.grid(column=0, row=2)
    frame4.grid(column=0, row=3)
    
    #參數設定畫面
    chkValue1 = tk.BooleanVar()
    chkValue2 = tk.BooleanVar()
    chkValue3 = tk.BooleanVar()
    chkValue4 = tk.BooleanVar()
    chkValue5 = tk.BooleanVar()
    chkValue6 = tk.BooleanVar()
    create_setting_window()
    
    #框架1----------------------------------------------------------------------------------
    fname = tk.StringVar()
    #名子
    First_name = tk.Label(frame1, textvariable=fname, fg="white", bg="#63493C", font=('',14,"bold")).place(x=8, y=10)
    #參數設定按鈕
    fil_setting = 'tkimage/wrench.png'
    img1 = Image.open(fil_setting)
    resized = img1.resize((30, 30))
    frame1.photoimg = ImageTk.PhotoImage(resized)
    setting_but = tk.Button(frame1, image=frame1.photoimg, command=create_setting_window,highlightbackground='#63493C', bg='#63493C', relief="flat", width=25, height=25)
    setting_but.place(x=460, y=9)
    
    #框架2-----------------------------------------------------------------------------------
    number_sentence = 0
    history=[]
    persona=[]
    frame2.propagate(0) #使用pack時，避免frame縮小
    #框架3-----------------------------------------------------------------------------------
    radioValue = tk.IntVar()

    #中文、英文按鈕
    zh_rbtn = tk.Radiobutton(frame3, text="中文", width=10, height=2, variable=radioValue, value=1, indicatoron=0)
    en_rbtn = tk.Radiobutton(frame3, text="英文", width=10, height=2, variable=radioValue, value=0, indicatoron=0)
    
    #中文文字顯示框
    zh_text = tk.Text(frame3, width=34, height=4, font=('', 14))
    zh_use = ["","",""]
    en_use = ["","",""]
    #元件位置
    zh_rbtn.place(x=10, y=5)
    en_rbtn.place(x=10, y=50)
    zh_text.place(x=100, y=5)
    #框架4------------------------------------------------------------------------------------
    remote_input_text = tk.StringVar()
    
    #麥克風
    mycanvas1 = tk.Canvas(frame4, width=100, height=100, bg="#EBE4DC", highlightbackground="#EBE4DC")
    mycanvas1.create_oval(20, 10, 90, 80, fill='#63493C', outline='#63493C') # 圓形
    labelimage = microphone_button(frame4)
    transmit = True
    
    #對話框
    mycanvas3 = tk.Canvas(frame4, width=385, height=10, bg="#EBE4DC", highlightbackground="#EBE4DC")
    mycanvas3.create_line(5, 5,385,5)
    remote_text = EntryWithPlaceholder(frame4, "Type a Message", '#EBE4DC')
    
    #傳送按鈕
    mycanvas2 = tk.Canvas(frame4, width=40, height=50, bg="#EBE4DC", highlightbackground="#EBE4DC")
    mycanvas2.create_oval(5, 10, 40, 50, fill='#63493C', outline='#63493C') # 圓形
    file_send = 'tkimage/ak3bn-z6k3z.png'
    img_send = Image.open(file_send)
    resized_send = img_send.resize((20, 20))
    frame4.photoimg = ImageTk.PhotoImage(resized_send)
    send_but = tk.Button(frame4, image=frame4.photoimg, bg='#63493C',highlightbackground='#63493C', command=text_transfer, relief="flat", width=20, height=20)
    send_but.place(x=449, y=48)
    
    #元件位置
    mycanvas1.place(x=1, y=10)
    mycanvas2.place(x=440, y=30)
    mycanvas3.place(x=100, y=10)
    remote_text.place(x=110, y=47)
    

    root.mainloop()