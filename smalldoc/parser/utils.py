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
Utilities for all parts of the parser module.
"""
def _sorted_by_name(items: list) -> list:
    return sorted(items, key=lambda item: item['name'])


def _is_to_be_shown(module_name: str, show_private: bool) -> bool:
    return not show_private and not module_name.startswith('_')