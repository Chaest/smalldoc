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
Main parsing methods.
"""
import sys
import pydoc
import logging

from .module_parser import _parse_module

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








