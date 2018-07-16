Device server: Eventloop
========================

Karabo middlelayer uses Python's asyncio, installing a custom event loop.
All devices in a device server share the **same event loop** which is run in a
single thread. Hence, every blocking call in any device instance results in
blocking every other device in the same device server.
However, the device developer is free to start threads using background, which
starts a thread if used with a function which is not a coroutine.
The event loop thread pool executor can have 200 threads.

Device server: TimeMiXin
========================

The middlelayer device server automatically connects and reconnects to a
TimeServer if the **timeServerId** is provided on initialization.
On updates of the TimeServer a singleton-like TimeMixin class is updated with
a reference timestamp to calculate the trainId's.
Each device will always calculate the trainId automatically if the device
server was once connected to a TimeServer.