# -*- coding: utf-8 -*-
# import getpass
import os
import sys
import cx_Oracle
import logging
import paramiko
import scp

from datetime import date
from datetime import datetime

from plugins.plugin_report_conf import *


def ssh_gather_data(l_configuration, l_logger, l_config_line, l_workbook, l_worksheet):
    """

    :param l_configuration: runtime configuration gathered from general.conf
    :param l_logger: runtime logger
    :param l_config_line: current report configuration line from REPORT_CONF
    :param l_workbook: current workbook
    :param l_worksheet: current worksheet
    :return: l_title, l_data
    """
    l_id,\
    l_plugin,\
    l_source_file,\
    l_worksheet_title,\
    l_chart_title,\
    l_chart_conf_file,\
    l_columns_conf_file = parse_report_conf_line(l_configuration, l_logger, l_config_line, l_workbook, l_worksheet)

    l_title = []
    l_data = []
    temp_data = []

    l_script_file = str(l_source_file).split()[0]
    head, tail = os.path.split(l_script_file)
    r_script_file = "/tmp/" + tail
    l_call_string = str(l_source_file).split('/')[1]
    r_call_string = "/tmp/" + l_call_string

    l_logger = logging.getLogger('oracle-awr-report.plugin_ssh')

    l_logger.debug("local call string is [" + l_call_string + "]")
    l_logger.debug("local scripts is [" + l_script_file + "]")

    l_logger.debug("remote call string is [" + r_call_string + "]")
    l_logger.debug("remote scripts is [" + r_script_file + "]")

    # ===============================================================================
    # send via scp shell script to host, execute it, and get datafile BEGIN
    # ===============================================================================
    if not l_configuration.get("SSH_PORT"):
        l_configuration["SSH_PORT"] = 22

    ssh_connect = paramiko.SSHClient()
    ssh_connect.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    if l_configuration.get("SSH_KEY") and not l_configuration.get("SSH_PASSWORD"):
        l_logger.info("Plugin [" + l_plugin + "]. Loading private key file: [" + str(l_configuration["SSH_KEY"]) + "]")
        if l_configuration.get("SSH_KEY_PASSPHRASE"):
            ssh_key = paramiko.RSAKey.from_private_key_file(l_configuration["SSH_KEY"], password=l_configuration["SSH_KEY_PASSPHRASE"])
        else:
            ssh_key = paramiko.RSAKey.from_private_key_file(l_configuration["SSH_KEY"])
        ssh_connect.connect(l_configuration["HOST"], username=l_configuration["SSH_USERNAME"], pkey=ssh_key)
    elif l_configuration.get("SSH_PASSWORD") and not l_configuration.get("SSH_KEY"):
        l_logger.info("Plugin [" + l_plugin + "]. Using password connection")
        ssh_connect.connect(l_configuration["HOST"], username=l_configuration["SSH_USERNAME"], password=str(l_configuration["SSH_PASSWORD"]))
    elif l_configuration.get("SSH_PASSWORD") and l_configuration.get("SSH_KEY"):
        l_logger.info("Plugin [" + l_plugin + "]. Loading private key file: ["
                      + str(l_configuration["SSH_KEY"]) + "]"
                      + ". Using password connection")
        if l_configuration.get("SSH_KEY_PASSPHRASE"):
            ssh_key = paramiko.RSAKey.from_private_key_file(l_configuration["SSH_KEY"], password=l_configuration["SSH_KEY_PASSPHRASE"])
        else:
            ssh_key = paramiko.RSAKey.from_private_key_file(l_configuration["SSH_KEY"])
        ssh_connect.connect(l_configuration["HOST"], username=l_configuration["SSH_USERNAME"], password=str(l_configuration["SSH_PASSWORD"]), pkey=ssh_key)

    scp_connect = scp.SCPClient(ssh_connect.get_transport())
    l_logger.debug("Tryng to put [" + l_script_file + "] via scp to [" + r_script_file + "]")
    scp_connect.put(l_script_file, r_script_file)

    ssh_stdin, ssh_stdout, ssh_stderr = ssh_connect.exec_command('chmod +x ' + r_script_file)
    if ssh_stdout.channel.recv_exit_status() != 0:
        l_logger.error("Error setting execute permissions on " + r_script_file + ": [" + str(ssh_stdout.channel.recv_exit_status()) + "]")

    ssh_stdin, ssh_stdout, ssh_stderr = ssh_connect.exec_command(r_call_string)
    if ssh_stdout.channel.recv_exit_status() != 0:
        l_logger.error("Exit status of " + r_script_file + ": [" + str(ssh_stdout.channel.recv_exit_status()) + "]")

    ssh_output = ssh_stdout.readlines()
    l_logger.debug("SSH Output:")
    l_logger.debug(ssh_output)
    ssh_output = ssh_output[0].split()
    data_file = str(ssh_output[0])
    ssh_output.pop(0)
    for i in range(len(ssh_output)):
        l_title.append(str(ssh_output[i]).replace("\n", ""))

    l_logger.debug("Data source file is [" + data_file + "]")
    l_logger.debug("Gathered title is [")
    l_logger.debug(l_title)
    l_logger.debug("]")

    ssh_stdin, ssh_stdout, ssh_stderr = ssh_connect.exec_command('rm -f ' + r_script_file)
    if ssh_stdout.channel.recv_exit_status() != 0:
        l_logger.error("Error when removing " + r_script_file
                       + ": [" + str(ssh_stdout.channel.recv_exit_status()) + "]")

    scp_connect.get(data_file)

    ssh_stdin, ssh_stdout, ssh_stderr = ssh_connect.exec_command('rm -f ' + data_file)
    if ssh_stdout.channel.recv_exit_status() != 0:
        l_logger.error("Error where removing data_file [" + data_file
                       + "] : [" + str(ssh_stdout.channel.recv_exit_status()) + "]")

    head, tail = os.path.split(data_file)
    data_file = tail

    scp_connect.close()
    ssh_connect.close()
    # ===============================================================================
    # send via scp shell script to host, execute it, and get datafile END
    # ===============================================================================

    # TODO: generate l_data from data_file

    try:
        if sys.version_info.major >= 3:
            data_source = open(data_file, encoding="utf_8")
        if sys.version_info.major == 2:
            data_source = open(data_file)
    except OSError as err:
        logging.critical("OS error: {0}".format(err))
        raise
    except Exception:
        logging.critical("Unexpected error:", sys.exc_info()[0])
        raise
    # for all rows in file
    for text_string in data_source.readlines():
        temp_data.append(text_string)

    for i in range(len(temp_data)):
        l_data.append(temp_data[i].split())

    size_of_column = len(l_data)
    size_of_row = len(l_data[0])
    for i in range(size_of_column):
        for j in range(size_of_row):
            l_data[i][j]=float(l_data[i][j])

    for i in range(size_of_column):
        l_data[i].insert(0, datetime.utcfromtimestamp(int(l_data[i][0])).strftime('%Y.%m.%d %H:%M:%S'))
    l_title.insert(0, 'datetime')

    data_source.close()
    os.remove(data_file)

    return l_title, l_data
