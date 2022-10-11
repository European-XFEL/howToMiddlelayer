Pipeline Proxy Example
======================

In the previous section we learned that devices can have `input` and `output`
channels. It is possible to access pipeline data with middlelayer proxies as well.

Output Proxies
--------------

Consider a remote device that has an `OutputChannel` with an equal schema as was presented
in the last section,

.. code-block:: Python

    class DataNode(Configurable):
        daqDataType = DaqDataType.TRAIN

        doubleProperty = Double(
            defaultValue=0.0,
            accessMode=AccessMode.READONLY)

    class ChannelNode(Configurable):
        data = Node(DataNode)


    output = OutputChannel(
        ChannelNode,
        displayedName="Output",
        description="Pipeline Output channel")


Then it is possible to create a middlelayer proxy and connect to the channel
with a channel policy **drop** via:

.. code-block:: Python

    from karabo.middlelayer import connectDevice, waitUntilNew

    proxy = await connectDevice("device")
    # This is a non-blocking connect in a background task
    proxy.output.connect()

    # Inspect the data
    while True:
        value = proxy.output.schema.data.doubleProperty
        if value > 100:
            break
        await waitUntilNew(proxy.output.schema.data.doubleProperty)

    # Disconnect if you are not interested anymore, this saves network traffic
    # which other channels can use.
    proxy.output.disconnect()

As can be seen, it is possible to use `waitUntilNew` on the properties in the output proxy.
Additionally, handlers can be registered for convenient use, **before** connecting:

.. code-block:: Python

    from karabo.middlelayer import Hash, connectDevice, get_timestamp

    proxy = await connectDevice("deviceId")
    # Register handlers (# strong reference)

    async def data_handler(data, meta):
        # do something with data hash
        assert isinstance(data, Hash)

        # meta is an object containing source and timestamp information
        source = meta.source # string
        # get the timestamp object from timestamp variable
        timestamp = meta.timestamp.timestamp
        # make sure trainId is corrected
        timestamp = get_timestamp(meta.timestamp.timestamp)
        # do something

    async def connect_handler(channel):
       """Connect stream handler of channel"""

    async def eos_handler(channel):
       """End of stream handler of channel"""

    async def close_handler(channel):
       """Close stream handler of channel"""

    proxy.output.setDataHandler(data_handler)
    proxy.output.setConnectHandler(connect_handler)
    proxy.output.setEndOfStreamHandler(eos_handler)
    proxy.output.setCloseHandler(close_handler)
    proxy.output.connect()

Furthermore, from **Karabo 2.16.X** onwards, it is possible to reassign handlers after disconnecting.
Using proxies for pipeline data is a very powerful feature and sometimes it is only needed
to get a few context-specific pipeline packages. For this purpose, from **Karabo 2.16.X** onwards, the
`PipelineContext` can be used.


Pipeline Context
----------------

This context represents a specific input channel connection to a karabo device
and is not connected automatically, but may be connected using :meth:`async with` or :meth:`with`

.. code-block:: Python

    channel = PipelineContext("deviceId:output")
    async with channel:
        # wait for and retrieve exactly one data, metadata pair
        data, meta = await channel.get_data()
        source = meta.source
        timestamp = get_timestamp(meta.timestamp.timestamp)

    with channel:
        await channel.get_data()

It is possible to ask for the connection status using :meth:`is_alive` and
wait for the pipeline connection awaiting :meth:`wait_connected`

.. code-block:: Python

    async with channel:
        if not channel.is_alive():
            await channel.wait_connected()

    # Leaving the context, will disconnect
    assert not channel.is_alive()

However, awaiting a connection is already implicitly done when waiting
for pipeline data to arrive in :meth:`get_data`.

