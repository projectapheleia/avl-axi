# Copyright 2025 Apheleia
#
# Description:
# Apheleia Verification Library Agent Configuration

import avl


class AgentCfg(avl.Object):

    def __init__(self, name: str, parent: avl.Component) -> None:
        """
        Initialize the avl-apb Agent Configuration

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
__all__ = ["AgentCfg"]
