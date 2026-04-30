import pymysql
import os
import socket
from pymysql.err import OperationalError
import time

def windows():
    os.system("mode con clos=80 lines=30")
    os.system("title 学生成绩管理系统")
def welcome():
    os.system("cls")  # 清屏
    print("=" * 40)
    print("‖                                       ‖")
    print("‖            学生成绩管理系统           ‖")
    print("‖                                       ‖")
    print("=" * 40)
    input('\n按回车进入系统>>>')
def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"
User = None
Passwd = None

def log_in():
    state = 0
    for i in range(1,6):
        global User
        User = input('请输入用户名>>>')
        global Passwd
        Passwd = input('请输入密码>>>')
        try:
            conn_1 = pymysql.connect(
                host='8.163.39.232',
                user=str(User),
                password=str(Passwd),
                database='studentsscore',
                charset='utf8'
            )
            cursor_1 = conn_1.cursor()
            cursor_1.close()
            conn_1.close()
            state = 1
        except OperationalError as e:
            if e.args[0] == 1045:
                print(f"您的用户名或密码错误,请重新输入(还有{5-i}次机会)")
            else:
                print(f'未知错误{e},您还有{5-i}次机会')
        finally:
            if state == 1:
                print("✅ 登录成功！欢迎使用学生成绩管理系统")
                break
    if state == 1:
        time.sleep(2)
        return True
    else:
        print('登陆失败')
        time.sleep(1)
        return False

def log(cursor,id,operation):
    global User
    oper_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    log_sql = 'insert into log(id,user,operation,time,ip) values(%s,%s,%s,%s,%s)'
    cursor.execute(log_sql,(id,User,operation,oper_time,get_ip()))

def menu_ui():
    os.system("cls")
    print("\n"+ "========= 学生成绩管理系统 =========\n")
    menu = [
        "‖1. 添加学生        7. 修改学生信息‖",
        "‖2. 添加教师        8. 修改教师信息‖",
        "‖3. 查询成绩        9. 修改学生成绩‖",
        "‖4. 录入成绩       10. 查询学生信息‖",
        "‖5. 删除学生       11. 查询教师信息‖",
        "‖6. 删除教师        0. 退出系统    ‖"
    ]

    for item in menu:
        print(item)

    print("\n" + "====================================")
    return input("\n"+ "请输入功能序号：")

def add_student(conn, cursor):
    try:
        stu_name = input("请输入学生姓名>>>")
        while True:
            stu_gender = input('请输入学生性别>>>')
            if stu_gender in ['男','女']:
                break
            else:
                print("输入有误，请重新输入(男/女)")
        while True:
            try:
                stu_age = int(input('请输入学生年龄>>>'))
                if 0<stu_age<=100:
                    break
                else:
                    print("输入有误，请重新输入")
            except ValueError:
                conn.rollback()
                print("请输入有效数字")
        sql = 'insert into student(stu_name,stu_gender,stu_age) values (%s,%s,%s)'
        cursor.execute(sql, (stu_name, stu_gender, stu_age))
        new_id = cursor.lastrowid
        log(cursor,'s'+str(new_id),'添加学生')
        conn.commit()
        print(f'学生{stu_name}添加成功,id为{new_id}')
        input('按回车退出>>>')
    except OperationalError as e:
        conn.rollback()
        print(f'未知错误:{e}')
        input('按回车退出>>>')
    except Exception as e:
        conn.rollback()
        print(f'操作错误:{e}')

