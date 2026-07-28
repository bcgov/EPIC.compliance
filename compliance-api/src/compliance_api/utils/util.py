# Copyright © 2024 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utility helpers shared across the API."""

import os
import re


def allowedorigins():
    """Return allowed origin."""
    _allowedcors = os.getenv("CORS_ORIGIN")
    allowedcors = []
    if _allowedcors and "," in _allowedcors:
        for entry in re.split(",", _allowedcors):
            allowedcors.append(entry)
    return allowedcors


class Singleton(type):
    """Singleton meta."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Call for meta."""
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def get_sorted_numbers_from_generated_code(codes: list[str], replace):
    """Return sorted numbers from the generated codes."""
    existing = sorted([int(r[0].split("_")[-1].replace(replace, "")) for r in codes])
    expected = 1
    for num in existing:
        if num != expected:
            return expected
        expected += 1

    return expected
