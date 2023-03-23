#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
COPYRIGHT = '''
Copyright © 2023 Ichiro Furusato. All Rights Reserved.
These materials are owned and copyrighted by Ichiro Furusato, and use is subject
to terms of the Neocortext Software License, included as the file 'LICENSE' with
the distribution. This notice and attribution to the author may not be removed.

rc5tx comes with ABSOLUTELY NO WARRANTY. This is free software, and you are
welcome to redistribute it under the conditions of its LICENSE.'''

DESCRIPTION = '''
Description: rc5tx copies *.WAV files from a source directory tree to a target
directory tree as a sorted list, writing each file to a numbered directory using
the Roland RC-5 file structure as a basis.

It looks to the current working directory for a .rc5tx.prefs file.'''

#
# author:   Ichiro Furusato
# created:  2023-03-19
# modified: 2023-03-23
# 
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import sys, os, signal, traceback, json, shutil, calendar, time
from pathlib import Path
from datetime import datetime
import scipy
from scipy.io import wavfile
from colorama import init, Fore, Style
init()

import warnings
warnings.filterwarnings(action='ignore', category=wavfile.WavFileWarning) 

from core.logger import Logger, Level

# if DRY_RUN=True no files are modified
DRY_RUN = False
# if NO_DURATION_STATS=True then don't bother getting the WAV file duration
NO_DURATION_STATS = False

# get pref file, from current working directory
PREF_FILENAME = '.rc5tx.pref'
PREF_FILE = os.path.join(str(os.getcwd()), PREF_FILENAME)

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
            if DRY_RUN:
                _log.info('deleting target file (dry run):\t'+Fore.WHITE+'{}'.format(f))
            else:
                try:
                    _log.info('deleting target file:\t'+Fore.WHITE+'{}'.format(f))
                    os.remove(f)
                except OSError as e:
                    _log.error('Error: {} - {}.'.format(e.filename, e.strerror))
                    return False
        _log.info('target directory successfully cleaned.')
        return True
    else:
        _log.info('user did not want to clean target directory, will overwrite any existing matching files.')
        return True

# get length of wave file in seconds ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈

# function to convert the information into some readable format
def output_duration(length):
    hours = length // 3600  # hours
    length %= 3600
    mins = length // 60     # minutes
    length %= 60
    seconds = length        # seconds
    return hours, mins, seconds

def get_wav_duration(_log, file):
    if NO_DURATION_STATS:
        return '--:--:--'
    _log.info('getting duration of file: {}…'.format(os.fspath(file)))
    try:
        # sample_rate holds the sample rate of the wav file in (sample/sec) format
        # data is the numpy array that consists of actual data read from the wav file
        sample_rate, data = wavfile.read(os.fspath(file))
        len_data = len(data)        # holds length of the numpy array
        t = len_data / sample_rate  # returns duration but in floats
        hours, mins, seconds = output_duration(int(t))
        duration_hms = '{:02d}:{:02d}:{:02d}'.format(hours, mins, seconds)
#       duration_hms = '{:02d}:{:02d}:{:02d}'.format(hours, mins, seconds)
        return duration_hms
    except Exception as e:
        _log.error('error getting wave length: {}'.format(e))
        return 'EE:EE:EE'

# transfer files ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
def transfer_files(_log, source, source_files, target):
    catalog = {}
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
            source_filename = os.path.basename(source_file)
            duration_s = get_wav_duration(_log, source_file)
            target_file = os.path.join(target_dir, source_filename)
            shutil.copy2(source_file, target_file)
            _log.info('…to directory:\t'+Fore.MAGENTA+'{}'.format(target_dir))
            catalog['{:02d}'.format(i+1)] = ( duration_s, target_file )
        except OSError as e:
            _log.error('Error: {} - {}.'.format(e.filename, e.strerror))
    return catalog

# get timestamp ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
def get_timestamp():
    # create GMT timestamp as date-time
    date_time = datetime.fromtimestamp(calendar.timegm(time.gmtime()))
    return date_time.strftime("%d-%m-%YT%H:%M:%S")

