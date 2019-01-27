```shell
[root@mail test_py]# python ./sxstats.py 
Linux Distribution: CentOS 6.10 Final
Platform: Linux-2.6.32-754.9.1.el6.x86_64-x86_64-with-centos-6.10-Final
Architecture: 64bit ELF
Machine: x86_64
Node: mail.xxxx.com
System: Linux
Release: 2.6.32-754.9.1.el6.x86_64
Version: #1 SMP Thu Dec 6 08:02:15 UTC 2018
FQDN: mail.scalix.com
Jre Version: java version "1.8.0_191"
Java(TM) SE Runtime Environment (build 1.8.0_191-b12)
Java HotSpot(TM) Server VM (build 25.191-b12, mixed mode)

Packages installed: scalix-res-12.8.0.25754-1.noarch
scalix-server-12.8.0.15039-1.rhel6.x86_64
scalix-sis-12.8.0.26774-1.noarch
scalix-swa-12.8.0.28855-0.noarch
scalix-text-extractors-1.0-2.rhel6.i686
scalix-mobile-12.1.0.14474-1.noarch
scalix-iconv-extras-1.2-7.rhel6.i686
scalix-postgres-12.8.0-15983.noarch
scalix-tomcat-9.0.14-56.noarch
scalix-tomcat-connector-12.6.0-14721.rhel6.noarch
scalix-platform-12.8.0.28866-0.noarch
scalix-sac-12.8.0.25754-1.noarch
scalix-wireless-12.8.0.29044-1.noarch
scalix-spamassassin-0.0.12-1.noarch
scalix-libical-0.44.976-2.rhel6.i686
scalix-chardet-1.0.20071031-2.rhel6.i686
```

 ```shell
 [root@web ~]# ./sxstats.sh 
Gather system information
Writing to the file /root/sxstats_2016_04_18_12_26/system.info

Check Java version

Determine what scalix packages are installed
Writing to the file /root/sxstats_2016_04_18_12_26/packages.info
processing scalix-tomcat-7.0.68-41.noarch
processing scalix-wireless-12.6.0.14972-1.noarch
processing scalix-sis-12.6.0.16042-1.noarch
processing scalix-postgres-12.5.2-15963.noarch
processing scalix-platform-12.6.0.15073-1.noarch
processing scalix-swa-12.6.0.16352-1.noarch
processing scalix-tomcat-connector-12.5.2-14721.rhel7.noarch

Found instance web. Instance folder /var/opt/scalix/wb/tomcat
Filtered logs will be at folder /root/sxstats_2016_04_18_12_26/web_web_app_logs
parsing catalina.2016-04-12.log
parsing catalina.2016-04-13.log
parsing catalina.2016-04-14.log
parsing catalina.2016-04-15.log
parsing catalina.2016-04-16.log
parsing catalina.2016-04-17.log
parsing catalina.2016-04-18.log
parsing host-manager.2016-04-12.log
parsing host-manager.2016-04-13.log
parsing host-manager.2016-04-14.log
parsing host-manager.2016-04-15.log
parsing host-manager.2016-04-16.log
parsing host-manager.2016-04-17.log
parsing host-manager.2016-04-18.log
parsing localhost.2016-04-12.log
parsing localhost.2016-04-13.log
parsing localhost.2016-04-14.log                                                                                                                                            
parsing localhost.2016-04-15.log                                                                                                                                            
parsing localhost.2016-04-16.log                                                                                                                                            
parsing localhost.2016-04-17.log                                                                                                                                            
parsing localhost.2016-04-18.log
parsing manager.2016-04-12.log
parsing manager.2016-04-13.log
parsing manager.2016-04-14.log
parsing manager.2016-04-15.log
parsing manager.2016-04-16.log
parsing manager.2016-04-17.log
parsing manager.2016-04-18.log
parsing scalix-api-activity.log
parsing scalix-api-hibernate.log
parsing scalix-api.log
parsing scalix-sis-indexer.log
parsing scalix-sis-search.log
parsing scalix-swa-activity.log
parsing scalix-swa.log
parsing scalix-swa-remote-client.log
parsing scalix-wireless-activity.log
parsing scalix-wireless.log
[root@web ~]# 

 ```
