import tkinter as tk
import sqlite3

def delete_persona():
    cur.execute("DELETE FROM persona WHERE pId=? and persona=?", (pid.get(), persona_index_text))
    con.commit()
    ltbx_persona.delete(persona_index)
    persona_text.set("")
    
def update_persona():
    persona = [i[0] for i in cur.execute("SELECT persona FROM persona WHERE pId=?", (pid.get(), ))]
    if persona_text.get():
        if persona_text.get() not in persona:
            ltbx_persona.delete(persona_index)
            ltbx_persona.insert(persona_index, persona_text.get())
            cur.execute("UPDATE persona set persona=? WHERE pId=? and persona=?", (persona_text.get(), pid.get(), persona_index_text))
            con.commit()
            persona_text.set("")
        else:
            tk.messagebox.showerror('persona修改','persona已存在')
    else:
        tk.messagebox.showerror('persona修改','persona不能是空值')
        
def add_persona():
    persona = [i[0] for i in cur.execute("SELECT persona FROM persona WHERE pId=?", (pid.get(), ))]
    if persona_text.get():
        if persona_text.get() not in persona:
            cur.execute("INSERT INTO persona (pId,persona) VALUES (?, ?)", (pid.get(), persona_text.get()))
            con.commit()
            select_pId(pid.get())
            persona_text.set("")
        else:
            tk.messagebox.showerror('persona新增','persona已存在')
    else:
        tk.messagebox.showerror('persona新增','請輸入persona')
        
def delete_person(): # 刪除person
    x = pid.get()
    total = [i[0] for i in cur.execute("SELECT pId FROM person WHERE pId>?", (x, ))]
    cur.execute("DELETE FROM person WHERE pId=?", (x, ))
    cur.execute("DELETE FROM persona WHERE pId=?", (x, ))
    con.commit()
    
    for i in total:
        up = "p"+str(int(i.split('p')[1])-1).zfill(4)
        cur.execute("UPDATE person set pId=? WHERE pId=?", (up, i))
        cur.execute("UPDATE persona set pId=? WHERE pId=?", (up, i))
        con.commit()
    x = "p"+str(int(x.split('p')[1])-1).zfill(4)
    select_pId(x)
    
def update_person(): # 更新person
    if pname_text.get():
        name = [i[0] for i in cur.execute("SELECT pName FROM person")]
        if pname_text.get() not in name:
            cur.execute("UPDATE person set pName=? WHERE pId=?", (pname_text.get(), pid_text.get()))
            con.commit()
            select_pId(pid_text.get())
            app.destroy()
            pname_text.set("")
        else:
            tk.messagebox.showerror('person修改','pName已存在')
    else:
        tk.messagebox.showerror('person修改','請輸入pName')

def add_person(): # 新增person
    if pname_text.get():
        name = [i[0] for i in cur.execute("SELECT pName FROM person")]
        if pname_text.get() not in name:
            cur.execute("INSERT INTO person (pId,pName) VALUES (?, ?)", (pid_text.get(), pname_text.get()))
            con.commit()
            select_pId(pid_text.get())
            app.destroy()
            pname_text.set("")
        else:
            tk.messagebox.showerror('person新增','pName已存在')
    else:
        tk.messagebox.showerror('person新增','請輸入pName')

def select_person(): # 查詢person
    name = [i[0] for i in cur.execute("SELECT pName FROM person where pId='%s'" % pid_text.get())]
    if name:
        if pid_text.get() and pname_text.get():
            if name[0] == pname_text.get():
                 select_pId(pid_text.get())
                 app.destroy()
            else:
                tk.messagebox.showerror('person查詢','輸入錯誤')
        elif pid_text.get():
            select_pId(pid_text.get())
            app.destroy()
    else:
        if pname_text.get():
            x = [i[0] for i in cur.execute("SELECT pId FROM person where pName='%s'" % pname_text.get())]
            if x:
                select_pId(x[0])
                app.destroy()
            else:
                tk.messagebox.showerror('person查詢','查無此輸入')
        else:
            tk.messagebox.showerror('person查詢','查無此輸入')
    
