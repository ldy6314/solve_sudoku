# DLX类是"dancing link"数据结构
# solve_sudoku函数用来求解9宫数独
# 由于使用了python3.8 的 新特性":="(海象运算符)，请使用python3.8版本运行

class DLX:
    def __init__(self, n, m):
        self.n = n
        self.ans_d = 0
        self.ans = [0 for i in range(81)]
        self.sz = n+1
        self.S = [0 for i in range(n+1)]
        self.row, self.col, self.L, self.R, self.U, self.D = \
            [[0 for i in range(m+1)] for j in range(6)]

        # 初始化虚拟节点
        for i in range(n+1):
            self.L[i], self.R[i], self.U[i], self.D[i] = i-1, i+1, i, i
        self.L[0], self.R[n] = n, 0

    def add_row(self, row, lst):
        first = self.sz

        for c in lst:
            sz = self.sz
            self.L[sz] = sz-1
            self.R[sz] = sz+1
            self.D[sz] = c
            self.U[sz] = self.U[c]
            self.D[self.U[c]] = sz
            self.U[c] = sz
            self.row[sz] = row
            self.col[sz] = c
            self.S[c] += 1
            self.sz += 1

        self.R[self.sz - 1] = first
        self.L[first] = self.sz-1

    def remove(self, c):
        self.L[self.R[c]] = self.L[c]
        self.R[self.L[c]] = self.R[c]
        c_cur = c
        while (c_cur := self.D[c_cur]) != c:
            r_cur = c_cur
            while (r_cur := self.R[r_cur]) != c_cur:
                self.U[self.D[r_cur]] = self.U[r_cur]
                self.D[self.U[r_cur]] = self.D[r_cur]
                self.S[self.col[r_cur]] -= 1

    def restore(self, c):
        c_cur = c
        while (c_cur := self.U[c_cur]) != c:
            r_cur = c_cur
            while (r_cur := self.R[r_cur]) != c_cur:
                self.D[self.U[r_cur]] = r_cur
                self.U[self.D[r_cur]] = r_cur
                self.S[self.col[r_cur]] += 1

        self.R[self.L[c]] = c
        self.L[self.R[c]] = c

    def dfs(self, d):
        if self.R[0] == 0:
            self.ans_d = d
            return True

        c = self.R[0]
        cur_c = c
        while (cur_c := self.R[cur_c]) != 0:
            if self.S[cur_c] < self.S[c]:
                c = cur_c
        self.remove(c)
        cur_c = c
        while (cur_c := self.D[cur_c]) != c:
            self.ans[d] = self.row[cur_c]
            cur_r = cur_c
            while (cur_r := self.R[cur_r]) != cur_c:
                self.remove(self.col[cur_r])

            if self.dfs(d+1):
                return True
            cur_r = cur_c
            while (cur_r := self.L[cur_r]) != cur_c:
                self.restore(self.col[cur_r])
        self.restore(c)

    def solve(self):
        if not self.dfs(0):
            return None
        return self.ans[:self.ans_d]


def solve_sudoku(puzzle):
    SLOT, ROW, COL, SUB = 0, 1, 2, 3

    solver = DLX(9*9*4, 8000)

    def encode(x, y, z):
        return x*81 + y*9 + z + 1

    def decode(code):
        code = code - 1
        z = code % 9
        code //= 9
        y = code % 9
        code //= 9
        x = code
        return x, y, z

    for i in range(9):
        for j in range(9):
            for v in range(9):
                if puzzle[i][j] == '0' or puzzle[i][j] == str(v+1):
                    lst = []
                    lst.append(encode(SLOT, i, j))
                    lst.append(encode(ROW, i, v))
                    lst.append(encode(COL, j, v))
                    lst.append(encode(SUB, i//3*3 + j//3, v))
                    solver.add_row(encode(i, j, v), lst)

    for code in solver.solve():
        rr, cc, vv = decode(code)
        puzzle[rr][cc] = str(vv+1)


if __name__ == '__main__':
    puzzle = []
    for i in range(9):
        line = input()
        puzzle.append(list(line))

    solve_sudoku(puzzle)
    for i in puzzle:
        print("".join(i))
