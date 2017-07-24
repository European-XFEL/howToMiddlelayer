Synchronizing to single future completion withing a set of futures, or
completion of all futures of the set is supported by `firstCompleted`,
`firstException`, and `allCompleted`.
As the set may contain only a single future it should not be surprising that all
functions have the same argument and return signatures. Necessary arguments are
the futures as positional arguments and keyword arguments to modify (e.g. timeout,
cancel still pending on return, etc.) the functions behaviour. The functions
return three dictionaries (done, pending and error) specifying the status of
the futures when the function returns.

Two examples of `allCompleted` usage followed by a description of useful
details should provide sufficient insight into how-to-code the functions.

The first example shows a timeout wait for connections to be established to a set
of client devices.

.. code-block:: Python

        self.state = State.STARTING
        self.clients = ['dev1', 'dev2', 'dev3']
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

The second example is waits indefinitely for motor devices to reached their target positions.

.. code-block:: Python

        # tbd from David's code
        self.state = xyz

The following details should be remembered when using the above support functions

* tbd 1
* tbd 2
