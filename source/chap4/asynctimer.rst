Async Timer
===========

There are different ways in the middlelayer to continous or repeated checks
and procedures.
Since **Karabo 2.16.X** the **AsyncTimer** for can be used for repeating tasks.

A striking possibility is to bunch device status updates. Not only does the middlelayer
bunch updates but also the Karabo Gui Server device is throttling device updates.
In the code example below, two examples of status throttling are depicated using the
**AsyncTimer**.


.. literalinclude:: code/asynctimer.py
   :language: python
