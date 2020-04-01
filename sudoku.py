# 由于使用了python3.8 的 新特性":="(海象运算符)，请使用python3.8版本运行
import tkinter
import re
from tkinter import messagebox
from dlx import *


class Callback:
    """
    用于限制每个单元格只能输入1-9的类，里面可以对给定的一个Sring_var对象进行限制
    """
    def __init__(self, string_var):
        self.string_var = string_var

    def __call__(self, *args):     # 重载call方法用于对于每个单元格输入检测，保证格子里只能填一位数字（不含0）
        cc = self.string_var.get()  # 获得entry框内输入的字符串， 是一个任意的字符串，也有可能时空串
        if not cc:                 # 如果时空串先设置成空格，防止cc = cc[0] 报错
            cc = " "
        cc = cc[0]                 # 只要获取输入的第一个字符
        if cc not in "123456789":
            self.string_var.set("")  # 如果第一个字符不是数字，则不显示出来
        else:
            self.string_var.set(cc)  # 显示输入的第一个数字，后面的数字会忽略


class SudoUi:
    """
       UI界面和一些处理的代码
    """
    def __init__(self):
        self.win = tkinter.Tk()
        # self.frame 放所有的Entry,使用9*9的 grid布局
        self.frame = tkinter.Frame()
        # self.cmd_frame 放两个按钮
        self.cmd_frame = tkinter.Frame()
        self.colors = ["pink", "#CCFFFF"]  # 两种背景色， 粉红和 浅蓝（使用RGB字符串表示）
        self.s_var = [None for i in range(81)]    # 每个entry对应一个StringVar对象，方便对entry的读写
        self.blocks = [[None for i in range(9)] for j in range(9)] # 表示所有的小格子，等下都会初始化
        # 成Entry对象， 可以利用二位列表的索引，定位到相应的格子，方便对格子的操作
        self.set_ui()  # 设置窗体的显示内容，和按钮的回调函数

    def set_ui(self):
        self.win.title("数独求解器")
        self.win.geometry("240x220")
        self.win.resizable(False, False)  # 不可改变主窗口的大小
        for r in range(9):
            for c in range(9):
                index = r//3*3 + c//3      # index表示每个小九宫格的编号
                color = 0 if index in [0, 2, 4, 6, 8] else 1  # color表示当前格子的背景色
                # 把每个九宫格的位置和StringVar对应起来，方便后面的操作
                self.s_var[r*9+c] = tkinter.StringVar()
                # 初始化第r行c列的Entry,设置宽度，显示居中，并于对应的StringVar绑定
                self.blocks[r][c] = tkinter.Entry(self.frame, width=3, justify="center", textvar=self.s_var[r*9+c])
                # r*9+c是把二维的坐标转化成对应的一维坐标，trace方法是用来跟踪entry的输入情况并进行控制
                # 保证一个框内只能填一个1~9的数字
                self.s_var[r*9+c].trace("w", Callback(self.s_var[r*9+c]))
                # 根据格子所在的小九宫格号，设定背景颜色
                self.blocks[r][c].configure(background=self.colors[color])
                # 把上、下、左、右键的操作与光标的移动绑定
                for key_event in ['Left', 'Up', 'Right', 'Down']:
                    self.blocks[r][c].bind(f"<{key_event}>", self.change_focus)
                self.blocks[r][c].grid(row=r, column=c)
        # 清空按钮
        clear_btn = tkinter.Button(self.cmd_frame, width=10, text="清空", command=self.clear)
        # 确定按钮
        commit_btn = tkinter.Button(self.cmd_frame, width=10, text='确定', command=self.solve)
        clear_btn.grid(row=0, column=0, sticky=tkinter.E)
        commit_btn.grid(row=0, column=1, sticky=tkinter.N)
        # 从上到下摆放连两个frame
        self.frame.pack()
        self.cmd_frame.pack()

    def mainloop(self):
        self.win.mainloop()

    def change_focus(self, event):  # 利用光标键改变焦点的函数
        # event.widget 表示的是哪一个控件触发了事件
        # 去掉下面的一行的注释符号，可以打印出控件的名字，方便理解这个函数
        # print(event.widget)
        s = str(event.widget)       # 获取Entry的名字，因为根据名字的最后几位的数字
        # 根据Entry的名字可以算出其所在的行和列
        patten = re.compile("[0-9]*[0-9]")     # 正则表达式匹配出最后的数字
        if not (res := patten.search(s)):  # 使用正则表达式提取出
            ent_number = 1                 # 第一个Entry的名字是'Entry'，而不是'Entry1'需要处理下
        else:
            ent_number = int(res[0])       # 得出Entry控件的编号
        # 更具Entry的编号算出行和列
        row = (ent_number-1) // 9
        col = (ent_number-1) % 9
        # 左上右下的按键编码是37-40， -37可以与下面的移动向量联系起来
        curd = event.keycode - 37
        direct = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        # 根据按键设置焦点
        self.blocks[(row+direct[curd][0]) % 9][(col+direct[curd][1]) % 9].focus_set()

    def solve(self):
        puzzle = [[] for i in range(9)]  # puzzle表示当前数独里的所有数字，空用字符'0’
        # 形成的一个二维字符矩阵
        # 下面的循环是活动所有格子的数字，存到puzzle里
        for i in range(9):
            for j in range(9):
                number = self.s_var[i*9+j].get()
                if not number:
                    number = '0'
                puzzle[i].append(number)
        if not self.check_blocks(puzzle):  # 如果已经填的数字不合规直接显示错误
            messagebox.showerror("输入错误", "填入的数据不符合数独规则")
            return

        solve_sudoku(puzzle)  # 使用DLX算法， 求解数独， puzzle内保存的就是填好以后的答案
        # DLX算法，请自行上网搜索”精准覆盖问题" 和  ”使用DLX算法求解数独”
        # dxl.py文件内右python版的代码
        # 根据puzzle把Entry内的内容填上，填上的数用红色表示
        for row in range(9):
            for col in range(9):
                cur = row*9 + col
                if self.s_var[cur].get() == "":
                    self.s_var[cur].set(puzzle[row][col])
                    self.blocks[row][col].configure(fg='red')

    #  清空函数
    def clear(self):
        for s in self.s_var:
            s.set("")

    #  检查已经填写的数字是否符合数独规则
    def check_blocks(self, form):
        res = True
        row = [[0 for j in range(10)] for i in range(9)]
        col = [[0 for j in range(10)] for i in range(9)]
        sub = [[0 for j in range(10)] for i in range(9)]

        for i in range(9):
            for j in range(9):
                number = int(form[i][j])
                row[i][number] += 1
                col[j][number] += 1
                sub[i // 3 * 3 + j // 3][number] += 1

        for index in range(9):
            for num in range(1, 10):
                if row[index][num] > 1 or col[index][num] > 1 or sub[index][num] > 1:
                    res = False

        return res


if __name__ == '__main__':
    app = SudoUi()    # 生成一个数独界面的对象
    app.mainloop()    # 进入界面主循环