def select_score(conn, cursor):
    try:
        while True:
            name = input('请输入要查找学生的姓名(按"q"/"Q"退出)>>>')
            if name in ['q','Q']:
                break
            else:
                sql = "select * from student where stu_name = %s"
                cursor.execute(sql,(name,))
                res = cursor.fetchall()
                if len(res) == 0:
                    print("学生不存在，请重新输入")
                elif len(res) == 1:
                    id = res[0][0]
                    sql = 'select * from score where stu_id = %s'
                    cursor.execute(sql,(id,))
                    result = cursor.fetchall()
                    if len(result) == 0:
                        print('学生暂无成绩')
                    else:
                        [print(f"考试次数：{item[5]} | 语文：{item[1]} | 数学：{item[2]} | 英语：{item[3]} | 批改教师ID：{item[4]}") for item in result]
                    log(cursor,'s'+str(id),'查询成绩')
                    conn.commit()
                else:
                    for i in res:
                        print(i)
                    res_id = [student[0] for student in res]
                    while True:
                        try:
                            stu_id = int(input("请输入要选择的学生id>>>"))
                            if stu_id in res_id:
                                sql = 'select * from score where stu_id = %s'
                                cursor.execute(sql,(int(stu_id),))
                                result = cursor.fetchall()
                                if len(result) == 0:
                                    print('学生暂无成绩')
                                else:
                                    [print(f"考试次数：{item[5]} | 语文：{item[1]} | 数学：{item[2]} | 英语：{item[3]} | 批改教师ID：{item[4]}") for item in result]
                                input('按回车回到上一级>>>')
                                log(cursor,'s'+str(stu_id),'查询成绩')
                                conn.commit()
                                break
                            else:
                                print("输入有误，请重新输入")
                        except ValueError:
                            conn.rollback()
                            print("请输入数字")
    except OperationalError as e:
        conn.rollback()
        print(f'未知错误:{e}')
    except Exception as e:
        conn.rollback()
        print(f'操作错误:{e}')

def add_teacher(conn, cursor):
    try:
        tch_name = input('请输入教师姓名>>>')
        while True:
            tch_course = input("请输入教师教学科目>>>")
            if tch_course in ['语文','数学','英语']:
                break
            else:
                print('输入有误，请重新输入(语文/数学/英语)')
        sql = 'insert into teacher(tch_name,tch_course) values (%s,%s)'
        cursor.execute(sql, (tch_name, tch_course))
        new_id = cursor.lastrowid
        log(cursor,'t'+str(new_id),'添加教师')
        conn.commit()
        print(f'教师{tch_name}添加成功，id为{new_id}')
        input('按回车退出>>>')

    except Exception as e:
        conn.rollback()
        print(f"添加失败,错误信息:{e}")
        input('按回车退出>>>')

