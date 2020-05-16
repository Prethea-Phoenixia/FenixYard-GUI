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
        assert self.column == o.row, "Matrix of different size cannot be multiplied."

        result = Matrix(self.row, o.column)

        for i in range(self.row):

            for j in range(o.column):

                cij = 0

                for k in range(o.row):
                    cij += self.mat[i][k] * o.mat[k][j]

                result.mat[i][j] = cij
        return result

    def add_col(self, list_of_values):
        assert len(list_of_values) == len(
            self.mat
        ), "Shape mismatch while trying to add_col"
        for val in list_of_values:
            self.mat[list_of_values.index(val)].append(val)
        self.column += 1
        return self

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


def lssq(a, b):
    assert a.row == b.row and b.column == 1, "Size mismatch for A and b"
    at = a.transpose()
    ata = at * a
    atb = at * b
    bvals = [x[0] for x in atb.mat]

    rref = ata.add_col(bvals)
    rref.print_aug()
    x = rref.gauss()
    return x


if __name__ == "__main__":
    a = Matrix(3, 2)
    b = Matrix(3, 1)
    a.mat = [[0, 1], [1, 1], [2, 1]]
    b.mat = [[6], [0], [0]]
    r = lssq(a, b)
    print()
    print(r)
