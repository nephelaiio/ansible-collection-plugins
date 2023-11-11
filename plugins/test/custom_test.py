"""
This module provides utility functions for testing network properties and regex patterns in given records.

Functions:
    test_network(record=None, net="0.0.0.0/0", prop="ansible_host"):
        Tests if an IP address in a given record falls within a specified network range.

    test_property(record=None, regex=".*", prop=""):
        Tests if the value of a specified property in a given record matches a regular expression.

Classes:
    TestModule:
        Contains methods related to testing, encapsulating the test functions for easy access and organization.

The module uses the 'netaddr' library to handle network address calculations and 're' for regex pattern matching.
It is designed to provide simple and flexible testing utilities that can be integrated into larger systems or used
for quick checks and validations of network configurations or data records.

Note:
    The module disables the 'line-too-long' pylint warning to accommodate longer lines, typically URLs or detailed
    explanations in docstrings, without compromising readability.

Example Usage:
    - Use 'test_network' to check if an IP address within a data record falls under a given CIDR network.
    - Use 'test_property' to validate if a certain field in a data record matches a specified regex pattern.
    - 'TestModule' class can be instantiated to access these testing functions in a structured manner.
"""

import re

from netaddr import IPAddress, IPNetwork


def test_network(record=None, net="0.0.0.0/0", prop="ansible_host"):
    """
    Tests if the IP address in a given record falls within a specified network range.

    Args:
        record (dict, optional): The record containing the IP address to test. If None, the function returns None. Defaults to None.
        net (str, optional): The network range in CIDR notation to test the IP address against. Defaults to "0.0.0.0/0" (all IPs).
        prop (str, optional): The key in the record dict that holds the IP address. Defaults to "ansible_host".

    Returns:
        dict or None: The original record if its IP address falls within the specified network range, None otherwise.
    """

    if record and prop in record:
        if IPAddress(record[prop]) in IPNetwork(net):
            return record
    return None


def test_property(record=None, regex=".*", prop=""):
    """
    Tests if the value of a specified property in a given record matches a regular expression.

    Args:
        record (dict, optional): The record containing the property to test. If None, the function returns None. Defaults to None.
        regex (str, optional): The regular expression to test the property's value against. Defaults to ".*" (matches anything).
        prop (str, optional): The key in the record dict that holds the property value. Defaults to an empty string.

    Returns:
        dict or None: The original record if the property's value matches the regex, None otherwise.
    """

    if record and prop in record:
        if re.match(regex, record[prop]):
            return record
    return None


class TestModule():
    """
    A class encapsulating test functions related to network and property validations.

    This class is designed to organize and provide access to various test functions. It acts as a container for
    methods that execute specific tests, such as checking network addresses or matching regex patterns in data records.

    Methods:
        tests(): Returns a dictionary mapping test function names to their respective function objects.
    """

    def tests(self):
        """
        Retrieves the test functions available in this module.

        This method returns a dictionary where keys are the names of the test functions and values are the
        function objects themselves. This is useful for dynamically accessing and calling test functions.

        Returns:
            dict: A dictionary mapping the names of test functions ('test_network', 'test_property') to the actual function objects.
        """

        return {"test_network": test_network, "test_property": test_property}