def add_score(conn, cursor):
    try:
        while True:
            name = input('请输入要添加成绩的学生姓名(按"q"/"Q"退出)>>>')
            if name in ['q', 'Q']:
                break
            else:
                sql = "select * from student where stu_name = %s"
                cursor.execute(sql, (name,))
                res = cursor.fetchall()
                if len(res) == 0:
                    print('学生不存在')
                elif len(res) == 1:
                    id = res[0][0]
                    while True:
                        try:
                            chinese = int(input(f'请输入{name}的语文成绩>>>'))
                            if 0<=chinese<=100:
                                break
                            else:
                                print('输入有误，请重新输入(0-100)')
                        except ValueError:
                            conn.rollback()
                            print('请输入数字')
                    while True:
                        try:
                            math = int(input(f'请输入{name}的数学成绩>>>'))
                            if 0<=math<=100:
                                break
                            else:
                                print('输入有误，请重新输入(0-100)')
                        except ValueError:
                            conn.rollback()
                            print('请输入数字')
                    while True:
                        try:
                            english = int(input(f'请输入{name}的英语成绩>>>'))
                            if 0<=english<=100:
                                break
                            else:
                                print('输入有误，请重新输入(0-100)')
                        except ValueError:
                            conn.rollback()
                            print('请输入数字')
                    while True:
                        tch_id = input('请输入改卷老师id>>>')
                        sql = 'select * from teacher where tch_id = %s and tch_state = 1'
                        cursor.execute(sql, (tch_id,))
                        res1 = cursor.fetchall()
                        if len(res1) == 0:
                            print('老师id不存在，请重新输入')
                        else:
                            tch_id = res1[0][0]
                            break
                    while True:
                        try:
                            sco_num = int(input('请输入第几次考试>>>'))
                            sql_check = 'select * from score where stu_id=%s and sco_num=%s'
                            cursor.execute(sql_check, (id, sco_num))
                            if sco_num > 0:
                                if cursor.fetchall():
                                    print('该次考试学生成绩已录入')
                                else:
                                    break
                            else:
                                print('输入有误,请重新输入')
                        except ValueError:
                            conn.rollback()
                            print('输入有误,请输入整数')
                    sql = 'insert into score(stu_id,chinese,math,english,tch_id,sco_num) values (%s,%s,%s,%s,%s,%s)'
                    cursor.execute(sql,(id,chinese,math,english,tch_id,sco_num))
                    log(cursor, 's' + str(id), '添加成绩')
                    conn.commit()
                    print(f'{name}成绩添加成功')
                    input('按回车退出>>>')
                else:
                    for i in res:
                        stu_info = i
                        print(f"ID={stu_info[0]}, 姓名={stu_info[1]}, 性别={stu_info[2]}, 年龄={stu_info[3]}")
                    res_id = [student[0] for student in res]
                    while True:
                        try:
                            stu_id = int(input("请输入要选择的学生id>>>"))
                            if stu_id in res_id:
                                while True:
                                    try:
                                        chinese = int(input(f'请输入{name}的语文成绩>>>'))
                                        if 0 <= chinese <= 100:
                                            break
                                        else:
                                            print('输入有误，请重新输入(0-100)')
                                    except ValueError:
                                        conn.rollback()
                                        print('请输入数字')
                                while True:
                                    try:
                                        math = int(input(f'请输入{name}的数学成绩>>>'))
                                        if 0 <= math <= 100:
                                            break
                                        else:
                                            print('输入有误，请重新输入(0-100)')
                                    except ValueError:
                                        conn.rollback()
                                        print('请输入数字')
                                while True:
                                    try:
                                        english = int(input(f'请输入{name}的英语成绩>>>'))
                                        if 0 <= english <= 100:
                                            break
                                        else:
                                            print('输入有误，请重新输入(0-100)')
                                    except ValueError:
                                        conn.rollback()
                                        print('请输入数字')
                                while True:
                                    tch_id = input('请输入改卷老师id>>>')
                                    sql = 'select * from teacher where tch_id = %s and tch_state = 1'
                                    cursor.execute(sql, (tch_id,))
                                    res1 = cursor.fetchall()
                                    if len(res1) == 0:
                                        print('老师id不存在，请重新输入')
                                    else:
                                        tch_id = res1[0][0]
                                        break
                                while True:
                                    try:
                                        sco_num = int(input('请输入第几次考试>>>'))
                                        sql_check = 'select * from score where stu_id=%s and sco_num=%s'
                                        cursor.execute(sql_check, (stu_id, sco_num))
                                        if sco_num > 0:
                                            if cursor.fetchall():
                                                print('该次考试学生成绩已录入')
                                            else:
                                                break
                                        else:
                                            print('输入有误,请重新输入')
                                    except ValueError:
                                        conn.rollback()
                                        print('输入有误,请输入整数')
                                sql = 'insert into score(stu_id,chinese,math,english,tch_id,sco_num) values (%s,%s,%s,%s,%s,%s)'
                                cursor.execute(sql, (stu_id, chinese, math, english, tch_id, sco_num))
                                log(cursor,'s' + str(stu_id), '添加成绩')
                                conn.commit()
                                print(f'{name}成绩添加成功')
                                input('按回车退出>>>')
                                break
                            else:
                                print("输入有误，请重新输入")
                        except ValueError:
                            conn.rollback()
                            print("请输入数字")
    except OperationalError as e:
        conn.rollback()
        print(f'未知错误:{e}')
    except Exception as e:
        conn.rollback()
        print(f'操作错误:{e}')

