README for rc5tx (BOSS RC-5 Transfer)
=====================================

![RC-5 Loopers](img/loopers.jpg?raw=true "BOSS RC-5 Loopers")


Description
-----------

Copies *.WAV files from a source directory to a target directory, using the
**Roland BOSS RC-5 Loop Station** file structure as a basis.

This will recursively copy any *.WAV files found in the source directory tree
and sort them *alphabetically* (regardless of original location), writing them
to sequentially-numbered directories (001_1/, 002_1/, 099_1/, etc.) in the
target directory. The RC-5 supports up to 99 "memories", play-selectable via its
MEMORY knob.

Note that if you are proficient using rsync and set up a source tree mirroring
the directory structure of the RC-5, you do not need this script.


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
  /media/furusato/BOSS\ RC-5/ROLAND/WAVE
```
on Linux.

I don't own a Windows computer so I don't know. I spent about 20 minutes trying
to find an reasonable example. This was the best I could do:
```
\?usb#vid_0781&pid_55ab#04016ceecfc0c8eb#{4d36e967-e325-11ce-bfc1-08002be10318\ROLAND\WAVE
```
Whatever 😑.


To Execute the Script
---------------------

To execute the script, try:
```
  rc5tx.py SOURCE TARGET
```
where SOURCE is the full path to a directory containing 1-99 *.WAV files, and
TARGET is the full path to a directory named "WAVE", usually the directory on a
BOSS RC-5 Loop Station guitar pedal. E.g.,
```
  rc5tx.py /Users/furusato/Desktop/rc5-source/WAVE /Volumes/BOSS RC-5/ROLAND/WAVE
```
Depending on your operating system's path requirements you may need to escape
any space characters in the file path, or perhaps surround it with quotes.

Type for help:
```
  rc5tx.py
```

Saved Preferences
-----------------

After the application has successfully executed it stores the SOURCE and TARGET
values in a .rc5tx.pref file in your home directory.

Subsequent executions of the script no longer require the two arguments, with the
previous source and target values used as defaults.

If you want to avoid the existing preferences just delete the prefs file. Including
new command line arguments will override the defaults, with the new values becoming
the defaults.


Upon Completion
---------------

Once you have completed the file transfer you can then unmount the RC-5 using
whatever is the norm for your operating system. Do not simply disconnect the USB
plug. Once unmounted the RC-5 goes back into its normal mode.


Option to Clear Existing WAV Files on the RC-5
----------------------------------------------

When you execute the script you will have the option to clear the target drive of
any existing *.WAV files. If you decline the script will still run; any existing
files with the same name will be overwritten by the script. If an RC-5 directory
contains more than one WAV file it's not known what will happen, so clearing the
drive is recommended. This has the benefit of replacing any WAV files that have
been modified by a clumsy attempt to halt play that accidentally put the RC-5 in
OVERDUBBING (yellow display) mode.

**NOTE:** If you care about any of the stored files on the RC-5, be sure you have
backup copies of anything on the pedal before executing the script.

---

<sup><sub>Roland, BOSS and LOOP STATION are registered trademarks of Roland Corporation.</sub></sup>
