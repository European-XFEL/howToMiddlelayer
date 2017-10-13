There are 21 elements on the Kanban board that are to be documented.
Not all are listed here, but these will be, initially, split into six chapters:

- 1.Introduction
    - Motivation
    - Middle layer vs Macros
    - Architecture Overview

- 2.Middle Layer Fundamentals
    - Coroutines
    - Karabo Futures
    - Decorators
    - background() Mechanism
    - Blocking Calls: Using Synchronous Functions in Coroutines

- 3.Basic ML Device Single Device Monitoring
    - Class basics: Slots and Properties
    - Nodes
    - Device vs DeviceNode
    - Reading and Setting Device Properties
    - waitUntil()

- 4.Controlling Several Devices
    - Connect / Reconnect
    - State aggregation
    - Usage of background()
    - firstCompleted()
    - allCompleted()

- 5.Self Management
    - Initialisation
    - Deletion
    - onCancelled()

- 6.Advanced Usage
    - External Processes
    - Keeping a Slot
    - Access Levels
    - Schema Injection
    - Overwrite Elements
    - Queues
    - Table elements

Each chapter will have its own simple example device, and will refer to
existing devices that are on Gitlab (Dave's work and fastValve, for instance)

Keep in mind that this structure will be subject to changes as the documentation
evolves.
