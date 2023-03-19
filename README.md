README for rc5tx (Boss RC-5 Transfer)
=====================================

Description
-----------

Copies *.WAV files from a source directory tree to a target directory tree as 
a sorted list, using the Roland RC-5 file structure as a basis.


Requirements
------------

* Python3
* colorama (library for command line colors)

The latter can be installed via pip3:
```
    pip3 install colorama
```

To Use
------

Try:
```
rc5tx.py SOURCE TARGET
```
where SOURCE is a directory tree containing 1-99 *.WAV files, and TARGET is
a directory named "WAVE", usually the directory on a Boss RC-5 Loop Station
guitar pedal. E.g., 
```
rc5tx.py /Users/furusato/Desktop/rc5-source/WAVE /Volumes/BOSS RC-5/ROLAND/WAVE
```

Type for help:
```
rc5tx.py
```
After the application has successfully been executed the first time it stores
the SOURCE and TARGET values in a .rc5tx.pref file in the user's home directory.

