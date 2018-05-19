from threading import Thread
import time
import os
import signal
import hashlib


class KillThread(Thread):
    def _kill(self, seconds):
        seconds = int(seconds)
        while True:
            time.sleep(seconds)
            os.kill(os.getpid(), signal.SIGINT)

    def kill_delay(self, seconds):
        t = Thread(target=self._kill, args=(seconds, ))
        t.start()


class GeneralTools(object):
    def __init__(self):
        pass

    def article2md5(self, row):
        md5 = hashlib.md5()
        if isinstance(row, list):
            row = ''.join(row)
        md5.update(row.encode())
        return md5.hexdigest()

    def debug_decorate(is_debug):
        def inner_func(func):
            def inner_func2(*args, **kwargs):
                if is_debug:
                    func(*args, **kwargs)
            return inner_func2
        return inner_func

    @debug_decorate(False)
    def print_log(self, log):
        print(log)
