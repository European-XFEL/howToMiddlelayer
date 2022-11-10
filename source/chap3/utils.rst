.. role:: Python(code)
  :language: Python

Util functions
==============

Remove Quantity Values from core functions
++++++++++++++++++++++++++++++++++++++++++

A good practice is to work with fixed expectations about units and timestamps and strip
them away in critical math operations, especially when relying on the external libray `numpy`.
Decorate a function to remove `KaraboValue` input with `removeQuantity`.

This function works as well with async declarations and can be used as

.. code-block:: Python

    @removeQuantity
    def calculate(x, y):
        assert not isinstance(x, KaraboValue)
        assert not isinstance(y, KaraboValue)
        return x, y


    @removeQuantity
    def calculate(boolean_x, boolean_x):
        assert not isinstance(x, KaraboValue)
        assert not isinstance(y, KaraboValue)
        # Identity comparison possible!
        return x is y


.. note:: This decorator does not cast to base units! Retrieving the magnitude of the
          `KaraboValue` allows for identity comparison.


Maximum and minimum
+++++++++++++++++++

Typically, values in devices and proxies are a `KaraboValue` which comes with a timestamp
and a unit.
However, not every simple mathmatical operation with KaraboValues is supported
by common packages. In order to take the `maximum` and `minimum` of an iterable
please have a look:

.. code-block:: Python


    from karabo.middlelayer import maximum, minimum, QuantityValue, minutesAgo

    t1 = minutesAgo(1)
    t2 = minutesAgo(10)

    a = QuantityValue(3, "m", timestamp=t1)
    b = QuantityValue(1000, "mm", timestamp=t2)
    m = maximum([a, b])
    assert m == 3 * unit.meter
    m = minimum([a, b])
    assert m == 1000 * millimeter)
    # Timestamp is the newest one -> 1
    assert m.timestamp == t1
