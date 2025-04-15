#!/usr/bin/env python3

import json
import re
import unittest

import yaml

from docker_rate_limit_check.docker_rate_limit import DockerRateLimit
from docker_rate_limit_check.output_format import RateLimitOutputFormat


class TestDockerRateLimit(unittest.TestCase):
    def setUp(self) -> None:
        self.rate_limit = DockerRateLimit(rate_limit_max=300, rate_limit_remaining=20)

    def test_asdict(self) -> None:
        expected_dict = {
            'rate_limit_max': 300,
            'rate_limit_remaining': 20,
            'identifier': None,
            'rate_limit_used': 280
        }
        self.assertEqual(self.rate_limit.asdict(), expected_dict)

    def test_to_output_format(self) -> None:
        self.assertEqual(
            self.rate_limit.to_json(),
            self.rate_limit.to_output_format(RateLimitOutputFormat.JSON))
        self.assertEqual(
            self.rate_limit.to_prometheus(),
            self.rate_limit.to_output_format(RateLimitOutputFormat.PROMETHEUS))
        self.assertEqual(
            self.rate_limit.to_yaml(),
            self.rate_limit.to_output_format(RateLimitOutputFormat.YAML))

    def test_to_json(self) -> None:
        expected_dict = {
            'rate_limit_max': 300,
            'rate_limit_remaining': 20,
            'identifier': None,
            'rate_limit_used': 280
        }
        self.assertEqual(json.loads(self.rate_limit.to_json()), expected_dict)

    def test_to_prometheus(self) -> None:
        # Regular expressions to match HELP and metric lines
        help_pattern = re.compile(r'^# HELP .*$')
        metric_pattern = re.compile(r'^([-_A-Za-z0-9]*){(.*)} ([0-9]*)')

        output = self.rate_limit.to_prometheus()

        # Check that every metric line has a HELP line
        for i, line in enumerate(output.split('\n')):
            if i % 2 == 0:
                self.assertTrue(help_pattern.match(line))
            else:
                self.assertTrue(metric_pattern.match(line))

        # Check that the expected metrics are present with correct values
        expected_metrics = [
            'docker_hub_rate_limit_max{identifier="None"} 300',
            'docker_hub_rate_limit_remaining{identifier="None"} 20',
            'docker_hub_rate_limit_used{identifier="None"} 280'
        ]
        metrics = [line for i, line in enumerate(output.split('\n')) if i % 2 == 1]

        for expected_metric in expected_metrics:
            self.assertIn(expected_metric, metrics)

    def test_to_yaml(self) -> None:
        expected_dict = {
            'rate_limit_max': 300,
            'rate_limit_remaining': 20,
            'identifier': None,
            'rate_limit_used': 280
        }
        self.assertEqual(yaml.safe_load(self.rate_limit.to_yaml()), expected_dict)
