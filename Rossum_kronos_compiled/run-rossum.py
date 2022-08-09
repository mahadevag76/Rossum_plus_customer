#!/usr/bin/env python3

import inspect
import os
import signal
import sys
import time
import re
from collections import OrderedDict
import traceback

from config_loader import sys_env, read_yaml, write_yaml

user_config = read_yaml(
    os.path.dirname(os.path.abspath(__file__)) + os.sep + "config.yaml"
)
sysenv = sys_env(user_config["env_var"])

sys.path.extend(
    [
        sysenv.test_env,
        sysenv.plugins_path,
        sysenv.core_modules_path,
        sysenv.user_modules_path,
        sysenv.core_plugins_path,
        sysenv.user_plugins_path,
    ]
)

from logging_loader import rlogger

rlogger.add_logger(
    name="_main_",
    sink=sys.stdout,
    myformat=rlogger.formatter.format,
    level="TRACE",
    colorize=True,
    myfilter=rlogger.my_filter,
)
logger = rlogger.set_module_name("rossum_x")

import plugin_loader

plugin_loader.sysenv = sysenv
plugin_loader.read_yaml = read_yaml
plugin_loader.write_yaml = write_yaml
pm = plugin_loader.plugin_loader().register_plugins()

from helper import *

# from reporting import Report
from process_logs import archive_log
import test_case as test_case

test_case.sysenv = sysenv
test_case.user_config = user_config
test_case.pm = pm

"""
To run generic test cases:
    import test_case as test_case

To run inherited class test cases:
    import <inheritor class name> as test_case
    Ex: import test_case_manet as test_case
"""


# Handle ctrl+c
def signal_handler(sig, frame):
    print("Press ctrl+c to exit")

    try:
        testcase_obj.end_logs(result)
    except Exception as e:
        pass

    try:
        for teardown_fn in testcase_obj.fn_info_lst["teardown"]:
            myteardown = getattr(testcase_obj, teardown_fn)
            myteardown()
    except Exception as e:
        pass

    if dvars:
        # Default report with testcase name, result, start_time & end_time
        # logger.info(json.dumps(rvars))

        # Custom report adds log_path and run_cmd
        pass
        # ## custom_report = testcase_obj.get_report(dvars)
        # xls_report = Report(custom_report, evars.report_name, False)
    else:
        log.error("Nothing to report!")

    pm.hook.service_end_hook(evars=evars, pvars=pvars, dvars=dvars)
    # post_process_logs(evars)
    archive_log(evars.log_folder)

    sys.exit(1)


def get_testcase(testcase_file):
    # Take testcase_file path as input and return class object or False

    sys.path.append(os.path.dirname(testcase_file))

    try:
        user_testcase = __import__(
            os.path.splitext(os.path.basename(testcase_file))[0]
        )
    except Exception as e:
        log.error(
            "Skipping: testcase file "
            + os.path.basename(testcase_file)
            + " import failed"
        )
        log.error(str(e))
        sys.path.pop()
        return False

    sys.path.pop()

    # try:
    class_name_pattern = re.compile(
        r"\s*class ([a-zA-Z0-9_-]+)[\s]*\([a-zA-Z0-9_-]*\)\:.*"
    )
    test_class = []
    classname = []
    try:
        test_class = class_name_pattern.findall(
            inspect.getsource(user_testcase)
        )
    except Exception as e:
        pass

    if test_class:
        classname = [
            name
            for name, obj in inspect.getmembers(user_testcase)
            if inspect.isclass(obj)
        ]

    if (
        not test_class
        or test_class[0] not in classname
        or "TestCase" not in classname
    ):
        log.error("Incorrect test file: testcase class not found")
        return False

    testcase_obj = getattr(user_testcase, test_class[0])()

    for tag_name in ["setup", "test", "teardown"]:
        if testcase_obj.deco_dict[tag_name] is None:
            log.error(
                os.path.basename(testcase_file)
                + " import failed due to missing "
                + tag_name
                + " function.."
            )
            return False

    # except Exception as e:
    #     log.error("Incorrect test file: " + str(e))
    #     return(False)

    return testcase_obj


# ctrl+c handler
signal.signal(signal.SIGINT, signal_handler)

# Get user args
# dvars = OrderedDict()
pvars = NamedDict()
# rvars = OrderedDict()
evars = test_case.Env_Vars()
arguments = evars.get_valid_args()

rlogger.set_filter_level(arguments["log_type"])

rlogger.add_logger(
    name="_rf_",
    sink=evars.log_folder + "/RossumFramework.log",
    myformat="{time:YYYY-MM-DD HH:mm:ss}|{extra[mod_name]: <8}|{level: <4}|{message}",
    level="DEBUG",
    colorize=False,
)

if rlogger.my_filter.level == "DEBUG":
    rlogger.add_logger(
        name="_rfi_",
        sink=evars.log_folder + "/RossumFramework_info.log",
        myformat="{time:YYYY-MM-DD HH:mm:ss}|{extra[mod_name]: <8}|{level: <4}|{message}",
        level="INFO",
        colorize=False,
    )

