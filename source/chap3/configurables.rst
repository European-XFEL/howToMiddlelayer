.. _configurables:

Configurables
=============

Devices can have :ref:`Nodes <nodes>` with properties. Node
structures are, as devices, created with :class:`Configurable` classes.

It might be necessary to access the top-level device within a `Node` and this can
be straightforwardly done with `Configurable.get_root()` as shown below.

.. literalinclude:: code/configurables.py
   :language: python


Furthermore, it is possible to do a bulkset of a `Hash` container on a `Configurable`
and only consider the changes.
Note that, if a single value cannot be validated, the whole `Hash` is not set.
In all cases the timestamp information is preserved, either from the value of the Hash element
or an eventual `KaraboValue` that is coming from a `Proxy`, e.g. via `connectDevice`.

.. literalinclude:: code/configurable_set.py
   :language: python