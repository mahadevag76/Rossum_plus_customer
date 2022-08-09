from test_case import *


class BaseClass(TestCase):
    def __init__(self):

        super().__init__()

    def log_init(self, base_log):

        res = super().log_init(base_log)
        return res

    def pre_setup(self):

        res = super().pre_setup()
        self.__result__ = [False]

        return res

    def post_teardown(self):

        res = super().post_teardown()

        return res

    def end_logs(self, tc_res):

        res = super().end_logs(tc_res)

        return res

    def test_extend(self, tc_fn_info):

        res = super().test_extend(tc_fn_info)
        return res

    def pre_retry(self, retry_counter):

        res = super().pre_retry(retry_counter)
        return res

    def testgen_logic(self, path=None, sheet=None):
        res = super().testgen_logic(path=path, sheet=sheet)
        return res

    """
    User functions
    """
