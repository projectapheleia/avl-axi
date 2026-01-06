.. _item:

.. inheritance-diagram:: avl_axi._item
    :parts: 1

AVL-AXI Item
=============

Due to the inherent independence of reads and writes the :any:`SequenceItem` is split into :any:`WriteItem` and :any:`ReadItem`.

All System parameters are inherited from the interface but marked as "hidden" (prefixed and suffixed with "_"). This provides the full context \
for any additional functionality to be implemented without additional hook. (e.g. custom checks or coverage).

Only payload signals are included in the items. Protocol signals such as valid and ready are explicitly driven and observed buy the drivers and \
monitors respectively.

Due to the number of sidebands and combinations of parameters, the item variables are assigned in loops defined in :any:`avl_axi._signals`.

Items string formats are transposed by default to make the display more human readable:

.. code-block:: shell

    +-----------+------+--------+-------+--------+---------+-------------+--------------------+-------+-----+----------------+-------+-----+-------+----------------+---------------+---------------+
    | name      | awid | awaddr | awlen | awsize | awburst | awatop      | wdata              | wstrb | rid | rdata          | rresp | bid | bresp | aw_wait_cycles | w_wait_cycles | b_wait_cycles |
    +-----------+------+--------+-------+--------+---------+-------------+--------------------+-------+-----+----------------+-------+-----+-------+----------------+---------------+---------------+
    | from_mseq | 0x1  | 0x1000 | 0x0   | 0x3    | FIXED   | LOAD_LE_CLR | 0xffff00000000ffff | 0x0   | 0x1 | 0xffffffffffff | OKAY  | 0x1 | OKAY  | 0              | 0             | 0             |
    +-----------+------+--------+-------+--------+---------+-------------+--------------------+-------+-----+----------------+-------+-----+-------+----------------+---------------+---------------+


    +-----------+------+--------+-------+--------+---------+-------------+-------+-------+-----+--------+-------+-----+-------+----------------+---------------+---------------+
    | name      | awid | awaddr | awlen | awsize | awburst | awatop      | wdata | wstrb | rid | rdata  | rresp | bid | bresp | aw_wait_cycles | w_wait_cycles | b_wait_cycles |
    +-----------+------+--------+-------+--------+---------+-------------+-------+-------+-----+--------+-------+-----+-------+----------------+---------------+---------------+
    | from_mseq | 0x3  | 0x1000 | 0x7   | 0x3    | INCR    | LOAD_LE_SET | 0x1   | 0x0   | 0x3 | 0xaa00 | OKAY  | 0x3 | OKAY  | 0              | 0             | 0             |
    |           |      |        |       |        |         |             | 0x2   | 0x0   | 0x3 | 0xaa00 | OKAY  |     |       |                | 0             |               |
    |           |      |        |       |        |         |             | 0x3   | 0x0   | 0x3 | 0xaa00 | OKAY  |     |       |                | 0             |               |
    |           |      |        |       |        |         |             | 0x4   | 0x0   | 0x3 | 0xaa00 | OKAY  |     |       |                | 0             |               |
    |           |      |        |       |        |         |             | 0x5   | 0x0   | 0x3 | 0xaa00 | OKAY  |     |       |                | 0             |               |
    |           |      |        |       |        |         |             | 0x6   | 0x0   | 0x3 | 0xaa00 | OKAY  |     |       |                | 0             |               |
    |           |      |        |       |        |         |             | 0x7   | 0x0   | 0x3 | 0xaa00 | OKAY  |     |       |                | 0             |               |
    |           |      |        |       |        |         |             | 0x8   | 0x0   | 0x3 | 0xaa00 | OKAY  |     |       |                | 0             |               |
    +-----------+------+--------+-------+--------+---------+-------------+-------+-------+-----+--------+-------+-----+-------+----------------+---------------+---------------+

Set / Get Functions
-------------------

Due to the configurable nature of the interface the user should use the :any:`SequenceItem.set` and :any:`SequenceItem.get` functions. These handle access to the underlying \
value while safely ignoring / providing defaults for missing fields. This allows the user to safely code generic functions without having to constantly check the parameters of \
the given interface.

Enumerations
------------

AVL ENUMs are not used for the enumerated types in AVL-AXI. This is due to the configurability of the width in many cases. Certain parameters add additional values \
to a given enum. As such enums in :any:`avl_axi._types` are implemented as Logic variables with custom fmt and values functions. Class variables are also present to make for \
easy export.

By default the most complete enum is the default, but fields are removed by width constraints.

Randomization
-------------

Where possible AVL `Z3 <https://microsoft.github.io/z3guide/programming/Z3%20Python%20-%20Readonly/Introduction/>`_ are added to the enum :any:`avl_axi._types` \
and :any:`SequenceItem` to ensure legal values are generated.

Any enum value marked as "RESERVED" should be excluded in randomization by default, however these constraints can be removed using the remove_constraint function in the item \
or variable.

Resize
------

By default items contain `defaultdicts <https://docs.python.org/3/library/collections.html#collections.defaultdict>`_ for all W and R payloads. A :any:`SequenceItem.resize` function is \
provided to pad any remaining data based on awlen / arlen.\
This function is called automatically in the :any:`SequenceItem.post_randomize` function or by the sequence when directed stimulus is used.

`defaultdicts <https://docs.python.org/3/library/collections.html#collections.defaultdict>`_ have been used for performance. The overhead of creating the 256 beats worth of data is high. \
The monitors naturally populate all beats with the correct payloads. This is checked using the :any:`SequenceItem.sanity` function, called before the monitor exports the item. :any:`SequenceItem.resize` is \
called as part of the sequence to fully populate the remaining data in both the randomized and directed sequences.

The downside is that the data contained in the W and R phases are now dicts / arrays indexed by position. However, the :any:`ManagerSequence.write` and :any:`ManagerSequence.read` functions allow these to be defined as \
dicts or lists for the users convenience.

Comparison functions remain unchanged.

Should the user which to limit the number of beats in a transaction, standard constraints are usable:

.. code-block:: python

    # Constraint Writes
    self.add_constraint("c_custom_write", lambda x : ULE(x, 8), self.awlen)

    # Constrain Reads
    self.add_constraint("c_custom_read", lambda x : ULE(x, 8), self.arlen)


Sanity
------

A :any:`SequenceItem.sanity` function is provided to ensure and intra item constraints are kept. For example arid and rid must match within a single item.
This function is called by the :any:`WriteMonitor` and :any:`ReadMonitor` when the transaction response phase is completed.

.. _regular_transactions_only:

Regular Transactions Only
-------------------------

One possible configuration option is to limit the AXI bus to issue only regular transactions. This is a limited range of lengths, sizes and burst types.

The :any:`SequenceItem` supports this function using both constraints and the :any:`SequenceItem.post_randomize` function. Address alignment is handled in :any:`SequenceItem.post_randomize` \
for simplicity and performance consideration

.. _fixed_burst_disable:

Fixed Burst Disable
-------------------

Another possible configuration prevents ths AXI bus issuing FIXED burst types. This is handled automatically with constraints and sanity checks.

.. _max_transaction_bytes:

Max Transaction Bytes
---------------------

All AXI interfaces have a maximum number of transaction bytes. This defaults to 4096. This is handled automatically with constraints and sanity checks.
