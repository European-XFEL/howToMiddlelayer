from karabo.middlelayer import (
    Configurable, Device, Double, Hash, Int32, MetricPrefix, Node,
    QuantityValue, Slot, State, Unit, minutesAgo)


class FilterNode(Configurable):
    filterPosition = Double(
        displayedName="Filter Position",
        unitSymbol=Unit.METER,
        metricPrefixSymbol=MetricPrefix.MILLI,
        absoluteError=0.01)


class MotorDevice(Device):

    channel = Int32(
        defaultValue=0)

    targetPosition = Double(
        defaultValue=0.0)

    velocity = Double(
        defaultValue=0.0,
        minInc=0.0,
        maxInc=10)

    node = Node(FilterNode, displayedName="Filter")


    def updateFromExternal(self):
        # get external data, everytime the timestamp is considered, either
        # via Hash attributes or `KaraboValue`
        h = Hash("targetPosition", 4.2,
                 "velocity", QuantityValue(4.2, timestamp=minutesAgo(2)),
                 "node.filterPosition", 2)
        # 1. All values will be applied only if they changed
        self.set(h, only_changes=True)

        # 2. All values will be applied
        self.set(h)

        h = Hash("targetPosition", 4.2,
                 "velocity", QuantityValue(100.2, timestamp=minutesAgo(2)),
                 "node.filterPosition", 12)
        # NO VALUE will be applied as velocity is outside limits!
        self.set(h, only_changes=True)
