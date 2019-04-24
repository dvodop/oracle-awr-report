# -*- coding: utf-8 -*-
import os
import sys
import xlsxwriter

from xlsxwriter.utility import xl_rowcol_to_cell

from plugins.plugin_report_conf import *


# writing data to worksheet function
def default_write_to_the_worksheet(l_configuration, l_logger, l_config_line, l_workbook, l_worksheet,
                                   l_title,
                                   l_data,
                                   l_header_format,
                                   l_integer_format,
                                   l_float_format):
    """

    :param l_configuration: runtime configuration gathered from general.conf
    :param l_logger: runtime logger
    :param l_config_line: current report configuration line from REPORT_CONF
    :param l_workbook: current workbook
    :param l_worksheet: current worksheet
    :param l_title: first line to worksheet, columns titles
    :param l_data: data which must be written to worksheet
    :param l_header_format:
    :param l_integer_format:
    :param l_float_format:
    :return:
    """
    l_id,\
    l_plugin,\
    l_source_file,\
    l_worksheet_title,\
    l_chart_title,\
    l_chart_conf_file,\
    l_columns_conf_file = parse_report_conf_line(l_configuration, l_logger, l_config_line, l_workbook, l_worksheet)
    d_row_i = 0
    d_col_i = 0
    # fille columns title
    for d_i in l_title:
        l_worksheet.write(d_row_i, d_col_i, d_i)
        d_col_i = d_col_i + 1

    l_worksheet.set_row(d_row_i, None, l_header_format)

    d_row_i = d_row_i + 1
    d_col_i = 0

    # fill data to cells
    for d_i in l_data:
        l_worksheet.write_row(d_row_i, d_col_i, d_i)
        l_worksheet.set_row(d_row_i, None, l_integer_format)
        d_row_i = d_row_i + 1


# writing data and formulas to worksheet function
def custom_write_to_the_worksheet(l_configuration, l_logger, l_config_line, l_workbook, l_worksheet,
                                  l_title,
                                  l_data,
                                  l_header_format,
                                  l_integer_format,
                                  l_float_format):
    """

    :param l_configuration: runtime configuration gathered from general.conf
    :param l_logger: runtime logger
    :param l_config_line: current report configuration line from REPORT_CONF
    :param l_workbook: current workbook
    :param l_worksheet: current worksheet
    :param l_title: first line to worksheet, columns titles
    :param l_data: data which must be written to worksheet
    :param l_header_format:
    :param l_integer_format:
    :param l_float_format:
    :return:
    """
    l_id,\
    l_plugin,\
    l_source_file,\
    l_worksheet_title,\
    l_chart_title,\
    l_chart_conf_file,\
    l_columns_conf_file = parse_report_conf_line(l_configuration, l_logger, l_config_line, l_workbook, l_worksheet)

    l_column_conf = []

    l_logger.debug('Processing calculated columns for ' + l_worksheet_title + '. Configuration file: ' + l_columns_conf_file)
    try:
        # open calculating columns configuration file
        l_logger.debug('Trying to open column config file: ' + l_columns_conf_file)
        if sys.version_info.major >= 3:
            l_config_file = open(l_columns_conf_file, encoding="utf_8")
        if sys.version_info.major == 2:
            l_config_file = open(l_columns_conf_file)
    except OSError as err:
        l_logger.error("OS error: {0}".format(err))
        raise
    except Exception:
        l_logger.error("Unexpected error:", sys.exc_info()[0])
        raise

    # read config
    for l_line in l_config_file.readlines():
        if not l_line.startswith("\n") and not l_line.startswith("#"):
            l_text_string = l_line.replace("\r", "").replace("\n", "")
            l_column_conf.append(l_text_string.split(":"))
    l_config_file.close()
    l_logger.debug('Successfully read column config file ' + l_config_line[6])

    # write data to worksheet
    row_i = 1
    # fill columns title
    for col_i in range(len(l_title)):
        l_worksheet.write(0, col_i, l_title[col_i])
    # add columns title from configuration file
    for column_id in range(len(l_column_conf)):
        # write title
        l_worksheet.write(0, int(l_column_conf[column_id][0]), str(l_column_conf[column_id][1]))
    l_worksheet.set_row(0, None, l_header_format)
    # and write data to xls
    for result_i in l_data:
        # here write data
        for col_i in range(len(result_i)):
            l_worksheet.write(row_i, col_i, result_i[col_i])
        # here write formulas
        for l_line_i in range(len(l_column_conf)):
            l_worksheet.write_formula(row_i,
                                      int(l_column_conf[l_line_i][0]),
                                      l_column_conf[l_line_i][2].replace("_ROWID_", str(row_i + 1)))
        l_worksheet.set_row(row_i, None, l_integer_format)
        row_i = row_i + 1


