import pymysql
import os

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


conn = pymysql.connect(
    host='8.163.39.232',
    user="admin",
    password="88888888",
    database='studentsscore',
    charset='utf8'
)
cursor = conn.cursor()

def add_student():
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
            print("请输入有效数字")
    sql = 'insert into student(stu_name,stu_gender,stu_age) values (%s,%s,%s)'
    cursor.execute(sql, (stu_name, stu_gender, stu_age))
    conn.commit()
    new_id = cursor.lastrowid
    print(f'学生{stu_name}添加成功,id为{new_id}')
    input('按回车退出>>>')

def select_score():
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
                print(result)
            else:
                for i in res:
                    print(i)
                res_id = [student[0] for student in res]
                while True:
                    try:
                        stu_id = int(input("请输入要选择的学生id>>>"))
                        if stu_id in res_id:
                            sql = 'select * from score where stu_id = %s'
                            cursor.execute(sql,(stu_id,))
                            result = cursor.fetchall()
                            print(result)
                            input('按回车退出>>>')
                            break
                        else:
                            print("输入有误，请重新输入")
                    except ValueError:
                        print("请输入数字")

def add_teacher():
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
        conn.commit()
        new_id = cursor.lastrowid
        print(f'教师{tch_name}添加成功，id为{new_id}')
        input('按回车退出>>>')
    except Exception as e:
        conn.rollback()
        print(f"添加失败,错误信息:{e}")
        input('按回车退出>>>')

def add_score():
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
                        print('请输入数字')
                while True:
                    try:
                        math = int(input(f'请输入{name}的数学成绩>>>'))
                        if 0<=math<=100:
                            break
                        else:
                            print('输入有误，请重新输入(0-100)')
                    except ValueError:
                        print('请输入数字')
                while True:
                    try:
                        english = int(input(f'请输入{name}的英语成绩>>>'))
                        if 0<=english<=100:
                            break
                        else:
                            print('输入有误，请重新输入(0-100)')
                    except ValueError:
                        print('请输入数字')
                while True:
                    tch_id = input('请输入改卷老师id>>>')
                    sql = 'select * from teacher where tch_id = %s'
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
                        if sco_num > 0:
                            break
                        else:
                            print('输入有误,请重新输入')
                    except ValueError:
                        print('输入有误,请输入整数')
                sql = 'insert into score(stu_id,chinese,math,english,tch_id,sco_num) values (%s,%s,%s,%s,%s,%s)'
                cursor.execute(sql,(id,chinese,math,english,tch_id,sco_num))
                conn.commit()
                print(f'{name}成绩添加成功')
                input('按回车退出>>>')
                break
            else:
                for i in res:
                    print(i)
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
                                    print('请输入数字')
                            while True:
                                try:
                                    math = int(input(f'请输入{name}的数学成绩>>>'))
                                    if 0 <= math <= 100:
                                        break
                                    else:
                                        print('输入有误，请重新输入(0-100)')
                                except ValueError:
                                    print('请输入数字')
                            while True:
                                try:
                                    english = int(input(f'请输入{name}的英语成绩>>>'))
                                    if 0 <= english <= 100:
                                        break
                                    else:
                                        print('输入有误，请重新输入(0-100)')
                                except ValueError:
                                    print('请输入数字')
                            while True:
                                tch_id = input('请输入改卷老师id>>>')
                                sql = 'select * from teacher where tch_id = %s'
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
                                    if sco_num > 0:
                                        break
                                    else:
                                        print('输入有误,请重新输入')
                                except ValueError:
                                    print('输入有误,请输入整数')
                            sql = 'insert into score(stu_id,chinese,math,english,tch_id,sco_num) values (%s,%s,%s,%s,%s,%s)'
                            cursor.execute(sql, (stu_id, chinese, math, english, tch_id, sco_num))
                            conn.commit()
                            print(f'{name}成绩添加成功')
                            input('按回车退出>>>')
                            break
                        else:
                            print("输入有误，请重新输入")
                    except ValueError:
                        print("请输入数字")

def del_student():
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
                print(i)
            try:
                stu_id = int(input('请输入要选择的学生id>>>'))
                if stu_id in res_id:
                    sql = 'select * from score where stu_id = %s'
                    cursor.execute(sql,(stu_id,))
                    res_sco = cursor.fetchall()
                    if len(res_sco) == 0:
                        sql = 'delete from student where stu_id = %s'
                        cursor.execute(sql,(stu_id,))
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
                            conn.commit()
                            print(f'学生{name}删除成功')
                            input('按回车退出>>>')
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
                print('输入有误,退出中...')
                input('按回车退出>>>')

def del_teacher():
    name = input('请输入要删除的老师姓名>>>')
    sql = 'select * from teacher where name = %s'
    cursor.execute(sql,(name,))
    res = cursor.fetchall()
    if len(res) == 0:
        print('老师不存在')
        input('按回车退出>>>')
    elif len(res) == 1:
        sql = 'update teacher set stu_state=0 where name=%s'
        cursor.execute(sql,(name,))
        conn.commit()
        print(f'老师{name}删除成功')
        input('按回车退出>>>')
    else:
        res_id = [teacher[0] for teacher in res]
        for i in res:
            print(i)
        try:
            tch_id = int(input('请输入要选择的老师id>>>'))
            if tch_id in res_id:
                sql = 'update teacher set tch_state=0 where tch_id=%s'
                cursor.execute(sql,(tch_id,))
                conn.commit()
                print(f'老师{name}删除成功')
                input('按回车退出>>>')
            else:
                print('输入有误,退出中...')
                input('按回车退出>>>')
        except ValueError:
            print('输入有误,退出中...')
            input('按回车退出>>>')

