#!/usr/bin/env python

import os
import sys
import unittest

sys.path.append(os.path.realpath(__file__) + "/app")

suite = unittest.TestLoader().discover("tests")

results = unittest.TextTestRunner(verbosity=3).run(suite)

if len(results.errors) > 0 or len(results.failures) > 0:
    sys.exit(1)

sys.exit()
