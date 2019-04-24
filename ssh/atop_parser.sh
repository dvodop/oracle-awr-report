#!/usr/bin/env bash
# parser for atop daemon logs, running like this:
# 		/usr/bin/atop -a -w /var/log/atop/atop_20190417 600 

################################################################################################################################################
 #      Colored output variables
################################################################################################################################################
COLOR_NC='\e[0m' # No Color
COLOR_WHITE='\e[1;37m'
COLOR_BLACK='\e[0;30m'
COLOR_BLUE='\e[0;34m'
COLOR_LIGHT_BLUE='\e[1;34m'
COLOR_GREEN='\e[0;32m'
COLOR_LIGHT_GREEN='\e[1;32m'
COLOR_CYAN='\e[0;36m'
COLOR_LIGHT_CYAN='\e[1;36m'
COLOR_RED='\e[0;31m'
COLOR_LIGHT_RED='\e[1;31m'
COLOR_PURPLE='\e[0;35m'
COLOR_LIGHT_PURPLE='\e[1;35m'
COLOR_BROWN='\e[0;33m'
COLOR_YELLOW='\e[1;33m'
COLOR_GRAY='\e[0;30m'
COLOR_LIGHT_GRAY='\e[0;37m'

################################################################################################################################################
 #      Default variables
################################################################################################################################################
CURRENT_PID=$$
START_TIME=`date +%Y%m%d_%H%M`
LOG_LEVEL=30

DSK=0
CPU=0
SWAP=0
#PAG=0
RAM=0
declare -a DSK_NAMES
declare -a DSK_LOGS

################################################################################################################################################
 #	Output functions
################################################################################################################################################
echo_error() {
        LOG_LEVEL=$1
        shift
        if [ $LOG_LEVEL -le 40 ]
        then
                echo -e "  ERROR `date '+%y.%m.%d %H:%M:%S'`: ${COLOR_RED}$@${COLOR_NC}";
        fi
}
echo_warn()  {
        LOG_LEVEL=$1
        shift
        if [ $LOG_LEVEL -le 30 ]
        then
                echo -e "WARNING `date '+%y.%m.%d %H:%M:%S'`: ${COLOR_YELLOW}$@${COLOR_NC}";
        fi
}
echo_info()  {
        LOG_LEVEL=$1
        shift
        if [ $LOG_LEVEL -le 20 ]
        then
                echo -e "   INFO `date '+%y.%m.%d %H:%M:%S'`: ${COLOR_GREEN}$@${COLOR_NC}";
        fi
}
echo_debug() {
        LOG_LEVEL=$1
        shift
        if [ $LOG_LEVEL -le 10 ]
        then
                echo -e "  DEBUG `date '+%y.%m.%d %H:%M:%S'`: ${COLOR_CYAN}$@${COLOR_NC}";
        fi
}

echo_usage() {
        echo "Usage: `basename $0` [options]
                --help  -h                              show this help
		--loglevel	level			Logging level
								Default: WARNING
								Can be:
								 SILENT
								 ERROR
								 WARNING
								 INFO
								 DEBUG
		--dsk		block device name	Parse atop logs for block device
		--cpu					Parse atop logs for CPU
		--swap					Parse atop logs for swap
		--ram					Parse atop logs for RAM
	Note: supported RHEL6/OEL6;RHEL7/OEL7
"
#		--pag					Parse atop logs for PAG (paging frequency)
}

################################################################################################################################################
 #	Atop logs parsing functions
################################################################################################################################################
atop_parse_device() {
	local DEVICE=$1
	local ATOP_FILE=$2
	local TEMP_FILE=$3
	echo_debug $LOG_LEVEL "Processing ${ATOP_FILE} for ${DEVICE}"
	/usr/bin/atop -r $ATOP_FILE -P $DEVICE | awk '{if ( $6 == 600 ) print $0;}' | awk '{print $3" "$5}' | sort -u > $TEMP_FILE
}

################################################################################################################################################
 #	Parsing command line arguments
################################################################################################################################################
if [ $# -eq 0 ]
then
	echo_usage
	exit 1
fi

while [ "$1" != "" ]
do
	case "$1" in
		"-h"|"--help")
			echo_usage
			exit 0
		;;
		"--loglevel")
			case "$2" in
				"SILENT2")
					LOG_LEVEL=70
				;;
				"SILENT")
					LOG_LEVEL=60
				;;
				"ERROR")
					LOG_LEVEL=40
				;;
                                "WARNING")
                                        LOG_LEVEL=30
                                ;;
                                "INFO")
                                        LOG_LEVEL=20
                                ;;
                                "DEBUG")
                                        LOG_LEVEL=10
                                ;;
                                *)
                                        LOG_LEVEL=30
                                ;;
	                esac
                        shift 2
		;;		
		"--dsk")
			DSK=1
			DSK_NAMES+=("$2")
			DSK_LOGS+=("/tmp/atop_parser_DSK_$2_${START_TIME}_${CURRENT_PID}.log")
			LAST=${#DSK_NAMES[@]}
			LAST=$((LAST - 1 ))
#			echo "unixtime device read write avq avio" > ${DSK_LOGS[$LAST]}
			shift 2
		;;
		"--cpu")
			CPU=1
			CPU_LOG="/tmp/atop_parser_CPU_${START_TIME}_${CURRENT_PID}.log"
			shift
		;;
		"--swap")
			SWAP=1
			SWAP_LOG="/tmp/atop_parser_SWP_${START_TIME}_${CURRENT_PID}.log"
			shift
		;;
