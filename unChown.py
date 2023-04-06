#!/usr/bin/python3

import logging
import os
import sys
import time
from os.path import join
from typing import *


class unChown:
    """
    This is a script to undo an errant chown of ONLY owner.  The *imperfect* logic is that files and folders
    where owner uid != group gid should be modified to owner = gid, group = gid.  The script also looks at
    file stat info and only changes files where the ctime is after a certain threshold (i.e. when the chown mistake
    was made)
    """

    def __init__(self, bad_uid: int, ctime_cutoff: int, log_path: str):
        """
        *Note:* Only logs to file when used with a ```with``` statement.

        :param bad_uid: owners to be undone if they don't owner != group
        :param ctime_cutoff: no files with most recently change BEFORE this cutoff can be modified
        :param log_path:  path to start a recursive search
        """
        self.bad_uid = bad_uid
        self.ctime_cutoff = ctime_cutoff
        self.log_path = log_path
        # log file only created when called using a with statement.  Is list of changes made (or to make if --dry-run)
        self.log_file = None
        self.logger = logging.getLogger(type(self).__name__)

    def __enter__(self) -> 'unChown':
        self.log_file = open(self.log_path, "a")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.log_file:
            self.log_file.close()
            self.log_file = None

    def _shouldChown(self, stat: os.stat_result) -> bool:
        """
        Decide if file or folder should be chowned.
        :param stat: stat_result of the file/dir
        :return: True if should be unChown-ed else False
        """
        return stat.st_ctime >= self.ctime_cutoff and stat.st_gid != stat.st_uid and stat.st_uid == self.bad_uid

    def _doChown(self, path: str, stat: os.stat_result, dry_run: bool) -> bool:
        """
        Chown the file at ```path``` to owner = gid, group = gid
        :param path: path
        :param stat: stat_result for the path
        :param dry_run: True don't actually modify file. False, do modify file.
        :return: ```True``` if a chown was performed, else ```False```
        """
        if not dry_run:
            try:
                os.chown(path=path, uid=stat.st_gid, gid=stat.st_gid, follow_symlinks=False)
            except Exception as e:
                self.logger.warning("Couldn't chown: " + str(e))
                return False
        return True

    def _doLog(self, path: str, uid: int, gid: int) -> None:
        """
        Log to std.out and if run using a with statement to a file
        :param path: path to log
        :param uid: uid of fs object at path
        :param gid: gid of fs object at path
        :return:
        """
        log_line = f"{uid}:{gid} {path}"
        self.logger.info(log_line)
        if self.log_file:
            self.log_file.write(f'{log_line}\n')

    def _handlePath(self, path: str, dry_run=False) -> bool:
        """
        :param path: path to filesystem object
        :param dry_run:
        :return:
        """
        try:
            stat = os.lstat(path)
        except Exception as e:
            self.logger.warning(f"Unable to stat: {path}: {str(e)}")
            return False
        if self._shouldChown(stat) and self._doChown(path=path, stat=stat, dry_run=dry_run):
            self._doLog(path=path, uid=stat.st_uid, gid=stat.st_gid)
            return True
        return False

    def run(self, root_path: str, dry_run: bool = False) -> None:
        """
        :param root_path: path to start filesystem walk from
        :param dry_run: if ```True``` no changes will be made to file permissions, a log may be created *see:*
        constructor for more info
        :return:
        """
        for dir_path, dir_names, file_names in os.walk(top=root_path, topdown=True, followlinks=False):
            self._handlePath(path=dir_path, dry_run=dry_run)
            for file_name in file_names:
                file_path = join(dir_path, file_name)
                self._handlePath(path=file_path, dry_run=dry_run)


# [ROOT_DIR] {optional: --dry-run}
def parseArgs() -> List[str | bool]:
    args = sys.argv[1:]
    if len(args) == 1:
        args.append(False)
    elif len(args) == 2 and args[1].lower() == "--dry-run":  # dry-run == no changes to disk
        args[1] = True
    else:
        raise ValueError("expected at least 1 arg: {root path} and the optional --dry-run flag")
    return args


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    root_path, dry_run = parseArgs()  # location to start walk form
    log_path = f"log-{int(round(time.time(), 0))}"  # path to write log file
    ctime_cutoff = 1680734730 - 30  # only files/dirs with ctimes AT or AFTER this will be modified
    bad_uid = 1_000  # owner uid which should be changed

    with unChown(bad_uid=bad_uid, ctime_cutoff=ctime_cutoff, log_path=log_path) as chown:
        chown.run(root_path=root_path, dry_run=dry_run)
