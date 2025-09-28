.. _subordinate:

AVL-AXI Subordinate
===================

.. inheritance-diagram:: avl_axi._swdriver
    :parts: 2

.. inheritance-diagram:: avl_axi._srdriver
    :parts: 2

The subordinate side of the AVL-AXI agent does not follow the standard AVL / UVM structure of sequence, sequencer and driver.

As the subordinate is responsive the overhead of interacting between a monitor, sequence and driver is overly complicated \
and not required.

A single function is used to decide how to complete the request:

- :any:`SubordinateReadDriver.get_next_item` or :any:`SubordinateWriteDriver.get_next_item`

This function is called with the an argument of the item to be completed, the request side of the protocol has already \
populated the item in order to make a decision.

Rate Control
~~~~~~~~~~~~

The subordinate driver is responsible for rate control. Each phase (control, data and response) has independent rate control.\
In the case of control and data the rate limiter sets the delay between valid and ready, on response it defines the delay between valids.

.. code-block:: python

    avl.Factory.set_variable("*.agent.swdrv.control_rate_limit", lambda: 0.1)
    avl.Factory.set_variable("*.agent.swdrv.data_rate_limit", lambda: 0.1)
    avl.Factory.set_variable("*.agent.swdrv.reponse_rate_limit", lambda: 0.1)

.. _ordered_write_observation:

Ordered Write Observation
~~~~~~~~~~~~~~~~~~~~~~~~~

The :any:`SubordinateWriteDriver` supports ordered write observation if configured on the interface, however \
even without this configuration it can be set in teh driver explicitly by setting :any:`SubordinateWriteDriver.in_order`.

When either of these are set the responses are sent in control order. Otherwise the bvalid / bid are returned in random order.

.. _read_interleaving_disabled:

Read Interleaving Disabled
~~~~~~~~~~~~~~~~~~~~~~~~~~

The :any:`SubordinateReadDriver` supports read interleaving disabled if configured on the interface, however \
even without this configuration it can be set in teh driver explicitly by setting :any:`SubordinateReadDriver.in_order`.

When either of these are set the responses are sent in control order. Otherwise the rvalid / rid are returned in random order \
on a beat-by-beat basis.

.. _qosaccept:

QOS Accept
~~~~~~~~~~

The :any:`SubordinateReadDriver` and :any:`SubordinateWriteDriver` support QoS_Accept as static values passed by the factory if configured. The value is set after \
reset and persists until the next reset, unless explicitly controlled by the user.

.. code-block:: python

    avl.Factory.set_variable("*.agent.swdrv.qosaccept", 0x3)
    avl.Factory.set_variable("*.agent.srdrv.qosaccept", 0x7)

.. _smemory:

AVL-AXI Subordinate Memory
==========================

.. inheritance-diagram:: avl_axi._smemory
    :parts: 1

A memory model is provided as part of the :any:`SubordinateReadDriver` and :any:`SubordinateWriteDriver` to provide memory like semantics.

The user must provide valid memory ranges for the memory, accesses outside these ranges will return :any:`axi_resp_t.DECERR` (if supported).

.. _consistent_decerr:

Equally if the Constistant_DECERR property is enabled if any of the memory accesses are outside the memory range, all responses will recieve :any:`axi_resp_t.DECERR`.


.. code-block:: python

    avl.Factory.set_variable("*.agent.cfg.subordinate_ranges", [(0x0000, 0x2FFF)])
    avl.Factory.set_override_by_type(avl_axi.SubordinateWriteDriver, avl_axi.SubordinateWriteMemoryDriver)
    avl.Factory.set_override_by_type(avl_axi.SubordinateReadDriver, avl_axi.SubordinateReadMemoryDriver)

.. note::

    Users must override both the :any:`SubordinateReadDriver` and :any:`SubordinateWriteDriver` to their memory variants to work correctly.


The AVL-AXI :any:`SubordinateMemory` extends the AVL base class by adding Atomic Transactions.

+-------------+-------------------+
| AWATOP[5:0] | Description       |
+=============+===================+
| 0b000000    | Non-atomic        |
|             | operation         |
+-------------+-------------------+
| 0b01exxx    | AtomicStore       |
+-------------+-------------------+
| 0b10exxx    | AtomicLoad        |
+-------------+-------------------+
| 0b110000    | AtomicSwap        |
+-------------+-------------------+
| 0b110001    | AtomicCompare     |
+-------------+-------------------+

+-------------+-----------------+-------------------+
| AWATOP[2:0] | Operation       | Description       |
+=============+=================+===================+
| 0b000       | ADD             | Add               |
+-------------+-----------------+-------------------+
| 0b001       | CLR             | Bit clear         |
+-------------+-----------------+-------------------+
| 0b010       | EOR             | Exclusive OR      |
+-------------+-----------------+-------------------+
| 0b011       | SET             | Bit set           |
+-------------+-----------------+-------------------+
| 0b100       | SMAX            | Signed maximum    |
+-------------+-----------------+-------------------+
| 0b101       | SMIN            | Signed minimum    |
+-------------+-----------------+-------------------+
| 0b110       | UMAX            | Unsigned maximum  |
+-------------+-----------------+-------------------+
| 0b111       | UMIN            | Unsigned minimum  |
+-------------+-----------------+-------------------+

.. literalinclude:: ../../../examples/axi/axi5-atomic/cocotb/example.py
    :language: python

.. _emonitor:

AVL-AXI Exclusivity Monitor
===========================

.. inheritance-diagram:: avl_axi._emonitor
    :parts: 1

An exclusivity monitor is provided as part of the :any:`SubordinateReadDriver` and :any:`SubordinateWriteDriver` to provide exclusive / lock semantics.

This monitor drives the correct :any:`axi_resp_t.OKAY` / :any:`axi_resp_t.EXOKAY` response if the feature is enabled.

.. literalinclude:: ../../../examples/axi/axi5-exclusive/cocotb/example.py
    :language: python
