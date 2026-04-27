"""
Vexa Test Library

A comprehensive testing library for the Vexa client that provides:
- TestSuite class for managing multiple users and bots
- Bot class for individual bot operations
- Random user-meeting mapping functionality
- Background monitoring capabilities
"""

from bot import Bot
from test_suite import TestSuite

__all__ = ['TestSuite', 'Bot']
