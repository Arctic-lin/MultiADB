#!/bin/sh

function mute(){
	i=1
	while [ i -lt 10 ]
	do
		media volume --stream $i --set 0
		sleep 0.5
		i=$(($i+1))
	done
}

a=1
while (( $a>0 ))
do
    mute
	sleep 300
done
