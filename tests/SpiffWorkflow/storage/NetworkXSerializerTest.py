# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division
import sys, unittest, re, os
from util import run_workflow
dirname = os.path.dirname(__file__)
data_dir = os.path.join(dirname, '..', 'data')
sys.path.insert(0, os.path.join(dirname, '..', '..', '..'))

# this requires pygraphvis or pydot
write_files = False

from .SerializerTest import SerializerTest, SerializeEveryPatternTest
from SpiffWorkflow import Workflow
from SpiffWorkflow.storage.Exceptions import TaskSpecNotSupportedError, \
     TaskNotSupportedError
from SpiffWorkflow.storage.NetworkXSerializer import NetworkXSerializer
try:
    import networkx
except ImportError:
    pass  # this is caught below


class NetworkXSerializerTest(SerializerTest):
    CORRELATE = NetworkXSerializer

    def setUp(self):
        SerializerTest.setUp(self)
        self.serializer = NetworkXSerializer()
        self.serial_type = networkx.DiGraph

    def testConstructor(self):
        NetworkXSerializer()

    def testDeserializeWorkflowSpec(self):
        pass

    def testSerializeWorkflowSpec(self, path_file=None, data=None):
        serialized1 = self.wf_spec.serialize(self.serializer)
        self.assert_(isinstance(serialized1, self.serial_type))
        if self.wf_spec.file is not None and write_files:
            name = os.path.basename(self.wf_spec.file)
            networkx.write_dot(serialized1, name+'.spec.dot')

    def testDeserializeWorkflow(self):
        pass

    def testSerializeWorkflow(self, path_file=None, data=None):
        # run a workflow fresh from the spec to completion, see if it
        # serialises correctly.
        if path_file is None:
            path_file = os.path.join(data_dir, 'spiff', 'workflow1.path')
            path      = open(path_file).read()
        elif os.path.exists(path_file):
            path = open(path_file).read()
        else:
            path = None
        workflow = run_workflow(self, self.wf_spec, path, data)
        try:
            serialized1 = workflow.serialize(self.serializer)
        except TaskNotSupportedError as e:
            return
        else:
            self.assert_(isinstance(serialized1, self.serial_type))
            if workflow.spec.file is not None and write_files:
                name = os.path.basename(workflow.spec.file)
                networkx.write_dot(serialized1, name+'.dot')

        # try an freshly started workflow
        workflow = Workflow(self.wf_spec)
        serialized1 = workflow.serialize(self.serializer)
        self.assert_(isinstance(serialized1, self.serial_type))


class NetworkXSerializeEveryPatternTest(SerializeEveryPatternTest):

    def setUp(self):
        super(SerializeEveryPatternTest, self).setUp()
        self.serializerTestClass = NetworkXSerializerTest(methodName='testConstructor')
        self.serializerTestClass.setUp()


def suite():
    try:
        import networkx
    except ImportError:
        import warnings
        warnings.warn("NetworkX not found. Skipping tests.")
        return lambda x: None
    else:
        tests = unittest.defaultTestLoader.loadTestsFromTestCase(NetworkXSerializerTest)
        tests.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(NetworkXSerializeEveryPatternTest))
        return tests
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
