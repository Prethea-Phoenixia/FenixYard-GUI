from copy import copy, deepcopy


class Matrix:
    def __init__(self, rows, columns):
        self.mat = []
        for i in range(0, rows):
            row = []
            for n in range(0, columns):
                row.append(0)
            self.mat.append(row)
        self.row = rows
        self.column = columns

    def print(self):
        for row in self.mat:
            print("[", end="")
            for column in row:
                print(" {:^8.1E}  ".format(column), end="")
            print("]")

    # prints an augmented matrix
    def print_aug(self):
        for row in self.mat:
            print("[", end="")
            i = 0
            for column in row:
                if i == len(row) - 1:
                    print("| {:^8.1E}  ".format(column), end="")
                else:
                    print(" {:^8.1E}  ".format(column), end="")
                i += 1
            print("]")

    def get(self, row, column):
        return self.mat[row][column]

    def set(self, row, column, val):
        self.mat[row][column] = val

    def get_row(self, a):
        return self.mat[a]

    def set_row(self, a, row):
        self.mat[a] = row

    def swp_row(self, a, b):
        a_row = self.get_row(a)
        b_row = self.get_row(b)

        self.set_row(a, b_row)
        self.set_row(b, a_row)

    def find_arg(self, x):
        i = 0
        for row in self.mat:
            e = 0
            for col in row:
                if col == x:
                    return (i, e)
                e += 1

    def transpose(self):
        row, column = self.column, self.row
        t = Matrix(row, column)
        i = 0
        for ro in self.mat:
            j = 0
            for n in ro:
                t.mat[j][i] = n
                j += 1
            i += 1
        return t

    def __mul__(self, o):

        if isinstance(o, Matrix):
            assert (
                self.column == o.row
            ), "Matrix of different size cannot be multiplied."

            result = Matrix(self.row, o.column)

            for i in range(self.row):
                for j in range(o.column):
                    cij = 0
                    for k in range(o.row):
                        cij += self.mat[i][k] * o.mat[k][j]

                    result.mat[i][j] = cij
            return result

        elif isinstance(o, float) or isinstance(o, int):
            result = Matrix(self.row, self.column)

            for i in range(self.row):
                for j in range(self.column):
                    cij = self.mat[i][j] * o
                    result.mat[i][j] = cij
            return result

        else:
            raise NotImplementedError

    def __add__(self, o):
        assert (
            self.column == o.column and self.row == o.row
        ), "Size mismatch when adding"

        result = Matrix(self.row, self.column)
        for i in range(self.row):
            for j in range(self.column):
                cij = 0

                cij = self.mat[i][j] + o.mat[i][j]

                result.mat[i][j] = cij
        return result

    def __sub__(self, o):
        assert (
            self.column == o.column and self.row == o.row
        ), "Size mismatch when subtracting"

        result = Matrix(self.row, self.column)
        for i in range(self.row):
            for j in range(self.column):
                cij = 0

                cij = self.mat[i][j] - o.mat[i][j]

                result.mat[i][j] = cij
        return result

    # find the element wise maxima value of an matrix.
    def max(self):
        maxima = None
        maxi = None
        maxj = None
        for i in range(0, self.row):
            for j in range(0, self.column):
                bigger = self.mat[i][j]

                if maxima is None or bigger > maxima:
                    maxima = bigger
                    maxi = i
                    maxj = j

        return maxima, maxi, maxj

    # find the element wise maxima value of an matrix.
    def min(self):
        minima = None
        mini = None
        minj = None
        for i in range(0, self.row):
            for j in range(0, self.column):
                smaller = self.mat[i][j]

                if minima is None or smaller < minima:
                    minima = smaller
                    mini = i
                    minj = j

        return minima, mini, minj

    def add_col(self, list_of_values):
        assert len(list_of_values) == len(
            self.mat
        ), "Shape mismatch while trying to add_col"
        i = 0
        for val in list_of_values:
            self.mat[i].append(val)
            i += 1
        self.column += 1
        return self

    def del_col(self, pos):
        for row in self.mat:
            row.pop(pos)
        self.column -= 1

    # solves an augmented matrix using gausian elimination
    def gauss(self):
        A = self.mat
        m = len(A)

        assert all(
            len(row) == m + 1 for row in A[1:]
        ), "Matrix rows have non-uniform length"
        n = m + 1

        for k in range(m):
            pivots = [abs(A[i][k]) for i in range(k, m)]
            i_max = pivots.index(max(pivots)) + k

            # Check for singular matrix
            assert A[i_max][k] != 0, "Matrix is singular!"

            # Swap rows
            A[k], A[i_max] = A[i_max], A[k]

            for i in range(k + 1, m):
                f = A[i][k] / A[k][k]
                for j in range(k + 1, n):
                    A[i][j] -= A[k][j] * f

                # Fill lower triangular matrix with zeros:
                A[i][k] = 0

        # Solve equation Ax=b for an upper triangular matrix A
        x = []
        for i in range(m - 1, -1, -1):
            x.insert(0, A[i][m] / A[i][i])
            for k in range(i - 1, -1, -1):
                A[k][m] -= A[k][i] * x[0]
        return x

    # return the inverse matrix of sel
    def inverse(self):
        assert self.row == self.column
        result = []
        for i in range(self.row):
            original = deepcopy(self)
            idr = [0] * original.row
            idr[i] = 1
            original.add_col(idr)
            result.append(original.gauss())

        res_matrix = Matrix(self.row, 0)

        for col in result:
            res_matrix.add_col(col)

        return res_matrix

    def mk_aug_self(self, ans):
        assert self.row == ans.row and ans.column == 1
        result = Matrix(self.row, self.column + 1)
        result.mat = deepcopy(self.mat)
        for i in range(0, self.row):
            result.mat[i].extend(ans.mat[i])
        return result


