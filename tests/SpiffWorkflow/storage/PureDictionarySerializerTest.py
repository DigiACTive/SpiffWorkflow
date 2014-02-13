# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division
import sys, unittest, re, os
dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dirname, '..', '..', '..'))

from SpiffWorkflow.storage.PureDictionarySerializer import PureDictionarySerializer
from .DictionarySerializerTest import DictionarySerializerTest, DictionarySerializeEveryPatternTest

class PureDictionarySerializerTest(DictionarySerializerTest):
    CORRELATE = PureDictionarySerializer

    def setUp(self):
        DictionarySerializerTest.setUp(self)
        self.serializer = PureDictionarySerializer()

    def testConstructor(self):
        PureDictionarySerializer()


class PureDictionarySerializeEveryPatternTest(DictionarySerializeEveryPatternTest):

    def setUp(self):
        super(PureDictionarySerializeEveryPatternTest, self).setUp()
        self.serializerTestClass = PureDictionarySerializerTest(methodName='testConstructor')
        self.serializerTestClass.setUp()


def suite():
    tests = unittest.defaultTestLoader.loadTestsFromTestCase(PureDictionarySerializerTest)
    tests.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(PureDictionarySerializeEveryPatternTest))
    return tests
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
