# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, print_function
# Daniel Axtens. Copyright (C) DigiACTive Pty Ltd 2014
#
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
from SpiffWorkflow.storage.PureDictionarySerializer import \
    PureDictionarySerializer
from SpiffWorkflow.storage.Serializer import Serializer
from SpiffWorkflow import Task
try:
    import networkx as nx
except ImportError:
    import warnings
    warnings.warn("NetworkX not found. NetworkXSerializer will not work.")

try:
    unicode
except NameError:
    unicode = str

_dictserializer = PureDictionarySerializer()

_class_to_shape_mapping = {
    'SpiffWorkflow.specs.Simple.Simple': 'box',
    'SpiffWorkflow.specs.StartTask.StartTask': 'circle',
    'SpiffWorkflow.specs.ExclusiveChoice.ExclusiveChoice': 'diamond',
    'SpiffWorkflow.specs.Join.Join': 'box',
    'SpiffWorkflow.specs.MultiInstance.MultiInstance': 'diamond',
    'SpiffWorkflow.specs.MultiChoice.MultiChoice': 'diamond',
}

_class_to_shape_default = 'ellipse'

# if you wish to export to pygraphviz, these must be ASCII-encodable
_operators = {
    'SpiffWorkflow.operators.Equal': '=',
    'SpiffWorkflow.operators.NotEqual': '!=',
    'SpiffWorkflow.operators.LessThan': '<',
    'SpiffWorkflow.operators.GreaterThan': '>',
    'SpiffWorkflow.operators.Match': 'matches',
}

# http://www.graphviz.org/doc/info/colors.html
_state_to_colour_mapping = {
    Task.MAYBE: '#FFFFFF',
    Task.LIKELY: '#FFFFFF',
    Task.FUTURE: '#FFFFFF',
    Task.WAITING: '#FF0000',
    Task.READY: '#FF0000',
    Task.COMPLETED: '#CCCCCC',
    Task.CANCELLED: '#000000',
}

_state_to_text_colour_mapping = {
    Task.MAYBE: '#000000',
    Task.LIKELY: '#000000',
    Task.FUTURE: '#000000',
    Task.READY: '#000000',
    Task.COMPLETED: '#000000',
    Task.CANCELLED: '#FFFFFF'
}


class NetworkXSerializer(Serializer):
    def serialize_workflow_spec(self, wf_spec,
                                class_to_shape_mapping={},
                                class_to_shape_default=None,
                                **kwargs):
        class_to_shape_mapping = update_mapping_with(_class_to_shape_mapping,
                                                     class_to_shape_mapping)
        class_to_shape_default = class_to_shape_default or \
            _class_to_shape_default
        thedict = _dictserializer.serialize_workflow_spec(wf_spec, **kwargs)
        graph = nx.DiGraph()
        # add nodes
        for name, spec in thedict['task_specs'].items():
            label = name
            data = {'data': spec}
            if spec['class'] in class_to_shape_mapping:
                data['shape'] = class_to_shape_mapping[spec['class']]
            else:
                data['shape'] = class_to_shape_default

            if 'threshold' in spec:
                threshold = spec['threshold']
                plural = True
                if threshold is None:
                    threshold = 'all'
                elif isinstance(threshold, dict):
                    threshold = threshold['__attrib__']
                elif threshold == 1:
                    plural = False

                label += ('\nRequires competion of %s task' %
                          unicode(threshold)) + ('s.' if plural else '.')

            graph.add_node(name, data, label=label)

        # add edges
        for inname, task_spec in thedict['task_specs'].items():
            seen = []
            if 'context' in task_spec:
                if isinstance(task_spec['context'], list):
                    for outname in task_spec['context']:
                        graph.add_edge(inname, outname, style='dotted')
                else:
                    graph.add_edge(inname, task_spec['context'],
                                   style='dotted')
            if 'cond_task_specs' in task_spec:
                for operation, outname in task_spec['cond_task_specs']:
                    seen.append(outname)
                    operator, attribs = operation
                    if attribs is None:
                        label = ''
                    else:
                        label = ("%s %s %s" % (attribs[0][1],
                                               _operators[operator],
                                               attribs[1][1]))
                    graph.add_edge(inname, outname, label=label)

            if 'default_task_spec' in task_spec:
                outname = task_spec['default_task_spec']
                seen.append(outname)
                label = '(otherwise)'
                graph.add_edge(inname, outname, label=label)

            for outname in [x for x in task_spec['outputs'] if not x in seen]:
                graph.add_edge(inname, outname)
        return graph

    def deserialize_workflow_spec(self, s_state, **kwargs):
        raise NotImplementedError

    def serialize_workflow(self, workflow,
                           class_to_shape_mapping={},
                           class_to_shape_default=None,
                           state_to_colour_mapping={},
                           state_to_text_colour_mapping={},
                           by_name=True,  # or by UUID, which is closer to dump
                                          # but not very useful
                           **kwargs):
        class_to_shape_mapping = update_mapping_with(_class_to_shape_mapping,
                                                     class_to_shape_mapping)
        class_to_shape_default = class_to_shape_default or \
            _class_to_shape_default
        state_to_colour_mapping = update_mapping_with(_state_to_colour_mapping,
                                                      state_to_colour_mapping)
        state_to_text_colour_mapping = update_mapping_with(
            _state_to_text_colour_mapping, state_to_text_colour_mapping)
        s_state = _dictserializer.serialize_workflow(workflow, **kwargs)
        graph = nx.DiGraph()

        self._serialize_workflow_chunk(s_state['task_tree'],
                                       s_state['wf_spec']['task_specs'],
                                       graph,
                                       class_to_shape_mapping,
                                       class_to_shape_default,
                                       state_to_colour_mapping,
                                       state_to_text_colour_mapping,
                                       by_name
                                       )
        return graph

    def deserialize_workflow(self, s_state, **kwargs):
        raise NotImplementedError

    def _serialize_workflow_chunk(self, s_state, task_spec, graph,
                                  class_to_shape_mapping={},
                                  class_to_shape_default=None,
                                  state_to_colour_mapping={},
                                  state_to_text_colour_mapping={},
                                  by_name=True,
                                  parent=None):
        if by_name:
            node_name = s_state['task_spec']
        else:
            node_name = s_state['id'].hex
        data = {'label': s_state['task_spec'],
                'fillcolor': state_to_colour_mapping[s_state['state']],
                'fontcolor': state_to_text_colour_mapping[s_state['state']],
                'style': 'filled',
                }
        klass = task_spec[s_state['task_spec']]['class']
        if klass in class_to_shape_mapping:
            data['shape'] = class_to_shape_mapping[klass]
        else:
            data['shape'] = class_to_shape_default

        graph.add_node(node_name, data)

        if parent is not None:
            graph.add_edge(parent, node_name)

        for child in s_state['children']:
            self._serialize_workflow_chunk(child, task_spec, graph,
                                           class_to_shape_mapping,
                                           class_to_shape_default,
                                           state_to_colour_mapping,
                                           state_to_text_colour_mapping,
                                           by_name, parent=node_name)


def update_mapping_with(original_mapping, update):
    new_mapping = original_mapping.copy()
    new_mapping.update(update)
    return new_mapping