def del_student(conn, cursor):
    try:
        name = input('请输入要删除的学生姓名>>>')
        sql = 'select * from student where stu_name = %s'
        cursor.execute(sql,(name,))
        res = cursor.fetchall()
        if len(res) == 0:
            print('学生不存在,退出中...')
            input('按回车退出>>>')
        elif len(res) == 1:
            id = res[0][0]
            sql = 'select * from score where stu_id = %s'
            cursor.execute(sql,(id,))
            res_sco = cursor.fetchall()
            if len(res_sco) == 0:
                sql = 'delete from student where stu_id = %s'
                cursor.execute(sql,(id,))
                log(cursor,'s'+str(id),'删除学生')
                conn.commit()
                print(f'学生{name}删除成功')
                input('按回车退出>>>')
            else:
                choose = input('学生还有成绩记录，是否继续删除(Y/N)')
                if choose in ["Y",'y']:
                    sql = 'delete from score where stu_id = %s'
                    cursor.execute(sql,(id,))
                    conn.commit()
                    sql = 'delete from student where stu_id = %s'
                    cursor.execute(sql,(id,))
                    log(cursor,'s' + str(id), '删除学生')
                    conn.commit()
                    print(f'学生{name}删除成功')
                    input('按回车退出>>>')
                elif choose in ["N",'n']:
                    print('退出中...')
                    input('按回车退出>>>')
                else:
                    print('输入有误，退出中...')
                    input('按回车退出>>>')
        else:
            res_id = [student[0] for student in res]
            for i in res:
                stu_info = i
                print(f"ID={stu_info[0]}, 姓名={stu_info[1]}, 性别={stu_info[2]}, 年龄={stu_info[3]}")
            try:
                stu_id = int(input('请输入要选择的学生id>>>'))
                if stu_id in res_id:
                    sql = 'select * from score where stu_id = %s'
                    cursor.execute(sql,(stu_id,))
                    res_sco = cursor.fetchall()
                    if len(res_sco) == 0:
                        sql = 'delete from student where stu_id = %s'
                        cursor.execute(sql,(stu_id,))
                        log(cursor,'s' + str(stu_id), '删除学生')
                        conn.commit()
                        print(f'学生{name}删除成功')
                        input('按回车退出>>>')
                    else:
                        choose = input('学生还有成绩记录，是否继续删除(Y/N)')
                        if choose in ["Y", 'y']:
                            sql = 'delete from score where stu_id = %s'
                            cursor.execute(sql, (stu_id,))
                            conn.commit()
                            sql = 'delete from student where stu_id = %s'
                            cursor.execute(sql, (stu_id,))
                            log(cursor,'s' + str(stu_id), '删除学生')
                            conn.commit()
                            print(f'学生{name}删除成功')
                        elif choose in ["N", 'n']:
                            print('退出中...')
                            input('按回车退出>>>')
                        else:
                            print('输入有误，退出中...')
                            input('按回车退出>>>')
                else:
                    print('输入有误,退出中...')
                    input('按回车退出>>>')
            except ValueError:
                conn.rollback()
                print('输入有误,退出中...')
                input('按回车退出>>>')
    except OperationalError as e:
        conn.rollback()
        if e.args[0] == 1142:
            print('权限不足,请联系管理员')
            input('按回车键退出>>>')
        else:
            conn.rollback()
            print(f'未知错误:{e}')
            input('按回车键退出>>>')
    except Exception as e:
        conn.rollback()
        print(f'操作错误:{e}')

def del_teacher(conn, cursor):
    try:
        name = input('请输入要删除的老师姓名>>>')
        sql = 'select * from teacher where tch_name = %s'
        cursor.execute(sql,(name,))
        res = cursor.fetchall()
        if len(res) == 0:
            print('老师不存在')
            input('按回车退出>>>')
        elif len(res) == 1:
            sql = 'update teacher set tch_state=0 where tch_name=%s'
            cursor.execute(sql,(name,))
            log(cursor,'t' + str(res[0][0]), '删除教师')
            conn.commit()
            print(f'老师{name}删除成功')
            input('按回车退出>>>')
        else:
            res_id = [teacher[0] for teacher in res]
            for i in res:
                tch = i
                print(f"教师ID：{tch[0]} | 姓名：{tch[1]} | 科目：{tch[2]} | 状态：{'正常' if tch[3]==1 else '已删除'}")
            try:
                tch_id = int(input('请输入要选择的老师id>>>'))
                if tch_id in res_id:
                    sql = 'update teacher set tch_state=0 where tch_id=%s'
                    cursor.execute(sql,(tch_id,))
                    log(cursor,'t' + str(tch_id), '删除教师')
                    conn.commit()
                    print(f'老师{name}删除成功')
                    input('按回车退出>>>')
                else:
                    print('输入有误,退出中...')
                    input('按回车退出>>>')
            except ValueError:
                conn.rollback()
                print('输入有误,退出中...')
                input('按回车退出>>>')
    except OperationalError as e:
        conn.rollback()
        if e.args[0] == 1142:
            conn.rollback()
            print('权限不足,请联系管理员')
            input('按回车键退出>>>')
        else:
            conn.rollback()
            print(f'未知错误:{e}')
            input('按回车键退出>>>')
    except Exception as e:
        conn.rollback()
        print(f'操作错误:{e}')

