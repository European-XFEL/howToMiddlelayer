.. _serialization

Serialization
=============

What is a Hash
---------------
The :class:`Hash` is Karabo's container, across all APIs. All data transferred
over network or saved to file by Karabo is in this format.
There exists two implementations: in C++, used by the C++ and Bound APIs, and 
the Middlelayer Python implementation.
This document covers serialization details of :class:`karabo.middlelayer.Hash`.

There are various ways to create a :class:`Hash`:

.. code-block:: Python

   from karabo.middlelayer import Hash

   value = 'a_string'
   h = Hash()
   h['key'] = value

   h = Hash('key', value)

   dict_ = {'key': value}
   h = Hash(dict_)

:class:`Hash` can be considered as a supercharged :class:`OrderedDict`
The big difference to normal Python containers is the dot-access method.
The :class:`Hash` has a built-in knowledge about it containing itself.
Thus, one can access subhashes by ``hash['key.subhash']``.

It also allows to store extra metadata, called `attributes` linked to a datum.

Most commonly, you will find as attribute the trainId, telling when was the
datum created.
These attributes are also key-value pairs stored in a dictionary:

.. code-block:: Python

   h.setAttribute('key', 'tid', 5)
   h['key', 'source'] = 'mdl'

   # It is possible to access a single attribute at a time:
   h.getAttribute('key', 'tid')
   5

   h['key', 'source']
   'mdl'


   # Or all at once:
   h.getAttributes('key')
   {'tid': 5, 'source': 'mdl'}

   h['key', ...]
   {'tid': 5, 'source': 'mdl'}

.. note::
    There are two ways of accessing and setting attributes.
    One is `setAttribute` and `getAttribute`, made to respect the C++
    implementation, the other consists of using multiple keys and ellipses

    With this in mind ``h['one', 'b']`` accesses the `b` attribute, whereas
    ``h['one.b']`` accesses the value `b` of the inner hash `one`

XML Serialization
-----------------
The Middlelayer API offers `saveToFile` and `loadFromFile`, which,
given a :class:`Hash` and a file name, will store or load the hash to XML:

.. code-block:: Python

   from karabo.middlelayer import Hash as Mash
   from karabo.middlelayer import saveToFile as save_mdl, loadFromFile as load_mdl

   save_mdl(h, 'mash.xml')

This will result in an XML like the following:

.. code-block:: xml

    <root KRB_Artificial="">
        <key KRB_Type="STRING", tid="KRB_UINT64:5" source="KRB_STRING:mdl">a_string</key>
    </root>

As shown here, the `tid` and `source` are also stored as xml attributes of `key`.
The definition of the entry for key specifies the data type (`KRB_Type`) and 
any attributes. These types (`KRB_*`) are specified using the types as defined 
in the Framework and have the values separated by a colon, and are the same type
accross APIs.

The `root` xml node is there as marker to specify that the information is an
encoded :class:`Hash`.

Cross-API
*********
As the format of a Hash is well defined, it is also possible to deserialize
a Hash from another API:

.. code-block:: Python

   from karabo.bound import Hash as Bash
   from karabo.bound import saveToFile as save_bound, loadFromFile as load_bound

   value = 'a_string'
   bash = Bash('key', value)
   bash.setAttribute('key', 'tid', 5)
   bash.setAttribute('key', 'source', 'bound')

   save_bound(bash, "bash.xml")

   loaded = load_mdl("bash.xml")
   
   type(loaded)
   karabo.middlelayer_api.hash.Hash

   loaded
   Hash([('key', 'a_string')])

   loaded[key, ...]
   {'tid': 5, 'source': 'bound'}


.. note:: 
    These examples are using both Python APIs, but the behaviour is the same
    with C++, which also provides saveTo and loadFrom files. These examples work
    from and to any API.


.. note::
    Although the two Python APIs provide identical functionalities with similar
    names, their implementation differ greatly, as the Bound API uses C++ whilst
    the Middlelayer is pure Python, and their usage should not be mixed.

    Trying to deserialize a Hash from another API does work, but
    serialization does not!

Binary Serialization
--------------------
Binary serialization is used to send data over network. The Framework usually
does the serialization, and developers needn't think of it.

The same hash will result in a binary object::

    0x01 0x00 0x00 0x00 0x03 key 0x1c 0x00 0x00 0x00 0x02 0x00 0x00 0x00 0x03 
    tid 0x12 0x00 0x00 0x00 0x05 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x06 source
    0x1c 0x00 0x00 0x00 0x03 0x00 0x00 0x00 mdl 0x08 0x00 0x00 0x00 a_string

Which is decomposed as follows::

    0x01 0x00 0x00 0x00                           # header, indicating how many entries in hash, here 1
    0x03 key                                      # the first byte define the length of the key, here of length 3 (k, e, and y), followed by its value
    0x1c 0x00 0x00 0x00                           # the type of the value for `key`, a string
    0x02 0x00 0x00 0x00                           # 2 attributes!
        0x03 tid                                  # the length of the first attribute key, followed by its value
        0x12 0x00 0x00 0x00                       # the type of the `tid` attribute, uint64
        0x05 0x00 0x00 0x00 0x00 0x00 0x00 0x00   # tid, with a value of 5
        0x06 source                               # the length of the second attribute key, followed by its value
        0x1c 0x00 0x00 0x00                       # the type of the `source` attribute
        0x03 0x00 0x00 0x00 mdl                   # the length of the value of `source` and the value itself †
    0x08 0x00 0x00 0x00                           # the length of the value for `key`
    a_string                                      # the value of the string for the `key` key.

†: The reason why the length field of the `mdl` value is an uint32, as opposed
to the length field for one of the keys, which are uint8, is that it is a value.

.. warning::
    A :class:`Hash` can contain keys of any length. However, the binary
    serialization only allowd keys up to 255 bytes. An error will be thrown
    for longer keys.

Cross-API
*********
As with xml, all APIs understand the binary format:

.. code-block:: Python

   from karabo.bound import BinarySerializerHash, Hash as Bash
   from karabo.middlelayer import decodeBinary, encodeBinary

   value = 'a_string'
   bash = Bash('key', value)
   bash.setAttribute('key', 'tid', 5)
   bash.setAttribute('key', 'source', 'bound')

   serializer = BinarySerializerHash.create(Bash('Bin'))
   bound_binary = serializer.save(bash)  # Results in the binary explained above

   loaded = decodeBinary(bound_binary)

   type(loaded)
   karabo.middlelayer_api.hash.Hash

   loaded
   Hash([('key', 'a_string')])

   loaded[key, ...]
   {'tid': 5, 'source': 'bound'}

Going from Middlelayer to Bound would be:

.. code-block:: Python

   mdl_binary = encodeBinary(h)
   loaded = serializer.load(mdl_binary)

   type(loaded)
   karathon.Hash


Table Element
-------------
In order to be serialized, a :class:`VectorHash` needs to be put within a hash
first. If your device has a table called `table` as one of its properties, then
it would be serialized as such:

.. code-block:: Python

    h = Hash()
    value, attrs = self.table.descriptor.toDataAndAttrs(self.table)
    h['table'] = value
    h['table', ...] = attrs

Then `h` can be serialized.

To restore it:

.. code-block:: Python

   value = h['table']
   attrs = h['table', ...]

   table = self.table.descriptor.toKaraboValue(value, attrs)
   setattr(self, 'table', table)
