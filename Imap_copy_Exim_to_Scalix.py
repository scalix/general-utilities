#!/usr/bin/python
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

from __future__ import print_function #2.6
#import os
import imaplib


SOURCE_MAILSERVER_TYPE = "Exim"
DESTINATION_MAILSERVER_TYPE = "Scalix"
LOG_LEVEL = 2
SECTION_SPLITTER = "-"*20
#EXIM_DEFAULT_FOLDERS = ['\"INBOX\"', '\"INBOX.Sent\"',
# '\"INBOX.Trash\"', '\"INBOX.Drafts\"', '\"INBOX.Junk\"']# Exim default folders
#SCALIX_DEFAULT_FOLDERS = ['INBOX'  , '\"Sent Items\"', '\"Deleted Items\"',# 'Drafts' ,'Calendar',
# 'Contacts', 'Notes', 'Tasks', '\"Public Folders\"', '\"Other Users\"']    # Scalix default folders

class Imap4Connect:
    """ class used to for connect to  IMAP server
    """
    def __init__(self):
        print (SECTION_SPLITTER + "START" + SECTION_SPLITTER + '\n')

    @staticmethod
    def imap4_connect(server, port, login, passwd, ssl):
        """ if ssl is true - use secure connection to server

        """
        if LOG_LEVEL >= 1:
            print ("Try connect to  "+ server + ":" + str(port) + "\n")
        if ssl:
            conn = imaplib.IMAP4_SSL(server, port)
        else:
            conn = imaplib.IMAP4(server, port)
        connt_result, _ = conn.login(login, passwd)
        if LOG_LEVEL >= 1:
            print (connt_result)
        return conn

    @staticmethod
    def imap4_disconnect(connectoin):
        """Imap server disconnect
        """
        connectoin.shutdown()
#___________________________________________________________________

class Imap4FolderList:
    """ class used to for got folder list from  IMAP server
    """
    def __init__(self):
        self.log = True
        self.exim_splitter = " \".\" " # Exim folderlist SPLITTER
        self.scalix_splitter = "\"/\" "  # Scalix folderlist SPLITTER
        self.default_copy = {'\"INBOX\"':'INBOX', '\"INBOX.Sent\"':'\"Sent Items\"',
                             '\"INBOX.Trash\"':'\"Deleted Items\"', '\"INBOX.Drafts\"':'Drafts'}

    def get_folders(self, conn, server_type):
        """Get all folders from server and sort array by len
        """
        server_folders_lists = []

        _, _folders = conn.list()

        splitter = {
                  'Exim': self.exim_splitter,
                  'Scalix':self.scalix_splitter,
                   }[server_type]

        for folder in _folders:
            # get only folder name
            server_folders_lists.append(folder.decode("utf-8").split(splitter)[1])
        # sort array by element len
        server_folders_lists.sort(key=lambda s: len(s))

        return server_folders_lists


    def get_result_folders(self, source_server_folders):
        """Get folders name from source server and change folder name for new server
        """
        destination_folders = []
        for _folder in source_server_folders:
            if _folder in self.default_copy:
                destination_folders.append(self.default_copy[_folder])
            else:
                #On Exim folder list	folder with subfolder displayed as: "INBOX.folder.subfolder.subsubfolder...."
                #we must delete "INBOX" and got "folder/subfolder/subsubfolder..." like in Scalix
                destination_folders.append('\"' + _folder.replace(".", "/")[7:])
        return destination_folders

    def get_result_folder(self, source_server_folder):
        """Get folder name from source server and change folder name for new server
        """
        if source_server_folder in self.default_copy:
            return self.default_copy[source_server_folder]
        else:
            #On Exim folder list	folder with subfolder displayed as: "INBOX.folder.subfolder.subsubfolder...."
            #we must delete "INBOX" and got "folder/subfolder/subsubfolder..." like in Scalix
            return '\"' +  source_server_folder.replace(".", "/")[7:]