def select_student(conn, cursor):
    try:
        print('1.查询所有学生信息')
        print('2.查询单名学生信息')
        print('q.退出')
        while True:
            choose = input('请选择功能>>>')
            if choose in ['q','Q']:
                break
            elif choose == '1':
                sql = 'select * from student'
                cursor.execute(sql)
                res = cursor.fetchall()
                if len(res) == 0:
                    print('暂无学生信息')
                else:
                    for i in res:
                        print(f"学生ID：{i[0]} | 姓名：{i[1]} | 性别：{i[2]} | 年龄：{i[3]}")
                input('按回车退出>>>')
                log(cursor,'all','查询全体学生')
                conn.commit()
                break
            elif choose == '2':
                while True:
                    try:
                        id = int(input('请输入要查找的学生id(0退出)>>>'))
                        if id == 0:
                            break
                        sql = 'select * from student where stu_id = %s '
                        cursor.execute(sql,(id,))
                        res = cursor.fetchall()
                        if len(res) == 0:
                            print('ID不存在,请重新输入')
                        else:
                            print(f"学生ID：{res[0][0]} | 姓名：{res[0][1]} | 性别：{res[0][2]} | 年龄：{res[0][3]}")
                            log(cursor,'s'+str(id),'查询学生')
                            conn.commit()
                            break
                    except ValueError:
                        print('请输入数字')
            else:
                print('输入有误，请重新输入')
    except OperationalError as e:
        print(f'未知错误:{e}')
    except Exception as e:
        print(f'操作错误:{e}')

def select_teacher(conn, cursor):
    try:
        print('1.查询所有教师信息')
        print('2.查询单名教师信息')
        print('q.退出')
        while True:
            choose = input('请选择功能>>>')
            if choose in ['q', 'Q']:
                break
            elif choose == '1':
                sql = 'select * from teacher where tch_state = 1'
                cursor.execute(sql)
                res = cursor.fetchall()
                if len(res) == 0:
                    print('暂无教师信息')
                else:
                    for i in res:
                        print(f"教师ID：{i[0]} | 姓名：{i[1]} | 授课科目：{i[2]} | 状态：{'正常' if i[3]==1 else '已删除'}")
                input('按回车退出>>>')
                log(cursor,'all','查询全体教师')
                conn.commit()
            elif choose == '2':
                while True:
                    try:
                        id = int(input('请输入要查找的教师id(0退出)>>>'))
                        if id == 0:
                            break
                        sql = 'select * from teacher where tch_id = %s and tch_state = 1'
                        cursor.execute(sql, (id,))
                        res = cursor.fetchall()
                        if len(res) == 0:
                            print('ID不存在,请重新输入')
                        else:
                            print(f"教师ID：{res[0][0]} | 姓名：{res[0][1]} | 授课科目：{res[0][2]} | 状态：{'正常' if res[0][3]==1 else '已删除'}")
                            log(cursor,'t'+str(id),'查询教师')
                            conn.commit()
                            break
                    except ValueError:
                        print('请输入数字')
            else:
                print('输入有误，请重新输入')
    except OperationalError as e:
        print(f'未知错误:{e}')
    except Exception as e:
        print(f'操作错误:{e}')