# there is no PAG on rhel6 with atop-1.26-1.el6.2.x86_64
#		"--pag")
#			PAG=1
#			PAG_LOG="/tmp/atop_parser_PAG_${START_TIME}_${CURRENT_PID}.log"
#			echo "unixtime" > $PAG_LOG
#			echo_warn $LOG_LEVEL "Log file for PAG is [$PAG_LOG]"
#			shift
#		;;
		"--ram")
			RAM=1
			RAM_LOG="/tmp/atop_parser_MEM_${START_TIME}_${CURRENT_PID}.log"
			shift
		;;
		*)
			echo_error $LOG_LEVEL "Unknown parameter [$1]"
			echo_usage
			exit 1
		;;
	esac
done


if [ $LOG_LEVEL -lt 70 ]
then
	if [ $DSK -eq 1 ]
	then
		for i in ${!DSK_NAMES[@]}
		do
			echo "unixtime read write avq avio" > ${DSK_LOGS[$LAST]}
			echo_warn $LOG_LEVEL "Log file for DSK $2 is [${DSK_LOGS[$LAST]}]"
		done
	fi
	if [ $CPU -eq 1 ]
	then
		echo "unixtime sys user irq idle wait" > $CPU_LOG
		echo_warn $LOG_LEVEL "Log file for CPU is [$CPU_LOG]"
	fi
	if [ $RAM -eq 1 ]
	then
		echo "unixtime free cache buff slab" > $RAM_LOG
		echo_warn $LOG_LEVEL "Log file for RAM is [$RAM_LOG]"
	fi
	if [ $SWAP -eq 1 ]
	then
		echo "unixtime total free vmcom vmlim" > $SWAP_LOG
		echo_warn $LOG_LEVEL "Log file for SWAP is [$SWAP_LOG]"
	fi
fi


################################################################################################################################################
 #	Parsing log files
################################################################################################################################################


for file in /var/log/atop/atop_*; do
	[ -e "$file" ] || continue
	echo_debug $LOG_LEVEL "parsing [$file]"
	if [ $DSK -eq 1 ]
	then
		DEVICE="DSK"
		TEMP_FILE="/tmp/atop_parser_${DEVICE}_${START_TIME}_${CURRENT_PID}.temp"
		atop_parse_device $DEVICE $file $TEMP_FILE
		for i in ${!DSK_NAMES[@]}
		do
			DEVICE_NAME=${DSK_NAMES[$i]}
			while read -r LINE
			do
				v_unixtime=`echo $LINE | awk '{print $1}'`
				v_time=`echo $LINE | awk '{print $2}'`
#				echo "q" | /usr/bin/atop -l -r $file -b $v_time -L 160 | head -n 20 | egrep "^DSK .*" | egrep "$DEVICE_NAME" | awk -F "|" '{print $2" "$4" "$5" "$10" "$11}' | awk -v ut=$v_unixtime '{print ut" "$1" "$3" "$5" "$7" "$9}' >> ${DSK_LOGS[$i]}
				echo "q" | /usr/bin/atop -l -r $file -b $v_time -L 160 | head -n 20 | egrep "^DSK .*" | egrep "$DEVICE_NAME" | awk -F "|" '{print $2" "$4" "$5" "$10" "$11}' | awk -v ut=$v_unixtime '{print ut" "$3" "$5" "$7" "$9}' >> ${DSK_LOGS[$i]}
			done < $TEMP_FILE
		done
		rm -f $TEMP_FILE
	fi

	if [ $CPU -eq 1 ]
	then
		DEVICE="CPU"
		TEMP_FILE="/tmp/atop_parser_${DEVICE}_${START_TIME}_${CURRENT_PID}.temp"
		atop_parse_device $DEVICE $file $TEMP_FILE
		while read -r LINE
		do
			v_unixtime=`echo $LINE | awk '{print $1}'`
			v_time=`echo $LINE | awk '{print $2}'`
			echo "q" | /usr/bin/atop -l -r $file -b $v_time -L 160 | head -n 20 | egrep "^CPU." | awk -F "|" -v ut=$v_unixtime ' { print ut" "$2" "$3" "$4" "$5" "$6 } ' | awk ' { print $1, $3, $5, $7, $9, $11 } ' | sed 's/%//g' >> $CPU_LOG
		done < $TEMP_FILE
		rm -f $TEMP_FILE
	fi

	if [ $SWAP -eq 1 ]
	then
		DEVICE="SWP"
		TEMP_FILE="/tmp/atop_parser_${DEVICE}_${START_TIME}_${CURRENT_PID}.temp"
		SWP_TEMP_LOG="${TEMP_FILE}.log"
		atop_parse_device $DEVICE $file $TEMP_FILE
		while read -r LINE
		do
			v_unixtime=`echo $LINE | awk '{print $1}'`
			v_time=`echo $LINE | awk '{print $2}'`
			# echo "q" | /usr/bin/atop -l -r $file -b $v_time -L 160 | head -n 20 | egrep "^SWP." |  awk -F "|" ' { print $2, $3, $10, $11 } ' | awk -v ut=$v_unixtime '{print ut, $2, $4, $6, $8 } ' | sed 's/G//g' >> $SWP_TEMP_LOG
			echo "q" | /usr/bin/atop -l -r $file -b $v_time -L 160 | head -n 20 | egrep "^SWP." |  awk -F "|" ' { print $2, $3, $10, $11 } ' | awk -v ut=$v_unixtime '{print ut, $2, $4, $6, $8 } ' >> $SWP_TEMP_LOG
		done < $TEMP_FILE
				awk ' {
