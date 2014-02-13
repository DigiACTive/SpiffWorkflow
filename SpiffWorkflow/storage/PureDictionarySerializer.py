# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, print_function
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
from SpiffWorkflow.storage.DictionarySerializer import DictionarySerializer
from SpiffWorkflow.operators import Attrib, Assign
from SpiffWorkflow.specs import Join
import copy


class PureDictionarySerializer(DictionarySerializer):
    """A version of the DictionarySerializer that does not pickle anything."""
    
    def _serialize_dict(self, thedict):
        newdict = {}
        for key, value in thedict.items():
            newdict[key] = self._serialize_item(value)

        return newdict

    def _deserialize_dict(self, s_state):
        newdict = {}
        for key, value in s_state.items():
            newdict[key] = self._deserialize_item(value)

        return newdict

    def _serialize_list(self, thelist):
        return [self._serialize_item(item) for item in thelist]

    def _deserialize_list(self, s_state):
        return [self._deserialize_item(item) for item in s_state]

    def _serialize_item(self, item):
        if isinstance(item, Attrib):
            return {'__attrib__': self._serialize_attrib(item)}
        elif isinstance(item, Assign):
            return {'__assign__': self._serialize_assign(item)}
        return copy.deepcopy(item)

    def _deserialize_item(self, s_state):
        if isinstance(s_state, dict):
            if '__attrib__' in s_state:
                return self._deserialize_attrib(s_state['__attrib__'])
            elif '__assign__' in s_state:
                return self._deserialize_assign(s_state['__assign__'])
        return copy.deepcopy(s_state)

    def _serialize_assign(self, assign):
        return {'__assign__':
                {'left_attribute': assign.left_attribute,
                 'right_attribute': assign.right_attribute,
                 'right': assign.right}}

    def _deserialize_assign(self, s_state):
        return Assign(**s_state['__assign__'])

    # we override these as spec.threshold was being pickled
    def _serialize_join(self, spec):
        s_state = self._serialize_task_spec(spec)
        s_state['split_task'] = spec.split_task
        s_state['threshold'] = self._serialize_item(spec.threshold)
        s_state['cancel_remaining'] = spec.cancel_remaining
        return s_state

    def _deserialize_join(self, wf_spec, s_state):
        spec = Join(wf_spec,
                    s_state['name'],
                    split_task=s_state['split_task'],
                    threshold=self._deserialize_item(s_state['threshold']),
                    cancel=s_state['cancel_remaining'])
        self._deserialize_task_spec(wf_spec, s_state, spec=spec)
        return spec
