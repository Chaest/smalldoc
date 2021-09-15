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
Part of the parser dedicated to module parsing.
"""
import sys
import os
import inspect
import pydoc

from os.path import isdir, exists

from .utils import _sorted_by_name, _is_to_be_shown
from .class_parser import _parse_class
from .function_parser import _parse_function

def _parse_module(module, show_private=False) -> dict:
    module_path = os.path.dirname(os.path.abspath(module.__file__))
    sub_modules = _get_valid_sub_modules(module_path)

    for sub_module_path in sub_modules:
        sys.path.append(f'{module_path}/{sub_module_path}')

    return {
        'name': module.__name__,
        'description': module.__doc__.strip(),
        'functions': _sorted_by_name([
            _parse_function(function)
            for function in inspect.getmembers(module, inspect.isfunction)
            if _is_to_be_shown(function[0], show_private)
        ]),
        'classes': _sorted_by_name([
            _parse_class(classe, show_private)
            for classe in inspect.getmembers(module, inspect.isclass)
            if _is_to_be_shown(classe[0], show_private)
        ]),
        'modules': _sorted_by_name([
            _parse_module(pydoc.safeimport(f'{module.__name__}.{sub_module_path}'))
            for sub_module_path in sub_modules
        ])
    }


def _is_valid_module_name(module_name):
    return not module_name.startswith(('.', '__'))


def _is_valid_sub_module(module_path: str, sub_module_path: str) -> bool:
    full_path = f'{module_path}/{sub_module_path}'
    return all((
        isdir(full_path),
        _is_valid_module_name(sub_module_path),
        exists(f'{full_path}/__init__.py')
    ))


def _get_valid_sub_modules(module_path: str) -> list:
    return [
        sub_module_path
        for sub_module_path in os.listdir(module_path)
        if _is_valid_sub_module(module_path, sub_module_path)
    ]