if ( $2 ~ '/G/' ) {
    gsub("G","",$2)
    $2=$2*1024*1024/4
}
if ( $2 ~ '/M/' ) {
    gsub("M","",$2)
    $2=$2*1024/4
}
if ( $3 ~ '/G/' ) {
    gsub("G","",$3)
    $3=$3*1024*1024/4
}
if ( $3 ~ '/M/' ) {
    gsub("M","",$3)
    $3=$3*1024/4
}
if ( $4 ~ '/G/' ) {
    gsub("G","",$4)
    $4=$4*1024*1024/4
}
if ( $4 ~ '/M/' ) {
    gsub("M","",$4)
    $4=$4*1024/4
}
if ( $5 ~ '/G/' ) {
    gsub("G","",$5)
    $5=$5*1024*1024/4
}
if ( $5 ~ '/M/' ) {
    gsub("M","",$5)
    $5=$5*1024/4
}
printf "%s %8.1f %8.1f %8.1f %8.1f\n", $1, $2, $3, $4, $5 } ' $SWP_TEMP_LOG >> $SWAP_LOG
		rm -f $SWP_TEMP_LOG
		rm -f $TEMP_FILE
	fi

	if [ $RAM -eq 1 ]
	then
		DEVICE="MEM"
		TEMP_FILE="/tmp/atop_parser_${DEVICE}_${START_TIME}_${CURRENT_PID}.temp"
		RAM_TEMP_LOG="${TEMP_FILE}.log"
		atop_parse_device $DEVICE $file $TEMP_FILE
		while read -r LINE
		do
			v_unixtime=`echo $LINE | awk '{print $1}'`
			v_time=`echo $LINE | awk '{print $2}'`
			echo "q" | /usr/bin/atop -l -r $file -b $v_time -L 160 | head -n 20 | egrep "^MEM." | awk -v ut=$v_unixtime '{print ut, $7, $10, $16, $19 } ' >> $RAM_TEMP_LOG
		done < $TEMP_FILE
#$1=strftime("%Y-%m-%d-%H:%M", $1);
		awk ' {
if ( $2 ~ '/G/' ) {
    gsub("G","",$2)
    $2=$2*1024*1024/4
}
if ( $2 ~ '/M/' ) {
    gsub("M","",$2)
    $2=$2*1024/4
}
if ( $3 ~ '/G/' ) {
    gsub("G","",$3)
    $3=$3*1024*1024/4
}
if ( $3 ~ '/M/' ) {
    gsub("M","",$3)
    $3=$3*1024/4
}
if ( $4 ~ '/G/' ) {
    gsub("G","",$4)
    $4=$4*1024*1024/4
}
if ( $4 ~ '/M/' ) {
    gsub("M","",$4)
    $4=$4*1024/4
}
if ( $5 ~ '/G/' ) {
    gsub("G","",$5)
    $5=$5*1024*1024/4
}
if ( $5 ~ '/M/' ) {
    gsub("M","",$5)
    $5=$5*1024/4
}
printf "%s %8.1f %8.1f %8.1f %8.1f\n", $1, $2, $3, $4, $5 } ' $RAM_TEMP_LOG >> $RAM_LOG
		rm -f $RAM_TEMP_LOG
		rm -f $TEMP_FILE
	fi
done

if [ $LOG_LEVEL -eq 70 ]
then
	if [ $DSK -eq 1 ]
	then
		for i in ${!DSK_NAMES[@]}
		do
			echo "${DSK_LOGS[$LAST]} unixtime read write avq avio"
		done
	fi
	if [ $CPU -eq 1 ]
	then
		echo "$CPU_LOG unixtime sys user irq idle wait"
	fi
	if [ $RAM -eq 1 ]
	then
		echo "$RAM_LOG unixtime free cache buff slab"
	fi
	if [ $SWAP -eq 1 ]
	then
		echo "$SWAP_LOG unixtime total free vmcom vmlim"
	fi
fi

exit 0

