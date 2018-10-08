#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import cx_Oracle
import xlsxwriter
import logging
import getpass

from datetime import date
from xlsxwriter.utility import xl_rowcol_to_cell

# __all__


# variables definition
v_configuration = {}
#
v_parameter_name = ''
v_parameter_value = ''
v_prefix = ''
v_worksheet_name = ''
#
v_dbid = int()
v_begin_snap = int()
v_end_snap = int()
v_log_level = 30
v_current_chart_id = 0
# 
v_column_title = []
v_conf = []
v_chart_conf = []

# ==================================================================
# ==================================================================
# Subroutines
# ==================================================================
# ==================================================================


# writing data to worksheet function
def write_to_the_worksheet(v_d_worksheet, v_d_title, v_d_data):
    d_row_i = 0
    d_col_i = 0
    # fille columns title
    for d_i in v_d_title:
        v_d_worksheet.write(d_row_i, d_col_i, d_i)
        d_col_i = d_col_i + 1

    v_d_worksheet.set_row(d_row_i, None, header_format)

    d_row_i = d_row_i + 1
    d_col_i = 0
    
    # fill data to cells
    for d_i in v_d_data:
        v_d_worksheet.write_row(d_row_i, d_col_i, d_i)
        v_d_worksheet.set_row(d_row_i, None, integer_format)
        d_row_i = d_row_i + 1


# adding chart to worksheet on all data function
def add_chart_to_xlsx(v_d_worksheet_title, v_d_chart_title, v_d_title, v_d_data):
    global v_workbook
    global v_worksheet

    # creating chart to worksheet
    v_d_chart = v_workbook.add_chart({'type': 'line'})
    v_count_snap = len(v_d_data)

    # adding data to charts, column by column
    for col_i in range(2, len(v_d_title)):
        v_d_chart.add_series({
            'name': v_d_title[col_i],
            'categories': '=' + v_d_worksheet_title + '!$A$2:$A$' + str(v_count_snap+1),
            'values': '=' + v_d_worksheet_title + '!' +
                      xl_rowcol_to_cell(1, col_i, row_abs=True, col_abs=True) +
                      ':' +
                      xl_rowcol_to_cell(v_count_snap, col_i, row_abs=True, col_abs=True),
            'line': {'width': 1, 'dash_type': 'solid'}
             })

    # chart title
    v_d_chart.set_title({
        'name': v_d_chart_title,
        'layout': {'x': 0.1, 'y': 0.04},
        'name_font': {
            'name': 'Arial',
            'color': 'black',
            'size': 9,
        }
    })

    # X-axis parameters
    v_d_chart.set_x_axis({
        'date_axis': True,
        'name_font': {
            'name': 'Arial',
            'color': 'black', 'size': 9
        },
        'num_font': {
            'name': 'Arial',
            'color': 'black', 'size': 9, 'rotation': -90
        },
    })

    # Y-axis parameters
    v_d_chart.set_y_axis({
        'num_format': '#,###',
        'num_font': {'name': 'Arial', 'color': 'black', 'size': 9},
        'name_font': {
            'name': 'Arial',
            'color': 'black',
            'size': 9,
            'rotation': 0
        },
    })

    # Chart size
    v_d_chart.set_size({'width': 850, 'height': 476})
    # Printing chart on worksheet
    v_worksheet.insert_chart('B5', v_d_chart, {'x_scale': 1, 'y_scale': 1})

# ==================================================================
# ==================================================================
# Main routine
# ==================================================================
# ==================================================================

os.environ["NLS_LANG"] = "AMERICAN_AMERICA.AL32UTF8"

# ==================================================================
# parsing of configuration file "general.conf" BEGIN
# ==================================================================
# default logging parameters
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s %(levelname)s %(message)s')

try:
    # try to open main configuration file
    v_config_file = open("conf.d/general.conf")
except OSError as err:
    logging.error("OS error: {0}".format(err))
    raise
except Exception:
    logging.error("Unexpected error:", sys.exc_info()[0])
    raise
# for all rows in file
for v_text_string in v_config_file.readlines():
    # if row is not empty and don't start from #
    if not v_text_string.startswith("\n") and not v_text_string.startswith("#"):
        v_parameter_name, v_parameter_value = v_text_string.split('=')
        v_configuration[v_parameter_name] = v_parameter_value.replace("\n", "").replace("\"", "")
