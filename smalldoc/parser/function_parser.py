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
Part of the parser dedicated to function parsing.
"""
import re
import pydoc
import inspect

from .utils import _sorted_by_name

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