def create_person_element(mode):
    global app
    if app.winfo_exists() == 1:
        app.deiconify()
    else:
        app = tk.Toplevel()
    for widget in app.winfo_children():
        widget.destroy()
    app.wm_attributes("-topmost", 1) #讓子放窗保持在上面
    app_head = tk.Label(app, textvariable=app_text1, font=('', 16), width=30, height=2).grid(column=0, columnspan=2, row=0, pady=20)
    app_explain = tk.Label(app, textvariable=app_text2, font=('', 12)).grid(column=0, columnspan=2, row=1)
    tk.Label(app, text="pId", font=('', 12)).grid(column=0, row=2, pady=30)
    tk.Label(app, text="pName", font=('', 12)).grid(column=0, row=3)
    app_pId = tk.Entry(app, textvariable=pid_text, width=20, font=('', 12)).grid(column=1,row=2)
    app_pName = tk.Entry(app, textvariable=pname_text, width=20, font=('', 12)).grid(column=1,row=3)
    tk.Button(app, text='確定', width=12, command=lambda x=mode : select_person() if x==0 else (add_person() if x==1 else update_person())).grid(column=0, columnspan=2, row=4, pady=30)
        
def person_admin(mode):
    create_person_element(mode)
    
    if mode == 0:  # 搜尋
        pid_text.set("")
        pname_text.set("")
    elif mode == 1:  # 新增
        pname.set("")
        count = [i[0] for i in cur.execute("SELECT count(*) FROM person")] #
        count = count[0]
        num_add = "p"+str(count+1).zfill(4)
        pid_text.set(str(num_add))
        app_pId = tk.Entry(app,textvariable=pid_text, width=20, font=('', 12), state='disabled').grid(column=1,row=2)
    elif mode == 2: # 修改
        pid_text.set(pid.get())
        app_pId = tk.Entry(app,textvariable=pid, width=20, font=('', 12), state='disabled').grid(column=1,row=2)
    else: # 刪除
        print("")
    
    app_head_text = ["搜尋person", "新增person", "修改person"]
    app_explain_text = ["輸入pId或pName", "輸入pName", "修改pName"]
    app_text1.set(app_head_text[mode])
    app_text2.set(app_explain_text[mode])
    
#查詢紀錄
def select_record(num):
    x = int(current_pId.split('p')[1])
    count = [i[0] for i in cur.execute("SELECT count(*) FROM person")] #
    count = count[0]
    
    if num == "1":
        select_pId("p0001")
    elif num == "0":
        pId = "p"+str(count).zfill(4)
        select_pId(pId)
    elif num == "-1":
        if x != 1:
            x -= 1
            pId = "p"+str(x).zfill(4)
            select_pId(pId)
    else:
        if count != x:
            x += 1
            pId = "p"+str(x).zfill(4)
            select_pId(pId)

#查詢pId，放入pId、pName、persona
def select_pId(pId):
    global current_pId
    current_pId = pId
    pid.set(pId)
    name = [i[0] for i in cur.execute("SELECT pName FROM person where pId='%s'" % pId)]
    pname.set(name[0])
    
    ltbx_persona.delete(0, tk.END)
    personas = [item[0] for item in cur.execute("SELECT persona FROM persona where pId='%s'" % pId)]
    for persona in personas:
        ltbx_persona.insert(tk.END, persona)

def show(event):
    # 取得事件對象object
    object = event.widget
    # 取得所選的項目索引
    index = object.curselection()
    global persona_index
    for i in index:
        persona_index = i
    # 由索引取得所選的項目，關聯到label中
    persona_text.set(object.get(index))
    global persona_index_text
    persona_index_text = object.get(index)
#初始化
def __init__():
    pId = "p0001"
    select_pId(pId)


