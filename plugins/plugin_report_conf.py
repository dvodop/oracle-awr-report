# -*- coding: utf-8 -*-
import sys


def parse_report_conf_line(l_configuration, l_logger, l_config_line, l_workbook, l_worksheet):
    """

    :param l_configuration: runtime configuration gathered from general.conf
    :param l_logger: runtime logger
    :param l_config_line: current report configuration line from REPORT_CONF
    :param l_workbook: current workbook
    :param l_worksheet: current worksheet
    :return: parsed to variables l_config_line
    """
    # id:plugin:script file:worksheet title:название графика:конф отрисовки графика:конфиг для вычисляемых столбцов
    #  0:     1:          2:              3:               4:                     5:                              6
    l_id = l_config_line[0]
    l_plugin = l_config_line[1]
    l_source_file = l_config_line[2]
    l_worksheet_title = l_config_line[3]
    if l_config_line[3] == "":
        l_chart_title = l_configuration["TITLE"] + " " + "не именованный график"
    else:
        l_chart_title = l_configuration["TITLE"] + " " + l_config_line[4]
    l_chart_conf_file = l_config_line[5]
    l_columns_conf_file = l_config_line[6]

    if sys.version_info.major == 2:
        l_chart_title = l_chart_title.decode('utf8')

    return l_id, l_plugin, l_source_file, l_worksheet_title, l_chart_title, l_chart_conf_file, l_columns_conf_file
