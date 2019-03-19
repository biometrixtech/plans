class ContingencyTable(object):
    def __init__(self, number_rows, number_columns):
        self.number_rows = number_rows
        self.number_columns = number_columns

        self.table = [[0 for x in range(self.number_columns + 1)] for y in range(self.number_rows + 1)]

        self.degrees_freedom = (self.number_rows - 1) * (self.number_columns - 1)

        self.chi_square = 0
        self.chi_square_significant_05 = None
        self.chi_square_significant_10 = None

    def calculate(self):

        total = 0
        chi_square = 0

        # first remove empty rows and update number of rows
        delete_list = []
        for r in range(self.number_rows):
            test_total = 0
            for c in range(self.number_columns):
                test_total += self.table[r][c]
            if test_total == 0:
                delete_list.append(r)

        delete_list.sort(reverse=True)

        for d in delete_list:
            #for c in range(self.number_columns):
            del self.table[d]

        self.number_rows = self.number_rows - len(delete_list)

        for c in range(self.number_columns):
            column_total = 0
            for r in range(self.number_rows):
                column_total += self.table[r][c]
                total += self.table[r][c]  # only need to calculate this one this pass through
            self.table[self.number_rows][c] = column_total

        for r in range(self.number_rows):
            row_total = 0
            for c in range(self.number_columns):
                row_total += self.table[r][c]
            self.table[r][self.number_columns] = row_total

        # now calc expected values and chi-square
        for c in range(self.number_columns):
            for r in range(self.number_rows):
                expected_value = (self.table[r][self.number_columns] * self.table[self.number_rows][c]) / float(total)
                if expected_value > 0:
                    chi_square += ((expected_value - self.table[r][c]) ** 2) / expected_value

        self.chi_square = chi_square
        self.chi_square_significant_05 = self.is_chi_square_significant_05(chi_square)
        self.chi_square_significant_10 = self.is_chi_square_significant_10(chi_square)

    def is_chi_square_significant_05(self, chi_square):

        chi_square_table = self.get_05_chi_square_table()

        is_significant = False

        if self.degrees_freedom <= 42:
            critical_value = chi_square_table[self.degrees_freedom]
            if chi_square >= critical_value:
                is_significant = True

        return is_significant

    def is_chi_square_significant_10(self, chi_square):

        chi_square_table = self.get_10_chi_square_table()

        is_significant = False

        if self.degrees_freedom <= 42:
            critical_value = chi_square_table[self.degrees_freedom]
            if chi_square >= critical_value:
                is_significant = True

        return is_significant

    def get_05_chi_square_table(self):

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

    def get_10_chi_square_table(self):

        cs = {}
        cs[1] = 2.7055
        cs[2] = 4.6052
        cs[3] = 6.2514
        cs[4] = 7.7794
        cs[5] = 9.2363
        cs[6] = 10.6446
        cs[7] = 12.017
        cs[8] = 13.3616
        cs[9] = 14.6837
        cs[10] = 15.9872
        cs[11] = 17.275
        cs[12] = 18.5493
        cs[13] = 19.8119
        cs[14] = 21.0641
        cs[15] = 22.3071
        cs[16] = 23.5418
        cs[17] = 24.769
        cs[18] = 25.9894
        cs[19] = 27.2036
        cs[20] = 28.412
        cs[21] = 29.6151
        cs[22] = 30.8133
        cs[23] = 32.0069
        cs[24] = 33.1962
        cs[25] = 34.3816
        cs[26] = 35.5632
        cs[27] = 36.7412
        cs[28] = 37.9159
        cs[29] = 39.0875
        cs[30] = 40.256
        cs[31] = 41.4217
        cs[32] = 42.5847
        cs[33] = 43.7452
        cs[34] = 44.9032
        cs[35] = 46.0588
        cs[36] = 47.2122
        cs[37] = 48.3634
        cs[38] = 49.5126
        cs[39] = 50.6598
        cs[40] = 51.805
        cs[41] = 52.9485
        cs[42] = 54.0902

        return cs