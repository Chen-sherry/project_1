import pymysql
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import socket
from pymysql.err import OperationalError
import time

class Login_Windows:
    def __init__(self,root):
        self.root = root
        self.root.title("登录")
        self.root.geometry("300x200")
        self.try_count = 5

        tk.Label(root,text="用户名").pack(pady=5)
        self.entry_user = tk.Entry(root)
        self.entry_user.pack()

        tk.Label(root,text='密码').pack(pady=5)
        self.entry_passwd = tk.Entry(root)
        self.entry_passwd.pack()

        tk.Button(root,text='登录',command=self.check_login).pack(pady=10)

        self.DB = None

    def check_login(self):
        user = self.entry_user.get().strip()
        password = self.entry_passwd.get().strip()

        if not user or not password:
            messagebox.showerror('错误','用户名或密码不能为空')
            return

        try:
            self.DB = DB(user,password)
            messagebox.showinfo('成功','登录成功')
            self.DB.log('None','登录')
            self.DB.conn.commit()
            self.root.destroy()
            self.open_main()

        except OperationalError as e:
            self.try_count -= 1
            if e.args[0] == 1045:
                messagebox.showerror('失败','用户名或密码错误\n剩余'+str(self.try_count)+'次机会')
            else:
                messagebox.showerror('错误','未知错误'+str(e))

            if self.try_count <= 0:
                messagebox.showerror('退出','错误次数过多,退出中...')
                time.sleep(2)
                self.root.quit()

    def open_main(self):
        main_root = tk.Tk()
        MainWindow(main_root,self.DB)
        main_root.mainloop()

