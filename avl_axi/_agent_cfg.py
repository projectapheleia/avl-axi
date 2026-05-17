# Copyright 2025 Apheleia
#
# Description:
# Apheleia Verification Library Agent Configuration

import avl


class AgentCfg(avl.Object):

    def __init__(self, name: str, parent: avl.Component) -> None:
        """
        Initialize the avl-axi Agent Configuration

        :param name: Name of the agent instance
        :type name: str
        :param parent: Parent component
        :type parent: Component
        """
        super().__init__(name, parent)

        # Agent Attributes
        self.has_manager = avl.Factory.get_variable(f"{self.get_full_name()}.has_manager", False)
        """Has Manager Driver"""
        self.has_subordinate = avl.Factory.get_variable(f"{self.get_full_name()}.has_subordinate", False)
        """Has Subordinate Driver"""
        self.has_monitor = avl.Factory.get_variable(f"{self.get_full_name()}.has_monitor", False)
        """Has Monitor Driver"""
        self.has_coverage = avl.Factory.get_variable(f"{self.get_full_name()}.has_coverage", False)
        """Has Functional Coverage"""
        self.has_bandwidth = avl.Factory.get_variable(f"{self.get_full_name()}.has_bandwidth", False)
        """Has Bandwidth Monitor"""
        self.has_trace = avl.Factory.get_variable(f"{self.get_full_name()}.has_trace", False)
        """Has Trace Generator"""
        self.subordinate_ranges = avl.Factory.get_variable(f"{self.get_full_name()}.subordinate_ranges", None)
        """Subordinate memory ranges"""
        self.narrow_transfer_lane_steering = avl.Factory.get_variable(f"{self.get_full_name()}.narrow_transfer_lane_steering", False)
        """When True, drivers place wdata/wstrb (and de-shift rdata) on the byte
        lanes mandated by AXI A3.2.3 / A3.4.1 for narrow transfers (transfers
        where 1<<awsize is smaller than the data bus). Enable when the agent's
        bus is wider than the awsize/arsize of the transactions being driven
        and the DUT depends on spec-compliant byte-lane placement (e.g. a
        downsizer). Leave False otherwise to preserve legacy behaviour."""
__all__ = ["AgentCfg"]
