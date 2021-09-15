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

import os
import logging

import smalldoc

WORKING_DIR = f'{os.path.dirname(__file__)}/data'
MODULE_NAME = 'fakemodule'

logger = logging.getLogger(__name__)

def test_write_doc():
    parsed_module = smalldoc.parse(WORKING_DIR, MODULE_NAME)
    result = smalldoc.write(parsed_module)
    logger.debug(result)