class DB:
    def __init__(self,user,password):
            self.user = user
            self.conn = pymysql.connect(
                host='8.163.39.232',
                user=user,
                password=password,
                database='studentsscore',
                charset='utf8'
            )
            self.cursor = self.conn.cursor()

    def close(self):
        self.log('None','登出')
        self.conn.commit()
        self.conn.close()
        self.cursor.close()

    @staticmethod
    def get_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"

    def log(self,id,operation):
        oper_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_sql = 'insert into log(id,user,operation,time,ip) values(%s,%s,%s,%s,%s)'
        self.cursor.execute(log_sql, (id,self.user, operation, oper_time, self.get_ip()))

    def db_add_student(self,name,gender,age):
        try:
            sql = 'insert into student(stu_name,stu_gender,stu_age) values (%s,%s,%s)'
            self.cursor.execute(sql,(name,gender,age))
            new_id = self.cursor.lastrowid
            self.log('s'+str(new_id),'添加学生')
            self.conn.commit()
            return new_id
        except OperationalError as e:
            self.conn.rollback()
            return e

    def db_add_teacher(self,name,course):
        try:
            sql = 'insert into teacher(tch_name,tch_course) values (%s,%s)'
            self.cursor.execute(sql, (name, course))
            new_id = self.cursor.lastrowid
            self.log( 't' + str(new_id), '添加教师')
            self.conn.commit()
            return new_id
        except OperationalError as e:
            self.conn.rollback()
            return e

    def db_select_score(self,id):
        try:
            sql = 'select * from score where stu_id = %s'
            self.cursor.execute(sql,(id,))
            res = self.cursor.fetchall()
            self.log('s'+str(id),'查询成绩')
            self.conn.commit()
            if len(res) == 0:
                sql = 'select id from student where stu_id = %s'
                self.cursor.execute(sql,(id,))
                res_1 = self.cursor.fetchall()
                if len(res_1) == 0:
                    return 0
                else:
                    return 1
            else:
                return res
        except OperationalError as e:
            self.conn.rollback()
            return e

    def db_add_score(self,id,chinese,math,english,tch_id,num):
        try:
            sql = 'select * from student where stu_id=%s'
            self.cursor.execute(sql,(id,))
            temp = self.cursor.fetchall()
            if len(temp) == 0:
                return 'id不存在'
            sql = 'select * from teacher where tch_id = %s and tch_statc = 1'
            self.cursor.execute(sql,(tch_id,))
            temp = self.cursor.fetchall()
            if len(temp) == 0:
                return '改卷教师id不存在'
            sql = 'select * from score where stu_id = %s and num = %s'
            self.cursor.execute(sql,(id,num))
            temp = self.cursor.fetchall()
            if len(temp) != 0:
                return '该次考试已录入成绩'
            sql = 'insert into score(stu_id,chinese,math,english,tch_id,sco_num) values (%s,%s,%s,%s,%s,%s)'
            self.cursor.execute(sql,(id,chinese,math,english,tch_id,num))
            self.log(id,'录入成绩')
            self.conn.commit()
            return "录入成功"
        except OperationalError as e:
            self.conn.rollback()
            return e

    def db_delete_student(self,id):
        try:
            sql = 'select * from student where stu_id = %s'
            self.cursor.execute(sql,(id,))
            res = self.cursor.fetchall()
            if len(res) == 0:
                messagebox.showerror('删除失败','学生不存在')
            sql = 'select * from score where stu_id = %s'
            self.cursor.execute(sql,(id,))
            if len(self.cursor.fetchall()) != 0:
                if messagebox.askyesno('存在记录','学生存在成绩记录\n是否继续删除(不保留成绩)'):
                    sql = 'delete from student where stu_id = %s'
                    self.cursor.execute(sql,(id,))
                    sql = 'delete from score where stu_id = %s'
                    self.cursor.execute(sql,(id,))
                    self.log('s'+str(id),'删除学生')
                    self.conn.commit()
                    messagebox.showinfo('删除成功','学生删除成功')
                else:
                    messagebox.showinfo('未删除','返回上级')
            else:
                sql = 'delete from student where stu_id = %s'
                self.cursor.execute(sql,(id,))
                self.log('s'+str(id),'删除学生')
                self.conn.commit()
                messagebox.showinfo('删除成功','学生删除成功')
        except OperationalError as e:
            self.conn.rollback()
            messagebox.showerror('未知错误',str(e))

    def db_delete_teacher(self,id):
        try:
            sql = 'select * from teacher where tch_id = %s and tch_state = 1'
            self.cursor.execute(sql,(id,))
            res = self.cursor.fetchall()
            if len(res) == 0:
                messagebox.showerror('删除失败','教师不存在')
            else:
                sql = 'update teacher set tch_state=0 where tch_id=%s'
                self.cursor.execute(sql,(id,))
                self.log('t'+str(id),'删除教师')
                self.conn.commit()
                messagebox.showinfo('删除成功','教师删除成功')
        except OperationalError as e:
            self.conn.rollback()
            messagebox.showerror('未知错误',str(e))

    def db_change_student(self,id,name,gender,age):
        try:
            sql = 'select * from student where stu_id = %s'
            self.cursor.execute(sql,(id,))
            re = self.cursor.fetchall()
            if len(re) == 0:
                return 0
            sql = 'update student set stu_name = %s,stu_gender = %s,stu_age = %s where stu_id = %s'
            self.cursor.execute(sql,(name,gender,age,id))
            self.log('s'+str(id),'修改学生信息')
            self.conn.commit()
            return 1
        except OperationalError as e:
            self.conn.rollback()
            return e

    def db_change_teacher(self,id,name,course):
        try:
            sql = 'select * from teacher where tch_id = %s and tch_state = 1'
            self.cursor.execute(sql,(id,))
            res = self.cursor.fetchall()
            if len(res) == 0:
                return 0
            sql = 'update teacher set tch_name = %s,tch_course = %s where tch_id = %s'
            self.cursor.execute(sql,(name,course,course))
            self.log('t'+str(id),'修改教师信息')
            self.conn.commit()
            return 1
        except OperationalError as e:
            self.conn.rollback()
            return e

    def db_change_score(self,id,chinese,math,english,tch_id,num):
        try:
            sql = 'select * from score where stu_id = %s and sco_num = %s'
            self.cursor.execute(sql,(id,num))
            re = self.cursor.fetchall()
            if len(re) == 0:
                return 0
            sql = 'update score set chinese = %s, math = %s, english = %s, tch_id = %s where stu_id = %s and sco_num = %s'
            self.cursor.execute(sql,(chinese,math,english,tch_id,id,num))
            self.log('s'+str(id),'修改成绩')
            self.conn.commit()
            return 1
        except OperationalError as e:
            self.conn.rollback()
            return e

    def db_select_student(self,id):
        try:
            sql = 'select * from student where stu_id = %s'
            self.cursor.execute(sql,(id,))
            res = self.cursor.fetchall()
            if len(res) == 0:
                return 0
            else:
                self.log('s' + str(id), '查询学生')
                self.conn.commit()
                return res
        except OperationalError as e:
            self.conn.rollback()
            return e

    def db_select_teacher(self,id):
        try:
            sql = 'select * from teacher where tch_id = %s and tch_state = 1'
            self.cursor.execute(sql,(id,))
            res = self.cursor.fetchall()
            if len(res) == 0:
                return 0
            else:
                self.log('t'+str(id),'查询教师')
                self.conn.commit()
                return res
        except OperationalError as e:
            self.conn.rollback()
            return e

    def db_select_once_score(self,id,num):
        try:
            sql = 'select * from score where stu_id = %s and sco_num = %s'
            self.cursor.execute(sql,(id,num))
            re = self.cursor.fetchall()
            if len(re) == 0:
                return 0
            self.log('s'+str(id),'查询成绩')
            self.conn.commit()
            return re
        except OperationalError as e:
            self.conn.rollback()
            return e

