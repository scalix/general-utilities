#!/bin/bash

echo -e "Date\t\t\tTotal\tHttpd(CLOSE_WAIT)\tJava 8009(CLOSE_WAIT)\tJava 8080(CLOSE_WAIT)"

while :
do
    output=$(netstat -apn | grep ':80')
    total=$(echo -n "$output" | grep ':80' | wc -l)
    httpd_close_wait=$(echo -n "$output"| grep CLOSE | grep 'httpd\|apache2' | wc -l)
    java_close_wait=$(echo -n "$output" | grep CLOSE | grep 'java')
    java_close_wait_8009=$(echo -n "$java_close_wait" |grep 8009 | wc -l)
    java_close_wait_8080=$(echo -n "$java_close_wait" |grep 8080 | wc -l)
    echo -ne "$(date '+%F %R:%S')\t$total\t\t$httpd_close_wait\t\t\t$java_close_wait_8009\t\t\t$java_close_wait_8080\t\t"\\r
    sleep 1
done
 
