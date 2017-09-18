import unittest
import analysis

answer_keys_original = {
    'Less than 967.33': False,
    'Between 967.33 and 1093.53, inclusive': False,
    'More than 1093.53 but less than 1202.22': False,
    'Between 1202.22 and 1328.41, inclusive': False,
    'More than 1328.41': False,
}


class TestScoreForecast(unittest.TestCase):

    def test_forecast_3_keys(self):
        self.ans_keys_3 = {
            'a': True,
            'b': False,
            'c': False
        }

        self.forecast_3 = {
            'a': '60%',
            'b': '10%',
            'c': '30%'
        }

        self.assertEqual(analysis.score_forecast(self.forecast_3, self.ans_keys_3), 0.26)


if __name__ == '__main__':
    unittest.main()
