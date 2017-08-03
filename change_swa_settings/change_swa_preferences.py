#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Simple script which will change config option for Scalix Web access
application

"""

import argparse
import imaplib
import operator
import re
import time
import warnings
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from email.base64mime import body_decode
from email.errors import InvalidBase64CharactersDefect
from typing import AnyStr, Generator, List, Union, Set, Tuple, Any
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, ParseError

import collections

PREFERENCE_TEMPLATE = """<?xml version="1.0"?>
<preferences>
    <preference name="hideEmailAddresses">false</preference>
    <preference name="dateSeparatorChar">/</preference>
    <preference name="signatureActiveForForwards">true</preference>
    <preference name="newMailSound"/>
    <preference name="autoLoginActive">false</preference>
    <preference name="freeBusyPublishInterval">5</preference>
    <preference name="dirSearchOrder">system,personal</preference>
    <preference name="calendarsPaneVisible">true</preference>
    <preference name="locale">en_US</preference>
    <preference name="messagePaneVisible">true</preference>
    <preference name="defaultCalendarView">0</preference>
    <preference name="todoPaneVisible">false</preference>
    <preference name="from">sxadmin-test@allwebsuite.com</preference>
    <preference name="timeSeparatorChar">:</preference>
    <preference name="msgCompositionFontFamily">times new roman, new york, times, serif</preference>
    <preference name="signatureText"></preference>
    <preference name="includeMessageOnReply">true</preference>
    <preference name="useRichText">true</preference>
    <preference name="preferredDateTimeFormat">1</preference>
    <preference name="weekStart">0</preference>
    <preference name="miniCalendarPaneVisible">true</preference>
    <preference name="msgCompositionFontSize">3</preference>
    <preference name="signatureActiveForReplies">true</preference>
    <preference name="workDayEnd">1020</preference>
    <preference name="upcomingAppointmentsRange">7</preference>
    <preference name="timeWindowSize">ONE_MONTH</preference>
    <preference name="workWeek">1,2,3,4,5</preference>
    <preference name="workDayStart">480</preference>
    <preference name="foldersPaneVisible">true</preference>
    <preference name="modePaneVisible">true</preference>
    <preference name="refreshFolderList"/>
    <preference name="themesSelectedThemeId">scalix-default</preference>
    <preference name="freeBusyPublishRange">2</preference>
    <preference name="autoAcknowledgeReadReceipts">true</preference>
    <preference name="calendarSetsPaneVisible">false</preference>
    <preference name="showBcc">false</preference>
    <preference name="autoSpellCheck">false</preference>
    <preference name="blockRemoteImages">true</preference>
    <preference name="signatureActiveForNewMessages">true</preference>
    <preference name="eventsPaneVisible">true</preference>
