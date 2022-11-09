from karabo.middlelayer import Device, AsyncTimer

STATUS_THROTTLE = 0.5
STATUS_THROTTLE_MAX = 2


class StackedStatus(Device):
    """This is a device that has a lot of status updates.

    The `status` property is in the base device and commonly used to provide
    information to the operator what is happening.

    In this example the status updates are concatenated and send out after
    a maximum snooze time of the timer `STATUS_THROTTLE_MAX`.

    The timer is a single shot timer.
    """

    async def onInitialization(self):
        self.stacked_status = []
        # Single shot timer example
        self.status_timer = AsyncTimer(
            self._timer_callback, timeout=STATUS_THROTTLE,
            flush_interval=STATUS_THROTTLE_MAX, single_shot=True)

    def post_status_update(self, status):
        """Cache a status and start the async timer"""
        self.stacked_status.append(status)
        # Start the timer, it will postpone by another `STATUS_THROTTLE`
        # if started already.
        self.status_timer.start()

    async def _timer_callback(self):
        self.status = "\n".join(self.stacked_status)
        self.stacked_status = []
        self.update()


class QueueStatus(Device):
    """This is a device that has a lot of status updates.

    In this example, a status list is continously emptied with a status
    throttle time of `STATUS_THROTTLE`
    """

    async def onInitialization(self):
        self.status_queue = []
        self.status_timer = AsyncTimer(
            self._timer_callback, timeout=STATUS_THROTTLE)
        # Start the timer to continously check the queue.
        self.status_timer.start()

    def queue_status_update(self, status):
        """Queue a status update for the device"""
        self.status_queue.append(status)

    async def _timer_callback(self):
        if self.status_queue:
            self.status = self.status_queue.pop(0)
            # Potential check for status changes before setting
            self.update()