def lssq(a, b):
    assert a.row == b.row and b.column == 1, "Size mismatch for A and b"
    at = a.transpose()
    ata = at * a
    atb = at * b
    bvals = [x[0] for x in atb.mat]

    rref = ata.add_col(bvals)
    x = rref.gauss()
    return x


def nnls(A, y, epsilon):
    """
    A:        n         X:         Y:
        [   ,   ,   ]   [   ]   [   ]
     m  [   ,   ,   ] x [   ] = [   ]
        [   ,   ,   ]   [   ]   [   ]

    w:
        [   ,   ,   ]

    Ap:
        [   ,   ]
     m  [   ,   ]
        [   ,   ]

    """
    assert A.row == y.row and y.column == 1, "Size mismatch for A and b"
    m, n = A.row, A.column

    P = []

    # R = {1,...,n}
    R = list(range(0, n))
    # set x = to all 0 vector for dim n
    x = Matrix(n, 1)
    for i in range(0, n):
        x.mat[i][0] = 0

    # w:1
    #   [  ]
    # m [  ]
    #   [  ]

    w = A.transpose() * (y - A * x)

    while len(R) > 0 and w.max()[0] > epsilon:
        j = w.max()[1:2][0]

        R.pop(j)

        P.append(j)

        Ap = Matrix(m, len(P))
        e = 0
        for val_row in A.mat:
            i = 0
            i_o = 0
            for val in val_row:
                if i_o in P:
                    Ap.mat[e][i] = val
                    i += 1
                i_o += 1
            e += 1

        s = Matrix(n, 1)

        sp = (((Ap.transpose()) * Ap).inverse()) * (Ap.transpose()) * y

        i = 0
        for row in s.mat:
            if i in P:
                s.mat[i] = sp.mat[0]
            i += 1

        i = 0
        for row in s.mat:
            if i in R:
                s.mat[i] = [0]
            i += 1

        while sp.min()[0] <= 0:
            minalp = None
            for p in P:
                if s.mat[p][0] <= 0:
                    curr_alp = x.mat[p][0] / (x.mat[p][0] - s.mat[p][0])
                    if minalp is None or curr_alp < minalp:
                        minalp = curr_alp

            alpha = minalp
            x = x + (s - x) * alpha
            for p in P:
                if x[p][0] == 0:
                    R.pop(p)
                    P.append(p)

            sp = (((Ap.transpose()) * Ap).inverse()) * (Ap.transpose()) * y

            i = 0
            for row in s.mat:
                if i in P:
                    s.mat[i] = sp.mat[0]
                i += 1

            i = 0
            for row in s.mat:
                if i in R:
                    s.mat[i] = [0]
                i += 1

        x.mat = s.mat
        w = A.transpose() * (y - A * x)

    return [ans[0] for ans in x.mat]


if __name__ == "__main__":
    a = Matrix(4, 2)
    b = Matrix(4, 1)
    a.mat = [[0.0372, 0.2869], [0.6861, 0.7071], [0.6233, 0.6245], [0.6344, 0.6170]]
    b.mat = [[0.8587], [0.1781], [0.0747], [0.8405]]

    print("reference starting matrix")
    d = a.mk_aug_self(b)
    d.print_aug()
    print("reference solution")
    print("constrained [0,0.6929] unconstrained [-2.5627,3.1108]")
    print()
    print("testing unconstrained least square")
    print(lssq(a, b))
    print()
    print("testing NNLS")
    print(nnls(a, b, 1e-5))