try:
    pm.hook.service_start_hook(evars=evars, pvars=pvars)
except Exception as e:
    # print("exception in run-rossum - ", e)
    try:
        pm.hook.service_end_hook(evars=evars, pvars=pvars, dvars=dvars)
    except Exception as e:
        pass
    exit(1)

log = pvars.log

# Init logs then process user args
evars.log_init(pvars.log)
retvar = evars.process_args()
# dvars.update(json.loads(str(evars)))

# Exit if no valid testcase files found
if not evars.testcase_files:
    log.error("test cases not found")
    # dvars["test_files"] = "No testfiles found"
    pm.hook.service_end_hook(evars=evars, pvars=pvars, dvars=dvars)
    exit(3)

if evars.scale_time:
    wait(int(evars.scale_time))


# summary = OrderedDict()
# Loop through Testcase files
for testcase_file in evars.testcase_files:
    # log.info("Executing testcases from file " + testcase_file)
    testcase_obj = get_testcase(testcase_file)

    if testcase_obj is False:
        # dvars["test_files"][testcase_file].update({"status": "Testcase object creation failed"})
        continue

    testcase_obj.current = OrderedDict()
    testcase_obj.current["status"] = OrderedDict()
    testcase_obj.current["tf_name"] = testcase_file

    testcase_obj.log_init(pvars.log)

    try:
        execution_list = testcase_obj.get_tc_list(evars)
    except Exception as e:
        dvars[testcase_file] = "Testcase list enquiry failed"
        log.error("corrupt test file - " + testcase_file)
        continue

    # summary.update({os.path.basename(testcase_file): OrderedDict()})
    g_skip_teardown = testcase_obj.skip_teardown

    if not execution_list:
        dvars[testcase_file] = "No testcases matched in testfile"
        log.error("No testcase matched in testcase file - " + testcase_file)
    else:
        tmp_report = OrderedDict()
        for cnt, fn_info in enumerate(execution_list):

            testcase_obj.current["idx"] = cnt
            testcase_obj.current.update(fn_info)

            retry_counter = 0
            result = "timeout"

            if fn_info["uid"]:
                normalised_fn_info = (
                    fn_info["name"] + "@@@" + str(fn_info["uid"])
                )
            else:
                normalised_fn_info = fn_info["name"]

            testcase_obj.current["tc_name"] = normalised_fn_info

            if testcase_obj.current["tc_name"] not in list(
                dvars["test_files"][testcase_file]["fn_lst"].keys()
            ):
                dvars["test_files"][testcase_file]["fn_lst"].update(
                    OrderedDict([(testcase_obj.current["tc_name"], {})])
                )
            dvars["test_files"][testcase_file]["fn_lst"][
                testcase_obj.current["tc_name"]
            ].update(testcase_obj.current)

            if fn_info["retry"] is not None:
                dretry = 0
                try:
                    dretry = int(fn_info["retry"])
                except Exception as e:
                    testcase_obj.log.error(
                        "Incorrect retry value using "
                        + "default - "
                        + str(dretry)
                    )
                    testcase_obj.log.error(str(e))
            else:
                dretry = int(evars.default_retry)

            while result == "timeout" and retry_counter <= dretry:
                rlogger.add_logger(
                    name="_tf_",
                    sink=evars.log_folder
                    + os.sep
                    + os.path.splitext(
                        os.path.basename(testcase_obj.current["tf_name"])
                    )[0]
                    + ".log",
                    myformat=rlogger.formatter.format,
                    level=rlogger.my_filter.level,
                    colorize=False,
                )

                testcase_obj.pre_retry(retry_counter)

                time.sleep(2)
                result = "error"
                setup_result = None

                test_start = time.time()

                testcase_obj.log.stat(
                    "Starting testcase "
                    + testcase_obj.current["tc_name"]
                    + " ("
                    + os.path.basename(testcase_obj.current["tf_name"])
                    + ") "
                    + "[Try "
                    + str(retry_counter)
                    + "/"
                    + str(dretry)
                    + "] -> "
                    + epoch2time(test_start),
                    "All",
                )

                try:
                    # Run setup for first testcase even on skip_teardown.
                    if (not testcase_obj.skip_teardown) or (
                        cnt == 0 and retry_counter == 0
                    ):
                        for setup_fn in testcase_obj.fn_info_lst["setup"]:
                            mysetup = getattr(testcase_obj, setup_fn)
                            setup_result = mysetup()
                            testcase_obj.current["status"][
                                "setup"
                            ] = setup_result
                            testcase_obj.current["status"][
                                "test"
                            ] = setup_result

                        testcase_obj.skip_teardown = (
                            testcase_obj.skip_teardown or g_skip_teardown
                        )
                except Exception as e:
                    log.warn(
                        "Skipping: Error while executing testcase - "
                        + testcase_obj.current["tc_name"],
                        exc_info=False,
                    )
                    log.warn(traceback.format_exc())
                    log.error(
                        "Setup for Testcase "
                        + testcase_obj.current["tc_name"]
                        + " - aborted : "
                        + str(e)
                    )
                    result = "abort"
                    testcase_obj.current["status"]["setup"] = "abort"
                    testcase_obj.current["status"]["test"] = "abort"

                # testcase_obj.topology_object.init_nodes()
                if (
                    setup_result or setup_result is None
                ) and result != "abort":

                    try:
                        method_to_call = getattr(testcase_obj, fn_info["name"])

                        if cnt == 0:
                            testcase_obj.prev_args = False
                        else:
                            testcase_obj.prev_args = execution_list[cnt - 1][
                                "args"
                            ]

                        testcase_obj.args = fn_info["args"]
                        tmp_result = method_to_call()
                        del testcase_obj.args

                        if tmp_result:
                            result = "pass"
                        else:
                            result = "fail"
                    except AssertionError:
                        log.error("Assertion error occured")
                        log.warn(traceback.format_exc())
                        result = "fail"
                    except Exception as e:
                        if str(e) == "timeout":
                            log.warn(
                                "Testcase "
                                + testcase_obj.current["tc_name"]
                                + " - timeout"
                            )
                            result = "timeout"
                        else:
                            log.warn(
                                "Skipping: Error while executing "
                                + "testcase - "
                                + testcase_obj.current["tc_name"]
                            )
                            log.warn(traceback.format_exc())
                            log.error(
                                "Testcase "
                                + testcase_obj.current["tc_name"]
                                + " - aborted : "
                                + str(e)
                            )
                            result = "abort"
                    testcase_obj.current["status"]["test"] = result
                    # testcase_obj.topology_object.cleanup_nodes()

                try:
                    # Run teardown for last testcase even on skip_teardown.
                    if (
                        not testcase_obj.skip_teardown
                        or (
                            (cnt == len(execution_list) - 1)
                            and result != "timeout"
                        )
                        or (
                            (cnt == len(execution_list) - 1)
                            and retry_counter >= dretry
                        )
                    ):
                        for teardown_fn in testcase_obj.fn_info_lst[
                            "teardown"
                        ]:
                            myteardown = getattr(testcase_obj, teardown_fn)
                            teardown_result = myteardown()
                            testcase_obj.current["status"][
                                "teardown"
                            ] = teardown_result
                except Exception as e:
                    if setup_result and result != "abort":
                        log.error("Exception in teardown - " + str(e))
                        log.error(traceback.format_exc())
                    testcase_obj.current["status"]["teardown"] = "abort"
                    pass

                test_end = time.time()
                testcase_obj.log.stat(
                    "Ending testcase "
                    + testcase_obj.current["tc_name"]
                    + "( "
                    + os.path.basename(testcase_obj.current["tf_name"])
                    + ") -> "
                    + epoch2time(test_end)
                )
                testcase_obj.log.stat(
                    "Test Result: "
                    + result.upper()
                    + " | Time taken: "
                    + str(int(test_end - test_start))
                    + " secs)",
                    "All",
                )

                rlogger.remove_logger("_tf_")

                testcase_obj.end_logs(result)
                evars = testcase_obj.evars

                # Increment retry_counter at the end of loop
                retry_counter = retry_counter + 1

            if testcase_obj.current["tc_name"] not in list(tmp_report.keys()):
                tmp_report[testcase_obj.current["tc_name"]] = OrderedDict()

            # summary[os.path.basename(testcase_file)].update(
            #     OrderedDict({testcase_obj.current["tc_name"]: result}))

            tmp_report[testcase_obj.current["tc_name"]].update(
                OrderedDict(
                    {
                        "result": result,
                        "start_time": test_start,
                        "end_time": test_end,
                    }
                )
            )

            # if testcase_file not in list(rvars.keys()):
            #     rvars[testcase_file] = OrderedDict()

            # rvars[testcase_file].update(tmp_report)
            dvars["test_files"][testcase_file]["fn_lst"][
                testcase_obj.current["tc_name"]
            ].update(tmp_report[testcase_obj.current["tc_name"]])

if dvars:
    # Default report with testcase name, result, start_time & end_time
    # logger.info(json.dumps(rvars))

    # Custom report adds log_path and run_cmd
    pass
    # ## custom_report = testcase_obj.get_report(dvars)
    # xls_report = Report(custom_report, evars.report_name, False)
else:
    custom_report = False
    log.info("Nothing to report!")

# post_process_logs(evars)
archive_log(evars.log_folder)

pm.hook.service_end_hook(evars=evars, pvars=pvars, dvars=dvars)

# ## Exit with error number for devops

retval = 0

if not dvars:
    exit(3)

for tf, tfvar in dvars["test_files"].items():
    if tfvar["existance"] == 1:
        for tc, tcvar in tfvar["fn_lst"].items():
            if tcvar["result"] != "pass":
                retval = 1
                break
    else:
        retval = 2
        break

exit(retval)
