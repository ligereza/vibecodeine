import argparse
from abc import ABC, abstractmethod
import subprocess
import json
import os

class Executor(ABC):
    @abstractmethod
    def run_command(self, command):
        pass

class RealExecutor(Executor):
    def run_command(self, command):
        return subprocess.run(command)

class DryExecutor(Executor):
    def __init__(self):
        self.logged_commands = []

    def run_command(self, command):
        self.logged_commands.append(command)
