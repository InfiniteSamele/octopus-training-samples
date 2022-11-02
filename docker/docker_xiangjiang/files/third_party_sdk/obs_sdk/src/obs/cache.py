#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Copyright 2019 Huawei Technologies Co.,Ltd.
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License.  You may obtain a copy of the
# License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations under the License.

import weakref, collections
import time


class _LocalCacheThread(object):
    class Dict(dict):
        def __del__(self):
            pass

    def __init__(self, maxlen=10):
        self.weak = weakref.WeakValueDictionary()
        self.strong = collections.deque(maxlen=maxlen)

    @staticmethod
    def nowTime():
        return int(time.time())

    def get(self, key):
        value = self.weak.get(key)
        if value is not None and hasattr(value, 'expire') and self.nowTime() > value['expire']:
            value = None
        return value

    def set(self, key, value):
        self.weak[key] = strongRef = self.Dict(value)
        self.strong.append(strongRef)
         
class _LocalCacheProcess(object):

    def __init__(self, maxlen=10):
        import multiprocessing, atexit
        self._mgr = multiprocessing.Manager() 
        self.weak = self._mgr.dict()
        atexit.register(self.close)

    @staticmethod
    def nowTime():
        return int(time.time())

    def get(self, key):
        value = self.weak.get(key)
        if value is not None and hasattr(value, 'expire') and self.nowTime() > value['expire']:
            del self.weak[key]
            value = None
        return value

    def set(self, key, value):
        self.weak[key] = value
        
    def close(self):
        if self._mgr:
            try:
                self._mgr.shutdown()
                self._mgr = None
            except:
                pass
        
        
LocalCache = _LocalCacheThread