</preferences>
"""


class PreferenceEmail(object):
    """Generic class for preference email

    """

    REPLACE_INVALID_XML = False

    def __init__(self, uid: int, message: EmailMessage):
        self.__uid = uid
        self.__message = message
        self.__preferences = None

    @property
    def uid(self) -> int:
        """Message UID.

        :return: int
        """
        return self.__uid

    @property
    def message(self) -> EmailMessage:
        """Imap rfc822 message class

        :return: EmailMessage
        """
        return self.__message

    @property
    def preferences(self) -> Element:
        """Get preference xml obj

        :return: xml root Element
        """
        if not self.__preferences:
            try:
                self.__preferences = self.__parse_preferences()
            except ParseError as parserError:
                warnings.warn(parserError, RuntimeWarning)
                if PreferenceEmail.REPLACE_INVALID_XML:
                    self.__preferences = ElementTree.fromstring(
                        PREFERENCE_TEMPLATE
                    )
                else:
                    raise SystemError('Unfortunately we could not parse xml '
                                      'data in this email. You may re-run your'
                                      ' script with \'--debug 15\' for '
                                      'debugging purpose or add '
                                      '\'--replace-invalid-xml true\' to use'
                                      ' SWA preference xml template instead of '
                                      'invalid xml in this email.')
        return self.__preferences

    def __parse_preferences(self) -> Element:
        """Parsers body content into xml object

        :return: Element
        """
        try:
            return ElementTree.fromstring(self.__message.get_content())
        except InvalidBase64CharactersDefect as _:
            return self.__parse_linear_base64()

    def __parse_linear_base64(self) -> Element:
        """Original parser will fail in case such email
        ```
        Content-Type: text/plain\r\n
        Content-Transfer-Encoding: base64\r\n\r\n
        PHByZW...==\r\n
        ...
        ...==\r\n
        ```
        as a workaround getting raw body and split by '\n' and parse xml
        as string list
        :return: Element
        """
        def decode_payload(data: Any) -> Generator:
            """

            :return: generator
            """
            if isinstance(data, (str, bytes)):
                data = data.splitlines()
            for line in filter(None, data):
                if line[-2:] in ['==', b'=='] or line[-1] in ['+', b'+']:
                    yield body_decode(line)
                else:
                    yield line

        return ElementTree.fromstringlist(
            decode_payload(self.__message.get_payload())
        )

    @staticmethod
    def from_bytes(uid: int, data: bytes):
        """Constructs PreferenceEmail object from raw email data

        :param uid: int
        :param data: bytes
        :return: PreferenceEmail
        """
        return PreferenceEmail(
            uid,
            BytesParser(policy=policy.strict).parsebytes(data)
        )

    def as_bytes(self) -> bytes:
        """Get RFC822 email message bytes

        :return: bytes
        """
        # maybe something was changed so just reload
        self.__message.set_content(
            ElementTree.tostring(self.preferences),
            'text',
            'plain'
        )
        return self.__message.as_bytes()


def create_imap_connection(conn_data: argparse.Namespace) -> imaplib.IMAP4:
    """Creates new connection to the imap server and authorize user

    :param conn_data: argparse.Namespace
    :return: imaplib.IMAP4
    """
    imap_cls = imaplib.IMAP4
    port = conn_data.port
    if conn_data.use_ssl:
        imap_cls = imaplib.IMAP4_SSL
        if port == imaplib.IMAP4_PORT:
            port = imaplib.IMAP4_SSL_PORT
    conn = imap_cls(conn_data.host, port)
    status, data = conn.login(conn_data.username, conn_data.password)
    if status != 'OK':
        raise Exception('Could not connect to the imap server. '
                        'Error message {}'.format(data))

    return conn


def is_iterable(item) -> bool:
    """Checks if variable is sequence excluding string and bytes

    :param item:
    :return: boolean
    """
    return isinstance(item, collections.Iterable) and not \
        isinstance(item, (bytes, str))


def linear_list(data: List[Any]) -> Generator[bytes, bytes, bytes]:
    """Join multidimensional list (imaplib response) into linear list

    :param data:
    :return: generator
    """
    for item in iter(data):
        if is_iterable(item):
            yield from linear_list(item)
        else:
            yield item


def build_imap_response_line(lines: List[Any]) -> Tuple[bytes, List[bytes]]:
    """Build line from imaplib library fetch response in more usable format.
    This function will return for e.g. '1 (UID 444 RFC822 {6868})', ['0.6868']

    :param lines: iterable
    :return: Tuple[bytes, List[bytes]]
    """
    lines = iter(lines)
    for line in lines:
        result = []
        literals = []
        while True:
            if is_iterable(line):
                line, literal = line
                literals.append(literal)
            result.append(line)
            if line[-1] == operator.itemgetter(0)(b')'):
                break
            line = lines.__next__()
        yield b''.join(result), literals


def fetch_from_imap(conn: imaplib.IMAP4, *args, cmd='fetch', **kwargs) -> \
        Tuple[bytes, List[bytes]]:
    """Function which will call imaplib function but it always will check status
    of the executed command and will raise Exception if IMAP command failed

    :param conn: imaplib.IMAP4 object
    :param args:
    :param cmd: string
    :param kwargs:
    :return: Tuple[bytes, List[bytes]]
    """
    # first lets execute CHECK IMAP command. It will flush any pending
    # operation in session
    conn.check()
    status, data = getattr(conn, cmd)(*args, **kwargs)
    if status != 'OK':
        raise Exception('Failed to execute fetch command: {}'.format(data))
    return build_imap_response_line(data)


def fetch_message_rfc822(conn: imaplib.IMAP4, uid: AnyStr) -> PreferenceEmail:
    """Fetches email

    :param conn: imaplib.IMAP4
    :param uid: UID
    :return: PreferenceEmail
    """
    #  bellow we are calling conn.uid('fetch', uid, (RFC822))
    #  see IMAP4.uid or IMAP.fetch function docstring  for details
    fetch_args = [conn, 'fetch', uid, '(RFC822)']
    warn_msg = 'Message RFC822 was not fetched using UID {}'.format(uid)
    for line, literals in fetch_from_imap(*fetch_args, cmd='uid'):
        match = re.search(rb'RFC822\s+\{(\d+)\}', line)
        if match:
            msg_size = int(match.group(1))
            for literal in literals:
                if len(literal) == msg_size:
                    return PreferenceEmail.from_bytes(int(uid), literals[0])
            else:
                warnings.warn(
                    'Unable to find message body. Maybe message body was not '
                    'fully transferred. Fetch response line {},  literals {}'
                    '.'.format(line, literals),
                    RuntimeWarning
                )
        else:
            warnings.warn(
                'Imap fetch line does not contain RFC822 atom in response. '
                'Fetch response line {}, literals {}.'.format(line, literals),
                RuntimeWarning
            )
    else:
        warnings.warn(warn_msg, RuntimeWarning)


def find_swa_preference_email(conn: imaplib.IMAP4) -> \
        Tuple[Union[PreferenceEmail, None], Set[int]]:
    """Searches for preference messages. It will grab first email and the rest
    emails preferences if they exists will be ignored - its the same behaviour
    as SWA has.

    :param conn: imaplib.IMAP4
    :return: tuple first is PreferenceEmail what we found found , second
        value - set of orphan email preferences uids

    """
    email = None
    orphan_preference_emails = set()
    for line, _ in fetch_from_imap(conn, '1:*', '(UID ENVELOPE FLAGS)'):
        if b'[prefs(v2.1) data]' in line and b'\\Deleted' not in line:
            match = re.search(rb'UID\s(\d+)', line)
            if not match:
                continue
            if not email:
                email = fetch_message_rfc822(conn, match.group(1))
            else:
                orphan_preference_emails.add(int(match.group(1)))
    return email, orphan_preference_emails


def find_option_and_change(document: ElementTree, name: AnyStr, value: AnyStr):
    """Finds option in xml document and sets value

    :param document: ElementTree object
    :param name: swa option name
    :param value: value for option
    :return:
    """
    xpath = './/preference[@name="{tag_name}"]'.format(tag_name=name)
    for elem in document.findall(xpath):
        elem.text = value
        break
    else:
        warnings.warn(
            'SWA option {name} is not found in SWA preference document. This'
            ' option wont be added to the document with value '
            '"{value}".'.format(name=name, value=value),
            RuntimeWarning
        )


def create_preference_message() -> PreferenceEmail:
    """Creates new email with a swa preferences from a template

    :return: PreferenceEmail
    """
    msg = EmailMessage()
    msg['X-Oddpost-Class'] = 'prefs'
    msg['Subject'] = '[prefs(v2.1) data]'
    msg['From'] = 'swa@scalix.com'
    msg.set_charset('utf-8')
    msg.set_content(PREFERENCE_TEMPLATE)
    return PreferenceEmail(0, msg)


def change_swa_settings(conn: imaplib.IMAP4, swa_options: dict):
    """Changes swa preference email or create a new one if message with
    preference does not exists.

    :param swa_options:
    :param conn: imaplib.IMAP4
    :return:
    """
    status, data = conn.select('#Scalix/Oddpost')
    if status != 'OK':
        raise Exception('Could not select folder #Scalix/Oddpost. '
                        'Imap response: {}'.format(data))

    orphan_uids = set()
    if not int(data[0]):
        #  there are no messages in mailbox fetching will fail so we will
        #  skip it
        email = create_preference_message()
    else:
        email, orphan_uids = find_swa_preference_email(conn)

    if not email:
        email = create_preference_message()

    # lets apply changes to the preferences
    for key, value in swa_options.items():
        find_option_and_change(email.preferences, key, value)

    # if we have UID for previous email jus tadd it to delete
    if email.uid:
        orphan_uids.add(email.uid)

    if orphan_uids:
        uids_del = b','.join([str(uid).encode() for uid in orphan_uids])
        status, data = conn.uid('STORE', uids_del.decode(), '+FLAGS',
                                '\\Deleted')
        if status != 'OK':
            warnings.warn(
                'Could not delete duplicate preference emails {}'
                '. Error {}.'.format(orphan_uids, data),
                RuntimeWarning
            )

    status, data = conn.append('#Scalix/Oddpost', '\\Seen',
                               imaplib.Time2Internaldate(time.time()),
                               email.as_bytes())
    if status != 'OK':
        if email.uid:
            conn.uid('STORE', email.uid, '-FLAGS', '\\Deleted')
        raise Exception('Could not save email. Error message {}'.format(data))

    conn.expunge()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('--host', type=str, required=True,
                        help='Imap server hostname or ip')
    parser.add_argument('--username', type=str, required=True,
                        help='Username to login')
    parser.add_argument('--password', type=str, required=True,
                        help='User password')
    parser.add_argument('--settings', nargs='*', required=True,
                        help='Multiplier SWA preference option which need to '
                             'change. Usage for e.g. '
                             'OPTION=VALUE OPTION2=VALUE')
    parser.add_argument('--port', type=int, help='Imap server port',
                        default=imaplib.IMAP4_PORT)
    parser.add_argument('--use-ssl', type=bool, help='Use ssl connection',
                        default=False)
    parser.add_argument('--replace-invalid-xml', type=bool,
                        help='Use default SWA preference template for invalid'
                             ' xml document in email.',
                        default=False)
    parser.add_argument('--debug', default=0, type=int,
                        help='Sets debug level for the imaplib module.')

    cmd_args = parser.parse_args()

    swa_settings = {}
    for option in cmd_args.settings:
        if '=' not in option:
            raise Exception('Invalid SWA configuration option format : {}.'
                            ' Supported format: OPTION=VALUE'.format(option))
        option_name, option_value = option.split('=', 1)
        swa_settings[option_name] = option_value.strip('\'"')

    imaplib.Debug = cmd_args.debug
    PreferenceEmail.REPLACE_INVALID_XML = cmd_args.replace_invalid_xml

    change_swa_settings(create_imap_connection(cmd_args), swa_settings)
