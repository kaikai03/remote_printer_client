
import errno
import os
import subprocess
from platform import system
from subprocess import PIPE
from time import sleep
from EDGE.common.exceptions import WebDriverException
from EDGE.web.common import utils

try:
    from subprocess import DEVNULL
    _HAS_NATIVE_DEVNULL = True
except ImportError:
    DEVNULL = -3
    _HAS_NATIVE_DEVNULL = False


class Service(object):

    def __init__(self, executable, port=0, log_file=DEVNULL, env=None, start_error_message=""):
        self.path = executable

        self.port = port
        if self.port == 0:
            self.port = utils.free_port()

        if not _HAS_NATIVE_DEVNULL and log_file == DEVNULL:
            log_file = open(os.devnull, 'wb')

        self.start_error_message = start_error_message
        self.log_file = log_file
        # Default value for every python subprocess: subprocess.Popen(..., creationflags=0)
        self.creationflags = 0
        self.env = env or os.environ

    @property
    def service_url(self):
        
        return "http://%s" % utils.join_host_port('localhost', self.port)

    def command_line_args(self):
        raise NotImplementedError("This method needs to be implemented in a sub class")

    def start(self):
        
        try:
            cmd = [self.path]
            cmd.extend(self.command_line_args())
            self.process = subprocess.Popen(cmd, env=self.env,
                                            close_fds=system() != 'Windows',
                                            stdout=self.log_file,
                                            stderr=self.log_file,
                                            stdin=PIPE,
                                            creationflags=self.creationflags)
        except TypeError:
            raise
        except OSError as err:
            if err.errno == errno.ENOENT:
                raise WebDriverException(
                    "'%s' executable needs to be in PATH. %s" % (
                        os.path.basename(self.path), self.start_error_message)
                )
            elif err.errno == errno.EACCES:
                raise WebDriverException(
                    "'%s' executable may have wrong permissions. %s" % (
                        os.path.basename(self.path), self.start_error_message)
                )
            else:
                raise
        except Exception as e:
            raise WebDriverException(
                "The executable %s needs to be available in the path. %s\n%s" %
                (os.path.basename(self.path), self.start_error_message, str(e)))
        count = 0
        while True:
            self.assert_process_still_running()
            if self.is_connectable():
                break

            count += 1
            sleep(0.5)
            if count == 60:
                raise WebDriverException("Can not connect to the Service %s" % self.path)

    def assert_process_still_running(self):
        return_code = self.process.poll()
        if return_code:
            raise WebDriverException(
                'Service %s unexpectedly exited. Status code was: %s'
                % (self.path, return_code)
            )

    def is_connectable(self):
        return utils.is_connectable(self.port)

    def send_remote_shutdown_command(self):
        try:
            from urllib import request as url_request
            URLError = url_request.URLError
        except ImportError:
            import urllib2 as url_request
            import urllib2
            URLError = urllib2.URLError

        try:
            url_request.urlopen("%s/shutdown" % self.service_url)
        except URLError:
            return

        for x in range(30):
            if not self.is_connectable():
                break
            else:
                sleep(1)

    def stop(self):
        
        if self.log_file != PIPE and not (self.log_file == DEVNULL and _HAS_NATIVE_DEVNULL):
            try:
                self.log_file.close()
            except Exception:
                pass

        if not self.process:
            return

        try:
            self.send_remote_shutdown_command()
        except TypeError:
            pass

        try:
            if self.process:
                for stream in [self.process.stdin,
                               self.process.stdout,
                               self.process.stderr]:
                    try:
                        stream.close()
                    except AttributeError:
                        pass
                self.process.terminate()
                self.process.wait()
                self.process.kill()
                self.process = None
        except OSError:
            pass

    def __del__(self):
        # `subprocess.Popen` doesn't send signal on `__del__`;
        # so we attempt to close the launched process when `__del__`
        # is triggered.
        try:
            self.stop()
        except Exception:
            pass
