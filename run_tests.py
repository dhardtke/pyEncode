#!/usr/bin/env python3

import os
import sys
import unittest

sys.path.append(os.path.realpath(__file__) + "/app")

# tell the app instance to use the config values from app.config.testing
os.environ["PYENCODE_ADDITIONAL_CONFIG"] = "app.config.testing"

suite = unittest.TestLoader().discover("tests")
results = unittest.TextTestRunner(verbosity=3).run(suite)

if len(results.errors) > 0 or len(results.failures) > 0:
    sys.exit(1)

sys.exit()
