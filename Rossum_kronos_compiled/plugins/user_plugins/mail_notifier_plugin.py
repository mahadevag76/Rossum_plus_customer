#!/usr/bin/env python3

from plugin_base import *
from plugin_helper import *


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

    run_summary = {
        "tf": {"passed": testfiles_import, "total": testfiles_run},
        "tc": {"passed": testcases_pass, "total": testcases_run},
    }

    return tf_retval, tc_retval, run_summary


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
                sl_counter += 1
                start_time_str = time.strftime(
                    "%Y-%m-%d %H:%M:%S",
                    time.localtime(int(tcval["start_time"])),
                )
                end_time_str = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(int(tcval["end_time"]))
                )
                if "custom" not in list(tcval.keys()):
                    tcval = {}
                    tcval.update({"custom": {"log_path": "NA"}})
                    tcval.update({"custom": {"run-cmd": "NA"}})

                retvar.append(
                    [
                        sl_counter,
                        tf,
                        tc,
                        tcval["result"],
                        start_time_str,
                        end_time_str,
                        tcval["custom"]["log_path"],
                        tcval["custom"]["run-cmd"],
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


class mail_notifier_plugin(pluginBase):
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

        """
        User code in this function is executed in run_rossum.py
        after all testcases execution ends.

        Provides access to evars & report variable and expects user to return Bool
        """
        # ## User code Start
        # report = False

        valid_emails = []
        if evars.mail_recipients is not None:
            for email in evars.mail_recipients:
                if email_pattern.match(email):
                    valid_emails.append(email)
                else:
                    logger.warn(email + "is not a valid email")

            if len(valid_emails) > 0:

                if dvars:
                    # xls_report = Report(report, evars.report_name, False)
                    hmaker = html_maker()
                    # name, sheet_data, heading=True, color_col=3, blank_rows=1, blank_cols=1
                    tf_val, tc_val, run_summary = process_summary(dvars)

                    gen_val = [
                        [
                            os.path.basename(os.path.abspath(evars.test_env))
                            + " QA results ("
                            + hmaker.now_date
                            + ")"
                        ],
                        ["Log folder", evars.log_folder],
                        ["Report file", evars.report_name],
                    ]

                    hmaker.add_sheet("gen_report", gen_val, [1], 4)
                    gen_report = hmaker.generate_sheet("gen_report", "100%")

                    hmaker.add_sheet("tf_report", tf_val, [1], 4)
                    tf_report = hmaker.generate_sheet(
                        "tf_report", "48%", [], "left"
                    )

                    hmaker.add_sheet("tc_report", tc_val, [1], 4)
                    tc_report = hmaker.generate_sheet(
                        "tc_report", "48%", [], "right"
                    )

                    hmaker.add_sheet(
                        "report", process_report(evars, dvars), [1], 4
                    )
                    master_report = hmaker.generate_sheet(
                        "report", "100%", [7, 8]
                    )

                    """
                    mycmd = 'cd ' + str(evars.test_env) + '&& git log -4 --pretty="format:%h||%cd||%ce||%s" --date=short'
                    res = run_cmd(cmd_str=mycmd, sout=False, eout=False, use_shell=True)
                    commit_lst = [line.split("||") for line in res["sout"].splitlines()]
                    commit_lst.insert(0, ["Commit Hash","Commit Date","Committer Email","Commit Message"])
                    commit_lst.insert(0, ["Last 4 commits - repo " + os.path.basename(os.path.abspath(evars.test_env))])

                    hmaker.add_sheet("commit_report", commit_lst, [1, 2], 5)
                    commit_report = hmaker.generate_sheet("commit_report", "100%")
                    """

                    both_clear = '<div style="clear: both">'
                    mail_report = (
                        hmaker.sheet_html_start
                        + "<BR><BR>"
                        + both_clear
                        + tf_report
                        + tc_report
                        + both_clear
                        + "<BR><BR>"
                        + gen_report
                        + "<BR><BR>"
                        + master_report
                        + "<BR><BR>"
                        + hmaker.sheet_html_end
                    )
                    # + "<BR><BR>" + commit_report

                    username = "mahadevg@vayavyalabs.com"
                    password = "itphcgqqeurkqcxa"

                    to_addrs = valid_emails
                    body = mail_report

                    run_result = "FAILED"
                    if (
                        run_summary["tf"]["passed"]
                        == run_summary["tf"]["total"]
                    ):
                        if (
                            run_summary["tc"]["passed"]
                            == run_summary["tc"]["total"]
                        ):
                            run_result = "PASSED"

                    subject = (
                        "["
                        + run_result
                        + "] "
                        + os.path.basename(os.path.abspath(evars.test_env))
                        + " QA results ("
                        + hmaker.now_date
                        + ")"
                    )

                    try:
                        with SmtpServer(username, password) as server:
                            SendMail(server, to_addrs, subject, body)
                            # SendMail(server, to_addrs, subject, body, [evars.log_folder + ".zip"])
                        logger.info("Mail sent successfully!")
                    except Exception as e:
                        logger.error("Mail sent failed.." + str(e))

                    del hmaker

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
        parser.add_argument(
            "--mail",
            nargs="+",
            dest="mail_recipients",
            help="send mail to mail recipients",
        )
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
