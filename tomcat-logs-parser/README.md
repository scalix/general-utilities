Usage
******
```bash
[root@mail]# parse_tomcat_logs.py $(/opt/scalix-tomcat/bin/sxtomcat-get-inst-dir $(/opt/scalix-tomcat/bin/sxtomcat-get-mounted-instances))/logs
```

Result:
```plain
.
├── scalix-api.log
│   ├── CheckAuthInterceptor.log
│   ├── MapiFactory.log
│   └── SyncService.log
├── scalix-caa.log
│   ├── CAAConfigLoader.log
│   └── NotificationEventListener.log
├── scalix-swa-activity.log
│   └── PlatformRequest.log
├── scalix-swa.log
│   ├── Authenticate.log
│   └── HttpRequestHandler.log
├── scalix-swa-remote-client.log
│   └── RemoteLog.log
├── scalix-wireless-activity.log
│   └── SyncCommand.log
├── scalix-wireless-client-activity.log
│   └── Connection.log
└── scalix-wireless.log
    ├── HttpRequestHandler.log
    └── WirelessServlet.log
```