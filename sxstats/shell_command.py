# -*- coding: utf-8 -*-
"""Simplified version (originally developed with asycnio)

"""
import os
import shlex
import subprocess


class ShellCommandRuntimeException(Exception):
    """General exception for failed shell commands. Raised when shell command
    returns with nonzero exit code

    """

    def __init__(self, command, response):
        self.message = 'External command. Failed to execute "{cmd}"' \
                       ' {resp}'.format(resp=response, cmd=command)
        super(ShellCommandRuntimeException, self).__init__(self.message)
        self.result = response
        self.command = command


class ShellCommandNotFound(ShellCommandRuntimeException):
    """Helper exception for exit code 127 - when there are no such command

    """
    pass


class ShellIORedirection(object):
    """Helper class to create IO redirection and append them into ShellCommand

    """

    __slots__ = ('input', 'redir', 'out')

    def __init__(self, in_='', redir='', out=''):
        self.input = in_
        self.redir = redir
        self.out = out

    def __repr__(self):
        return "{0}{1}{2}".format(self.input, self.redir, self.out)

    @staticmethod
    def error_to_out():
        """Creates 2>&1 shell redirection

        :return: ShellIORedirection object
        """
        return ShellIORedirection(2, '>&', 1)


def is_quoted(data):
    """Checks if string is surrounded with ' or "

    :param data: string
    :return: True if it escaped otherwise False
    """
    return not set([data[0], data[-1]]) - set(['"', '\'']) and len(data) > 1


def _unify_newlines(s):
    """Because all asyncio subprocess output is read in binary mode, we don't
    get universal newlines for free. But it's the right thing to do, because we
    do all our printing with strings in text mode, which translates "\n" back
    into the platform-appropriate line separator. So for example, "\r\n" in a
    string on Windows will become "\r\r\n" when it gets printed."""

    return s.replace('\r\n', '\n')


def using_command_full_path(name, use_which=False):
    """Dummy function which will wrap command name with extra commands
    which help to determine full path of executable and run it.
    By default it will use command `type -P` to determine executable full path
    because command `which` can be not installed on some systems but
    `type ` is always there. And also `which` has a cache and sometimes it
    needs a time to get path to some executable.

    :param name: string
    :param use_which: boolean if True it will use `which`
    :return:
    """
    command = 'type -P'
    if use_which:
        command = 'which'
    return '$({0} {1})'.format(command, name)


