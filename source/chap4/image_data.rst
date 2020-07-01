Images
======

Karabo has the strong capability of sending ``ImageData`` via network. The middlelayer
API provides this possibility as well.

Image Element
-------------

The ``Image`` element is a helper class to provide ``ImageData``

Along the raw pixel values it also stores useful metadata like encoding,
bit depth or binning and basic transformations like flip, rotation, ROI.

This special hash ``Type`` contains an ``NDArray`` element and is constructed:

.. code-block:: Python

    import numpy as np
    from karabo.middlelayer import Configurable, Device, EncodingType

    class Device(Configurable):

        image = Image(
            data=ImageData(np.zeros(shape=(10, 10), dtype=np.uint64),
                           encoding=EncodingType.GRAY),
            displayedName="Image")

Hence, the `Image` element can be initialized with an `ImageData`
KaraboValue.

Alternatively, the `Image` element can be initialized by providing `shape`
and `dtype` and the `encoding`:

.. code-block:: Python

    image = Image(
        displayedName="Image"
        shape=(2600, 2000),
        dtype=UInt8,
        encoding=EncodingType.GRAY)

The `dtype` can be provided with a simple Karabo descriptor or the numpy
dtype, e.g. numpy.uint8.

Image Data
----------

The Karabo ``ImageData`` is supposed to provide an encapsulated NDArray.

This ``KaraboValue`` can estimate from the input array the associated
attributes of the `ImageData`, such as binning, encoding, etc. The minimum requiremnt
to initialize is a numpy array with dtype and shape.

.. code-block:: Python

    import numpy as np
    from karabo.middlelayer import ImageData

    data = ImageData(np.zeros(shape=(10, 10), dtype=np.uint64))


Further attributes can be provided as keyword arguments on object creation, also
on runtime. The ``ImageData`` can be set on runtime on an ``Image`` element.
**However, changing attributes on runtime will not alter the Schema information**

.. code-block:: python

    class ImageData(KaraboValue):
        def __init__(self, value, *args, binning=None, encoding=None,
                     rotation=None, roiOffsets=None, dimScales=None, dimTypes=None,
                     bitsPerPixel=None, flipX=False, flipY=False, **kwargs):

- binning [uint64]: Array or list of the binning of the image, e.g. [0, 0]
- encoding [int32]: The encoding of the image, e.g. EncodingType.GRAY (enum)
- rotation [int32]: The rotation of the image, either 0, 90, 180 or 270
- roiOffsets [uin64]: Array or list of the roiOffset, e.g. [0, 0]
- dimScales [str]: Description of the dim scales
- dimTypes [int32]: The dimension types array or list
- bitsPerPixel: The bits per pixel
- flipX: boolean, either `True` or `False`
- flipY: boolean, either `True` or `False`

