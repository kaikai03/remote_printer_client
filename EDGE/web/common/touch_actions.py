# Licensed to the Software Freedom Conservancy (SFC) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The SFC licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.


from EDGE.web.remote.command import Command


class TouchActions(object):
    def __init__(self, driver):
        
        self._driver = driver
        self._actions = []

    def perform(self):
        
        for action in self._actions:
            action()

    def tap(self, on_element):
        
        self._actions.append(lambda: self._driver.execute(
            Command.SINGLE_TAP, {'element': on_element.id}))
        return self

    def double_tap(self, on_element):
        
        self._actions.append(lambda: self._driver.execute(
            Command.DOUBLE_TAP, {'element': on_element.id}))
        return self

    def tap_and_hold(self, xcoord, ycoord):
        
        self._actions.append(lambda: self._driver.execute(
            Command.TOUCH_DOWN, {
                'x': int(xcoord),
                'y': int(ycoord)}))
        return self

    def move(self, xcoord, ycoord):
        
        self._actions.append(lambda: self._driver.execute(
            Command.TOUCH_MOVE, {
                'x': int(xcoord),
                'y': int(ycoord)}))
        return self

    def release(self, xcoord, ycoord):
        
        self._actions.append(lambda: self._driver.execute(
            Command.TOUCH_UP, {
                'x': int(xcoord),
                'y': int(ycoord)}))
        return self

    def scroll(self, xoffset, yoffset):
        
        self._actions.append(lambda: self._driver.execute(
            Command.TOUCH_SCROLL, {
                'xoffset': int(xoffset),
                'yoffset': int(yoffset)}))
        return self

    def scroll_from_element(self, on_element, xoffset, yoffset):
        
        self._actions.append(lambda: self._driver.execute(
            Command.TOUCH_SCROLL, {
                'element': on_element.id,
                'xoffset': int(xoffset),
                'yoffset': int(yoffset)}))
        return self

    def long_press(self, on_element):
        
        self._actions.append(lambda: self._driver.execute(
            Command.LONG_PRESS, {'element': on_element.id}))
        return self

    def flick(self, xspeed, yspeed):
        
        self._actions.append(lambda: self._driver.execute(
            Command.FLICK, {
                'xspeed': int(xspeed),
                'yspeed': int(yspeed)}))
        return self

    def flick_element(self, on_element, xoffset, yoffset, speed):
        
        self._actions.append(lambda: self._driver.execute(
            Command.FLICK, {
                'element': on_element.id,
                'xoffset': int(xoffset),
                'yoffset': int(yoffset),
                'speed': int(speed)}))
        return self

    # Context manager so TouchActions can be used in a 'with .. as' statements.
    def __enter__(self):
        return self  # Return created instance of self.

    def __exit__(self, _type, _value, _traceback):
        pass  # Do nothing, does not require additional cleanup.
