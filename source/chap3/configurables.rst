.. _configurables:

Configurables
=============

Devices can have :ref:`Nodes <nodes>` with properties. Node
structures are, as devices, created with :class:`Configurable` classes.

It might be necessary to access the top-level device within a `Node` and this can
be straightforwardly done with `Configurable.get_root()` as shown below.

.. literalinclude:: code/configurables.py
   :language: python

