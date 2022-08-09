from base_class import *
from time import sleep


class my_sample_test(BaseClass):
    """
    Sample working TestCase with One TestCase
    """

    def __init__(self):
        super().__init__()
        
    @TestCase.testgen(path="user_testcases/abc.xlsx", sheet="abc")

    @BaseClass.setup
    def my_setup(self):
        self.logger.info("print from my setup")
        #xlvalue = self.args["input_file"]
        #self.logger.info(xvalue)
        #sleep(0.25)
        self.skip_teardown = True
        return True

    @BaseClass.test(tags=[["sanity_tc1"]])
    def test_case_1(self):
        self.logger.info("print from TestCase1")
        sleep(0.25)
        return True
    @BaseClass.test(tags=[["sanity_tc2"]])
    def test_case_2(self):
        self.logger.info("print from TestCase2")
        sleep(0.25)
        return True
    @BaseClass.test(tags=[["sanity_tc3"]])  
    def test_case_3(self):
        self.logger.info('print from TestCase3')
        m = 14
        k = int(m / 2)
        for y in range(1, m, 2):
            for j in range(0, k):
                print(end=" ")

            k = k - 1

            for z in range(1, y + 1):
                print("*", end="")
            print("")

        n = m - 3
        k = int(n / 2) - 3
        while n >= 1:
            for j in range(0, k):
                print(end=" ")

            k = k + 1

            for n1 in range(1, n + 1):
                print("*", end="")
            print("\r")
            n -= 2

        sleep(0.25)
        return (True)
    @BaseClass.teardown
    def my_teardown(self):
        self.logger.info("print from my teardown")
        sleep(0.25)
