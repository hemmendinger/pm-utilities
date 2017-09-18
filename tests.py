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


class TestScoreOrderedForecast(unittest.TestCase):
    answer_key = {
        'a': False,
        'b': True,
        'c': False,
        'd': False
    }

    forecast_1 = {
        'a': '25%',
        'b': '25%',
        'c': '50%',
        'd': '0%'
    }

    forecast_2 = {
        'a': '25%',
        'b': '25%',
        'c': '30%',
        'd': '20%'

    }

    answer_order = {
        1: 'a',
        2: 'b',
        3: 'c',
        4: 'd',
    }

    def test_sum_from_keys(self):
        forecasts = {'d': 0.0, 'a': 0.25, 'b': 0.25, 'c': 0.5}
        keys = ['b', 'c', 'd']
        self.assertEqual(analysis.sum_from_keys(keys, forecasts), 0.75)


    def test_forecast_ordered_1(self):
        self.assertAlmostEqual(
            analysis.score_ordered_forecast(
                forecast=self.forecast_1,
                answer_key=self.answer_key,
                answer_order=self.answer_order),
            0.208, places=3)

    def test_forecast_ordered_2(self):
        self.assertEqual(
            analysis.score_ordered_forecast(
                forecast=self.forecast_2,
                answer_key=self.answer_key,
                answer_order=self.answer_order),
            0.235)



if __name__ == '__main__':
    unittest.main()
