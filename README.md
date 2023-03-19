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


To Mount the RC-5 as a USB Device
---------------------------------

You must first connect the RC-5 to your computer via a USB cable, then push
the SETUP button, then rotate the MEMORY/LOOP LEVEL knob clockwise untl you
see "SETUP / STORAGE" on the display and then push the MEMORY/LOOP LEVEL knob
down. The display will change to "STORAGE / OFF". Again rotate the knob
clockwise one click until you see "CONNECTING..." on the display. At this point
your computer should mount the pedal as a USB device named "BOSS RC-5".

Once you've confirmed that the RC-5 has been mounted, obtain the absolute
path to its WAVE directory to use as the TARGET for the transfer, typically
something like
```
  /Volumes/BOSS RC-5/ROLAND/WAVE
```
on a Macintosh, or
```
  /media/username/BOSS\ RC-5/ROLAND/WAVE
```
on Linux.

I don't own a Windows computer so I don't know. I spent about 20 minutes trying
to find an reasonable example. This was the best I could do:
```
\?usb#vid_0781&pid_55ab#04016ceecfc0c8eb#{4d36e967-e325-11ce-bfc1-08002be10318\ROLAND\WAVE
```
Whatever.


To Execute the Script
---------------------

To execute the script, try:
```
  rc5tx.py SOURCE TARGET
```
where SOURCE is the full path to a directory containing 1-99 *.WAV files, and
TARGET is the full path to a directory named "WAVE", usually the directory on a
Boss RC-5 Loop Station guitar pedal. E.g.,
```
  rc5tx.py /Users/furusato/Desktop/rc5-source/WAVE /Volumes/BOSS RC-5/ROLAND/WAVE
```

Type for help:
```
  rc5tx.py
```
After the application has successfully been executed the first time it stores
the SOURCE and TARGET values in a .rc5tx.pref file in the user's home directory.

Once you have completed the file transfer you can then unmount the RC-5 using
whatever is the norm for your operating system. Do not simply disconnect the USB
plug. Once unmounted the RC-5 goes back into its normal mode.


Clearing the RC-5
-----------------

When you execute the script you will have the option to clear the target drive of
any existing *.WAV files. If you decline the script will still run; any existing
files with the same name will be overwritten by the script. If an RC-5 directory
contains more than one WAV file it's not known what will happen, so clearing the
drive is recommended. This has the benefit of replacing any WAV files that have
been modified by a clumsy attempt to halt play that accidentally put the RC-5 in
OVERDUBBING (yellow display) mode.

*NOTE:* If you care about any of the stored files on the RC-5, be sure you have
backup copies of anything on the pedal before executing the script.

