#!/usr/bin/env python3

import json
import re
import sys
import unittest
from io import StringIO
from unittest.mock import patch

from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

import yaml

import docker_rate_limit_check.__main__


class TestCliQuery(unittest.TestCase):
    def helper_test_query_dict(self, data: Dict[str, Any]) -> None:
        """
        Helper function to check the content of the query output.
        """

        expected_keys = [
            ('rate_limit_max', int),
            ('rate_limit_remaining', int),
            ('rate_limit_used', int),
            ('identifier', str)
        ]

        # Check all expected keys are present
        for tup in expected_keys:
            self.assertIn(tup[0], data, f'Missing "{tup[0]}" in JSON output')

        # Check that there are no unexpected keys
        for key in data:
            self.assertIn(
                key,
                [k[0] for k in expected_keys],
                f'Unexpected "{key}" in JSON output')

        # Check all expected keys are of the correct type
        for tup in expected_keys:
            self.assertIsInstance(
                data[tup[0]],
                tup[1],
                f'"{tup[0]}" in JSON output is not of type {tup[1]}')

    def helper_execute_cli(self, argv: List[str]) -> Tuple[int, str]:
        """
        Helper function to execute the CLI and capture the output.

        :param argv: List of command line arguments to pass to the CLI
        :return: Tuple containing the exit code and the captured output
        """

        # Create mock exit function to capture the exit code
        # and prevent the program from exiting
        exit_code = 0
        def mock_exit(exit_code: int) -> None:
             exit_code = exit_code

        # Patch sys.argv to simulate command line arguments
        # Patch sys.exit to capture the exit code
        # Patch sys.stdout to capture the output
        with patch.object(sys, 'argv', argv), \
             patch.object(sys, 'exit', mock_exit), \
             patch('sys.stdout', StringIO()) as mock_stdout:
                docker_rate_limit_check.__main__.main()

        return exit_code, mock_stdout.getvalue()

    def test_cli_query_json(self) -> None:
        argv = ['docker_rate_limit_check', 'query', '--format', 'json']
        exit_code, stdout = self.helper_execute_cli(argv)

        # Check the exit code
        self.assertEqual(exit_code, 0, 'Exit code is not 0')

        # Parse the JSON output
        try:
            stdout_dict = json.loads(stdout)
        except:  # noqa: E722
            self.fail(f'Output:\n\n{stdout}\n\nFailed to parse output as JSON')

        # Check the content of the output
        self.helper_test_query_dict(stdout_dict)

    def test_cli_query_yaml(self) -> None:
        argv = ['docker_rate_limit_check', 'query', '--format', 'yaml']
        exit_code, stdout = self.helper_execute_cli(argv)

        # Check the exit code
        self.assertEqual(exit_code, 0, 'Exit code is not 0')

        # Parse the YAML output
        try:
            stdout_dict = yaml.safe_load(stdout)
        except:  # noqa: E722
            self.fail(f'Output:\n\n{stdout}\n\nFailed to parse output as YAML')

        # Check the content of the output
        self.helper_test_query_dict(stdout_dict)

    def test_cli_query_prometheus(self) -> None:
        argv = ['docker_rate_limit_check', 'query', '--format', 'prometheus']
        exit_code, stdout = self.helper_execute_cli(argv)

        # Check the exit code
        self.assertEqual(exit_code, 0, 'Exit code is not 0')

        # Regular expressions to match HELP and metric lines
        help_pattern = re.compile(r'^# HELP .*$')
        metric_pattern = re.compile(r'^([-_A-Za-z0-9]*){(.*)} ([0-9]*)')

        # Split the output into lines
        lines = stdout.split('\n')
        lines = [line for line in lines if line.strip() != '']


        # Check that we have at least one line output
        self.assertGreater(
            len(lines),
            0,
            'No output when querying for Prometheus output')


        # Check that every metric line has a HELP line
        for i, line in enumerate(lines):
            if i % 2 == 0:
                self.assertTrue(help_pattern.match(line))
            else:
                self.assertTrue(metric_pattern.match(line))


        # Check that all "identifier" labels in metrics are the same
        metric_lines = [line for i, line in enumerate(lines) if i % 2 == 1]
        metric_labels = []

        for line in metric_lines:
            match = metric_pattern.match(line)
            self.assertIsNotNone(
                match,
                f'Prometheus metric line did not match metric pattern: {line}')
            assert match is not None  # for type checkers

            metric_labels.append(match.group(2))

        for i in range(1, len(metric_labels)):
            self.assertEqual(
                metric_labels[i],
                metric_labels[0],
                'Identifiers in metric lines do not match')


        # Check that identifier has correct type
        metric_label = metric_labels[0]
        self.assertIsNotNone(re.match(r'identifier="(.*)"', metric_label))


        # Check that exactly the expected metrics are present
        expected_metrics = [
            'docker_hub_rate_limit_max',
            'docker_hub_rate_limit_remaining',
            'docker_hub_rate_limit_used'
        ]
        found_metrics = []
        for line in metric_lines:
            match = metric_pattern.match(line)
            self.assertIsNotNone(
                match,
                f'Prometheus metric line did not match metric pattern: {line}')
            assert match is not None  # for type checkers

            found_metrics.append(match.group(1))

        self.assertEqual(
            sorted(expected_metrics),
            sorted(found_metrics))
