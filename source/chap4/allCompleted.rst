Synchronizing to single karabo-future completion within a set of 
karabo-futures, or completion of all karabo-futures of the set is supported 
by `firstCompleted`, `firstException`, and `allCompleted`. As the set may 
contain only a single karabo-future it should not be surprising that all
functions have the same argument and return signatures. Necessary arguments 
are the karabo-futures as positional or keyword arguments and keyword 
arguments to modify (e.g. timeout, not cancel pending karabo-futures on 
return, etc.) function behaviour. The functions return three dictionaries 
(done, pending and error) specifying the status of the karabo-futures 
when the function returns.

Two examples of `allCompleted` usage followed by a description of useful
details should provide sufficient insight into how-to-code the functions.

The first example shows a timeout wait for connections to be established 
to devices specified in a clients list of arbritrary length and no 
`firstCompleted` or `firstException` examples are given.

..  code-block:: Python

    @coroutine
    def do_setup(self):
        self.state = State.STARTING
        self.devices = []
        try:
            done, pending, error = yield from allCompleted(
                *[connectDevice(c) for c in self.clients], timeout=10)
            if pending:
                self.logger.warning('Missing clients {}'.format(
                      ', '.join([self.clients[k] for k in pending])))
            elif error:
                self.logger.warning('Error creating client proxy {}'.format(
                      ', '.join([self.clients[k] for k in error])))
            else:
                for k, v in done.items():
                    self.devices.append(v)
                self.state = State.PASSIVE
                return
        except Exception as e:
            self.logger.exception(
                'unexpected failure creating proxy-devices {}'.format(
                    e.__class__.__name__))
        self.state = State.UNKNOWN

The second example waits indefinitely for left, right and back motor device 
nodes to reach new target positions.

.. code-block:: Python

    @Slot(
        displayedName="Move",
        description="Move to absolute position specified by targetPosition.",
        allowedStates={State.STOPPED}
    )

    @coroutine
    def move(self):
        left, right, back = virtualToActual(
            self.Y.targetPosition,
            self.Pitch.targetPosition,
            self.Roll.targetPosition,
            self.Length,
            self.Width
        )

        self.left.targetPosition = left
        self.right.targetPosition = right
        self.back.targetPosition = back

        yield from allCompleted(
            moveL=self.left.move(), 
            moveR=self.right.move(), 
            moveB=self.back.move())

The following points should be remembered when using the support functions

* Functions wait indefinitely for their completion criteria unless the 
  `timeout` keyword arguement is set with the required timeout seconds, 
  when the function will return (a Timeout exception is not thrown).
* By default functions cancel any pending karabo-futures before returning, 
  setting the `cancel_pending` keyword arguement to False prevents 
  cancellation.  
* The order of karabo-futures in done, pending and error returned 
  dictionaries maintains the order of the karabo-futures of the calling 
  arguements. This feature is assumed in example 1 to the align clients 
  and devices lists.
* When Karabo-futures are specified as positional arguements, example 1, 
  returned dictionaries are keyed with the enumebration number (0, 1, 2 
  and 3). When specified as keyword arguements, example 2, they are keyed 
  with the keyword used ("moveL", "moveR" and "moveB"). 
 
TBD: explanation and examples for extracting exceptions and other things 
from returns... is in progress.
