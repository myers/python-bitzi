#!/usr/bin/env python

import unittest

import bitzi

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testBasicUseage(self):
        bc = bitzi.Bitcollider()
        ret = bc.analyze("COPYING")
        assert ret.has_key("bitprint")
        assert ret.has_key("tag.file.length")
        

    def testCallback(self):
        bc = bitzi.Bitcollider()

        global called 
        called = False
        def callback(percentDone, fileName, status):
            global called
            called = True

        dd = bc.analyze("COPYING", callback)
        assert called
        called = False
        dd = bc.analyze("COPYING")
        assert not called
    
        
if __name__ == "__main__":
    unittest.main()