v_config_file.close()

# LOGGING
v_logger = logging.getLogger()
if not v_configuration.get("LOGGING"):
    v_log_level = 30
elif v_configuration["LOGGING"] == "DEBUG":
    v_log_level = 10
elif v_configuration["LOGGING"] == "INFO":
    v_log_level = 20
elif v_configuration["LOGGING"] == "WARNING":
    v_log_level = 30
elif v_configuration["LOGGING"] == "ERROR":
    v_log_level = 40
elif v_configuration["LOGGING"] == "CRITICAL":
    v_log_level = 50
v_logger.setLevel(v_log_level)

if v_configuration.get("PREFIX"):
    v_prefix = v_configuration["PREFIX"]

# If we have not password in config file - ask it from command line
if not v_configuration.get("PASSWORD"):
    print("Please, enter password for Database")
    v_configuration["PASSWORD"] = getpass.getpass('Password:')

# ==================================================================
# parsing of configuration file "general.conf" END
# ==================================================================

# connecting to database
try:
    if not v_configuration.get("TNS_ALIAS"):
        v_db_host = v_configuration["HOST"]
        if v_configuration.get("PORT"):
            v_db_port = int(v_configuration["PORT"])
        else:
            v_db_port = 1521
        if v_configuration.get("SID"):
            v_db_sid = v_configuration["SID"]
        if v_configuration.get("SERVICE_NAME"):
            v_db_servicename = v_configuration["SERVICE_NAME"]

        if v_configuration.get("SID"):
            v_dsn = cx_Oracle.makedsn(v_db_host, v_db_port, v_db_sid)
        elif v_configuration.get("SERVICE_NAME"):
            v_dsn = cx_Oracle.makedsn(v_db_host, v_db_port, service_name = v_db_servicename)
        else:
            v_logger.error("Unknown SID/SERVICE_NAME parameter for db connection!")
            exit(1)

        v_configuration["TNS_ALIAS"] = v_dsn

    if v_configuration["USERNAME"] == "SYS":
        v_db_connection = cx_Oracle.connect(v_configuration["USERNAME"] + "/" +
                                            v_configuration["PASSWORD"] + "@" +
                                            v_configuration["TNS_ALIAS"], mode=cx_Oracle.SYSDBA)
    else:
        v_db_connection = cx_Oracle.connect(v_configuration["USERNAME"] + "/" +
                                            v_configuration["PASSWORD"] + "@" +
                                            v_configuration["TNS_ALIAS"])

except cx_Oracle.DatabaseError as connect_error:
    error, = connect_error.args
    if error.code == 1017:
        v_logger.error('Invalid database username or password ')
    else:
        v_logger.error('Database connection error: %s.'.format(connect_error))
    raise
v_logger.debug('Successfully connected to database: ' + v_configuration["TNS_ALIAS"])
v_cursor = v_db_connection.cursor()

# if variables not set in general.conf
# dbid
if not v_configuration.get("DBID"):
    v_sql_block = "select dbid from v$database"
    v_cursor.execute(v_sql_block)
    for result in v_cursor:
        v_dbid = result[0]
    v_logger.debug('Aquired dbid from database: ' + str(v_dbid))
else:
    v_dbid = v_configuration["DBID"]
    v_logger.debug('Aquired dbid from configuration file: ' + str(v_dbid))

# begin_snap
if not v_configuration.get("BEGIN_SNAP"):
    v_sql_block = "select min(snap_id) from dba_hist_snapshot where snap_timezone is not null and dbid = " + str(v_dbid)
    v_cursor.execute(v_sql_block)
    for result in v_cursor:
        v_begin_snap = result[0]
    v_logger.debug('Aquired begin snap from database: ' + str(v_begin_snap))
else:
    v_begin_snap = v_configuration["BEGIN_SNAP"]
    v_logger.debug('Aquired begin snap from configration file: ' + str(v_begin_snap))

