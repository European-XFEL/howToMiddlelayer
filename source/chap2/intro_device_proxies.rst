*******************************
Middlelayer Device with Proxies
*******************************

MonitorMotor is a middle layer device documenting best practice for
monitoring a single `remote device`, that is, a device written with either
of the C++ or Python API.

In this example, the device will initialise a `connection` with a `remote motor
device`, restart the connection if the remote device disappears or resets, and
display the `motorPosition` integer property of that device.

This example introduces the concepts of `Device, connectDevice, isAlive,
waitUntilNew,` and `wait_for`.

.. include:: monitor_control_proxies.rst
.. include:: device_nodes.rst