class ShellCommand(object):
    """Build shell command

    """

    __slots__ = ('__command', '__command_args',)

    class Response(object):
        """Helper class to represent results of executed command

        """

        __slots__ = ('__exit_code', '__response')

        def __init__(self, exit_code, response):
            self.__exit_code = exit_code
            self.__response = response

        @property
        def exit_code(self):
            """Returns command exit code

            :return: int
            """
            return self.__exit_code

        @property
        def response(self):
            """Returns command output

            :return: bytes
            """
            return self.__response

        def __iter__(self):
            for line in self.__response.split('\n'):
                yield line

        def __repr__(self):
            return 'Command exit code {0}. Response: {1}'.format(
                self.__exit_code, self.response)

    def __init__(self, command, *args, **kwargs):
        self.__command = command
        self.__command_args = []
        self.__append_arguments(*args, **kwargs)

    def __append_arguments(self, *args, **kwargs):
        """Append arguments into command

        :param args: list
        :param kwargs: dict
        :return:
        """
        for item in args:
            if not isinstance(item, ShellIORedirection):
                item = str(item)
                if not is_quoted(item):
                    try:
                        item = shlex.quote(str(item))
                    except AttributeError as _:
                        import pipes
                        item = pipes.quote(str(item))
            self.__command_args.append(item)

        for key, value in kwargs.items():
            self.__command_args.append("{0}={1}".format(key, value))

    @property
    def name(self):
        """Command name

        :return: string
        """
        return os.path.basename(self.__command)

    @property
    def basename(self):
        """Command base nname

        :return: string
        """
        return os.path.basename(self.__command)

    @property
    def arguments(self):
        """Command arguments

        :return: list
        """
        return self.__command_args

    def extend(self, *args, **kwargs):
        """Add extra command arguments

        :param args:
        :param kwargs:
        :return: None
        """
        self.__append_arguments(*args, **kwargs)

    def __gt__(self, other):
        """Creates shell IO redirection '>'

        :param other:
        :return: self
        """
        self.__command_args.extend(['>', str(other)])
        return self

    def __lt__(self, other):
        """Creates shell IO redirection '<'

        :param other:
        :return: self
        """
        self.__command_args.extend(['<', str(other)])
        return self

    def __rshift__(self, other):
        """Creates shell IO redirection '>>'

        :param other:
        :return: self
        """
        self.__command_args.extend(['>>', str(other)])
        return self

    def __or__(self, other):
        """Adds new command with logical || into existing command

        :param other:
        :return: self
        """
        if not isinstance(other, ShellCommand):
            raise RuntimeError('Object is not instance of ShellCommand')
        self.__command_args.extend(['||', str(other)])
        return self

    def __and__(self, other):
        """Adds new command with logical && into existing command

        :param other:
        :return: self
        """
        if not isinstance(other, ShellCommand):
            raise RuntimeError('Object is not instance of ShellCommand')
        self.__command_args.extend(['&&', str(other)])
        return self

    def __add__(self, other):
        """Creates shell PIPE for another command by adding | before other
        command. If other is instance of ShellIORedirection it just appends it.

        :param other:
        :return:
        """
        if not isinstance(other, (ShellCommand, ShellIORedirection)):
            raise RuntimeError('Object is not instance of ShellCommand')
        if isinstance(other, ShellIORedirection):
            self.__command_args.extend([str(other)])
        else:
            self.__command_args.extend(['|', str(other)])
        return self

    def __eq__(self, other):
        """Just compare

        :param other:
        :return:
        """
        return str(self) == str(other)

    def __call__(self):
        """Call class as a function
        Raises:
                ShellCommandNotFound - when command does not exists
                ShellCommandRuntimeException - if command execution returned
                nonzero exit code

        :return: ShellCommand.Response object
        """
        return self.execute()

    def build(self):
        """Builds command with all known arguments

        :return: string
        """
        args = ' '.join([str(item) for item in self.__command_args])
        return "{0} {1}".format(self.__command, args).strip()

    def __repr__(self):
        return self.build()

    def __bytes__(self):
        return self.build().encode()

    def run(self):
        """Executes command asynchronously.

        :return: ShellCommand.Response object
        """
        shell = subprocess.Popen(str(self),
                                 close_fds=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 stdin=None,
                                 executable='/bin/bash',
                                 shell=True,
                                 universal_newlines=True)

        stdout, stderr = shell.communicate()
        return ShellCommand.Response(shell.returncode,
                                     _unify_newlines(stdout or stderr))

    def execute(self):
        """Executes command and wait's when it finish

        Raises:
                ShellCommandNotFound - when command does not exists
                ShellCommandRuntimeException - if command execution returned
                nonzero exit code

        :return: ShellCommand.Response object
        """
        res = self.run()

        if res.exit_code == 0:
            return res

        exception = ShellCommandRuntimeException
        if res.exit_code == 127:
            exception = ShellCommandNotFound
        raise exception(str(self), res)


if __name__ == '__main__':
    import sys
    cmd = ShellCommand(sys.executable, '-h')
    print(cmd)
    print(cmd.basename)
    #print(cmd())
    result = cmd.execute()
    #print(result)
    print('*'*80)
    print('result.exit_code: ', result.exit_code)
    #print('result.response: ', result.response)
    print('as list: ', list(result))
    print('lets iterate throw it: ', [line for line in result])
