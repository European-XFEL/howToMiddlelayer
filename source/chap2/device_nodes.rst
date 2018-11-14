.. _device-nodes

Device Nodes - The `Middle Layer` Way
=====================================

Using :func:`connectDevice` or :func:`getDevice` are practical from within
macros. Unless it is required by strict constraints, the monitoring as
described in the previous section should be left to the API.
For middle layer device development, :class:`DeviceNode` is more appropriate and
is preferred.

.. note::
    DeviceNodes are **MANDATORY** properties and can only be set before
    instantiation, e.g. are **INITONLY**!

Defining a remote device is done as follows:

.. code-block:: Python

    motor1Proxy = DeviceNode(displayedName="RemoteDevice",
                             description="Remote motor 1")

    motor2Proxy = DeviceNode(displayedName="RemoteDevice",
                             description="Remote motor 2")

    motor3Proxy = DeviceNode(displayedName="RemoteDevice",
                             description="Remote motor 3")

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
    await waitUntilNew(*positions_list)

Setting a parameter is a simple assignment but calling a function needs
to be **awaited**:

.. code-block:: Python

    self.motor1Proxy.targetPosition = 42
    await self.motor1Proxy.move()

Doing so for several devices is done using :func:`gather`:

.. code-block:: Python

    async def moveSeveral(self, positions):
        futures = []

        for device, position in zip(self.devices, positions):
            await setWait(device, targetPosition=position)
            futures.append(device.move())

        await gather(*futures)

Function and parameter calls are now exactly as they were when using
:func:`getDevice` or :func:`connectDevice`, but now details regarding the
connection to remote devices are left to the middle layer API.

Proxy connection
****************

The DeviceNode holds a proxy to a remote device. During initialization the
DeviceNodes try to establish a proxy connection. Once this is done, the schema
of the main device will be updated.
Unfortunately, due to the nature of the DeviceNode, the operator does not see
if a device using DeviceNodes is fully functional in the beginning, as there is
no feedback on the connection status.

For this purpose, with **Karabo 2.3.0** a timeout parameter in seconds can be provided.

.. code-block:: Python

    motor1Proxy = DeviceNode(displayedName="RemoteDevice",
                             description="Remote motor 1",
                             timeout=1.5)

If the DeviceNode was not able to estasblish the proxy connection within this
timeframe an error is thrown and the holding device shuts down with an error
message which is visible in the log files.


Reference Implementations
-------------------------
The following devices implement the functionalities described above in a working
environment, and can be considered reference implementations:

* `fastValve`_ is a middle layer device interfacing with several remote devices
   through the use of :class:`DeviceNode`

.. _fastValve: http://in.xfel.eu/gitlab/karaboDevices/fastValve
