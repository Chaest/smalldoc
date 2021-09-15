# Copyright 2021 Jean-Pascal Thiery
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Part of the parser dedicated to class parsing.
"""
import inspect

from .utils import _sorted_by_name, _is_to_be_shown
from .function_parser import _parse_function


def _parse_class(class_to_parse, show_private=False) -> dict:
    classe = class_to_parse[1]
    doc = inspect.getdoc(classe)
    return {
        'name': class_to_parse[0],
        'doc': doc.strip() if doc else '',
        'functions': _sorted_by_name([
            _parse_function(function)
            for function in inspect.getmembers(classe, inspect.isfunction)
            if _is_to_be_shown(function[0], show_private)
        ]),
        'classes': _sorted_by_name([
            _parse_class(nested)
            for nested in inspect.getmembers(classe, inspect.isclass)
            if nested[0] != "__class__"
            and _is_to_be_shown(nested[0], show_private)
        ])
    }