# adding default chart to worksheet on all data function
def add_default_chart_to_xlsx(l_configuration, l_logger, l_config_line, l_workbook, l_worksheet,
                              l_title,
                              l_count_snap):
    """

    :param l_configuration: runtime configuration gathered from general.conf
    :param l_logger: runtime logger
    :param l_config_line: current report configuration line from REPORT_CONF
    :param l_workbook: current workbook
    :param l_worksheet: current worksheet
    :param l_title: columns titles
    :param l_count_snap: size of data going to chart
    :return:
    """
    l_id,\
    l_plugin,\
    l_source_file,\
    l_worksheet_title,\
    l_chart_title,\
    l_chart_conf_file,\
    l_columns_conf_file = parse_report_conf_line(l_configuration, l_logger, l_config_line, l_workbook, l_worksheet)

    # creating chart to worksheet
    l_chart = l_workbook.add_chart({'type': 'line'})

    # adding data to charts, column by column
    for d_i in range(2, len(l_title)):
        l_chart.add_series({
            'name': l_title[d_i],
            'categories': '=' + l_worksheet_title + '!$A$2:$A$' + str(l_count_snap + 1),
            'values': '=' + l_worksheet_title + '!' +
                      xl_rowcol_to_cell(1, d_i, row_abs=True, col_abs=True) +
                      ':' +
                      xl_rowcol_to_cell(l_count_snap, d_i, row_abs=True, col_abs=True),
            'line': {'width': 1, 'dash_type': 'solid'}
        })

    # chart title
    l_chart.set_title({
        'name': l_chart_title,
        'layout': {'x': 0.1, 'y': 0.04},
        'name_font': {
            'name': 'Arial',
            'color': 'black',
            'size': 9,
        }
    })

    # X-axis parameters
    l_chart.set_x_axis({
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
    l_chart.set_y_axis({
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
    l_chart.set_size({'width': 850, 'height': 476})
    # Printing chart on worksheet
    l_worksheet.insert_chart('B5', l_chart, {'x_scale': 1, 'y_scale': 1})


# adding custom charts to worksheet on selected data function
def add_custom_charts_to_xlsx(l_configuration, l_logger, l_config_line, l_workbook, l_worksheet,
                              l_count_snap):
    """

    :param l_configuration: runtime configuration gathered from general.conf
    :param l_logger: runtime logger
    :param l_config_line: current report configuration line from REPORT_CONF
    :param l_workbook: current workbook
    :param l_worksheet: current worksheet
    :param l_count_snap: size of data going to chart
    :return:
    """

    l_id,\
    l_plugin,\
    l_source_file,\
    l_worksheet_title,\
    l_chart_title,\
    l_chart_conf_file,\
    l_columns_conf_file = parse_report_conf_line(l_configuration, l_logger, l_config_line, l_workbook, l_worksheet)

    l_chart_conf = []
    l_current_chart_id = 0

    try:
        # open config file for custom charts
        l_logger.debug('Trying to open charts config file: ' + l_chart_conf_file)
        if sys.version_info.major >= 3:
            l_config_file = open(l_chart_conf_file, encoding="utf_8")
        if sys.version_info.major == 2:
            l_config_file = open(l_chart_conf_file)
    except OSError as err:
        l_logger.error("OS error: {0}".format(err))
        raise
    except Exception:
        l_logger.error("Unexpected error:", sys.exc_info()[0])
        raise

    # read config
    for l_line in l_config_file.readlines():
        if not l_line.startswith("\n") and not l_line.startswith("#"):
            l_text_string = l_line.replace("\r", "").replace("\n", "")
            l_chart_conf.append(l_text_string.split(":"))
    l_config_file.close()
    l_logger.debug('Successfully read chart config file ' + l_config_line[4])

    l_chart_conf = sorted(l_chart_conf, key=lambda x: int(x[0]), reverse=False)

    for chart_id in range(len(l_chart_conf)):
        if l_config_line[2] == "":
            l_chart_title = l_configuration["TITLE"] + " " + l_chart_conf[chart_id][2]
        else:
            l_chart_title = l_config_line[3] + " " + l_chart_conf[chart_id][2]
        # if this chart id is already exist
        if l_current_chart_id == int(l_chart_conf[chart_id][0]):
            # add column to chart
            if l_chart_type == 'line':
                l_chart.add_series({
                    'name': '=' + l_worksheet_title + '!' +
                            xl_rowcol_to_cell(0, int(l_chart_conf[chart_id][1]), row_abs=True, col_abs=True),
                    'categories': '=' + l_worksheet_title + '!$A$2:$A$' + str(l_count_snap + 1),
                    'values': '=' + l_worksheet_title + '!' +
                              xl_rowcol_to_cell(1, int(l_chart_conf[chart_id][1]), row_abs=True, col_abs=True) +
                              ':' +
                              xl_rowcol_to_cell(l_count_snap,
                                                int(l_chart_conf[chart_id][1]),
                                                row_abs=True, col_abs=True),
                    'line': {'width': 1, 'dash_type': 'solid'}
                })
            elif l_chart_type == 'scatter':
                l_chart.add_series({
                    'name': '=' + l_worksheet_title + '!' +
                            xl_rowcol_to_cell(0, int(l_chart_conf[chart_id][1]), row_abs=True, col_abs=True),
                    'categories': '=' + l_worksheet_title + '!' + scatter_column + ':$A$' + str(l_count_snap + 1),
                    'values': '=' + l_worksheet_title + '!' +
                              xl_rowcol_to_cell(1, int(l_chart_conf[chart_id][1]), row_abs=True, col_abs=True) +
                              ':' +
                              xl_rowcol_to_cell(l_count_snap,
                                                int(l_chart_conf[chart_id][1]),
                                                row_abs=True, col_abs=True),
                    'marker': {'type': 'circle', 'size': 3}
                    # 'line': {'width': 1, 'dash_type': 'solid'}
                })

        # if this chart id not exist
        else:
            # print chart to worksheet if it is time to it
            if l_current_chart_id != 0:
                l_chart.set_size({'width': 850, 'height': 300})
                l_worksheet.insert_chart('B' + str((l_current_chart_id - 1) * 15 + 3), l_chart,
                                         {'x_scale': 1, 'y_scale': 1})
                l_logger.debug('Added chart ' + str(l_current_chart_id))
            # creating new chart
            l_current_chart_id = int(l_chart_conf[chart_id][0])

            l_chart_type =  str(l_chart_conf[chart_id][3])
            l_logger.debug('Chart type is ' + l_chart_type)
            l_chart = l_workbook.add_chart({'type': l_chart_type})
            # l_chart = l_workbook.add_chart({'type': 'line'})

            # add column to chart
            if l_chart_type == 'line':
                l_chart.add_series({
                    'name': '=' + l_worksheet_title + '!' +
                            xl_rowcol_to_cell(0, int(l_chart_conf[chart_id][1]), row_abs=True, col_abs=True),
                    'categories': '=' + l_worksheet_title + '!$A$2:$A$' + str(l_count_snap + 1),
                    'values': '=' + l_worksheet_title + '!' +
                              xl_rowcol_to_cell(1, int(l_chart_conf[chart_id][1]), row_abs=True, col_abs=True) +
                              ':' +
                              xl_rowcol_to_cell(l_count_snap,
                                                int(l_chart_conf[chart_id][1]),
                                                row_abs=True, col_abs=True),
                    'line': {'width': 1, 'dash_type': 'solid'}
                })
            elif l_chart_type == 'scatter':
                scatter_column = xl_rowcol_to_cell(1, int(l_chart_conf[chart_id][1]), row_abs=True, col_abs=True)

            # main charts parameters
            l_chart.set_legend({
                'position': 'top',
                'font': {'name': 'Arial', 'size': 9},
                'layout': {
                    'x': 0.5,
                    'y': 0.04,
                    'width': 0.3,
                    'height': 0.1
                }
            })
            if sys.version_info.major >= 3:
                l_chart.set_title({
                    'name': l_chart_title,
                    'name_font': {
                        'name': 'Arial',
                        'color': 'black',
                        'size': 9
                    },
                    'overlay': ~True,
                    'layout': {
                        'x': 0.1,
                        'y': 0.1,
                    }
                })
            if sys.version_info.major == 2:
                l_chart.set_title({
                    'name': l_chart_title.decode('utf8'),
                    'name_font': {
                        'name': 'Arial',
                        'color': 'black',
                        'size': 9},
                    'overlay': ~True,
                    'layout': {
                        'x': 0.1,
                        'y': 0.1,
                    }
                })

            l_chart.set_x_axis({
                'date_axis': True,
                'name_font': {
                    'name': 'Arial',
                    'color': 'black',
                    'size': 9
                },
                'num_font': {
                    'name': 'Arial',
                    'color': 'black',
                    'size': 9,
                    'rotation': -90
                },
            })

            l_chart.set_y_axis({
                'num_format': '#,###',
                'num_font': {
                    'name': 'Arial',
                    'color': 'black',
                    'size': 9
                },
                'name_font': {
                    'name': 'Arial',
                    'color': 'black',
                    'size': 9,
                    'rotation': 0
                },
            })

    l_chart.set_size({'width': 850, 'height': 300})

    # print last chart to worksheet
    if l_chart_type == 'scatter':
        l_chart.set_style(11)
    l_worksheet.insert_chart('B' + str((l_current_chart_id - 1) * 15 + 3),
                             l_chart,
                             {'x_scale': 1, 'y_scale': 1})
    l_logger.debug('Added chart ' + str(l_current_chart_id))

    # set l_current_chart_id in zero for next worksheets with custom charts
    # l_current_chart_id = 0
