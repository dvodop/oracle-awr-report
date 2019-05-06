#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import xlsxwriter

from datetime import date
from importlib import import_module

from plugins.plugin_xlsx import *
from plugins.plugin_report_conf import *
# from plugins.plugin_oradb import *
from plugins import *

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
#
v_column_title = []
v_conf = []
v_files = []

# ==================================================================
# ==================================================================
# Main routine
# ==================================================================
# ==================================================================

os.environ["NLS_LANG"] = "AMERICAN_AMERICA.AL32UTF8"

v_configuration["GENERAL_CONF"] = "conf.d/general.conf"

logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s %(levelname)s %(message)s')

# if using GENERAL_CONF, open it and parse
if v_configuration.get("GENERAL_CONF"):
    try:
        # try to open main configuration file
        if sys.version_info.major >= 3:
            v_config_file = open(v_configuration["GENERAL_CONF"], encoding="utf_8")
        if sys.version_info.major == 2:
            v_config_file = open(v_configuration["GENERAL_CONF"])
    except OSError as err:
        logging.critical("OS error: {0}".format(err))
        raise
    except Exception:
        logging.critical("Unexpected error:", sys.exc_info()[0])
        raise
    # for all rows in file
    for v_text_string in v_config_file.readlines():
        # if row is not empty and don't start from #
        if not v_text_string.startswith("\n") and not v_text_string.startswith("#"):
            v_parameter_name, v_parameter_value = v_text_string.split('=')
            v_configuration[v_parameter_name] = v_parameter_value.replace("\r", "").replace("\n", "").replace("\"", "")

# LOGGING
v_logger = logging.getLogger()
if not v_configuration.get("LOGGING"):
    v_log_level = 30
    v_configuration["LOGGING"]="WARNING"
elif v_configuration["LOGGING"].upper() == "DEBUG":
    v_log_level = 10
elif v_configuration["LOGGING"].upper() == "INFO":
    v_log_level = 20
elif v_configuration["LOGGING"].upper() == "WARNING":
    v_log_level = 30
elif v_configuration["LOGGING"].upper() == "ERROR":
    v_log_level = 40
elif v_configuration["LOGGING"].upper() == "CRITICAL":
    v_log_level = 50
v_logger.setLevel(v_log_level)

if v_configuration.get("PREFIX"):
    v_prefix = v_configuration["PREFIX"]

if not v_configuration.get("TITLE"):
    v_configuration["TITLE"] = ""


# ==================================================================
# parsing of main configuration file
# and command line arguments END
# ==================================================================

# ==================================================================
# dynamically import modules BEGIN
# ==================================================================
lst = os.listdir("plugins")
#for file in lst:
#    res = {}
#    file_path = os.path.abspath("plugins") + os.sep + file
#    logging.debug("file_path is [" + file_path + "]")
#    if os.path.isdir(file_path) and os.path.exists(file_path + os.sep + "__init__.py"):
#        logging.debug("trying to append module files")
#        v_files.append()
    # load the modules
#    for module_file in v_files:
#        res[module_file] = __import__("plugins." + module_file, fromlist=["*"])
#logging.debug("files in plugins/")
#logging.debug(v_files)

for file in lst:
    if "__" not in file and file != "plugin_xlsx.py" and file != "plugin_report_conf.py" and file.endswith(".py"):
        # module_name = file[:-3]
        # import_module("plugins." + module_name, '*')
         module_name = file.split('.')[0]
         globals()[module_name] = import_module('plugins.' + module_name, '*')

modules = [m for m in sys.modules.values() if m.__name__.startswith('plugins.plugin_')]
# ==================================================================
# dynamically import modules END
# ==================================================================


# creating xls file
if len(v_configuration["TITLE"]) == 0:
    v_workbook = xlsxwriter.Workbook(v_prefix +
                                     "report_" + date.today().strftime("%Y%m%d") + ".xlsx",  {'constant_memory': True})
else:
    v_workbook = xlsxwriter.Workbook(v_prefix +
                                     v_configuration["TITLE"] + "_" + date.today().strftime("%Y%m%d") +
                                     ".xlsx",  {'constant_memory': True})
if not v_configuration.get("AUTHOR"):
    v_conf_author = 'unknown'
else:
    v_conf_author = v_configuration["AUTHOR"]
if not v_configuration.get("COMPANY"):
    v_conf_company = 'unknown'
else:
    v_conf_company = v_configuration["COMPANY"]
