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
            for column in row:
                print(" {:^6.2f}  ".format(column), end="")
            print("")

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

    def gauss(self):
        A = self.mat
        m = len(A)
        assert all(
            [len(row) == m + 1 for row in A[1:]]
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


if __name__ == "__main__":
    a = Matrix(2, 3)
    a.mat = [[2, 1, -1, 8], [-3, -1, 2, -11], [-2, 1, 2, -3]]
    print(a.gauss())
    a.print()