class MainWindow:
    def __init__(self,root,db):
        self.root = root
        self.DB = db
        self.root.title('主界面')
        self.root.geometry("600x500")
        self.menu()
        self.root.protocol("WM_DELETE_WINDOW", self.close_main)

    def menu(self):
        self.buttons = [
            " 1. 添加学生",
            " 2. 添加教师",
            " 3. 查询成绩",
            " 4. 录入成绩",
            " 5. 删除学生",
            " 6. 删除教师",
            " 7. 修改学生信息",
            " 8. 修改教师信息",
            " 9. 修改学生成绩",
            "10. 查询学生信息",
            "11. 查询教师信息",
            "12. 退出系统"
        ]
        col = 0
        row = 0
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        for idx,text in enumerate(self.buttons,1):
            btn = tk.Button(self.root,
                            text=text,
                            width=18,
                            command=lambda num=idx: self.click_btn(num)
                            )
            btn.grid(row=row,column=col,padx=10, pady=10)

            col += 1
            if col == 2:
                col = 0
                row += 1
        for r in range(row + 1):
            self.root.grid_rowconfigure(r, weight=1)

    def close_main(self):
        try:
            self.DB.log('None','登出')
            self.DB.conn.commit()
        except:
            pass
        self.DB.close()
        self.root.destroy()

    def click_btn(self,num):
        if num != 12:
            messagebox.showinfo("菜单选择", f"你选择了功能：{self.buttons[num-1][4:]}")
            OperationWindow(self.root,self.DB,num)
        else:
            messagebox.showinfo('退出', '退出中...')
            OperationWindow(self.root,self.DB,num)

