#!/usr/bin/env python3

from plugin_base import *
from plugin_helper import *

from collections import OrderedDict
import datetime



def process_summary(dvars):
    '''
    Returns list of list with Test file and Test case summary
    '''

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
            ["Test File Summary", "==>"],
            ["Import passed", testfiles_import],
            ["Import error", testfiles_errored],
            ["Import nonexist", testfiles_nonexist],
            ["Total Testfiles", testfiles_run]
        ]
    else:
        tf_retval = False

    if testcases_run != 0:
        tc_retval = [
            ["Test Case Summary", "==>"],
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


def process_report(evars, dvars):
    retvar = [
        [
            "S.No",
            "Test File",
            "Test-Case",
            "Result",
            "Test Start",
            "Test End",
            "Log",
            "Command",
        ]
    ]

    sl_counter = 0
    for tf, tfval in dvars["test_files"].items():
        if tfval["existance"] == 1:
            for tc, tcval in tfval["fn_lst"].items():
                if "result" not in list(tcval.keys()):
                    continue
                sl_counter += 1
                start_time_str = time.strftime(
                    "%Y-%m-%d %H:%M:%S",
                    time.localtime(int(tcval["start_time"])),
                )
                end_time_str = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(int(tcval["end_time"]))
                )
                if "custom" not in list(tcval.keys()):
                    tcval["custom"] = {}
                if "log_path" not in list(tcval["custom"].keys()):
                    tcval["custom"].update({"log_path": "NA"})
                if "run-cmd" not in list(tcval["custom"].keys()):
                    tcval["custom"].update({"run-cmd": "NA"})

                if "result" in list(tcval.keys()):
                    retvar.append(
                        [
                            sl_counter,
                            tf,
                            tc,
                            tcval["result"],
                            start_time_str,
                            end_time_str,
                            tcval["custom"]["log_path"],
                            tcval["custom"]["run-cmd"]
                        ]
                    )

        elif tfval["existance"] == -1:
            sl_counter += 1
            retvar.append(
                [sl_counter, tf, "NA", "tf_error", "NA", "NA", "NA", "NA"]
            )

        elif tfval["existance"] == -2:
            sl_counter += 1
            retvar.append(
                [sl_counter, tf, "NA", "tf_error", "NA", "NA", "NA", "NA"]
            )

    if len(retvar) > 1:
        return retvar
    else:
        return False


class excel_report_plugin(pluginBase):
    """
    Class name and class function names are all
    part of template and must not be changed.
    """

    def set_dependency(self):
        super().set_dependency(["local_logging_plugin"])

    @hookimpl
    def service_start_hook(self, evars, pvars):
        """
        User code in this function is executed in run_rossum.py
        before any testcases are even imported.

        Provides access to evars variable and expects user to return Bool
        """
        # ## User code Start
        # logger.info(str(os.path.basename(__file__)) + " - Print from service_start_hook")
        return True
        # ## User code End

    @hookimpl
    def service_end_hook(self, evars, pvars, dvars):

        '''
        User code in this function is executed in run_rossum.py
        after all testcases execution ends.

        Provides access to evars & report variable and expects user to return Bool

        add_sheet(sheet_name, sheet_data, heading=True, color_col=3,
                    color_dict=None, blank_rows=1, blank_cols=1)
        update_sheet(sheet_name, sheet_data, heading=True,
                        color_col=3, color_dict=None, blank_rows=1, blank_cols=1)
            - sheet_name: Name of the excel file tab
            - sheet_data: table data in list of list format
            - heading: Consider 1st row as heading and format accordingly
            - color_col: column number or list of column number that need to apply coloring logic
            - color_dict: Coloring logic in dict format
                Ex: color_match1 = {
                        "<0": colorbox.limegreen,
                        "=0": colorbox.limegreen,
                        ">0": colorbox.darksalmon,
                        "=NA": colorbox.lightgray
                    }
            - blank_rows: Number of rows to skip before adding table
            - blank_cols: Number of cols to skip before adding table

        '''
        # ## User code Start
        # Excel report coloring logic
        color_match1 = {
            "=PASS": colorbox.limegreen,
            "=Pass": colorbox.limegreen,
            "=pass": colorbox.limegreen,
            "=FAIL": colorbox.darksalmon,
            "=Fail": colorbox.darksalmon,
            "=fail": colorbox.darksalmon,
            "=NA": colorbox.lightgray,
            "=Na": colorbox.lightgray,
            "=na": colorbox.lightgray
        }

        if dvars:
            # xls_report = Report(report, evars.report_name, False)
            emaker = excel_maker(evars.report_name)
            # name, sheet_data, heading=True, color_col=3, blank_rows=1, blank_cols=1
            tf_val, tc_val = process_summary(dvars)

            '''
            Add Summary tab to excel report
            '''
            emaker.add_sheet("summary", tf_val, [1, 0], 1, None, 2, 2)
            emaker.generate_sheet("summary")

            emaker.update_sheet("summary", tc_val, [1, 0], 1, None, 8, 2)
            emaker.generate_sheet("summary")

            emaker.add_sheet(
                "report", process_report(evars, dvars), [1, 0], 4, color_match1, 2, 0
            )
            emaker.generate_sheet("report")

            # Free up memory
            del emaker

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
        return True
        # ## User code End

    @hookimpl
    def post_teardown_hook(self, selfo):
        """
        User code in this function is executed in each test case's port_teardown function

        Provides access to testcase object ie. selfo and expects user to return Bool
        """
        # ## User code Start
        return True
        # ## User code End
