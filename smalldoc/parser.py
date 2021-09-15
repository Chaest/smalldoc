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
Parser read your module then extract data from source code and your docstring to build a dict.
"""
import pydoc
import inspect
import sys
import os
import re
from os.path import isdir, exists
import logging

logger = logging.getLogger(__name__)


def parse(working_path: str, module_name: str, show_private=False) -> dict:
    """
    Parse your code and docstring then generate a dict with it.
    :param working_path: The working directory to fetch your module
    :param module_name: The name of the module you want to generate dict of your documentation
    :param show_private: If True, parser will navigate through your private methode. At False by default.
    :return: Dictionnary which contain metadata and doc.
    :rtype dict
    """
    logger.debug(f'loading path {working_path}')
    sys.path.append(working_path)
    try:
        mod = pydoc.safeimport(module_name)
        return _parse_module(mod, show_private) if mod is not None else None
    except pydoc.ErrorDuringImport as err:
        logger.error(f'Error while trying to load module {module_name}: {err}')
        raise pydoc.ErrorDuringImport from err


def _is_valid_module_name(module_name):
    return not module_name.startswith(('.', '__'))


def _sorted_by_name(items: list) -> list:
    return sorted(items, key=lambda item: item['name'])


def _is_to_be_shown(module_name: str, show_private: bool) -> bool:
    return not show_private and not module_name.startswith('_')


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


def _parse_function(function_to_parse) -> dict:
    function = function_to_parse[1]
    signature = inspect.signature(function)
    doc = inspect.getdoc(function)

    return {
        'name': function_to_parse[0],
        'parameters': _parse_function_args(function),
        'return': _parse_return_function(function),
        'def': f'def {function_to_parse[0]}{signature}',
        'doc': re.sub(r':\w.*((\n$)|$])?', '', doc) if doc else ''
    }


def _parse_function_args(function) -> list:
    args_spec = inspect.getfullargspec(function)

    docstr_args = {
        match['param']: match['description']
        for match in re.finditer(r':param\s*(?P<param>.*?):?\s+(?P<description>.*)', inspect.getdoc(function))
    }

    arguments = _sorted_by_name([
        {
            'name': arg,
            'type': args_spec.annotations[arg].__name__ if arg in args_spec.annotations else '',
            'doc': docstr_args.get(arg, '')
        }
        for arg in args_spec.args
    ])

    if args_spec.varargs:
        arguments.append({
            'name': f'*{args_spec.varargs}',
            'type': '',
            'doc': ''
        })
    if args_spec.varkw:
        arguments.append({
            'name': f'**{args_spec.varkw}',
            'type': '',
            'doc': ''
        })

    return arguments


def _parse_return_function(function) -> dict:
    doc = pydoc.getdoc(function)
    return {
        'type': _extract_from_doc('rtype', doc) if _no_annotation_return(function) else _annotation_return_type(function),
        'doc': _extract_from_doc('return', doc)
    }


def _extract_from_doc(element: str, doc: str) -> str:
    match = re.search(rf':{element}:?\s+(.*)', doc)
    return match.group(1).strip() if match else ''


def _no_annotation_return(function):
    return inspect.signature(function).return_annotation  == inspect.Signature.empty


def _annotation_return_type(function):
    return inspect.signature(function).return_annotation.__name__
