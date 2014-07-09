"This code is executed on the remote side and needs to be Python >=2.5 compatible"
import os
import sys
import subprocess
import fcntl
import errno


STDOUT = 1
STDERR = 2
RETURN_CODE = 3


def _set_nonblocking(f):
    flags = fcntl.fcntl(f, fcntl.F_GETFL) | os.O_NONBLOCK
    fcntl.fcntl(f, fcntl.F_SETFL, flags)


def _send_to_channel(channel, kind, file):
    try:
        data = file.read()

        if data:
            channel.send((kind, data))

    except IOError:
        e = sys.exc_info()[1]
        if e.errno not in (errno.EWOULDBLOCK, ):
            raise


def _remote_command(channel):
    command = channel.receive()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    _set_nonblocking(proc.stdout)
    _set_nonblocking(proc.stderr)

    # XXX: This might not be fully correct. This should probably look for EOF
    # on stdout/stderr rather than process exit
    while proc.poll() is None:
        _send_to_channel(channel, STDOUT, proc.stdout)
        _send_to_channel(channel, STDERR, proc.stderr)

    channel.send((RETURN_CODE, proc.returncode))


if __name__ == '__channelexec__':
    _remote_command(channel)  # NOQA
