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
* logging
* coloredlogs

# Usage

```
$ python3 oracle-awr-report.py 
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

***Note:** atop device name (in atop lvm statistic) has 12 chars length, so in long lvm names you should use, as parameter of lvm name for atop_parser.sh, tail of logical volume name*

# Run it in cygwin:
1. Install the followng cygwin-packages: `gcc python38 python38-devel python38-paramiko`
2. To host-OS install `oracle instant client`, you can use the [follwing article](https://www.ibm.com/docs/en/opw/8.2.0?topic=client-installing-oracle-instant-windows) as a guide; Let's consider, here and after, that `oracle instant client` software was installed into the path, which are seen from cygwin as `/cygdrive/c/oracle_instant_client/instantclient_19_11`
3. In cygwin set (and write setting into your `.bashrc`) oracle-related env-variables:
```bash
export ORACLE_HOME=/cygdrive/c/oracle_instant_client/instantclient_19_11
export LD_LIBRARY_PATH=$ORACLE_HOME
export PATH=$PATH:$ORACLE_HOME
export TNS_ADMIN=$ORACLE_HOME/network/admin
```
4. In cygwin do:
```bash
mkdir $ORACLE_HOME/bin
cp -v $ORACLE_HOME/sqlplus.exe $ORACLE_HOME/bin
```
5. In cygwin do:
```bash
python -m pip install cx_Oracle --upgrade
python -m pip install colored-logs
python -m pip install xlsxwriter
python -m pip install coloredlogs
python -m pip install scp
```
6. In cygwin, check that your python-shell launces and it loads modules successfully:
```bash
python << __EOF__
import cx_Oracle
import coloredlogs
import xlsxwriter
import scp
import paramiko
__EOF__
```
7. Now cygwin should be able to run this python-project (I mean: `oracle-awr-report`); 