def change_student(conn, cursor):
    try:
        id = int(input('请输入要修改信息的学生id>>>'))
        sql = 'select * from student where stu_id = %s'
        cursor.execute(sql,(id,))
        res = cursor.fetchall()
        if len(res) == 0:
            print('学生id不存在')
            input('按回车退出>>>')
        else:
            stu_info = res[0]
            print(f"当前学生信息：ID={stu_info[0]}, 姓名={stu_info[1]}, 性别={stu_info[2]}, 年龄={stu_info[3]}")
            choose = input('请确认学生现有信息,是否修改(Y/N)>>>')
            if choose in ["Y",'y']:
                while True:
                    temp = input('请重新输入学生信息(按空格分割 无需填写id)>>>')
                    temp = temp.strip().split()
                    if len(temp) == 3:
                        if temp[1] in ['男','女']:
                            try:
                                if 0<int(temp[2])<=100:
                                    sql = 'update student set stu_name = %s,stu_gender = %s,stu_age = %s where stu_id = %s'
                                    cursor.execute(sql,(temp[0],temp[1],int(temp[2]),id))
                                    log(cursor,'s'+str(id),'修改学生信息')
                                    conn.commit()
                                    sql = 'select * from student where stu_id = %s'
                                    cursor.execute(sql,(id,))
                                    res = cursor.fetchall()
                                    new_stu = res[0]
                                    print(f'修改后的信息如下：ID={new_stu[0]}, 姓名={new_stu[1]}, 性别={new_stu[2]}, 年龄={new_stu[3]}')
                                    input('按回车退出>>>')
                                    break
                                else:
                                    print('年龄输入不合理,请重新输入(1-100)')
                            except ValueError:
                                conn.rollback()
                                print('请输入有效数字(1-100)')
                        else:
                            print('性别输入错误,请重新输入')
                    else:
                        print('输入有误,请重新输入')
            else:
                print('退出中...')
                input('按回车退出>>>')
    except ValueError:
        conn.rollback()
        print('输入有误,退出中....')
        input('按回车退出>>>')
    except OperationalError as e:
        conn.rollback()
        print(f'未知错误:{e}')
    except Exception as e:
        conn.rollback()
        print(f'操作错误:{e}')

def change_teacher(conn, cursor):
    try:
        id = int(input('请输入要修改信息的教师id>>>'))
        sql = 'select * from teacher where tch_id = %s and tch_state = 1'
        cursor.execute(sql,(id,))
        res = cursor.fetchall()
        if len(res) == 0:
            print('教师id不存在')
            input('按回车退出>>>')
        else:
            tch = res[0]
            print(f"教师ID：{tch[0]} | 姓名：{tch[1]} | 科目：{tch[2]} | 状态：{'正常' if tch[3]==1 else '已删除'}")
            choose = input('请确认教师现有信息,是否修改(Y/N)>>>')
            if choose in ['Y','y']:
                while True:
                    temp = input('请重新输入教师信息(按空格分割 无需填写id,状态)>>>')
                    temp = temp.strip().split()
                    if len(temp) == 2:
                        if temp[1] in ['语文','数学','英语']:
                            sql = 'update teacher set tch_name = %s,tch_course = %s where tch_id = %s'
                            cursor.execute(sql, (temp[0], temp[1], id))
                            log(cursor,'t'+str(id),'修改教师信息')
                            conn.commit()
                            sql = 'select * from teacher where tch_id = %s'
                            cursor.execute(sql, (id,))
                            res = cursor.fetchall()
                            new_tch = res[0]
                            print(f'修改后的信息如下:教师ID：{new_tch[0]} | 姓名：{new_tch[1]} | 科目：{new_tch[2]} | 状态：{'正常' if new_tch[3]==1 else '已删除'}')
                            input('按回车退出>>>')
                            break
                        else:
                            print('学科输入错误,请重新输入')
                    else:
                        print('输入有误,请重新输入')

            else:
                print('退出中...')
                input('按回车退出>>>')
    except ValueError:
        conn.rollback()
        print('输入有误,退出中....')
        input('按回车退出>>>')
    except OperationalError as e:
        conn.rollback()
        print(f'未知错误:{e}')
    except Exception as e:
        conn.rollback()
        print(f'操作错误:{e}')

