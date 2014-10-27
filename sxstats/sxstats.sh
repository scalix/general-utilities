#!/bin/bash
#
# Copyright 2014 Scalix, Inc. (www.scalix.com)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 2 of the GNU General Public
# License as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Street #330, Boston, MA 02111-1307, USA.
#

REPORT_FOLDER="$(pwd)/sxstats_$(date +%Y_%m_%d_%H_%M)"
RPM_BASED=true

if [[ $(cat /etc/*-release) == *debian* ]]
then
    RPM_BASED=false
fi

[ -d "$REPORT_FOLDER" ] &&  rm -rf "$REPORT_FOLDER"

mkdir -p "$REPORT_FOLDER"

function get_system_info() {
    echo "Gather system information"

    local lsb=$(type -P lsb_release)
    local sysinfo_file="$REPORT_FOLDER/system.info"
    echo "Writing to the file $sysinfo_file"

    if [ $lsb ]; then
        $lsb -a >> $sysinfo_file
    else
        echo "Release" >>$sysinfo_file
        cat /etc/*-release >> $sysinfo_file
        cat /etc/issue >> $sysinfo_file
        uname -a >> $sysinfo_file
    fi
    echo "" >> $sysinfo_file
    echo "Checking Selinux" >> $sysinfo_file
    local selinuxenabled=$(type -P sestatus)
    if [ $selinuxenabled ]; then
        local output=$($selinuxenabled)
        echo $output >> $sysinfo_file
        if [[ $output == *enabled* ]]
        then
            echo "Warinig Selinux is enabled!!"
        fi
    else
        echo "Selinux not installed" >> $sysinfo_file
    fi

    echo
    echo "Check Java version"
    local javac=$(type -P java)
    if [ ! "$javac" ]; then
        echo "Could not determine java"
        echo "Could not determine java" >> $sysinfo_file
    else
        local java_version=$($javac -version 2>&1)
        echo "" >> $sysinfo_file
        echo "$java_version" >> $sysinfo_file
    fi

}

function get_installed_scalix_packages() {
    echo
    echo "Determine what scalix packages are installed"
    local pkgs_file="$REPORT_FOLDER/packages.info"
    echo "Writing to the file $pkgs_file"

    if test $RPM_BASED
    then
        local rpms=$($(type -P rpm) -qa | grep scalix | grep -v grep)
        for rpm in $rpms
        do
            local str="processing $rpm"
            echo $str
            echo $str >> $pkgs_file
            $(type -P rpm) -q $rpm --qf "\tName:%{NAME}\n\tVersion:%{VERSION}-%{RELEASE}\n\tSize:%{SIZE}\n\tArchitecture:%{ARCH}\n\tOS:%{OS}\n\tRelease:%{RELEASE}\n\tDistribution:%{DISTRIBUTION}\n" >> $pkgs_file
        done
    fi
}

function gather_java_errors() {
    local logs_dir="$REPORT_FOLDER/$1_web_app_logs"
    echo "Filtered logs will be at folder $logs_dir"
    mkdir -p $logs_dir
    for app_log in $(ls -d -1 $2/logs/*.log)
    do
        local filename=$(basename $app_log)
        echo "parsing $filename"
        grep -A 5 -B 5 "WARN\|ERROR\|FATAL\|Exception\|at.*\.java\:.*" $app_log >> "$logs_dir/$filename"
        #if file is empty lets remove it
        [ ! -s "$logs_dir/$filename" ] && rm -f "$logs_dir/$filename"
    done
}

get_system_info
get_installed_scalix_packages

if [ -d "/opt/scalix-tomcat/bin" ]; then
    echo
    for instance in $(/opt/scalix-tomcat/bin/sxtomcat-get-mounted-instances)
    do
        instance_dir=$(/opt/scalix-tomcat/bin/sxtomcat-get-inst-dir $instance)
        echo "Found instance $instance. Instance folder $instance_dir"
        gather_java_errors $instance $instance_dir
    done
fi