def select_student():
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
            for i in res:
                print(i)
            input('按回车退出>>>')
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
                        print(res)
                        break
                except ValueError:
                    print('请输入数字')
        else:
            print('输入有误，请重新输入')

def select_teacher():
        print('1.查询所有教师信息')
        print('2.查询单名教师信息')
        print('q.退出')
        while True:
            choose = input('请选择功能>>>')
            if choose in ['q', 'Q']:
                break
            elif choose == '1':
                sql = 'select * from teacher'
                cursor.execute(sql)
                res = cursor.fetchall()
                for i in res:
                    print(i)
                input('按回车退出>>>')
                break
            elif choose == '2':
                while True:
                    try:
                        id = int(input('请输入要查找的教师id(0退出)>>>'))
                        if id == 0:
                            break
                        sql = 'select * from teacher where tch_id = %s '
                        cursor.execute(sql, (id,))
                        res = cursor.fetchall()
                        if len(res) == 0:
                            print('ID不存在,请重新输入')
                        else:
                            print(res)
                            break
                    except ValueError:

                        print('请输入数字')
            else:
                print('输入有误，请重新输入')

def change_student():
    try:
        id = int(input('请输入要修改信息的学生id>>>'))
        sql = 'select * from student where stu_id = %s'
        cursor.execute(sql,(id,))
        res = cursor.fetchall()
        if len(res) == 0:
            print('学生id不存在')
            input('按回车退出>>>')
        else:
            print(res)
            choose = input('请确认学生现有信息,是否修改(Y/N)>>>')
            if choose in ["Y",'y']:
                temp = input('请重新输入学生信息(按空格分割 无需填写id)>>>')
                temp = temp.split()
                sql = 'update student set stu_name = %s,stu_gender = %s,stu_age = %s where stu_id = %s'
                cursor.execute(sql,(temp[0],temp[1],int(temp[2]),id))
                conn.commit()
                sql = 'select * from student where stu_id = %s'
                cursor.execute(sql,(id,))
                res = cursor.fetchall()
                print(f'修改后的信息如下:\n{res}')
                input('按回车退出>>>')
            else:
                print('退出中...')
                input('按回车退出>>>')
    except ValueError:
        print('输入有误,退出中....')
        input('按回车退出>>>')

def change_teacher():
    try:
        id = int(input('请输入要修改信息的教师id>>>'))
        sql = 'select * from teacher where tch_id = %s'
        cursor.execute(sql,(id,))
        res = cursor.fetchall()
        if len(res) == 0:
            print('教师id不存在')
            input('按回车退出>>>')
        else:
            print(res)
            choose = input('请确认教师现有信息,是否修改(Y/N)>>>')
            if choose in ['Y','y']:
                temp = input('请重新输入教师信息(按空格分割 无需填写id)>>>')
                temp = temp.split()
                sql = 'update teacher set tch_name = %s,tch_course = %s,tch_state = %s where tch_id = %s'
                cursor.execute(sql, (temp[0], temp[1], int(temp[2]), id))
                conn.commit()
                sql = 'select * from teacher where tch_id = %s'
                cursor.execute(sql, (id,))
                res = cursor.fetchall()
                print(f'修改后的信息如下:\n{res}')
                input('按回车退出>>>')

            else:
                print('退出中...')
                input('按回车退出>>>')
    except ValueError:
        print('输入有误,退出中....')
        input('按回车退出>>>')

def change_score():
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
                            new_score = new_score.strip()
                            if 0<=int(new_score[0])<=100 and 0<=int(new_score[1])<=100 and 0<=int(new_score[2])<=100:
                                sql = 'update score set chinese = %s, math = %s, english = %s, where stu_id = %s'
                                cursor.execute(sql,(new_score[0],new_score[1],new_score[2],id))
                                conn.commit()
                                sql = 'select * from score where stu_id = %s'
                                cursor.execute(sql,(id,))
                                res = cursor.fetchall()
                                print(f'修改后的成绩为:\n{res}')
                                input('按回车退出>>>')
                                break
                            else:
                                print('输入有误,请重新输入(0-100)')
                        except ValueError:
                            print('请输入整数,按空格分割')
                else:
                    print('输入有误,退出中...')
                    input('按回车退出>>>')
            except ValueError:
                print('输入有误,退出中...')
                input('按回车退出>>>')
    except ValueError:
        print('输入有误,退出中...')
        input('按回车退出>>>')

if __name__ == "__main__":
    windows()
    welcome()
    while True:
        chose = menu_ui()
        if chose == '0':
            print("\n" + " 感谢使用，再见！")
            break
        elif chose == '1':
            add_student()
        elif chose == '2':
            add_teacher()
        elif chose == '3':
            select_score()
        elif chose == '4':
            add_score()
        elif chose == '5':
            del_student()
        elif chose == '6':
            del_teacher()
        elif chose == '7':
            change_student()
        elif chose == '8':
            change_teacher()
        elif chose == '9':
            change_score()
        elif chose == '10':
            select_student()
        elif chose == '11':
            select_teacher()
        else:
            print('输入有误,请重新输入')
