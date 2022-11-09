from karabo.middlelayer import (
    Configurable, Device, Double, MetricPrefix, Node, Slot, State, Unit,
    background)


class FilterNode(Configurable):
    filterPosition = Double(
        displayedName="Filter Position",
        unitSymbol=Unit.METER,
        metricPrefixSymbol=MetricPrefix.MILLI,
        absoluteError=0.01)

    @Slot(allowedStates=[State.ON])
    async def move(self):
        # access main device via get_root to notify a state change
        root = self.get_root()
        root.state = State.MOVING
        # Move the filter position in a background task
        background(self._move_filter())

    async def _move_filter(self):
        try:
            pass
            # do something
        finally:
            root = self.get_root()
            root.state = State.ON


class GlobalDevice(Device):
    node = Node(FilterNode, displayedName="Filter")