if __name__ == "__main__":
    con = sqlite3.connect('dialog.db')      # 連線到資料庫檔案
    cur = con.cursor()                      # 建立cursoe物件
    
    window = tk.Tk()
    window.title('persona管理')
    pid = tk.StringVar()
    pname = tk.StringVar()
    persona_text = tk.StringVar()
    current_pId = ""
    persona_index = 0
    persona_index_text = ""
    
    app = tk.Toplevel()
    app.withdraw()
    app_text1 = tk.StringVar()
    app_text2 = tk.StringVar()
    pid_text = tk.StringVar()
    pname_text = tk.StringVar()
    
    #標頭
    lab_head = tk.Label(window, text="  persona", bg='LightBlue', fg = "DimGray", anchor="nw", font=('', 20), width=40, height=3)
    lab_head.grid(column=0, row=0, columnspan=8, rowspan=2)
    
    #null
    lab_null = tk.Label(window, text="", font=('', 12)).grid(column=2, row=2)
    
    #顯示pid、pname
    tk.Label(window, text="pId", font=('', 12)).grid(column=1, row=3, sticky="w", padx=20)
    lab_pId = tk.Label(window, textvariable=pid, font=('', 12), bg="white", borderwidth=2, relief="ridge", anchor="w", width=20
                        ).grid(column=2, row=3, columnspan=3, sticky="w", pady=10)
    
    tk.Label(window, text="pName", font=('', 12)).grid(column=1, row=4, sticky="w", pady=5, padx=20)
    ent_pname = tk.Entry(window,textvariable=pname, width=23, font=('', 12)).grid(column=2, columnspan=3, row=4, sticky="w")
    
    #顯示persona
    lab_persona = tk.Label(window, text="persona", font=('', 12)).grid(column=1, row=5, sticky="w", padx=20)
    ltbx_persona = tk.Listbox(window, width=30)
    ltbx_persona.bind("<<ListboxSelect>>", show)
    ltbx_persona.grid(column=1, row=6, rowspan=5, columnspan=10, sticky="w", ipadx=90, padx=20)
    
    #persona輸入
    tk.Label(window, text="persona輸入：", font=('', 12)).grid(column=1, columnspan=2, row=11, sticky="w", pady=20, padx=20)
    tk.Entry(window, textvariable=persona_text, width=30).grid(column=2, row=11, sticky="w", padx=20)
    
    tk.Button(window, text='新增Persona', command=add_persona).grid(column=1, row=12, pady=5, padx=20)
    tk.Button(window, text='修改Persona', command=update_persona).grid(column=2, row=12, pady=5)
    tk.Button(window, text='刪除Persona', command=delete_persona).grid(column=3, row=12, pady=5)
    
    #按鈕
    tk.Button(window, text='第一筆紀錄', width=12, command=lambda:select_record("1")).grid(column=6, row=3, sticky="e")
    tk.Button(window, text='最後一筆紀錄', width=12, command=lambda:select_record("0")).grid(column=6, row=4, sticky="e")
    tk.Button(window, text='前一筆紀錄', width=12, command=lambda:select_record("-1")).grid(column=6, row=5, sticky="e", pady=5)
    tk.Button(window, text='下一筆紀錄', width=12, command=lambda:select_record("+1")).grid(column=6, row=6, sticky="e")
    
    tk.Button(window, text='尋找Person', width=12, command=lambda:person_admin(0)).grid(column=6, row=7, sticky="e")
    tk.Button(window, text='新增Person', width=12, command=lambda:person_admin(1)).grid(column=6, row=8, sticky="e")
    tk.Button(window, text='修改Person', width=12, command=lambda:person_admin(2)).grid(column=6, row=9, sticky="e")
    tk.Button(window, text='刪除Person', width=12, command=lambda:delete_person()).grid(column=6, row=10, sticky="e")
    __init__()
    window.mainloop()
    con.close()
    