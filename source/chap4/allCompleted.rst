Complete Futures
================

Synchronizing to single karabo-future completion within a set of
karabo-futures, or completion of all karabo-futures of the set is supported
by `firstCompleted`, `firstException`, and `allCompleted`. As the set may
contain only a single karabo-future it should not be surprising that all
functions have the same argument and return signatures. Necessary arguments
are the karabo-futures as position or keyword arguments and optional two
keyword arguments (timeout and not cancel_pending) to modify function
behaviour. The functions return three dictionaries (done, pending, and error)
specifying the status of the karabo-futures when the function returns.

Two examples of `allCompleted` usage followed by a description of useful
details should provide sufficient insight into how-to-code the functions
and no `firstCompleted` or `firstException` examples are given.

The first example shows a timeout wait for connections to be established
to devices specified in a clients list of arbitrary length.

..  code-block:: Python

    async def setup(self):
        self.state = State.STARTING
        self.devices = []
        try:
            done, pending, error = await allCompleted(
                *[connectDevice(c) for c in self.clients],
                cancel_pending=False,
                timeout=10)

            if pending:
                self.logger.warning('Missing clients {}'.format(
                      ', '.join([self.clients[k] for k in pending])))
                for k, v in pending.items():
                    v.cancel()

            elif error:
                self.logger.warning('Error creating client proxy {}'.format(
                      ', '.join([self.clients[k] for k in error])))
                except_entry = [(k, v.__class__.__name__)
                              for k, v in error.items() if v is not None]
                pending_entry = [k for k, v in error.items() if v is None]

            else:
                for k, v in done.items():
                    self.devices.append(v)
                return

        except Exception as e:
            self.logger.exception(
                'unexpected failure creating proxy-devices {}'.format(
                    e.__class__.__name__))
        self.state = State.UNKNOWN

The second example waits indefinitely for left, right and back motor device
nodes to reach new target positions.

.. code-block:: Python

    @Slot(displayedName="Move",
           description="Move to absolute position specified by targetPosition.",
           allowedStates={State.STOPPED})
    async def move(self):
        left, right, back = virtualToActual(
            self.Y.targetPosition,
            self.Pitch.targetPosition,
            self.Roll.targetPosition,
            self.Length,
            self.Width)

        self.left.targetPosition = left
        self.right.targetPosition = right
        self.back.targetPosition = back

        await allCompleted(moveL=self.left.move(),
                           moveR=self.right.move(),
                           moveB=self.back.move())

The following points should be remembered when using the support functions

* Functions wait indefinitely for their completion criteria unless the
  `timeout` keyword argument is set with the required timeout seconds,
  when the function will return (a Timeout exception is not thrown).
* The returned done, pending and error dictionaries contain k,v pairs,
  where the key is the enumeration number (e.g. 0, 1, 2 and 3 in
  example 1) when the karabo-futures are specified as positional
  arguements, or as user specified values (e.g. "moveL", "moveR" and
  "moveB" in example 2) when specified as keyword arguements.
* The order of karabo-futures in done, pending and error returned
  dictionaries maintains the order of the karabo-futures of the calling
  arguements. This feature is assumed in example 1 to the align clients
  and devices lists when all Karabo-futures complete successfully.
* By default functions cancel any pending karabo-futures and append
  the corresponding k,v (with v = None) entry into error, before returning.
  Setting the `cancel_pending` keyword arguement to False prevents
  cancellation and the corresponding k,v (v = Karabo-future) entry is
  returned in pending. Example 1 sets cancel_pending False which ensures
  pending contains such entries which can be handled (e.g. cancelled) later.
* Karabo-futures which raise an exception have their k,v (v = Exception)
  entries returned in error. Example 1 shows how to build lists of
  exception and cancelled Karabo-futures in error.

