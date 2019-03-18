class ContingencyTable(object):
    def __init__(self, number_rows, number_columns):
        self.number_rows = number_rows
        self.number_columns = number_columns

        self.table = [[0 for x in range(self.number_columns)] for y in range(self.number_rows + 1)]

        self.degrees_freedom = (self.number_rows - 1) * (self.number_columns - 1)

        self.chi_square_significant = None

    def calculate(self):

        total = 0
        chi_square = 0
        for c in range(self.number_columns):
            column_total = 0
            for r in range(self.number_rows):
                column_total += self.table[r][c]
                total += self.table[r][c]  # only need to calculate this one this pass through
            self.table[self.number_rows+1][c] = column_total

        for r in range(self.number_rows):
            row_total = 0
            for c in range(self.number_columns):
                row_total += self.table[r][c]
            self.table[r][self.number_columns + 1] = row_total

        # now calc expected values and chi-square
        for c in range(self.number_columns):
            for r in range(self.number_rows):
                expected_value = (self.table[r][self.number_columns + 1] * self.table[self.number_rows + 1][c]) / float(total)
                chi_square += ((expected_value - self.table[r][c]) ** 2) / expected_value

        self.chi_square_significant = self.is_chi_square_significant(chi_square)

    def is_chi_square_significant(self, chi_square):

        chi_square_table = self.get_chi_square_table()

        is_significant = False

        if self.degrees_freedom <= 42:
            critical_value = chi_square_table[self.degrees_freedom]
            if chi_square >= critical_value:
                is_significant = True

        return is_significant

    def get_chi_square_table(self):

        cs = {}
        cs[1] = 3.8415
        cs[2] = 5.9915
        cs[3] = 7.8147
        cs[4] = 9.4877
        cs[5] = 11.0705
        cs[6] = 12.5973
        cs[7] = 14.0671
        cs[8] = 15.5073
        cs[9] = 16.919
        cs[10] = 18.307
        cs[11] = 19.6752
        cs[12] = 21.0261
        cs[13] = 22.362
        cs[14] = 23.6848
        cs[15] = 24.9958
        cs[16] = 26.2962
        cs[17] = 27.5871
        cs[18] = 28.8693
        cs[19] = 30.1435
        cs[20] = 31.4104
        cs[21] = 32.6706
        cs[22] = 33.9245
        cs[23] = 35.1725
        cs[24] = 36.415
        cs[25] = 37.6525
        cs[26] = 38.8851
        cs[27] = 40.1133
        cs[28] = 41.3372
        cs[29] = 42.5569
        cs[30] = 43.773
        cs[31] = 44.9853
        cs[32] = 46.1942
        cs[33] = 47.3999
        cs[34] = 48.6024
        cs[35] = 49.8018
        cs[36] = 50.9985
        cs[37] = 52.1923
        cs[38] = 53.3835
        cs[39] = 54.5722
        cs[40] = 55.7585
        cs[41] = 56.9424
        cs[42] = 58.124

        return cs