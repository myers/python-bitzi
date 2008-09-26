#!/usr/bin/env python

import bitzi, pprint, sys

bc = bitzi.Bitcollider()

ret = bc.analyze(sys.argv[1])

ret = bitzi.analyze2triples(ret)

pprint.pprint(ret)