# end_snap
if not v_configuration.get("END_SNAP"):
    v_sql_block = "select max(snap_id) from dba_hist_snapshot where snap_timezone is not null and dbid = " + str(v_dbid)
    v_cursor.execute(v_sql_block)
    for result in v_cursor:
        v_end_snap = result[0]
    v_logger.debug('Aquired end snap from database: ' + str(v_end_snap))
else:
    v_end_snap = v_configuration["END_SNAP"]
    v_logger.debug('Aquired end snap from configuration file: ' + str(v_end_snap))


v_db_connection.current_schema = "SYS"
v_db_connection.action = "awr_workshop"
v_db_connection.module = "excell_making"

# creating xls file
if len(v_configuration["DB_NAME"]) == 0:
    v_workbook = xlsxwriter.Workbook(v_prefix +
                                     "report_" + date.today().strftime("%Y%m%d") + ".xls",  {'constant_memory': True})
else:
    v_workbook = xlsxwriter.Workbook(v_prefix +
                                     v_configuration["DB_NAME"] + "_" + date.today().strftime("%Y%m%d") +
                                     ".xls",  {'constant_memory': True})
if not v_configuration.get("AUTHOR"):
    v_conf_author = 'unknown'
else:
    v_conf_author = v_configuration["AUTHOR"]
if not v_configuration.get("COMPANY"):
    v_conf_company = 'unknown'
else:
    v_conf_company = v_configuration["COMPANY"]
v_workbook.set_properties({
    'title': v_configuration["DB_NAME"],
    'subject': 'awr based charts for ' + v_configuration["DB_NAME"],
    'author': v_conf_author,
    'manager': '',
    'company': v_conf_company,
    'category': 'awr data',
    'keywords': 'awr, perfomance, analyze',
    'created':  date.today(),
    'comments': 'Created with cx_Oracle and xlsxwriter'})
header_format = v_workbook.add_format({'bg_color': '#FFBFBF',
                                       'align': 'center',
                                       'font_name': 'Arial',
                                       'font_size': 10})
integer_format = v_workbook.add_format({'num_format': '#,###0.0',
                                        'align': 'right',
                                        'font_name': 'Arial',
                                        'font_size': 10})
float_format = v_workbook.add_format({'num_format': '#,###0.0000',
                                      'align': 'right',
                                      'font_name': 'Arial',
                                      'font_size': 10})
if len(v_configuration["DB_NAME"]) == 0:
    v_logger.debug('Created xls report: ' + v_prefix +
                   "report_" + date.today().strftime("%Y%m%d") + ".xls")
else:
    v_logger.debug('Created xls report: ' + v_prefix +
                   v_configuration["DB_NAME"] + "_" + date.today().strftime("%Y%m%d") +
                   ".xls")

try:
    # open report configuration file
    v_config_file = open(v_configuration["REPORT_CONF"])
except OSError as err:
    v_logger.error("OS error: {0}".format(err))
    raise
except Exception:
    v_logger.error("Unexpected error:", sys.exc_info()[0])
    raise

for v_line in v_config_file.readlines():
    if not v_line.startswith("\n") and not v_line.startswith("#"):
        v = v_line.replace("\n", "")
        v_conf.append(v.split(":"))

v_config_file.close()
v_logger.debug('Successfully read report config file ' + v_configuration["REPORT_CONF"])

v_conf = sorted(v_conf, key=lambda x: int(x[0]), reverse=False)