# print catalog of transferred files ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
def print_catalog(_log, catalog):
    '''
    Writes a catalog of files copied to the console and a timestamped file.
    '''
    # create GMT timestamp as date-time
    date_time = datetime.fromtimestamp(calendar.timegm(time.gmtime()))
    # then format as filesystem-safe string
    timestamp = get_timestamp()
    fs_timestamp = timestamp.replace(':', '-')
    catalog_filename = 'catalog-rc5tx-{}.md'.format(fs_timestamp)
    with open(catalog_filename, 'a') as fout:
        fout.write('audio file catalog - {}\n--------------------------\n\n'.format(timestamp))
        fout.write('\n    memory:   size (KB):     duration:     file:\n')
        _log.info('catalog of files:\n\n' + Fore.WHITE + '    memory:   size (KB):     duration:     file:')
        for memory, info in catalog.items():
            duration_s = info[0]
            filepath = info[1]
            subdirname = os.path.basename(os.path.dirname(filepath))
            filename = os.path.basename(filepath)
            filesize = int(Path(filepath).stat().st_size / 1000.0)
            line = ('    {:<8}  {:>10}      {:>8}     {}/{}'.format(memory, filesize, duration_s, subdirname, filename))
            fout.write(line + '\n')
            print(Fore.WHITE + line)
        fout.write('\n')
        print('')
    _log.info('wrote catalog file: {}'.format(catalog_filename))

# help ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
def help():
#    COPYRIGHT = '''
#Copyright © 2023 Ichiro Furusato. All Rights Reserved.
#These materials are owned and copyrighted by Ichiro Furusato, and use is subject
#to terms of the Neocortext Software License, included as the file 'LICENSE' with
#the distribution. This notice and attribution to the author may not be removed.
#
#rc5tx comes with ABSOLUTELY NO WARRANTY. This is free software, and you are
#welcome to redistribute it under the conditions of its LICENSE.
    usage = '''
Usage: 

    rc5tx SOURCE_DIRECTORY TARGET_DIRECTORY'''
    help_text2 = '''
Upon successful execution a file named '{}' containing
the default values is written to the current working directory. If this file is
subsequently found, the two arguments are not required, though new command line
arguments will override the defaults and rewrite the prefs file.
'''.format(PREF_FILENAME)
    print(Fore.GREEN + COPYRIGHT)
    print(Fore.GREEN + DESCRIPTION)
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
            target_arg = pref_args.get('target')
        else:
            help()
            _log.warning('exit: expecting two arguments.')
            return
        _log.info('initialised.')

        # validate: source directory
        source = Path(source_arg)
        if source.exists():
            if source.is_dir():
                _log.info('source directory:\t'+Fore.WHITE+'{}'.format(source_arg))
            else:
                raise NotADirectoryError('source argument is not a directory: {}'.format(source_arg))
        else:
            raise FileNotFoundError('source directory does not exist: {}'.format(source_arg))
        # validate: target directory
        target = Path(target_arg)
        if target.exists():
            if not target.is_dir():
                raise NotADirectoryError('target argument is not a directory: {}'.format(target_arg))
        else:
            _log.error('target directory does not exist: {}'.format(target_arg))
            _log.error('Is the RC-5 mounted as a USB device?')
            return

        # validate: check source and target aren't the same
        if source == target:
            _log.error('exit: source and target directory are the same:\t'+Fore.WHITE+'{}'.format(source_arg))
            return
        # validate: 'WAVE' as target directory
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

        # validate: RC-5 has limit of 99 memories
        if len(source_files) > 99:
            _log.error('exit: too many source files ({})'.format(len(source_files)))
            return

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
                catalog = transfer_files(_log, source, source_files, target)
                if len(catalog) > 0:
                    # write prefs upon successful transfer
                    prefs_write(_log, source, target)
                    # print catalog
                    print_catalog(_log, catalog)
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
