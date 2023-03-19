#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright © 2023 Ichiro Furusato. All Rights Reserved.
# These materials are owned and copyrighted by Ichiro Furusato, and use is subject
# to terms of the Neocortext Software License, included as the file 'LICENSE' with
# the distribution. This notice and attribution to the author may not be removed.
#
# author:   Ichiro Furusato
# created:  2023-03-19
# modified: 2023-03-19
#
# Description: copies *.WAV files from a source directory tree to a target
# directory tree as a sorted list, using the Roland RC-5 file structure as
# a basis.

import sys, os, signal, traceback, json, shutil
from pathlib import Path
from datetime import datetime
from colorama import init, Fore, Style
init()

from core.logger import Logger, Level

# if dry_run=True no files are modified
dry_run = False
# get pref file
home_dir = str(Path.home())
pref_filename = '.rc5tx.pref'
PREF_FILE = os.path.join(home_dir, pref_filename)

# execution handler ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
def signal_handler(signal, frame):
    print('\nsignal handler : INFO  : Ctrl-C caught: exiting…')
    print('exit.')

# write prefs ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
def prefs_write(_log, source, target):
    _log.info('writing {} file…'.format(PREF_FILE))
    dictionary = {
        'source': str(source),
        'target': str(target)
    }
    json_object = json.dumps(dictionary, indent=4)
    with open(PREF_FILE, 'w') as outfile:
        outfile.write(json_object)
    _log.info('successfully wrote preferences file.')

# read prefs ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
def prefs_read(_log):
    _log.info('reading prefs file…')
    # data to be read
    with open(PREF_FILE, 'r') as openfile:
        dictionary = json.load(openfile)
    _log.info('successfully read prefs file.')
    return dictionary

# get filename from path ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
def get_filename(path):
    return path.name

# clean target directory ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
def clean_target_directory(_log, target):
    target_files = []
    target_list = target.rglob('*')
    for f in target_list:
        ext = os.path.splitext(f)[-1].lower()
        if f.is_file() and ext == '.wav':
            target_files.append(f)
    if len(target_files) == 0:
        _log.info('target directory contained no WAV files.')
        return True
    elif input(Fore.RED + 'Delete {} existing WAV files in the target directory. Are you sure? (y/n): '.format(len(target_files))).lower().strip() == 'y':
        for f in target_files:
            if dry_run:
                _log.info('deleting target file (dry run):\t'+Fore.WHITE+'{}'.format(f))
            else:
                try:
                    _log.info('deleting target file:\t'+Fore.WHITE+'{}'.format(f))
                    os.remove(f)
                except OSError as e:
                    _log.error('Error: %s - %s.' % (e.filename, e.strerror))
                    return False
        _log.info('target directory successfully cleaned.')
        return True
    else:
        _log.info('user did not want to clean target directory, will overwrite any existing matching files.')
        return True

# transfer files ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
def transfer_files(_log, source, source_files, target):
    file_count = len(source_files)
    _log.info('transferring {} files from source directory:\t'.format(file_count)+Fore.WHITE+'{}'.format(source))
    _log.info('                        to target directory:\t'+Fore.MAGENTA+'{}'.format(target))
    # TODO
    for i in range(file_count):
        source_file = source_files[i]
        _log.info('transferring:\t'+Fore.WHITE+'{}'.format(source_file))
        try:
            # ./WAVE/001_1, ./WAVE/002_1, ... ./WAVE/099_1
            target_dir_name = os.path.join(target, '0{:02d}_1'.format(i+1))
            target_dir = Path(target_dir_name)
            if not target_dir.is_dir():
                os.makedirs(target_dir)
            # do the deed
            shutil.copy2(source_file, target_dir)
            _log.info('…to directory:\t'+Fore.MAGENTA+'{}'.format(target_dir))
        except OSError as e:
            _log.error('Error: %s - %s.' % (e.filename, e.strerror))
            return False
    return True

