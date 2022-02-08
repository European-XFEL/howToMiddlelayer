.. _table-element:

Table Element (VectorHash)
==========================

Known as :class:`TABLE_ELEMENT` in the bound API, :class:`VectorHash` allows
users to specify custom entries, in the form of a table, that are,
programmatically, available later in the form of an iterable.

Like other karabo properties, :class:`VectorHash` is initialized by
displayedName, description, defaultValue, and accessMode. As well, it has a
`rows` field that describes what each row in the table contains.

This `rows` field expects a class that inherits from :class:`Configurable`.

.. code-block:: Python

    class RowSchema(Configurable):
        deviceId = String(
                displayedName="DeviceId",
                defaultValue="")
        instanceCount = Int(
                displayedName="Count")

This class can have as many parameters as desired, and these will be represented
as columns in the table.

With :class:`RowSchema`, the definition of the VectorHash is as follows:

.. code-block:: Python

    class MyMLDevice(Device):
        userConfig = VectorHash(
                       rows=RowSchema,
                       displayedName="Hot Initialisation",
                       defaultValue=[],
                       minSize=1, maxSize=4)

The user will now be presented with an editable table:

.. image:: graphics/VectorHash.png

Note that it is possible to provide the user with predefined entries, such as
default values or reading a configuration file, by providing a populated array
in the ``defaultValue`` option.
The ``minSize`` and ``maxSize`` arguments can limit the table's size if
needed.

.. code-block:: Python

    class MyMLDevice(Device):
        userConfig = VectorHash(
                       rows=RowSchema,
                       displayedName="Default Value Example",
                       defaultValue=[Hash("deviceId", "XHQ_EG_DG/MOTOR/1",
                                          "instanceCount", 1),
                                     Hash("deviceId", "XHQ_EG_DG/MOTOR/2",
                                          "instanceCount", 2)],
                       minSize=1, maxSize=4)


Using Entries
-------------


Once the VectorHash has been populated, it is possible to iterate through its
rows, which are themselves internally stored as a ``TableValue``, which itself
encapsulates a `numpy` array.
From **Karabo 2.14.0** onwards it is possible to convert the `np.array` value
to a list of Hashes with

.. code-block:: Python

    table = self.userConfig.to_hashlist()


Moreover, iterating over the encapsulated numpy array can be done like

.. code-block:: Python

    @Slot(displayedName="Do something with table")
    async def doSomethingTable(self):
        # This loops over the array (.value)
        for row in self.userConfig.value:
            # do something ...


Action on Update
----------------

If an action is required on VectorHash update, e.g. a row is added or removed,
then the VectorHash should be defined within a decorator:

.. code-block:: Python

    @VectorHash(rows=RowSchema,
                displayedName="Hot Initialisation",
                defaultValue=[])
    async def tableUpdate(self, updatedTable):
        self.userConfig = updatedTable
        # This loops over the array (.value)
        for row in updatedTable.value:
            # do something ...
