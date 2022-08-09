#!/usr/bin/env python3

from plugin_base import *

import json
import argparse


def process_summary(dvars):

    testfiles_run = 0
    testfiles_import = 0
    testfiles_errored = 0
    testfiles_nonexist = 0

    testcases_run = 0
    testcases_pass = 0
    testcases_fail = 0
    testcases_abort = 0
    testcases_timeout = 0
    testcases_error = 0

    for tf, tfvar in dvars["test_files"].items():
        testfiles_run += 1
        if tfvar["existance"] == 1:
            testfiles_import += 1
            for tc, tcvar in tfvar["fn_lst"].items():
                if "result" not in list(tcvar.keys()):
                    continue
                testcases_run += 1
                if tcvar["result"] == "pass":
                    testcases_pass += 1
                elif tcvar["result"] == "fail":
                    testcases_fail += 1
                elif tcvar["result"] == "abort":
                    testcases_abort += 1
                elif tcvar["result"] == "timeout":
                    testcases_timeout += 1
                elif tcvar["result"] == "error":
                    testcases_error += 1
        elif tfvar["existance"] == -1:
            testfiles_errored += 1
        elif tfvar["existance"] == -2:
            testfiles_nonexist += 1

    tmp_tf_count = testfiles_import + testfiles_errored + testfiles_nonexist

    tmp_tc_count = (
        testcases_pass
        + testcases_fail
        + testcases_abort
        + testcases_timeout
        + testcases_error
    )

    if testfiles_run != 0:
        tf_retval = [
            ["Test File Summary", "     "],
            ["Import passed", testfiles_import],
            ["Import error", testfiles_errored],
            ["Import nonexist", testfiles_nonexist],
            ["Total Testfiles", testfiles_run],
        ]
    else:
        tf_retval = False

    if testcases_run != 0:
        tc_retval = [
            ["Test Case Summary", "     "],
            ["Test-Case Passed", testcases_pass],
            ["Test-Case Failed", testcases_fail],
            ["Test-Case Aborted", testcases_abort],
            ["Test-Case Timeout", testcases_timeout],
            ["Test-Case Errored", testcases_error],
            ["Total Testcases", testcases_run],
        ]
    else:
        tc_retval = False

    return tf_retval, tc_retval


def print_table(dlist, heading, header=True):
    """
    print_table(
        [["Total", "2"], ["Passing", "2"], ["Failing", "5"],
        ["Abort", "5"], ["Timeout", "5"], ["Error", "5"]], header=False)
    """

    tmpl1 = []
    for idx, l1 in enumerate(dlist):
        tmpl2 = []
        for l2 in l1:
            tmpl2.append(str(l2))
        tmpl1.append(tmpl2)
    dlist = tmpl1

    rsize = {}
    for lidx, l1 in enumerate(dlist):
        for eidx, e in enumerate(l1):
            if eidx not in list(rsize.keys()):
                rsize[eidx] = 0
            if rsize[eidx] < len(e):
                rsize[eidx] = len(e)

    hrow = ""
    for l1 in dlist:
        for eidx, e in enumerate(l1):
            hrow = hrow + "-" * rsize[eidx]
        break
    hrow = hrow + "-" * (len(rsize) + 1) * 3

    ptext = heading
    # 4 substracted to compansate for 2+2 spaces before and after ptext
    header_p1 = "=" * int(((len(hrow) - len(ptext)) - 4) / 2)
    header_p2 = "=" * int(len(hrow) - (len(header_p1) + len(ptext)) - 4)

    logger.stat(hrow)
    logger.stat(header_p1 + "  " + ptext + "  " + header_p2)
    logger.stat(hrow)
    for l1 in dlist:
        tmp_str = ""
        for eidx, e in enumerate(l1):
            blank_str = " " * (rsize[eidx] - len(e))
            tmp_str += " | " + e + blank_str
        logger.stat(tmp_str + " |")
        if header:
            logger.stat(hrow)
            header = False
    logger.stat(hrow)


class print_summary_plugin(pluginBase):
    """
    Class name and class function names are all
    part of template and must not be changed.
    """

    def set_dependency(self):
        super().set_dependency(["b_logging_client_plugin"])

    @hookimpl
    def service_start_hook(self, evars, pvars):
        """
        User code in this function is executed in run_rossum.py
        before any testcases are even imported.

        Provides access to evars variable and expects user to return Bool
        """
        # ## User code Start
        # print(str(os.path.basename(__file__)) + " - Print from service_start_hook")

        return True
        # ## User code End

    @hookimpl(trylast=True)
    def service_end_hook(self, evars, pvars, dvars):
        if not dvars:
            return False

        """
        User code in this function is executed in run_rossum.py
        after all testcases execution ends.

        Provides access to evars & report variable and expects user to return Bool
        """
        # ## User code Start
        time.sleep(2)

        # print("****************evarsreport*********************")
        # print(str(report))
        # # print(json.dumps(dvars, indent=4))
        # print("*************************************")

        # Print summary to logs then close logs
        # logger.debug(json.dumps(report))

        tf_val, tc_val = process_summary(dvars)

        # if tf_val != False:
        #     print_table(tf_val[1:], "RESULT SUMMARY -> Test File", False)

        if tc_val:
            print_table(tc_val[1:], "RESULT SUMMARY -> Test Case", False)

        time.sleep(1)
        return True
        # ## User code End

    @hookimpl
    def argparse_hook(self, parser):
        """
        User code in this function is executed in test_case.py baseclass.
        Plugin specific user arguments can be added here.

        Provides user parser object and expects user to return it after adding arguments.
        """
        # ## User code Start
        # ## User code End

        return parser

    @hookimpl
    def pre_setup_hook(self, selfo):
        """
        User code in this function is executed in each test case's pre_setup function

        Provides access to testcase object ie. selfo and expects user to return Bool
        """
        # ## User code Start
        # print(str(os.path.basename(__file__)) + " - Print from pre_setup hook")
        return True
        # ## User code End

    @hookimpl
    def post_teardown_hook(self, selfo):
        """
        User code in this function is executed in each test case's port_teardown function

        Provides access to testcase object ie. selfo and expects user to return Bool
        """
        # ## User code Start
        # print(str(os.path.basename(__file__)) + " - Print from post_teardown hook")
        return True
        # ## User code End
