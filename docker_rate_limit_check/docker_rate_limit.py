#!/usr/bin/env python3

import json
from dataclasses import dataclass

from typing import Dict
from typing import Optional
from typing import Union

import yaml

from .output_format import RateLimitOutputFormat


@dataclass
class DockerRateLimit:
    """Contains information about Docker Hub rate limiting"""

    rate_limit_max: int
    rate_limit_remaining: int
    identifier: Optional[str]=None

    @property
    def rate_limit_used(self) -> int:  # pylint: disable=missing-function-docstring
        return self.rate_limit_max - self.rate_limit_remaining

    def asdict(self) -> Dict[str, Union[Optional[str], int]]:
        """
        Return attributes of this object as dictionary.

        :return: Dictionary representation of this object
        """

        attrs = [
            'rate_limit_max',
            'rate_limit_remaining',
            'identifier',
            'rate_limit_used'
        ]
        return {a: getattr(self, a) for a in attrs}

    def to_output_format(self, output_format: RateLimitOutputFormat) -> str:
        """
        Return attributes of this object in the requested format

        :param output_format: Format of output
        :return: Attributes of this object formatted in requested format
        """

        if output_format == RateLimitOutputFormat.JSON:
            return self.to_json()
        if output_format == RateLimitOutputFormat.YAML:
            return self.to_yaml()

        return None  # type: ignore

    def to_json(self, indent: int=4) -> str:
        """
        Return attributes of this object as JSON string

        :param indent: Number of spaces for indentation
        :return: JSON formatted string representation of this object
        """

        dict_representation = self.asdict()
        return json.dumps(dict_representation, indent=indent)

    def to_yaml(self) -> str:
        """
        Return attributes of this object as YAML string

        :return: YAML formatted string representation of this object
        """

        dict_representation = self.asdict()
        yaml_repr = yaml.safe_dump(dict_representation, explicit_start=True)
        yaml_repr = yaml_repr.strip()
        return yaml_repr
