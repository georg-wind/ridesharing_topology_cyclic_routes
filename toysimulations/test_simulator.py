import unittest
import networkx as nx

from toysimulations import ZeroDetourBus, Stop, Request

class TestZeroDetourBus(unittest.TestCase):
    def setUp(self):
        G = nx.cycle_graph(10)
        self.bus = ZeroDetourBus(G, req_gen=None, initpos=0)

    def test_interpolation(self):
        ground_truths = [#curtime, orig, dest, started_at, interp, rem_time
                         [2,   0,   3,   0,   2,   0],
                         [1.9, 0,   3,   0,   2, 0.1],
                         [3.1, 0,   3,   0,   3,   0],
                         ]
        for ground_truth in ground_truths:
            with self.subTest(ground_truth=ground_truth):
                curtime, started_from, going_to, started_at, true_pos,\
                    true_remaining_time = ground_truth
                got_pos, got_rem_time = self.bus.interpolate(
                    curtime, started_from, going_to, started_at)
                self.assertEqual(got_pos, true_pos)
                self.assertAlmostEqual(got_rem_time, true_remaining_time)

    def load_generator_from_list(self, req_list):
        for req_idx, (req_time, origin, dest) in enumerate(req_list):
            yield Request(req_idx, req_time, origin, dest)


    def test_no_simultaneity_2_requests(self):
        # req list is a 3 tuple:
        # (time_of_req, origin, dest)
        req_list = [(0.2, 1, 3),
                    (0.8, 2, 4)]
        self.bus.req_gen = self.load_generator_from_list(req_list)
        self.bus.simulate_all_requests()
        output = self.bus.req_data
        self.assertDictEqual(
            output,
            {0: {'req_epoch': 0.2, 'origin': 1, 'destination': 3,
                 'pickup_epoch': 1.2, 'dropoff_epoch': 3.2},
             1: {'req_epoch': 0.8, 'origin': 2, 'destination': 4,
                 'pickup_epoch': 2.2, 'dropoff_epoch': 4.2},
            }
        )

    def test_simultaneity_2_requests(self):
        # req list is a 3 tuple:
        # (epoch_of_req, origin, dest)
        req_list = [(0.2, 1, 3),
                    (1.2, 2, 4)]
        self.bus.req_gen = self.load_generator_from_list(req_list)
        self.bus.simulate_all_requests()
        output = self.bus.req_data
        self.assertDictEqual(
            output,
            {0: {'req_epoch': 0.2, 'origin': 1, 'destination': 3,
                 'pickup_epoch': 1.2, 'dropoff_epoch': 3.2},
             1: {'req_epoch': 1.2, 'origin': 2, 'destination': 4,
                 'pickup_epoch': 2.2, 'dropoff_epoch': 4.2},
            }
        )

    def test_long_involved_test(self):
        # req list is a 3 tuple:
        # (epoch_of_req, origin, dest)
        req_list = [(0.2, 1, 3),
                    (1.2, 2, 4),
                    (5,   4, 7), # insertion after idle
                    (7.8, 6, 4)]
        self.bus.req_gen = self.load_generator_from_list(req_list)
        self.bus.simulate_all_requests()
        output = self.bus.req_data
        # prune unnecesssary data from output. we want to match
        # only pickup epoch and dropoff-epoch

        only_epochs = {req_idx: {'pickup_epoch': data['pickup_epoch'],
                                 'dropoff_epoch': data['dropoff_epoch']}
                       for req_idx, data in output.items()}
        self.assertDictEqual(
            only_epochs,
            {0: {'pickup_epoch': 1.2, 'dropoff_epoch': 3.2},
             1: {'pickup_epoch': 2.2, 'dropoff_epoch': 4.2},
             2: {'pickup_epoch':   5, 'dropoff_epoch': 8},
             3: {'pickup_epoch':   9, 'dropoff_epoch': 11},
            }
        )

    def test_long_involved_test_inbetween_insert(self):
        # req list is a 3 tuple:
        # (epoch_of_req, origin, dest)
        req_list = [(0.2, 1, 3),
                    (1.2, 2, 4),
                    (5,   4, 8), # insertion after idle
                    (5.2, 6, 7)]
        self.bus.req_gen = self.load_generator_from_list(req_list)
        self.bus.simulate_all_requests()
        output = self.bus.req_data
        # prune unnecesssary data from output. we want to match
        # only pickup epoch and dropoff-epoch

        only_epochs = {req_idx: {'pickup_epoch': data['pickup_epoch'],
                                 'dropoff_epoch': data['dropoff_epoch']}
                       for req_idx, data in output.items()}
        self.assertDictEqual(
            only_epochs,
            {0: {'pickup_epoch': 1.2, 'dropoff_epoch': 3.2},
             1: {'pickup_epoch': 2.2, 'dropoff_epoch': 4.2},
             2: {'pickup_epoch':   5, 'dropoff_epoch': 9},
             3: {'pickup_epoch':   7, 'dropoff_epoch': 8},
            }
        )

    def test_volume_comp(self):
        # req list is a 3 tuple:
        # (epoch_of_req, origin, dest)
        req_list = [(0.2, 1, 3),
                    (1.2, 2, 4),
                    (5,   4, 8), # insertion after idle
                    (5.2, 6, 7)]
        self.bus.req_gen = self.load_generator_from_list(req_list)
        self.bus.simulate_all_requests()
        output = self.bus.insertion_data
        # prune unnecesssary data from output. we want to match
        # only pickup epoch and dropoff-epoch
        time_len_vol = [(row[0], row[1], row[2]) for row in output]

        self.assertListEqual(time_len_vol,
                             [(0.2, 1, 4), # cpe is counted, but length *before* insertion
                              (1.2, 2, 4),
                              (5, 1, 5),
                              (6, 2, 4) # 6 because jump
                              ]
                             )