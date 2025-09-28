.. _agent:

AVL-AXI Agent
=============

.. inheritance-diagram:: avl_axi._agent_cfg
    :parts: 1

.. inheritance-diagram:: avl_axi._agent
    :parts: 1

Unlike many VIPs AVL-AXI does not contain an environment.

The AVL-AXI verification components is designed to be integrated easily into existing AVL environments, and \
as such an agent can be individually configured without a wider global environment.

The agent is composed of a manager and subordinate side, which can be used independently or together, and \
and number of non-directional passive components. To configure the agents, the user must override the :doc:`avl_axi.AgentCfg </modules/avl_axi._agent_cfg>` class. \
The best way to do this is via the factory:

.. image:: /images/agent.png

.. code-block:: python

    avl.Factory.set_variable("*.agent.cfg.has_manager", True)
    avl.Factory.set_variable("*.agent.cfg.has_subordinate", True)
    avl.Factory.set_variable("*.agent.cfg.has_monitor", True)

.. note::

    The :doc:`avl_axi.AgentCfg </modules/avl_axi._agent_cfg>` does not configure the AXI bus itself, only the agent. \
    The bus configuration is done via RTL interface (see :ref:`configuration` for more details.)

Sub-Components
--------------

.. toctree::
   :maxdepth: 1

   item
   manager
   subordinate
   monitor
   bandwidth
   coverage
   trace

