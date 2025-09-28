.. _monitor:

AVL-AXI Monitor
===============

.. inheritance-diagram:: avl_axi._wmonitor
    :parts: 2

.. inheritance-diagram:: avl_axi._rmonitor
    :parts: 2

The :any:`ReadMonitor` and :any:`WriteMonitor` modules are passive components that observe the bus transactions and provides a way to collect and analyze the data.

Their behavior is as you would expect for any AVL or UVM monitor. It observes the bus signals and generates transactions based on the observed activity, \
passing it to the item_export for further processing.

.. code-block:: python

    avl.Factory.set_variable("*.agent_cfg.has_monitor", True)

Wait Cycles
-----------

In addition to constructing the :any:`SequenceItem` from the observed bus activity, the monitor also calculates the wait cycles.

Wait cycles are defined as the number of clock cycles between the request (valid) and the response (ready) signals and can be used \
for coverage or latency analysis.