# help ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
def help():
    help_text1 = '''
Copyright © 2023 Ichiro Furusato. All Rights Reserved.
These materials are owned and copyrighted by Ichiro Furusato, and use is subject
to terms of the Neocortext Software License, included as the file 'LICENSE' with
the distribution. This notice and attribution to the author may not be removed.

rc5tx comes with ABSOLUTELY NO WARRANTY. This is free software, and you are
welcome to redistribute it under the conditions of its LICENSE.

Description: rc5tx copies *.WAV files from a source directory tree to a target
directory tree as a sorted list, writing each file to a numbered directory using
the Roland RC-5 file structure as a basis.'''
    usage = '''
Usage: rc5tx SOURCE TARGET'''
    help_text2 = '''
Upon successful execution a file named '{}' containing
the default values is written to the user's home directory. If this file is
subsequently found, the two arguments are not required, though new command line
arguments will override the defaults and rewrite the prefs file.
'''.format(PREF_FILE)
    print(Fore.GREEN + help_text1)
    print(Fore.WHITE + usage)
    print(Fore.GREEN + help_text2)

# main ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main(argv):
    '''
        This is the main function of the transfer script.
    '''
    _log = Logger('rc5tx', Level.INFO)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        pref_file = Path(PREF_FILE)
        # we prefer 2 arguments over existence of prefs file
        if len(argv) == 2:
            _log.info('arguments:')
            for arg in argv:
                _log.info('arg: {}'.format(arg))
            source_arg = argv[0]
            target_arg = argv[1]
        elif pref_file.exists():
            _log.info('{} file found.'.format(PREF_FILE))
            # read prefs file...
            pref_args = prefs_read(_log)
            source_arg = pref_args.get('source')
            _log.info('pref_args source: {}'.format(source_arg))
            target_arg = pref_args.get('target')
            _log.info('pref_args target: {}'.format(target_arg))
        else:
            help()
            _log.info('exit: expecting two arguments.')
            return
        _log.info('initialised.')

        # validate source directory
        source = Path(source_arg)
        if source.exists():
            if source.is_dir():
                _log.info('source directory:\t'+Fore.WHITE+'{}'.format(source_arg))
            else:
                raise NotADirectoryError('source argument is not a directory: {}'.format(source_arg))
        else:
            raise FileNotFoundError('source directory does not exist: {}'.format(source_arg))
        # validate target directory
        target = Path(target_arg)
        if target.exists():
            if not target.is_dir():
                raise NotADirectoryError('target argument is not a directory: {}'.format(source_arg))
        else:
            raise FileNotFoundError('target directory does not exist: {}'.format(source_arg))

        # let's be safe
        if source == target:
            _log.error('exit: source and target directory are the same:\t'+Fore.WHITE+'{}'.format(source_arg))
            return
        # expect 'WAVE' as target directory
        wave_dir = os.path.basename(os.path.normpath(target))
        if wave_dir != 'WAVE':
            _log.error('expected target directory to be named "WAVE", not: '+Fore.WHITE+'{}'.format(wave_dir))
            return
        _log.info('target directory:\t'+Fore.MAGENTA+'{}'.format(target))

        # get all WAV files in source directory
        source_files = []
        source_list = source.rglob('*')
        for f1 in source_list:
            ext = os.path.splitext(f1)[-1].lower()
            if f1.is_file() and ext == '.wav':
                source_files.append(f1)

        # sort list by filename
        source_files.sort(key=get_filename)
        _log.info('found {} source files (sorted):'.format(len(source_files)))
        for f2 in source_files:
            _log.info('source:\t'+Fore.WHITE+'{}'.format(f2))

        # we've got source and target, continuing...
        _log.info('target directory:\t'+Fore.WHITE+'{}'.format(target_arg))
        if input(Fore.RED + 'Continue? (y/n): ').lower().strip() == 'y':
            _log.info(Fore.WHITE + 'continuing…')
            if clean_target_directory(_log, target):
                tstart = datetime.now()
                if transfer_files(_log, source, source_files, target):
                    # write prefs upon successful transfer
                    prefs_write(_log, source, target)
                # we're done...
                tend = datetime.now()
                elapsed = ( tend - tstart )
                elapsed_ms = int(elapsed.microseconds / 1000)
                _log.info(Fore.GREEN + 'processing complete: {}ms elapsed.'.format(elapsed_ms))
                _log.info('processed using command line:\n\n'+Fore.WHITE+'    rc5tx.py {} {}\n'.format(source, target))
            else:
                _log.warning('exit: clean target directory failed.')
        else:
            _log.info(Fore.GREEN + 'user cancelled.')

    except KeyboardInterrupt:
        _log.error('caught Ctrl-C; exiting…')
        sys.exit(1)
    except Exception:
        _log.error('error executing rc5tx: {}'.format(traceback.format_exc()))
    finally:
        _log.info(Fore.GREEN + 'complete.')

# ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
if __name__== "__main__":
    main(sys.argv[1:])

#EOF
