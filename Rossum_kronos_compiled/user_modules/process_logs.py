#!/usr/bin/env python3

import os
import shutil
import re


# Creating a separate info log
def rossum_info_log(log_folder):

    lf = log_folder + "/RossumFramework.log"
    if os.path.exists(lf):
        f0 = open(lf, "r+")
        f1 = open(log_folder + "/RossumFramework_info.log", "w+")
        buf = f0.readlines()
        for i in range(len(buf)):
            buf1 = buf[i].split("|")
            if "DBG" not in buf1[2]:
                f1.write(buf[i])
        f1.close()


def pmatch(fname):
    pattern_list = [
        re.compile(r"node[A-Z]+\.txt"),
        re.compile(r"pdu_node[A-Z]+\.log"),
        re.compile(r"pdu_node[A-Z]+\.bin"),
        re.compile(r"portMapperSvc\.log"),
        re.compile(r"routing_pdu_node[A-Z]+\.log"),
        re.compile(r"routing_pdu_node[A-Z]+\.bin"),
    ]
    for p in pattern_list:
        if p.match(fname):
            return True
    return False


def move_logs(evars, log_dir, tc_var):
    test_env = evars.test_env
    copy_testcase_files = []
    for tf in evars.testcase_files:
        if tc_var["tf_name"] in tf:
            copy_testcase_files.append(tf)

    user_inputs = log_dir + os.sep + "user_inputs" + os.sep
    log_files = []

    if not os.path.exists(user_inputs):
        os.makedirs(user_inputs)

    log_files.extend(
        [
            os.path.join(test_env, f)
            for f in os.listdir(test_env)
            if os.path.isfile(os.path.join(test_env, f)) and pmatch(f)
        ]
    )

    for lfile in log_files:
        shutil.move(lfile, log_dir)

    for tc in copy_testcase_files:
        shutil.copy(tc, user_inputs)


def post_process_logs(evars):
    if evars.log_type == "0":
        rossum_info_log(evars.log_folder)


def archive_log(log_folder):
    shutil.make_archive(
        log_folder,
        "zip",
        os.path.dirname(log_folder),
        os.path.basename(log_folder),
    )
