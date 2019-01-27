#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""

"""
from __future__ import (unicode_literals, with_statement, print_function,
                        absolute_import)
import platform
import re
import socket

from shell_command import ShellCommand, ShellCommandRuntimeException

_SYS_INFO_TEMPLATE = """Linux Distribution: {linux_distribution}
Platform: {platform}
Architecture: {architecture}
Machine: {machine}
Node: {node}
System: {system}
Release: {release}
Version: {version}
FQDN: {_fqdn}
Jre Version: {_jre}
Packages installed: {packages}
"""


class JREInfo(object):
    """

    """

    __slots__ = ('version', 'origin_version', '_raw')

    __version_reg_expr = re.compile(r'^java version "(.*)"$')

    __ibm_check_reg_expr = re.compile(r'IBM\s(\w+)\sVM')

    def __init__(self, data):
        self._raw = []
        for line in data:
            self._raw.append(line)
            version = self.__version_reg_expr.search(line.strip())
            if version:
                self.origin_version = version.group(1)
                if self.origin_version.startswith('1.'):
                    self.version = self.origin_version.lstrip('1.')
                else:
                    self.version = self.origin_version

    def is_ibm_jre(self):
        """

        :return:
        """
        for line in self._raw:
            if self.__ibm_check_reg_expr.search(line):
                return True
        return False

    def __unicode__(self):
        return self.__str__().encode()

    def __repr__(self):
        return self.version

    def __str__(self):
        return "\n".join(self._raw)


class System(object):
    """Platform information

    """
    __slots__ = ('architecture', 'platform', 'machine', 'node',
                 'system', 'release', 'version', 'linux_distribution',
                 '_fqdn', '_jre')

    def __init__(self):
        self._fqdn = None
        for func in self.__slots__:
            val = getattr(platform, func, lambda: None)()
            if isinstance(val, (tuple, set, list)):
                val = ' '.join(val)
            setattr(self, func, val)

    def __unicode__(self):
        return self.__str__().encode()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        data = {}
        for func in self.__slots__:
            data[func] = getattr(self, func.lstrip('_'))
        data['packages'] = self.packages
        return _SYS_INFO_TEMPLATE.format(**data)

    def is_64bit(self):
        """Is current system x64 bit system

        :return: bool
        """
        return self.machine == 'x86_64'

    def is_32bit(self):
        """Is current system x86 bit system

        :return: bool
        """
        return self.machine in ['i386', 'i586', 'i686']

    @property
    def fqdn(self):
        """Get Fully qualified domain name (FQDN)

        :return: AnyString
        """
        if not self._fqdn:
            self._fqdn = socket.getfqdn()
        return self._fqdn

    @property
    def ip_addresses(self):
        """List of IP addresses available in system

        :return: list
        """
        try:
            return socket.gethostbyaddr(self.fqdn)[-1]
        except socket.error as _:
            return ['127.0.0.1']

    @property
    def ip_addr(self):
        """System IP address or 127.0.0.1

        :return: AnyStr
        """
        return self.ip_addresses[0]

    def assigned_to_local_ip(self):
        """

        :return: bool
        """
        return self.ip_addr.startswith('127.')

    @property
    def jre(self):
        return self.jre_version()

    def jre_version(self):
        """

        :return:
        """
        return JREInfo(ShellCommand('java', '-version')())

    @property
    def packages(self):
        """

        :return:
        """
        cmds = [
            ShellCommand('rpm', '-qa', "'*scalix*'"),
            ShellCommand('dpkg', '--list', "'*scalix*'")
        ]
        for cmd in cmds:
            try:
                res = cmd().response
                if res:
                    return res
            except ShellCommandRuntimeException as _:
                pass
        return None


if __name__ == '__main__':
    print(System())
