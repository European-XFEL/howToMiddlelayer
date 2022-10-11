Pipeline Device Example: Images and Output Channel Schema Injection
===================================================================

Karabo has the strong capability of sending ``ImageData`` via network. Since, sometimes
the data type of the image is not know, the corresponding schema has to be injected.
Please find below a short example how MDL can use image data for pipelining. It shows
a trivial example how schema injection may be utilized on runtime of a device
for output channels with **setOutputSchema**.

This is available with **Karabo 2.11.0**

.. literalinclude:: code/pipeline_image.py
   :language: python
