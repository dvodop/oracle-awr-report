For create own plugin it must meet several conditions:
1. module file name is: **plugin_PLUGINNAME.py*
2. contain main function with name 
```
PLUGINNAME_gather_data
```

with parameters
```
(l_configuration, l_logger, l_config_line, l_workbook, l_worksheet)
```
where
* param l_configuration: runtime configuration gathered from general.conf
* param l_logger: runtime logger
* param l_config_line: current report configuration line from REPORT_CONF
* param l_workbook: current workbook
* param l_worksheet: current worksheet

3. return l_title, l_data
where
l_title - is list of columns titles
l_data - is list of lists of data

So, started plugin source is:
```
from plugins.plugin_report_conf import *

def PLUGINNAME_gather_data(l_configuration, l_logger, l_config_line, l_workbook, l_worksheet):
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


    return l_title, l_data
```
