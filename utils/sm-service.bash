#!/bin/bash

while [[ $# -gt 0 ]]
do
	case $1 in
		-e|--env)
			VENV=${2}
			shift
			shift
			;;
		-d|--dir)
			WORKING_DIR=${2}
			shift
			shift
			;;
		-c|--conf)
			CONFIG=${2}
			shift
			shift
			;;
		*)
			shift
			;;
	esac
done

if [[ -z "$VENV" ]] || [[ -z "$WORKING_DIR" ]] || [[ -z "$CONFIG" ]]
then
	echo "usage: $0 --env ENV --dir EXEC_DIR --config CONFIG_FILE"
	exit -1
fi

echo ". $VENV/bin/activate"
. $VENV/bin/activate
CMD="python $WORKING_DIR/sensorkit-monitor.py --config-file $CONFIG"
echo $CMD
exec $CMD
