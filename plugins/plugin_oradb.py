# -*- coding: utf-8 -*-
# import getpass
import os
import sys
import cx_Oracle
import logging

from plugins.plugin_report_conf import *


def oradb_gather_data(l_configuration, l_logger, l_config_line, l_workbook, l_worksheet):
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

    # check mandatory oracle parameters
    if not l_configuration.get("ORADB_TNS_ALIAS") \
            and not l_configuration.get("HOST") \
            and not (l_configuration.get("ORADB_SID") or l_configuration.get("ORADB_SERVICE_NAME")):
        l_logger.error("Not set database access parameters! Use TNS_ALIAS or HOST, SID/SERVICE_NAME parameters!")
        exit(1)
    # TODO: перенести в модуль подключения к oracle
    if not l_configuration.get("ORADB_USERNAME"):
        l_logger.error("Not set database username! Use ORADB_USERNAME parameter!")
        exit(1)
    # TODO: перенести в модуль подключения к oracle
    if not l_configuration.get("REPORT_CONF"):
        l_logger.error("Not set path to report configuration file. Use REPORT_CONF!")
        exit(1)

    # TODO: ask password just one time !!!
    # If we have not orapassword - ask it from command line
    # if not l_configuration.get("ORA_PASSWORD"):
    #    print("Please, enter password for Oracle Database")
    #    l_configuration["ORA_PASSWORD"] = getpass.getpass('Password:')

    # connecting to database
    try:
        if not l_configuration.get("ORADB_TNS_ALIAS"):
            l_db_host = l_configuration["HOST"]
            if l_configuration.get("ORADB_PORT"):
                l_db_port = int(l_configuration["ORADB_PORT"])
            else:
                l_db_port = 1521
            if l_configuration.get("ORADB_SID"):
                l_db_sid = l_configuration["ORADB_SID"]
            if l_configuration.get("ORADB_SERVICE_NAME"):
                l_db_servicename = l_configuration["ORADB_SERVICE_NAME"]

            if l_configuration.get("ORADB_SID"):
                l_dsn = cx_Oracle.makedsn(l_db_host, l_db_port, l_db_sid)
            elif l_configuration.get("ORADB_SERVICE_NAME"):
                l_dsn = cx_Oracle.makedsn(l_db_host, l_db_port, service_name=l_db_servicename)
            else:
                l_logger.error("Unknown SID/SERVICE_NAME parameter for db connection!")
                exit(1)

            l_configuration["ORADB_TNS_ALIAS"] = l_dsn

        if l_configuration["ORADB_USERNAME"].upper() == "SYS":
            l_db_connection = cx_Oracle.connect(l_configuration["ORADB_USERNAME"] + "/" +
                                                l_configuration["ORADB_PASSWORD"] + "@" +
                                                l_configuration["ORADB_TNS_ALIAS"], mode=cx_Oracle.SYSDBA)
        else:
            l_db_connection = cx_Oracle.connect(l_configuration["ORADB_USERNAME"] + "/" +
                                                l_configuration["ORADB_PASSWORD"] + "@" +
                                                l_configuration["ORADB_TNS_ALIAS"])

    except cx_Oracle.DatabaseError as connect_error:
        error, = connect_error.args
        if error.code == 1017:
            l_logger.error('Invalid database username or password ')
        else:
            l_logger.error('Database connection error: %s.'.format(connect_error))
        raise
    l_logger.debug('Successfully connected to database: ' + l_configuration["ORADB_TNS_ALIAS"])
    l_cursor = l_db_connection.cursor()

    # if variables not set in general.conf
    # dbid
    if not l_configuration.get("ORADB_DBID"):
        l_sql_block = "select dbid from v$database"
        l_cursor.execute(l_sql_block)
        for result in l_cursor:
            l_dbid = result[0]
        l_logger.debug('Aquired dbid from database: ' + str(l_dbid))
    else:
        l_dbid = l_configuration["ORADB_DBID"]
        l_logger.debug('Aquired dbid from configuration file: ' + str(l_dbid))

    # begin_snap
    if not l_configuration.get("ORADB_BEGIN_SNAP"):
        l_sql_block = "select min(snap_id) from dba_hist_snapshot where snap_timezone is not null and dbid = " + str(
            l_dbid)
        l_cursor.execute(l_sql_block)
        for result in l_cursor:
            l_begin_snap = result[0]
        l_logger.debug('Aquired begin snap from database: ' + str(l_begin_snap))
    else:
        l_begin_snap = l_configuration["ORADB_BEGIN_SNAP"]
        l_logger.debug('Aquired begin snap from configration file: ' + str(l_begin_snap))

    # end_snap
    if not l_configuration.get("ORADB_END_SNAP"):
        l_sql_block = "select max(snap_id) from dba_hist_snapshot where snap_timezone is not null and dbid = " + str(
            l_dbid)
        l_cursor.execute(l_sql_block)
        for result in l_cursor:
            l_end_snap = result[0] + 1
        l_logger.debug('Aquired end snap from database: ' + str(l_end_snap))
    else:
        l_end_snap = l_configuration["ORADB_END_SNAP"]
        l_logger.debug('Aquired end snap from configuration file: ' + str(l_end_snap))

    l_db_connection.current_schema = "SYS"
    l_db_connection.action = "awr_workshop"
    l_db_connection.module = "excel_making"

    l_logger.debug('Processing sql-query from file: ' + l_source_file)

    # read query from file
    if sys.version_info.major >= 3:
        l_sql_source = open(l_source_file, 'r', encoding="utf_8")
    if sys.version_info.major == 2:
        l_sql_source = open(l_source_file, 'r')
    l_sql_block = l_sql_source.read()
    l_sql_source.close()

    # execute query
    l_title = []
    l_data = []
    l_chart_title = ""
    l_chart_conf = []
    l_column_conf = []
    l_cursor = l_db_connection.cursor()
    l_cursor.prepare(l_sql_block)
    l_cursor.execute(None, {'v_dbid': l_dbid, 'v_begin_snap': l_begin_snap, 'v_end_snap': l_end_snap})
    for j in l_cursor.description:
        l_title.append(j[0])
    for j in l_cursor.fetchall():
        l_data.append(j)
    l_cursor.close()

    l_db_connection.close()
    
    return l_title, l_data