class Imap4Copy:
    """ Object used to for IMAP to IMAP folders and files copy
    attributes of messages are copied  too
    """

    def __init__(self):
        print (SECTION_SPLITTER + "COPY MESSAGES" + SECTION_SPLITTER + '\n')

    @staticmethod
    def imap4_append_messages(source_server, destination_server):
        """copy (Append ) messages from EXIM mail server server to Scalix
        """
        copy_status_ok = 0
        totalmessages = 0

        folders = Imap4FolderList()
        #scalix_folders = folderlist.get_folders(destination_server,DESTINATION_MAILSERVER_TYPE) #scalix
        exim_folders = folders.get_folders(source_server, SOURCE_MAILSERVER_TYPE) #exim

        #create folders on Scalix server
        for folder in folders.get_result_folders(exim_folders):
            result_select, _ = destination_server.select(folder)

            #folder do not exist
            if not result_select.count('OK'):
                result_create = destination_server.create(folder + "/")
                if LOG_LEVEL >= 2:
                    print("Create folder" + folder)
                    print(result_create)

        for folder in exim_folders:
            print (SECTION_SPLITTER + "OPEN " + folder + " " +SECTION_SPLITTER + '\n')

            result_select, _ = source_server.select(folder)
            if not result_select.count('OK'): #folder do not exist
                print ("Folder " + folder + " do not exist on server")
                return -1

            if LOG_LEVEL >= 2:
                print("Select folder : " + folder + "\n")

            # search and return uids of all messages.
            # In this place we can use filter : DELETED SEEN  "SINCE \"8-Aug-2006\" ...
            result_select, select_data = source_server.search(None, "ALL")

            #if no messages or incorrect filter
            if not result_select.count('OK'):
                print("In folder " + folder + " is no messages")
                return -1

            messages_uuids = len(select_data[0].split())
            totalmessages += messages_uuids

            if LOG_LEVEL >= 3:
                print(SECTION_SPLITTER + "Messages UIDs sections" +SECTION_SPLITTER + '\n')
                print(select_data)
                print(SECTION_SPLITTER  + SECTION_SPLITTER + '\n')

            result_folder = folders.get_result_folder(folder)
            if LOG_LEVEL >= 2:
                print("Target folder : " + result_folder + "\n")
                print(SECTION_SPLITTER + "Copy messages  sections" +SECTION_SPLITTER + '\n')

            for data in select_data[0].split():
                #typ, Flags = self.SS_conn.fetch(data, 'FLAGS') # get messages FLAGS: UNSEEN , DELETED, Junk = EXIM.SPAM, NonJunk, SEEN, $forwarded --??
                _, message = source_server.fetch(data, '(RFC822 FLAGS)') # message[0][1] --letter ; message[1] - FLAGS

                print('\n' + SECTION_SPLITTER + SECTION_SPLITTER)

                if LOG_LEVEL >= 2:
                    print("Copy message :" + data)

                if LOG_LEVEL >= 3:
                    print("Message flags:")
                    print(message[1])

                #if FLAGS = \Deleted --> copy to  "\"Deleted Items\"
                #if FLAGS = \Seen --> set FLAG \Seen
                #if FLAGS = \Unseen --> FLAGS += None
                #if message have attachment files --> FLAGS += \\X-Has-Attach
                message_flags = '('
                if message[1].count('\Seen'):
                    message_flags += '\Seen'
                message_flags += ')'

                #On Exim all deleted files placed in INBOX, but it visible only on folder "Deleted"
                #for deleted messages we have to change destination folder
                new_folder = result_folder
                if message[1].count("\Deleted"):
                    new_folder = "\"Deleted Items\""

                status = destination_server.append(new_folder, message_flags, None, message[0][1])
                if status[0] == "OK":
                    copy_status_ok += 1

                if LOG_LEVEL >= 3:
                    print ("Old target folder: " + folder)
                    print("New target folder: " + new_folder)

                if LOG_LEVEL >= 2:
                    print("Copy status: ")
                    print(status)

        print("\n\n" + SECTION_SPLITTER + "Results" + SECTION_SPLITTER + '\n')
        print("Total messages:" + str(totalmessages) + "\n")
        print("Copy OK:" + str(copy_status_ok))
        print("Errors:" + str(totalmessages - copy_status_ok))


if __name__ == '__main__':


    Imap_Connect = Imap4Connect()
    _source_server = Imap_Connect.imap4_connect("source_server", 993, "login", "password", True)
    _destination_server = Imap_Connect.imap4_connect("destination_server", 143, "login", "password", False)

    imap_copy = Imap4Copy()
    imap_copy.imap4_append_messages(_source_server, _destination_server)

    Imap_Connect.imap4_disconnect(_source_server)
    Imap_Connect.imap4_disconnect(_destination_server)