class OperationWindow:
    def __init__(self,root,db,choose):
        self.root = root
        self.DB = db
        self.choose = choose

        self.win = tk.Toplevel(self.root)
        self.win.title('功能操作')
        self.win.geometry("800x500")
        self.win.transient(self.root)
        self.win.grab_set()

        if choose==1:
            self.show_add_stu()
        elif choose==2:
            self.show_add_tch()
        elif choose==3:
            self.show_sel_sco()
        elif choose==4:
            self.show_add_sco()
        elif choose==5:
            self.show_del_stu()
        elif choose==6:
            self.show_del_tch()
        elif choose==7:
            self.show_cha_stu()
        elif choose==8:
            self.show_cha_tch()
        elif choose==9:
            self.show_cha_sco()
        elif choose==10:
            self.show_sel_stu()
        elif choose==11:
            self.show_sel_tch()
        else:
            self.exit()

    def show_add_stu(self):
        tk.Label(self.win,text='姓名:').grid(row=0,column=0,padx=10, pady=10)
        self.entry_name = tk.Entry(self.win)
        self.entry_name.grid(row=0,column=1,padx=10, pady=10)

        tk.Label(self.win,text='性别:').grid(row=1,column=0,padx=10, pady=10)
        self.var_gender = tk.StringVar(value="男")
        tk.Radiobutton(self.win,text='男',variable=self.var_gender,value='男').grid(row=1,column=1,padx=10, pady=10)
        tk.Radiobutton(self.win,text='女',variable=self.var_gender,value='女').grid(row=2,column=1,padx=10, pady=10)

        tk.Label(self.win,text='年龄:').grid(row=3,column=0,padx=10, pady=10)
        self.entry_age = tk.Entry(self.win)
        self.entry_age.grid(row=3,column=1,padx=10, pady=10)

        tk.Button(self.win,text='确认添加',command=self.add_stu).grid(row=4,column=1,padx=10, pady=10)
    def add_stu(self):
        name = self.entry_name.get()
        gender = self.var_gender.get()
        age = self.entry_age.get()

        if not name or not age:
            messagebox.showerror('错误','不能为空')
            return
        try:
            age = int(age)
        except:
            messagebox.showerror('错误','年龄必须为数字')
            return
        if 0<age<100:
            pass
        else:
            messagebox.showerror('错误','年龄输入不合理')
            return

        result = self.DB.db_add_student(name,gender,age)
        if type(result) is int:
            messagebox.showinfo('添加成功',f'学生id为{result}')
        else:
            messagebox.showerror('添加失败',f'未知错误:{result}')

    def show_add_tch(self):
        tk.Label(self.win,text='姓名:').grid(row=0,column=0,padx=10, pady=10)
        self.entry_name = tk.Entry(self.win)
        self.entry_name.grid(row=0,column=1,padx=10, pady=10)

        tk.Label(self.win, text='教学科目:').grid(row=1, column=0, padx=10, pady=10)
        self.var_course = tk.StringVar(value="语文")
        tk.Radiobutton(self.win, text='语文', variable=self.var_course, value='语文').grid(row=1, column=1, padx=10,pady=10)
        tk.Radiobutton(self.win, text='数学', variable=self.var_course, value='数学').grid(row=2, column=1, padx=10,pady=10)
        tk.Radiobutton(self.win, text='英语', variable=self.var_course, value='英语').grid(row=3, column=1, padx=10,pady=10)

        tk.Button(self.win,text='确认添加',command=self.add_tch).grid(row=4,column=1,padx=10, pady=10)
    def add_tch(self):
        name = self.entry_name.get()
        course = self.var_course.get()
        if not name:
            messagebox.showerror('错误','不能为空')
            return
        result = self.DB.db_add_teacher(name,course)
        if type(result) is int:
            messagebox.showinfo('添加成功',f'教师id为{result}')
        else:
            messagebox.showerror('添加失败',f'未知错误:{result}')

    def show_sel_sco(self):
        tk.Label(self.win,text='请输入学生id:').grid(row=0,column=0,padx=10, pady=10)
        self.entry_id = tk.Entry(self.win)
        self.entry_id.grid(row=0,column=1,padx=10, pady=10)

        tk.Label(self.win,text='请输入学生姓名:').grid(row=1,column=0,padx=10, pady=10)
        self.entry_name = tk.Entry(self.win)
        self.entry_name.grid(row=1,column=1,padx=10, pady=10)

        tk.Button(self.win,text='查询',command=self.sel_sco).grid(row=2,column=1,padx=10, pady=10)
    def sel_sco(self):
        id = self.entry_id.get()
        name = self.entry_name.get()

        if not id or not name:
            messagebox.showerror('错误','不能为空')
            return
        try:
            id = int(id)
        except:
            messagebox.showerror('错误','请输入整数id')
            return
        result = self.DB.db_select_score(id)
        if result == 0:
            messagebox.showerror('查询失败','未查询到该学生信息\n请确认输入信息')
        elif result == 1:
            messagebox.showerror('查询失败','该学生暂未考试')
        elif isinstance(result, (list, tuple)):
            for widget in self.win.winfo_children():
                if widget.winfo_y() > 100:
                    widget.destroy()

            columns = ['学生id','语文','数学','英语','批改教师id','考试次数']
            tree = ttk.Treeview(self.win,columns=columns,show='headings',height=8)

            for col in columns:
                tree.heading(col,text=col)
                tree.column(col,width=100,anchor='center')

            for row in result:
                tree.insert('','end',values=row)

            tree.grid(row=3,column=0,columnspan=2,padx=10, pady=10)

        else:
            messagebox.showerror('查询异常',f'未知错误:{result}')

    def show_add_sco(self):
        tk.Label(self.win,text='学生id:').grid(row=0,column=0,padx=10, pady=10)
        self.entry_id = tk.Entry(self.win)
        self.entry_id.grid(row=0,column=1,padx=10, pady=10)

        tk.Label(self.win, text='语文成绩:').grid(row=1, column=0, padx=10, pady=10)
        self.entry_chinese = tk.Entry(self.win)
        self.entry_chinese.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.win, text='数学成绩:').grid(row=2, column=0, padx=10, pady=10)
        self.entry_math = tk.Entry(self.win)
        self.entry_math.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(self.win, text='英语成绩:').grid(row=3, column=0, padx=10, pady=10)
        self.entry_english = tk.Entry(self.win)
        self.entry_english.grid(row=3, column=1, padx=10, pady=10)

        tk.Label(self.win,text='改卷教师id:').grid(row=4, column=0, padx=10, pady=10)
        self.entry_tch_id = tk.Entry(self.win)
        self.entry_tch_id.grid(row=4, column=1, padx=10, pady=10)

        tk.Label(self.win,text='考试次数:').grid(row=5, column=0, padx=10, pady=10)
        self.entry_num = tk.Entry(self.win)
        self.entry_num.grid(row=5, column=1, padx=10, pady=10)

        tk.Button(self.win,text='确认添加',command=self.add_sco).grid(row=6,column=1,padx=10, pady=10)
    def add_sco(self):
        id = self.entry_id.get()
        chinese = self.entry_chinese.get()
        math = self.entry_math.get()
        english = self.entry_english.get()
        tch_id = self.entry_tch_id.get()
        num = self.entry_num.get()

        if not id or not chinese or not math or not english or not tch_id or not num:
            messagebox.showerror('错误','不能为空')
            return
        try:
            id = int(id)
            chinese = int(chinese)
            math = int(math)
            english = int(english)
            tch_id = int(tch_id)
            num = int(num)
        except:
            messagebox.showerror('错误','请输入整数')
            return
        if 0<= chinese <=100 and 0<= math <=100 and 0<= english <=100 and id>0 and num>0 and tch_id>0:
             pass
        else:
            messagebox.showerror('错误','数值不合理或id不合理')
            return
        result = self.DB.db_add_score(id,chinese,math,english,tch_id,num)
        if result == 'id不存在':
            messagebox.showerror('输入错误',result)
        elif result == '改卷教师id不存在':
            messagebox.showerror('输入错误',result)
        elif result == '该次考试已录入成绩':
            messagebox.showerror('输入错误',result)
        elif result == '录入成功':
            messagebox.showinfo('录入成功',result)
        else:
            messagebox.showerror('错误',f'未知错误{result}')

    def show_del_stu(self):
        tk.Label(self.win,text='请输入学生id:').grid(row=0,column=0,padx=10, pady=10)
        self.entry_id = tk.Entry(self.win)
        self.entry_id.grid(row=0,column=1,padx=10, pady=10)

        tk.Label(self.win,text='请输入学生姓名:').grid(row=1,column=0,padx=10, pady=10)
        self.entry_name = tk.Entry(self.win)
        self.entry_name.grid(row=1,column=1,padx=10, pady=10)

        tk.Button(self.win,text='删除',command=self.del_stu).grid(row=2,column=1,padx=10, pady=10)
    def del_stu(self):
        id = self.entry_id.get()
        name = self.entry_name.get()

        if not id or not name:
            messagebox.showerror('错误', '不能为空')
            return
        try:
            id = int(id)
        except:
            messagebox.showerror('错误', '请输入整数id')
            return
        self.DB.db_delete_student(id)

    def show_del_tch(self):
        tk.Label(self.win, text='请输入教师id:').grid(row=0, column=0, padx=10, pady=10)
        self.entry_id = tk.Entry(self.win)
        self.entry_id.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.win, text='请输入教师姓名:').grid(row=1, column=0, padx=10, pady=10)
        self.entry_name = tk.Entry(self.win)
        self.entry_name.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(self.win, text='删除', command=self.del_tch).grid(row=2, column=1, padx=10, pady=10)
    def del_tch(self):
        id = self.entry_id.get()
        name = self.entry_name.get()

        if not id or not name:
            messagebox.showerror('错误', '不能为空')
            return
        try:
            id = int(id)
        except:
            messagebox.showerror('错误', '请输入整数id')
            return
        self.DB.db_delete_teacher(id)

    def show_cha_stu(self):
        tk.Label(self.win, text='请输入学生id:').grid(row=0, column=0, padx=10, pady=10)
        self.entry_id = tk.Entry(self.win)
        self.entry_id.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.win, text='请修改学生姓名:').grid(row=1, column=0, padx=10, pady=10)
        self.entry_name = tk.Entry(self.win)
        self.entry_name.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.win, text='请选择学生性别:').grid(row=2, column=0, padx=10, pady=10)
        self.var_gender = tk.StringVar(value="男")
        tk.Radiobutton(self.win, text='男', variable=self.var_gender, value='男').grid(row=2, column=1, padx=10,
                                                                                       pady=10)
        tk.Radiobutton(self.win, text='女', variable=self.var_gender, value='女').grid(row=2, column=2, padx=10,
                                                                                       pady=10)

        tk.Label(self.win, text='请修改学生年龄:').grid(row=3, column=0, padx=10, pady=10)
        self.entry_age = tk.Entry(self.win)
        self.entry_age.grid(row=3, column=1, padx=10, pady=10)

        tk.Button(self.win,text='查询当前信息',command=self.sel_stu).grid(row=4, column=1,padx=10, pady=10)
        tk.Button(self.win,text='修改信息',command=self.cha_stu).grid(row=4, column=2,padx=10, pady=10)

        messagebox.showinfo('提示', '查询信息只需要输入id\n不进行修改的信息请输入原信息')
    def cha_stu(self):
        id = self.entry_id.get()
        name = self.entry_name.get()
        gender = self.var_gender.get()
        age = self.entry_age.get()

        if not id or not name or not gender or not age:
            messagebox.showerror('错误', '不能为空')
            return
        try:
            id = int(id)
            age = int(age)
            if 0 > age or age < 100:
                messagebox.showerror('错误', '年龄不在合理范围')
                return
        except:
            messagebox.showerror('错误', '请输入整数id和年龄')
            return
        res = self.DB.db_change_student(id,name,gender,age)
        if res == 0:
            messagebox.showerror('修改失败','学生不存在')
        elif res == 1:
            messagebox.showinfo('修改成功','学生信息修改成功')
        else:
            messagebox.showerror('未知错误',res)

    def show_cha_tch(self):
        messagebox.showinfo('提示', '查询信息只需要输入id\n不进行修改的信息请输入原信息')

        tk.Label(self.win, text='请输入教师id:').grid(row=0, column=0, padx=10, pady=10)
        self.entry_id = tk.Entry(self.win)
        self.entry_id.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.win, text='请修改教师姓名:').grid(row=1, column=0, padx=10, pady=10)
        self.entry_name = tk.Entry(self.win)
        self.entry_name.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.win, text='教学科目:').grid(row=2, column=0, padx=10, pady=10)
        self.var_course = tk.StringVar(value="语文")
        tk.Radiobutton(self.win, text='语文', variable=self.var_course, value='语文').grid(row=2, column=1, padx=10,
                                                                                           pady=10)
        tk.Radiobutton(self.win, text='数学', variable=self.var_course, value='数学').grid(row=3, column=1, padx=10,
                                                                                           pady=10)
        tk.Radiobutton(self.win, text='英语', variable=self.var_course, value='英语').grid(row=4, column=1, padx=10,
                                                                                           pady=10)
        tk.Button(self.win, text='查询当前信息', command=self.sel_tch).grid(row=5, column=1, padx=10, pady=10)
        tk.Button(self.win, text='修改信息', command=self.cha_tch).grid(row=5, column=2, padx=10, pady=10)

        messagebox.showinfo('提示', '查询信息只需要输入id\n不进行修改的信息请输入原信息')
    def cha_tch(self):
        id = self.entry_id.get()
        name = self.entry_name.get()
        course = self.var_course.get()

        if not id or not name:
            messagebox.showerror('错误','不能为空')
            return
        try:
            id = int(id)
        except:
            messagebox.showerror('错误','请输入整数id')
            return
        re = self.DB.db_change_teacher(id,name,course)
        if re == 0:
            messagebox.showinfo('')

    def show_cha_sco(self):
        tk.Label(self.win, text='请输入学生id:').grid(row=0, column=0, padx=10, pady=10)
        self.entry_id = tk.Entry(self.win)
        self.entry_id.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.win, text='请输入考试次数:').grid(row=1, column=0, padx=10, pady=10)
        self.entry_num = tk.Entry(self.win)
        self.entry_num.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.win, text='请输入语文成绩:').grid(row=2, column=0, padx=10, pady=10)
        self.entry_chinese = tk.Entry(self.win)
        self.entry_chinese.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(self.win, text='请输入数学成绩:').grid(row=3, column=0, padx=10, pady=10)
        self.entry_math = tk.Entry(self.win)
        self.entry_math.grid(row=3, column=1, padx=10, pady=10)

        tk.Label(self.win, text='请输入英语成绩:').grid(row=4, column=0, padx=10, pady=10)
        self.entry_english = tk.Entry(self.win)
        self.entry_english.grid(row=4, column=1, padx=10, pady=10)

        tk.Label(self.win, text='请输入改卷教师id:').grid(row=5, column=0, padx=10, pady=10)
        self.entry_tch_id = tk.Entry(self.win)
        self.entry_tch_id.grid(row=5, column=1, padx=10, pady=10)

        tk.Button(self.win, text='查询当前信息', command=self.sel_once_sco).grid(row=6, column=1, padx=10, pady=10)
        tk.Button(self.win, text='修改信息', command=self.cha_sco).grid(row=6, column=2, padx=10, pady=10)

        messagebox.showinfo('提示', '查询信息只需要输入id与考试次数\n不进行修改的信息请输入原信息')
    def cha_sco(self):
        id = self.entry_id.get()
        num = self.entry_num.get()
        chinese = self.entry_chinese.get()
        math = self.entry_math.get()
        english = self.entry_english.get()
        tch_id = self.entry_tch_id.get()
        if not id or not num or not chinese or not math or not english or not tch_id:
            messagebox.showerror('错误','不能为空')
            return
        try:
            id = int(id)
            chinese = int(chinese)
            math = int(math)
            english = int(english)
            tch_id = int(tch_id)
            if  0 > chinese or chinese > 100 or 0 > math or math > 100 or 0 > english or english > 100:
                messagebox.showerror('错误','成绩输入不合理')
                return
        except:
            messagebox.showerror('错误','请输入整数')
            return
        res = self.DB.db_change_score(id,chinese,math,english,tch_id,num)
        if res == 0:
            messagebox.showerror('修改失败','成绩记录不存在')
        elif res == 1:
            messagebox.showinfo('修改成功','学生成绩已修改')
        else:
            messagebox.showerror('未知错误',res)

    def show_sel_stu(self):
        tk.Label(self.win, text='请输入学生id:').grid(row=0, column=0, padx=10, pady=10)
        self.entry_id = tk.Entry(self.win)
        self.entry_id.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.win, text='请输入学生姓名:').grid(row=1, column=0, padx=10, pady=10)
        self.entry_name = tk.Entry(self.win)
        self.entry_name.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(self.win, text='查询', command=self.sel_stu).grid(row=2, column=1, padx=10, pady=10)
    def sel_stu(self):
        id = self.entry_id.get()
        if not id:
            messagebox.showerror('错误','id不能为空')
            return
        try:
            id = int(id)
        except ValueError:
            messagebox.showerror('错误','请输入整数id')
            return
        res = self.DB.db_select_student(id)
        if isinstance(res, (list, tuple)):
            temp = res[0]
            messagebox.showinfo('查询结果',f'ID:    {temp[0]}\n姓名:  {temp[1]}\n性别:    {temp[2]}\n年龄:  {temp[3]}')
        elif res == 0:
            messagebox.showinfo('查询失败','学生不存在')
        else:
            messagebox.showerror('未知错误',res)

    def show_sel_tch(self):
        tk.Label(self.win, text='请输入教师id:').grid(row=0, column=0, padx=10, pady=10)
        self.entry_id = tk.Entry(self.win)
        self.entry_id.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.win, text='请输入教师姓名:').grid(row=1, column=0, padx=10, pady=10)
        self.entry_name = tk.Entry(self.win)
        self.entry_name.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(self.win, text='查询', command=self.sel_tch).grid(row=2, column=1, padx=10, pady=10)
    def sel_tch(self):
        id = self.entry_id.get()
        if not id:
            messagebox.showerror('错误','id不能为空')
            return
        try:
            id = int(id)
        except ValueError:
            messagebox.showerror('错误','请输入整数id')
            return
        res = self.DB.db_select_teacher(id)
        if isinstance(res, (list, tuple)):
            temp = res[0]
            messagebox.showinfo('查询结果',f'ID:    {temp[0]}\n姓名:  {temp[1]}\n科目:    {temp[2]}')
        elif res == 0:
            messagebox.showinfo('查询失败','教师不存在')
        else:
            messagebox.showerror('未知错误',res)

    def sel_once_sco(self):
        id = self.entry_id.get()
        num = self.entry_num.get()

        if not id or not num:
            messagebox.showerror('错误','学生id和考试次数不能为空')
            return
        try:
            id = int(id)
            num = int(num)
        except:
            messagebox.showerror('错误','学生id和考试次数请输入整数')
            return
        res = self.DB.db_select_once_score(id,num)
        if res == 0:
            messagebox.showinfo('查询','未查询到该学生该次考试成绩')
        elif isinstance(res, (list, tuple)):
            temp = res[0]
            messagebox.showinfo('查询结果',f'ID:  {temp[0]}\n语文成绩:  {temp[1]}\n数学成绩:  {temp[2]}\n英语成绩:  {temp[3]}\n改卷教师:  {temp[4]}\n考试次数:  {temp[5]}')
        else:
            messagebox.showerror('未知错误',res)

    def exit(self):
        self.DB.close()
        exit()

if __name__ == '__main__':
    root = tk.Tk()
    app = Login_Windows(root)
    root.mainloop()
