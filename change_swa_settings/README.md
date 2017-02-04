Simple console application to change specific user settings in Scalix Web Access.
 

To be able run this script you would need Python 3. Tested with Python 3.4.xx and 3.5.xx. 
 

> For python 3.4.x you need to install typing module if it not installed
> ```sh
> pip3 install typing
> ```

## Usage ##

```sh
usage: change_swa_preferences.py [-h] --host HOST --username USERNAME
                                 --password PASSWORD --settings
                                 [SETTINGS [SETTINGS ...]] [--port PORT]
                                 [--use-ssl USE_SSL] [--debug DEBUG]

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           Imap server hostname or ip
  --username USERNAME   Username to login
  --password PASSWORD   User password
  --settings [SETTINGS [SETTINGS ...]]
                        Multiplier SWA preference option which need to change.
                        Usage for e.g. OPTION=VALUE OPTION2=VALUE
  --port PORT           Imap server port
  --use-ssl USE_SSL     Use ssl connection
  --debug DEBUG         Sets debug level for the imaplib module.
```

Let's imagine that we need to change locale and signature text command will be looks like this
```sh
[host ~]:./change_swa_preferences.py  --host IMAP_HOST --username USERNAME --password USER_PSWD --settings signatureText='Here goes user signature' locale="it_IT"
```
