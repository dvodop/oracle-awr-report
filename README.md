oracle-awr-report.py is easy-to-use data exporter from different data sources (Oracle Database, ssh) to xlsx (Excel)

# Key features
* Export data from Oracle database to xlsx worksheet
* Export data by shell script to xlsx worksheet
* Charts drawing
* Customizing charts
* Adding computed columns

AWR SQL queries by [MaksimIvanovPerm](https://github.com/MaksimIvanovPerm)

# Prerequisite
* python3
* cx_Oracle
* xlswriter
* paramiko
* scp

# Usage

```
$ python oracle-awr-report.py 
```

## Main configuration **conf.d/general.conf**
_All config files openes with utf-8 encoding_

## Report configuration file
Format:
```
id:sql script:chart title:chart config file:columns config file
id:plugin:source file:worksheet title:chart title:charts config file:columns config file
```
where charts config file is one of following:
1. **none** - not print chart
2. **default** - use all data to print one chart only
3. **custom charts configuration file name**

where columns config file is one of following:
1. **default** - not use custom columns
2. **custom columns configuration file name**

Example:
```
1:oradb:oradb/RDBMSServiceTime.sql:RDBMSServiceTime:DB service time structure:default:default
2:oradb:oradb/WaitTimeStructure.sql:WaitTimeStructure:DB wait time structure:default:default
3:oradb:oradb/RedoStat.sql:RedoStat::conf.d/redostat.conf:default
4:ssh:ssh/atop_parser.sh --loglevel SILENT2 --swap:atop_swap:atopSWP:default:default
5:ssh:ssh/atop_parser.sh --loglevel SILENT2 --dsk sdc:atop_sdc::conf.d/atop_dsk_charts.conf:conf.d/atop_dsk_columns.conf
```

## Custom charts configuration file
Format:
```
# id:column number in char:column title:chart type

```

where chart type is one of following:
1. **line**
2. **scatter**

Example:
```
1:25:Redo writes per hour:line
1:27::
2:34:Redo write latency, ms:line
3:27:Redo write structure:line
3:33::
```

## Custom columns configuration file
Format:
```
column number:column title:formula
```

**\_ROWID\_** - is service variable for rowid substitution

Example:
```
11:db_file_sequential_read:=UserIOWaitsTime!W_ROWID_/10000
12:userio:=WaitTimeStructure!D_ROWID_/10000
13:rr-latency:=C_ROWID_/E_ROWID_
```

## Report worksheet example
![DB wait time structure](DOC/oracle-awr-report.png)

# Plugins

## ORADB
Plugin for gathering data from Oracle Database

## SSH
Plugin for gathering data by shell script via ssh.

Shell script must output one line with format:
```
File_with_data unixtimestamp column2_title column2_title columnt3_title...
```

Example:
```
/tmp/atop_parser_CPU_20190424_2018_24444.log unixtimestamp sys user irq idle wait
```

So, first column in data file must be unixtimestamp!

# ATOP
For gathering atop data from host prepared shell script **atop_parser.sh**. It work with atop log files /var/log/atop/atop_* created with interval=600 seconds

