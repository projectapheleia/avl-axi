.. _manager:

AVL-AXI Manager
===============


The manager side of the AVL-AXI agent follow the standard AVL / UVM structure of sequence, sequencer and driver.

Manager Sequence
-----------------

.. inheritance-diagram:: avl_axi._msequence
    :parts: 1

A very simple sequence is provided that generates a stream of :any:`SequenceItem` items.

The length of the sequence is defined by the n_items variable, which defaults to 1, but is expected to be override by the factory.

In addition a list of ranges can be provided to define the address space for the sequence. If not provided, the sequence will randomize \
the address along with all other variables of the item.

As the item is parameterized, only the manager side attributes present will be randomized.

The user is expected to extend the sequence for custom behavior.

The :any:`ManagerSequence` provides:

    - :any:`ManagerSequence.next` function to generate and send a random transaction
    - :any:`ManagerSequence.write` function to generate and send a fully constrained write transactions
    - :any:`ManagerSequence.read` function to generate and send a fully constrained read transactions

In the case of the :any:`ManagerSequence.read` and :any:`ManagerSequence.write` functions kwargs that match the signal names \
are used to define the transfer. Data and response values must be presented as lists where appropriate and undefined fields are \
left as 0.

Wait For
~~~~~~~~

The :any:`ManagerSequence.wait_for` variable can be set to None, done, control, data or response. This defines the phase of \
the items that must complete before the sequence moves on.

This field can be overridden on a per-transaction basis using the wait_for argument of of the :any:`ManagerSequence.write` and \
:any:`ManagerSequence.read` functions.

In order to have multiple outstanding transactions you can wait_for None, done or call the function from a cocotb.start sub-process.

Manager Drivers
---------------

Due to the independence of the read and write buses the AXI driver is split in 2:

.. inheritance-diagram:: avl_axi._mwdriver
    :parts: 2

.. inheritance-diagram:: avl_axi._mrdriver
    :parts: 2

The manager driver implements the legal protocol and splits the item into 3 tasks, each with a drive and quiesce parts

    - control
    - data
    - response

All manager driven protocol signals (valid, ready, last etc.) and handled by the drivers. In addition all subordinate driven protocol\
signals are observed and the sequence item updated accordingly. This means that should the user want to implement directed checks within the \
sequence they can do this easily.

Callbacks
~~~~~~~~~
:any:`SequenceItem` have a number of events based on the protocol:

    - done. The standard AVL Driver to Sequencer callback to indicate the items has been processed by the driver.
    - response. The standard AVL Driver to Sequencer to indicate the transfer is completed by the driver.
    - control. Custom to AVL-AXI. Callback to indicate the control phase (AW/AR) has completed.
    - data. Custome to AVL-AXI. Callback to indicate the data phase (W) of write transactions has completed.

The response, control and data callbacks each take the item itself as an argument to the callback.

The :any:`WriteMonitor` and :any:`ReadMonitor` also call the control, data and response callbacks for any custom implementations.

Rate Control
~~~~~~~~~~~~

The manager driver is responsible for rate control. Each phase (control, data and response) has independent rate control.\
In the case of control and data the rate limiter sets the delay between valids, on response it defines the delay of ready.

.. code-block:: python

    avl.Factory.set_variable("*.agent.mwdrv.control_rate_limit", lambda: 0.1)
    avl.Factory.set_variable("*.agent.mwdrv.data_rate_limit", lambda: 0.1)
    avl.Factory.set_variable("*.agent.mwdrv.reponse_rate_limit", lambda: 0.1)

.. _wakeup:

Wakeup Control (AXI5)
~~~~~~~~~~~~~~~~~~~~~

.. inheritance-diagram:: avl_axi._mwakedriver
    :parts: 2

In AXI5, the manager driver can control the wakeup signal. The pre_wakeup and post_wakeup variables are used to define the \
pre-wakeup and post-wakeup delays, respectively. These are defined as lambda functions that return a value between 0.0 and 1.0.

This feature ensures the wakeup signals are driven correctly according to the AXI protocol, while providing randomization of the assertion and \
de-assertion timing.

A dedicated wakeup driver is implemented to co-ordinate the wakeup across the read and write buses.

Before any item is presented on the control (AW or AR) buses or data (W) bus the wake will be asserted. Once an item has requested to goto sleep \
no more transactions will be started and once all outstanding responses are revieved the awakeup signal will be deasserted.

.. code-block:: python

    avl.Factory.set_variable("*.agent.mwakedrv.pre_wakeup", lambda: 0.1) # Early assertion of wakeup sign before driving the manager
    avl.Factory.set_variable("*.agent.mwakedrv.post_wakeup", lambda: 0.9) # Quick de-assertion of wakeup signal after driving the manager

Allow Early Data
~~~~~~~~~~~~~~~~

Technically there is no reason the WDATA cannot be sent before the AW phase. In reality this is unlikely due to the subordinate \
not knowing how to route the data until the control phase is complete.

However AVL-AXI allows for this scenario. It is only important to the :any:`ManagerWriteDriver` as Subordinates and\
monitors can stash the data regardless of order.

To enable early data the configuration option :any:`allow_early_data <avl_axi._mwdriver.ManagerWriteDriver.allow_early_data>` must be set to True.

.. code-block:: python

    avl.Factory.set_variable("*.agent.mwdrv.allow_early_data", True)

.. literalinclude:: ../../../examples/axi/axi5-early-wdata/cocotb/example.py
    :language: python

Maximum Outstanding Transactions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :any:`ManagerWriteDriver` and :any:`ManagerReadDriver` both support a :any`max_outstanding`
parameter which allows the user to limit the total number of transaction on the bus at any one time. By default there is no limit.

.. code-block:: python

    avl.Factory.set_variable("*.agent.mwdrv.max_outstanding", 16)

.. literalinclude:: ../../../examples/axi/axi5-max-outstanding/cocotb/example.py
    :language: python

.. note::

    :any:`allow_early_data <avl_axi._mwdriver.ManagerWriteDriver.allow_early_data>` and :any:`max_outstanding <avl_axi._driver.Driver.max_outstanding>` are mutually exclusive

.. _idunq:

Unique Indices
~~~~~~~~~~~~~~

The :any:`ManagerWriteDriver` and :any:`ManagerReadDriver` both support the Unique_ID_Support \
parameter. This ensures that only one transaction of a given id (awid or arid) can be outstanding on the bus at any given time. This is enabled via the RTL interface.

.. literalinclude:: ../../../examples/axi/axi5-idunq/cocotb/example.py
    :language: python
