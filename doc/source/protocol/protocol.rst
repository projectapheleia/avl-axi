.. _protocol:

Protocol Support
================

AVL-AXI is based on the AXI5 specification. ARM no longer refer to AXI3 or AXI4, rather preferring a matrix of options and paramaters.

AVL-AXI has followed the naming convention for these where possible.

For full details see `AXI Documentation <https://developer.arm.com/documentation/ihi0022/k/?lang=en>`_.

Where signals are indicated as supported as sideband, the signals / fields can be added to the protocol, but apart from allowing assignment \
and randomization as correctly sized logic buses there is no additional capability.

These signals should not effect the protocol and aren't modelled in any of the provided Manager or Subordinate components. They are, however, \
captured by the monitors and included in trace files.

Features / Configuration
------------------------
+----------------------------------------+-----------+
| Parameter Name                         | Supported |
+========================================+===========+
| :ref:`Atomic_Transactions              | YES       |
| <smemory>`                             |           |
+----------------------------------------+-----------+
| BURST_Present                          | YES       |
+----------------------------------------+-----------+
| Busy_Support                           | SIDEBAND  |
+----------------------------------------+-----------+
| CACHE_Present                          | SIDEBAND  |
+----------------------------------------+-----------+
| Cache_Line_Size                        | SIDEBAND  |
+----------------------------------------+-----------+
| Cache_Stash_Transactions               | SIDEBAND  |
+----------------------------------------+-----------+
| Check_Type                             | NO        |
+----------------------------------------+-----------+
| CMO_On_Read                            | SIDEBAND  |
+----------------------------------------+-----------+
| CMO_On_Write                           | SIDEBAND  |
+----------------------------------------+-----------+
| Coherency_Connection_Signals           | NO        |
+----------------------------------------+-----------+
| :ref:`Consistent_DECERR                | YES       |
| <consistent_decerr>`                   |           |
+----------------------------------------+-----------+
| DeAllocation_Transactions              | SIDEBAND  |
+----------------------------------------+-----------+
| Device_Normal_Independence             | NO        |
+----------------------------------------+-----------+
| DVM_Message_Support                    | NO        |
+----------------------------------------+-----------+
| DVM_v8                                 | NO        |
+----------------------------------------+-----------+
| DVM_v8_1                               | NO        |
+----------------------------------------+-----------+
| DVM_v8_4                               | NO        |
+----------------------------------------+-----------+
| DVM_v9_2                               | NO        |
+----------------------------------------+-----------+
| :ref:`Exclusive_Accesses               | YES       |
| <emonitor>`                            |           |
+----------------------------------------+-----------+
| :ref:`Fixed_Burst_Disable              | YES       |
| <fixed_burst_disable>`                 |           |
+----------------------------------------+-----------+
| InvalidateHint_Transaction             | SIDEBAND  |
+----------------------------------------+-----------+
| LEN_Present                            | YES       |
+----------------------------------------+-----------+
| Loopback_Signals                       | YES       |
+----------------------------------------+-----------+
| :ref:`Max_Transaction_Bytes            | YES       |
| <max_transaction_bytes>`               |           |
+----------------------------------------+-----------+
| MEC_Support                            | SIDEBAND  |
+----------------------------------------+-----------+
| MMUFLOW_Present                        | SIDEBAND  |
+----------------------------------------+-----------+
| MPAM_Support                           | SIDEBAND  |
+----------------------------------------+-----------+
| MTE_Support                            | NO        |
+----------------------------------------+-----------+
| Multi_Copy_Atomicity                   | SIDEBAND  |
+----------------------------------------+-----------+
| NSAccess_Identifiers                   | SIDEBAND  |
+----------------------------------------+-----------+
| :ref:`Ordered_Write_Observation        | YES       |
| <ordered_write_observation>`           |           |
+----------------------------------------+-----------+
| PBHA_Support                           | SIDEBAND  |
+----------------------------------------+-----------+
| Persist_CMO                            | SIDEBAND  |
+----------------------------------------+-----------+
| Poison                                 | SIDEBAND  |
+----------------------------------------+-----------+
| Prefetch_Transaction                   | SIDEBAND  |
+----------------------------------------+-----------+
| PROT_Present                           | SIDEBAND  |
+----------------------------------------+-----------+
| :ref:`QoS_Accept                       | YES       |
| <qosaccept>`                           |           |
+----------------------------------------+-----------+
| QOS_Present                            | SIDEBAND  |
+----------------------------------------+-----------+
| Read_Data_Chunking                     | NO        |
+----------------------------------------+-----------+
| :ref:`Read_Interleaving_Disabled       | YES       |
| <read_interleaving_disabled>`          |           |
+----------------------------------------+-----------+
| REGION_Present                         | SIDEBAND  |
+----------------------------------------+-----------+
| :ref:`Regular_Transactions_Only        | YES       |
| <regular_transactions_only>`           |           |
+----------------------------------------+-----------+
| RLAST_Present                          | YES       |
+----------------------------------------+-----------+
| RME_Support                            | SIDEBAND  |
+----------------------------------------+-----------+
| Shareable_Cache_Support                | SIDEBAND  |
+----------------------------------------+-----------+
| Shareable_Transactions                 | SIDEBAND  |
+----------------------------------------+-----------+
| SIZE_Present                           | YES       |
+----------------------------------------+-----------+
| STASHLPID_Present                      | SIDEBAND  |
+----------------------------------------+-----------+
| STASHNID_Present                       | SIDEBAND  |
+----------------------------------------+-----------+
| Trace_Signals                          | SIDEBAND  |
+----------------------------------------+-----------+
| :ref:`Unique_ID_Support <idunq>`       | YES       |
+----------------------------------------+-----------+
| UnstashTranslation_Transaction         | SIDEBAND  |
+----------------------------------------+-----------+
| Untranslated_Transactions              | SIDEBAND  |
+----------------------------------------+-----------+
| :ref:`Wakeup_Signals <wakeup>`         | YES       |
+----------------------------------------+-----------+
| WLAST_Present                          | YES       |
+----------------------------------------+-----------+
| Write_Plus_CMO                         | SIDEBAND  |
+----------------------------------------+-----------+
| WriteDeferrable_Transaction            | SIDEBAND  |
+----------------------------------------+-----------+
| WriteNoSnoopFull_Transaction           | SIDEBAND  |
+----------------------------------------+-----------+
| WriteZero_Transaction                  | SIDEBAND  |
+----------------------------------------+-----------+
| WSTRB_Present                          | SIDEBAND  |
+----------------------------------------+-----------+



.. note::

    \*SIDEBAND indicates driver and checks that values are consistent between request and response.
