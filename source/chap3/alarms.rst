.. _alarms

Alarms in Devices
=================

Each device is equipped with a ``globalAlarmCondition`` property which can
set if an alarm should be highlighted. All alarm levels are provided by
an enum of :class:`AlarmCondition` according to the severity of the alarm level.
In the middlelayer API the ``globalAlarmCondition`` does **NOT** require an
acknowledging of the alarm setting.

There are different ways of alarm monitoring depending on the environment. The
device developer can write an own alarm monitor as shown below observing the
difference of temperatures:

.. code-block:: Python

    from karabo.middlelayer import (
        AlarmCondition, background, connectDevice, Device, waitUntilNew)

    class AlarmDevice(Device):

        async def onInitialization(self):
            self.temp_upstream = await connectDevice("REMOTE_UPSTREAM")
            self.temp_downstream = await connectDevice("REMOTE_DOWNSTREAM")
            background(self.monitor())

        async def monitor(self):
            while True:
                await waitUntilNew(self.temp_upstream.value,
                                   self.temp_downstream.value)
                diff = abs(self.temp_upstream.value - self.temp_downstream.value)
                if diff > 5:
                    level = AlarmCondition.WARN
                elif diff > 10:
                    level = AlarmCondition.ALARM
                else:
                    level = AlarmCondition.NONE

                # Only set the new value if there is a difference!
                if level != self.globalAlarmCondition:
                    self.globalAlarmCondition = level

.. note::

    The default value of the ``globalAlarmCondition`` property is ``AlarmCondition.NONE``.
    Other simple settings are ``AlarmCondition.WARN``, ``AlarmCondition.ALARM`` and
    ``AlarmCondition.INTERLOCK``.

The alarm monitoring can also be automatically configured within a property with
different steps and information.


.. code-block:: Python

    from karabo.middlelayer import (
        AlarmCondition, background, connectDevice, Device, Double, waitUntilNew)

    class AlarmDevice(Device):

        temperatureDiff = Double(
            displayedName="Temperature Difference",
            accessMode=AccessMode.READONLY,
            defaultValue=0.0,
            warnLow=-5.0,
            alarmInfo_warnLow="A temperature warnLow",
            alarmNeedsAck_warnLow=True,
            warnHigh=5.0,
            alarmInfo_warnHigh="A temperature warnHigh",
            alarmNeedsAck_warnHigh=True,
            alarmLow=-10.0,
            alarmInfo_alarmLow="A temperature alarmLow",
            alarmNeedsAck_alarmLow=True,
            alarmHigh=10.0,
            alarmInfo_alarmHigh="Alarm: The temperature is critical",
            alarmNeedsAck_alarmHigh=True)


        async def onInitialization(self):
            self.temp_upstream = await connectDevice("REMOTE_UPSTREAM")
            self.temp_downstream = await connectDevice("REMOTE_DOWNSTREAM")
            background(self.monitor())

        async def monitor(self):
            while True:
                await waitUntilNew(self.temp_upstream.value,
                                   self.temp_downstream.value)
                diff = self.temp_upstream.value - self.temp_downstream.value
                self.temperatureDiff = diff