v_workbook.set_properties({
    'title': v_configuration["TITLE"],
    'subject': 'awr based charts for ' + v_configuration["TITLE"],
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
if len(v_configuration["TITLE"]) == 0:
    v_logger.info('Created xls report [' + v_prefix +
                   "report_" + date.today().strftime("%Y%m%d") + ".xls]")
else:
    v_logger.info('Created xls report [' + v_prefix +
                   v_configuration["TITLE"] + "_" + date.today().strftime("%Y%m%d") +
                   ".xls]")

try:
    # open report configuration file
    if sys.version_info.major >= 3:
        v_config_file = open(v_configuration["REPORT_CONF"], encoding="utf_8")
    if sys.version_info.major == 2:
        v_config_file = open(v_configuration["REPORT_CONF"])
except OSError as err:
    v_logger.error("OS error: {0}".format(err))
    raise
except Exception:
    v_logger.error("Unexpected error:", sys.exc_info()[0])
    raise

for v_line in v_config_file.readlines():
    if not v_line.startswith("\n") and not v_line.startswith("#"):
        v = v_line.replace("\r", "").replace("\n", "")
        v_conf.append(v.split(":"))

v_config_file.close()
v_logger.info('Successfully read report config file ' + v_configuration["REPORT_CONF"])

v_conf = sorted(v_conf, key=lambda x: int(x[0]), reverse=False)

# ==================================================================
# for each query in report configuration file
for config_line in v_conf:
    v_logger.info('Processing plugin [' + config_line[1]
                  + '] with script file [' + config_line[2]
                  + '] for id [' + str(config_line[0]) + ']')

    v_worksheet = v_workbook.add_worksheet(config_line[3])

    v_id,\
    v_plugin,\
    v_source_file,\
    v_worksheet_title,\
    v_chart_title,\
    v_chart_conf_file,\
    v_columns_conf_file = parse_report_conf_line(v_configuration, v_logger, config_line, v_workbook, v_worksheet)

    logging.debug("Current config_line is:")
    logging.debug("v_id=[" + v_id + "]")
    logging.debug("v_plugin=[" + v_plugin + "]")
    logging.debug("v_source_file=[" + v_source_file + "]")
    logging.debug("v_worksheet_title=[" + v_worksheet_title + "]")
    logging.debug("v_chart_title=[" + v_chart_conf_file + "]")
    logging.debug("v_columns_conf_file=[" + v_columns_conf_file + "]")

    # v_title, v_data = plugin_oradb.oradb_gather_data(v_configuration, v_logger, config_line, v_workbook, v_worksheet)
    # get data from plugin using source file - dynamic call function from dynamic imported modules
    for module in modules:
        if module.__name__ == 'plugins.plugin_%s' % v_plugin:
            gather_data = getattr(module, "%s_gather_data" % v_plugin)
            v_title, v_data = gather_data(v_configuration, v_logger, config_line, v_workbook, v_worksheet)

    # ==================================================================
    # if we not use calculating columns, write data to worksheet
    # if v_columns_conf == "":
    if v_columns_conf_file == "default":
        logging.debug("id [" + v_id + "] is default data inserting")
        default_write_to_the_worksheet(v_configuration, v_logger, config_line, v_workbook, v_worksheet,
                                       v_title,
                                       v_data,
                                       header_format,
                                       integer_format,
                                       float_format)
    # adding calculating columns
    # if v_columns_conf != "":
    else:
        logging.debug("id [" + v_id + "] is custom data inserting")
        custom_write_to_the_worksheet(v_configuration, v_logger, config_line, v_workbook, v_worksheet,
                                      v_title,
                                      v_data,
                                      header_format,
                                      integer_format,
                                      float_format)

    # ==================================================================
    # Chart printing

    # If default, use all data
    if v_chart_conf_file == "default":
        logging.debug("id [" + v_id + "] is default charts creating")
        add_default_chart_to_xlsx(v_configuration, v_logger, config_line, v_workbook, v_worksheet,
                                  v_title,
                                  len(v_data))

        v_logger.debug("Created default chars to this data")
    # If not default, use config file
    elif v_chart_conf_file != "none":
        logging.debug("id [" + v_id + "] is custom charts creating")
        add_custom_charts_to_xlsx(v_configuration, v_logger, config_line, v_workbook, v_worksheet,
                                  len(v_data))

        v_logger.debug("Created custom charts to this data")
    # if none, do not print charts
    elif v_chart_conf_file == "none":
        v_logger.debug("Don't creating charts for this data")

v_logger.debug("Closing workbook")
v_workbook.close()
exit()