def change_score(conn, cursor):
    try:
        id = int(input('请输入要修改成绩的学生id>>>'))
        sql = 'select * from score where stu_id = %s'
        cursor.execute(sql,(id,))
        res = cursor.fetchall()
        if len(res) == 0:
            print('学生id不存在或暂未考试,退出中...')
            input('按回车退出>>>')
        else:
            for i in res:
                print(i)
            try:
                choose = int(input('请选择要修改第__次考试的成绩>>>'))
                num = [score_num[-1] for score_num in res]
                if choose in num:
                    while True:
                        try:
                            new_score = input('请输入各科成绩(语文 数学 英语 按空格分割)>>>')
                            new_score_list = new_score.strip().split()
                            if len(new_score_list) == 3:
                                try:
                                    chinese = int(new_score_list[0])
                                    math = int(new_score_list[1])
                                    english = int(new_score_list[2])
                                    if 0<=chinese<=100 and 0<=math<=100 and 0<=english<=100:
                                        sql = 'update score set chinese = %s, math = %s, english = %s where stu_id = %s and sco_num = %s'
                                        cursor.execute(sql,(chinese,math,english,id,choose))
                                        log(cursor,'s'+str(id),'修改成绩')
                                        conn.commit()
                                        sql = 'select * from score where stu_id = %s and sco_num = %s'
                                        cursor.execute(sql,(id,choose))
                                        res = cursor.fetchall()
                                        print(f'修改后的成绩为:考试次数：{res[0][6]} | 语文：{res[0][2]} | 数学：{res[0][3]} | 英语：{res[0][4]} | 批改教师ID：{res[0][5]}) ')
                                        input('按回车退出>>>')
                                    else:
                                        print('输入有误,请重新输入(0-100)')
                                except ValueError:
                                    conn.rollback()
                                    print('请输入有效数字')
                            else:
                                print('输入有误,请重新输入')
                        except ValueError:
                            print('请输入整数,按空格分割')
                else:
                    print('输入有误,退出中...')
                    input('按回车退出>>>')
            except ValueError:
                print('输入有误,退出中...')
                input('按回车退出>>>')
    except ValueError:
        conn.rollback()
        print('输入有误,退出中...')
        input('按回车退出>>>')
    except OperationalError as e:
        conn.rollback()
        print(f'未知错误:{e}')
    except Exception as e:
        conn.rollback()
        print(f'操作错误:{e}')

if __name__ == "__main__":
    conn = None
    cursor = None
    windows()
    welcome()
    try:
        if log_in():
            conn = pymysql.connect(
                host='8.163.39.232',
                user=str(User),
                password=str(Passwd),
                database='studentsscore',
                charset='utf8'
            )
            cursor = conn.cursor()
            log(cursor,'None','登录数据库')
            conn.commit()
            while True:
                chose = menu_ui()
                if chose == '0':
                    print("\n" + " 感谢使用，再见！")
                    log(cursor,'None','登出数据库')
                    conn.commit()
                    cursor.close()
                    conn.close()
                    break
                elif chose == '1':
                    add_student(conn, cursor)
                elif chose == '2':
                    add_teacher(conn, cursor)
                elif chose == '3':
                    select_score(conn, cursor)
                elif chose == '4':
                    add_score(conn, cursor)
                elif chose == '5':
                    del_student(conn, cursor)
                elif chose == '6':
                    del_teacher(conn, cursor)
                elif chose == '7':
                    change_student(conn, cursor)
                elif chose == '8':
                    change_teacher(conn, cursor)
                elif chose == '9':
                    change_score(conn, cursor)
                elif chose == '10':
                    select_student(conn, cursor)
                elif chose == '11':
                    select_teacher(conn, cursor)
                else:
                    print('输入有误,请重新输入')
        else:
            print('系统自动退出中...')
            time.sleep(3)
            exit()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

