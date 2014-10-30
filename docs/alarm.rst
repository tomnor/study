

Command line utility alarm
**************************

A smooth alarm beeber for gnu/linux systems.

Has potential for improvement. Will learn about at I think.

Module content
==============

.. automodule:: alarm

Wordings about
==============

In my book the program `beep` is ideal for what I want to do, minus it is not
cross platform. But on my laptop, the beep doesn't beep. I am sure there is some
rule somewhere in the system config files preventing the beep, maybe it was even
me who put that rule at some point. But now I cannot revert it.

I thought i found it in ``/etc/modprobe.d/alsa-base-blacklist.conf``, it look like
this::

	# Uncomment these entries in order to blacklist unwanted modem drivers
	# blacklist snd-atiixp-modem
	# blacklist snd-intel8x0m
	# blacklist snd-via82xx-modem
	# Comment this entry in order to load snd-pcsp driver
	# blacklist snd-pcsp

The last line I commented so that pcsp (pc speaker I guess) is not blacklisted,
but no beep. "Normal" sounds work regardless of this setting.
