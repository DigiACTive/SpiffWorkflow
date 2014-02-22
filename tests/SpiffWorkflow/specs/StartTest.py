# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division
import sys
import unittest
import re
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from SpiffWorkflow.specs import WorkflowSpec, StartTask
from SpiffWorkflow.exceptions import WorkflowException
from SpiffWorkflow.specs.TaskSpec import TaskSpec
from SpiffWorkflow.storage import DictionarySerializer

from .TaskSpecTest import TaskSpecTest

class StartTaskTest(TaskSpecTest):
    CORRELATE = StartTask

    def create_instance(self):
        return self.wf_spec.start

    def testConstructor(self):
        print(self.spec)
        self.assertEqual(self.spec.name, 'Start')
        self.assertEqual(self.spec.data, {})
        self.assertEqual(self.spec.defines, {})
        self.assertEqual(self.spec.pre_assign, [])
        self.assertEqual(self.spec.post_assign, [])
        self.assertEqual(self.spec.locks, [])
        
    def testDelete(self):
        self.assertRaises(WorkflowException, self.spec.delete)

    def testConnect(self):
        self.assertEqual(self.spec.outputs, [])
        spec = TaskSpec(self.wf_spec, 'testtask')
        self.spec.connect(spec)
        self.assertEqual(self.spec.outputs, [spec])
        self.assertEqual(spec.inputs, [self.spec])

    def testFollow(self):
        self.assertRaises(WorkflowException, self.spec.follow, self.spec)

    def testSerialize(self):
        pass

    def testTest(self):
        spec = TaskSpec(self.wf_spec, 'testtask')
        self.spec.connect(spec)
        self.spec.test()

    # most of the other cases aren't Start specific. We could override them in
    # this case, but it's hard to see any benefit in terms of better coverage.

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(StartTaskTest)
