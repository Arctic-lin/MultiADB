#!/bin/sh

#adj：
#	Tokyo_GC:/ $ media volume --stream 0 --get
#	[v] will control stream=0 (STREAM_VOICE_CALL)
#	[v] will get volume
#	[v] Connecting to AudioService
#	[v] volume is 1 in range [1..7]

#function mute(){
	
#	i=0
#	while [ i -lt 11 ]
#	do
#		volume_name=$(media volume --stream $i --get | grep 'range' | grep -Eo '[0-9]+')
#		current_media=${volume_name:0:1}
#		min_media=${volume_name:1:2}
#		if (( $current_media != $min_media))
#		then
#			media volume --stream $i --set ${min_media}
#		fi
#		i=$(($i+1))
#	done
#}

function mute(){
	
	i=0
	while [ i -lt 10 ]
	do
		service call audio 10 i32 $i i32 0 i32 0
		i=$(($i+1))
	done
}
#---------------------执行体------------------

a=1
while (( $a>0 ))
do
  mute
	sleep 300
done