# ==================================================================
# for each query in report configuration file
for i in v_conf:
    # if this is sql file
    if os.path.isfile("sql/" + i[1]) and os.path.splitext("sql/" + i[1])[1] == '.sql':
        v_logger.debug('Processing sql-query from file: ' + i[1])
        # set worksheet title as query title
        v_worksheet_name = os.path.splitext(i[1])[0]

        # read query from file
        v_sql_source = open("sql/" + i[1], 'r')
        v_sql_block = v_sql_source.read()
        v_sql_source.close()

        # execute query
        v_title = []
        v_data = []
        v_chart_title = ""
        v_chart_conf = []
        v_column_conf = []
        v_cursor = v_db_connection.cursor()
        v_cursor.prepare(v_sql_block)
        v_cursor.execute(None, {'v_dbid': v_dbid, 'v_begin_snap': v_begin_snap, 'v_end_snap': v_end_snap})
        for j in v_cursor.description:
            v_title.append(j[0])
        for j in v_cursor.fetchall():
            v_data.append(j)
        v_cursor.close()

        # add worksheet to file
        v_worksheet = v_workbook.add_worksheet(v_worksheet_name)
        # if we not use calculating columns, write data to worksheet
        if i[4] == "":
            write_to_the_worksheet(v_worksheet, v_title, v_data)

        if i[2] == "":
            v_chart_title = v_configuration["DB_NAME"] + " " + "не именованный график"
        else:
            v_chart_title = v_configuration["DB_NAME"] + " " + i[2]

        # ==================================================================
        # adding calculating columns
        if i[4] != "":
            v_logger.debug('Processing calculated columns for ' + i[1] + '. Configuration file: ' + i[4])
            try:
                # open calculating columns configuration file
                v_logger.debug('Trying to open column config file: ' + i[4])
                v_config_file = open(i[4])
            except OSError as err:
                v_logger.error("OS error: {0}".format(err))
                raise
            except Exception:
                v_logger.error("Unexpected error:", sys.exc_info()[0])
                raise

            # read config
            for v_line in v_config_file.readlines():
                if not v_line.startswith("\n") and not v_line.startswith("#"):
                    v_text_string = v_line.replace("\n", "")
                    v_column_conf.append(v_text_string.split(":"))
            v_config_file.close()
            v_logger.debug('Successfully read column config file ' + i[4])

            # write data to worksheet
            row_i = 1
            # fill columns title
            for col_i in range(len(v_title)):
                v_worksheet.write(0, col_i, v_title[col_i])
            # add columns title from configuration file
            for column_id in range(len(v_column_conf)):
                # write title
                v_worksheet.write(0, int(v_column_conf[column_id][0]), str(v_column_conf[column_id][1]))
            v_worksheet.set_row(0, None, header_format)
            # and write data to xls
            for result_i in v_data:
                # here write data
                for col_i in range(len(result_i)):
                    v_worksheet.write(row_i, col_i, result_i[col_i])
                # here write formulas
                for v_line_i in range(len(v_column_conf)):
                    v_worksheet.write_formula(row_i,
                                              int(v_column_conf[v_line_i][0]),
                                              v_column_conf[v_line_i][2].replace("_ROWID_", str(row_i + 1)))
                v_worksheet.set_row(row_i, None, integer_format)
                row_i = row_i + 1

        # ==================================================================
        # Chart printing
        # If default, use all data
        if i[3] == "default":
            if sys.version_info.major >= 3:
                add_chart_to_xlsx(v_worksheet_name, v_chart_title, v_title, v_data)
            if sys.version_info.major == 2:
                add_chart_to_xlsx(v_worksheet_name, v_chart_title.decode('utf8'), v_title, v_data)
            v_logger.debug("Created default chars to this data")
        # If not default, use config file
        elif i[3] != "none":
            try:
                # open config file for custom charts
                v_logger.debug('Trying to open charts config file: ' + i[3])
                v_config_file = open(i[3])
            except OSError as err:
                v_logger.error("OS error: {0}".format(err))
                raise
            except Exception:
                v_logger.error("Unexpected error:", sys.exc_info()[0])
                raise

            # read config
            for v_line in v_config_file.readlines():
                if not v_line.startswith("\n") and not v_line.startswith("#"):
                    v_text_string = v_line.replace("\n", "")
                    v_chart_conf.append(v_text_string.split(":"))
            v_config_file.close()
            v_logger.debug('Successfully read chart config file ' + i[3])

            v_chart_conf = sorted(v_chart_conf, key=lambda x: int(x[0]), reverse=False)

            for chart_id in range(len(v_chart_conf)):
                if i[2] == "":
                    v_chart_title = v_configuration["DB_NAME"] + " " + v_chart_conf[chart_id][2]
                else:
                    v_chart_title = i[2] + " " + v_chart_conf[chart_id][2]
                # if this chart id is already exist
                if v_current_chart_id == int(v_chart_conf[chart_id][0]):
                    # add column to chart
                    v_chart.add_series({
                        'name': '=' + v_worksheet_name + '!' +
                                xl_rowcol_to_cell(0, int(v_chart_conf[chart_id][1]), row_abs=True, col_abs=True),
                        'categories': '=' + v_worksheet_name + '!$A$2:$A$' + str(len(v_data) + 1),
                        'values': '=' + v_worksheet_name + '!' +
                                  xl_rowcol_to_cell(1, int(v_chart_conf[chart_id][1]), row_abs=True, col_abs=True) +
                                  ':' +
                                  xl_rowcol_to_cell(len(v_data),
                                                    int(v_chart_conf[chart_id][1]),
                                                    row_abs=True, col_abs=True),
                        'line': {'width': 1, 'dash_type': 'solid'}
                    })
                # if this chart id not exist
                else:
                    # print chart to worksheet if it is time to it
                    if v_current_chart_id != 0:
                        v_chart.set_size({'width': 850, 'height': 300})
                        v_worksheet.insert_chart('B' + str((v_current_chart_id - 1) * 15 + 3), v_chart,
                                                 {'x_scale': 1, 'y_scale': 1})
                        v_logger.debug('Added chart ' + str(v_current_chart_id))
                    # creating new chart
                    v_current_chart_id = int(v_chart_conf[chart_id][0])

                    v_chart = v_workbook.add_chart({'type': 'line'})

                    # add column to chart
                    v_chart.add_series({
                        'name': '=' + v_worksheet_name + '!' +
                                xl_rowcol_to_cell(0, int(v_chart_conf[chart_id][1]), row_abs=True, col_abs=True),
                        'categories': '=' + v_worksheet_name + '!$A$2:$A$' + str(len(v_data) + 1),
                        'values': '=' + v_worksheet_name + '!' +
                                  xl_rowcol_to_cell(1, int(v_chart_conf[chart_id][1]), row_abs=True, col_abs=True) +
                                  ':' +
                                  xl_rowcol_to_cell(len(v_data),
                                                    int(v_chart_conf[chart_id][1]),
                                                    row_abs=True, col_abs=True),
                        'line': {'width': 1, 'dash_type': 'solid'}
                    })

                    # main charts parameters
                    v_chart.set_legend({'position': 'top',
                                        #'border': 'none',
                                         'font': {'name': 'Arial','size': 9},
                                         'layout': {'x': 0.5, 'y': 0.04,
                                                   'width': 0.3,
                                                   'height': 0.1
                                                  }
                    })
                    if sys.version_info.major >= 3:
                        v_chart.set_title({
                            'name': v_chart_title,
                            'name_font': {'name': 'Arial', 'color': 'black', 'size': 9},
                            'overlay': ~True,
                            'layout': {'x': 0.1, 'y': 0.1,
                                       # 'width': 0.2,
                                       # 'height': 0.1
                                       }
                        })
                    if sys.version_info.major == 2:
                        v_chart.set_title({
                            'name': v_chart_title.decode('utf8'),
                            'name_font': {'name': 'Arial','color': 'black','size': 9},
                            'overlay':~True,
                            'layout': {'x': 0.1, 'y': 0.1,
                                       #'width': 0.2,
                                       #'height': 0.1
                                      }
                        })

                    v_chart.set_x_axis({
                        'date_axis': True,
                        'name_font': {
                            'name': 'Arial',
                            'color': 'black', 'size': 9
                        },
                        'num_font': {
                            'name': 'Arial',
                            'color': 'black', 'size': 9, 'rotation': -90
                        },
                    })

                    v_chart.set_y_axis({
                        'num_format': '#,###',
                        'num_font': {'name': 'Arial', 'color': 'black', 'size': 9},
                        'name_font': {
                            'name': 'Arial',
                            'color': 'black',
                            'size': 9,
                            'rotation': 0
                        },
                    })

            v_chart.set_size({'width': 850, 'height': 300})

            # print last chart to worksheet
            v_worksheet.insert_chart('B' + str((v_current_chart_id - 1) * 15 + 3),
                                     v_chart,
                                     {'x_scale': 1, 'y_scale': 1})
            v_logger.debug('Added chart ' + str(v_current_chart_id))

            # set v_current_chart_id in zero for next worksheets with custom charts
            v_current_chart_id = 0
        # if none, do not print charts
        elif i[3] == "none":
            v_logger.debug("Don't creating charts for this data")

v_workbook.close()
v_db_connection.close()
exit()
