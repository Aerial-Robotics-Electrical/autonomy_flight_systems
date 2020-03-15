import unittest
import json
from route import Route

class TestRouteMethods(unittest.TestCase):
    def setUp(self):
        self.route = Route("interop_example.json") #data for unit test in this file

    def test_change_routes(self):
        newRoute = self.route.changeRoute(self.route.waypoints, [38.1417722222222, -76.4251083333333, 400.0], [[0,0,0], [0,0,0]])
        self.assertEqual(5, len(newRoute))
        self.assertEqual([[38.1446916666667, -76.4279944444445, 200.0], 
                        [38.1461944444444, -76.4237138888889, 300.0], 
                        [38.1438972222222, -76.42255, 400.0], 
                        [0, 0, 0], 
                        [0, 0, 0]], newRoute)

    
if __name__ == "__main__":
    unittest.main()
