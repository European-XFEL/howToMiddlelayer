Device Nodes or How to Orchestrate Devices the `Middle Layer` Way
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Using :func:`connectDevice` or :func:`getDevice` are practical from within
macros. Unless it is required by strict constraints, the monitoring as
described in the previous section should be left to the API.
For middle layer device development, :class:`DeviceNode` is more appropriate and
is preferred.

Defining a remote device is done as follows:

.. code-block:: Python

    motor1Proxy = DeviceNode(displayedName="RemoteDevice",
                             description="Remote motor 1",
                             accessMode=AccessMode.INITONLY)

    motor2Proxy = DeviceNode(displayedName="RemoteDevice",
                             description="Remote motor 2",
                             accessMode=AccessMode.INITONLY)

    motor3Proxy = DeviceNode(displayedName="RemoteDevice",
                             description="Remote motor 3",
                             accessMode=AccessMode.INITONLY)

And that's about it. It is however important to be aware of the workings
behind the scene, which are similar to what is described in the previous
section.

Accessing, setting, and waiting for updates from :class:`DeviceNode` is similar
to what was done previously.

Monitoring the position of these three motors is done so:

.. code-block:: Python

    positions_list = [dev.position for dev in [motor1Proxy,
                                               motor2Proxy,
                                               motor3Proxy]]
    yield from waitUntilNew(*positions_list)

Setting a parameter is a simple assignment but calling a function uses
**yield from**:

.. code-block:: Python

    self.motor1Proxy.targetPosition = 42
    yield from self.move()

Doing so for several devices is done using :func:`gather`:

.. code-block:: Python

    @coroutine
    def moveSeveral(self, positions):
        futures = []

        for device, position in zip(self.devices, positions):
            yield from setWait(device, targetPosition=position)
            futures.append(device.move())

        yield from gather(*futures)

Function and parameter calls are now exactly as they were when using
:func:`getDevice` or :func:`connectDevice`, but now details regarding the
connection to remote devices are left to the middle layer API.

Reference Implementations
-------------------------
The following devices implement the functionalities described above in a working
environment, and can be considered reference implementations:

* `fastValve`_ is a middle layer device interfacing with several remote devices
   through the use of :class:`DeviceNode`

.. _fastValve: http://in.xfel.eu/gitlab/karaboDevices/fastValve
