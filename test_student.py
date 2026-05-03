import unittest
from proj2 import *

testfile = 'sample.csv'

class TestParseFloat(unittest.TestCase):

    def test_valid_float(self):
        self.assertEqual(parse_float('3.14'), 3.14)

    def test_empty_string_returns_none(self):
        self.assertIsNone(parse_float(''))

    def test_none_returns_none(self):
        self.assertIsNone(parse_float(None))

    def test_integer_string(self):
        self.assertEqual(parse_float('5000'), 5000.0)


class TestParseRow(unittest.TestCase):

    def test_basic_row(self):
        fields = ['USA', '2000', '5000.0', '17.5', '6000.0', '21.0', '7000.0', '24.5']
        row = parse_row(fields)
        self.assertEqual(row.country, 'USA')
        self.assertEqual(row.year, 2000)
        self.assertEqual(row.electricity_and_heat_co2_emissions, 5000.0)

    def test_missing_fields_become_none(self):
        fields = ['Brazil', '2015', '', '', '', '200.0', '2.5', '900.0']
        row = parse_row(fields)
        self.assertIsNone(row.electricity_and_heat_co2_emissions)
        self.assertIsNone(row.electricity_and_heat_co2_emissions_per_capita)

    def test_row_is_frozen(self):
        fields = ['USA', '2000', '5000.0', '17.5', '6000.0', '21.0', '7000.0', '24.5']
        row = parse_row(fields)
        with self.assertRaises(Exception):
            row.country = 'Canada'


class TestMakeList(unittest.TestCase):

    def test_empty_rows(self):
        self.assertIsNone(make_list([], 0))

    def test_single_row(self):
        rows = [['USA', '2000', '5000.0', '17.5', '6000.0', '21.0', '7000.0', '24.5']]
        result = make_list(rows, 0)
        self.assertIsNotNone(result)
        self.assertIsNone(result.next)
        self.assertEqual(result.value.country, 'USA')

    def test_index_past_end(self):
        rows = [['USA', '2000', '5000.0', '17.5', '6000.0', '21.0', '7000.0', '24.5']]
        self.assertIsNone(make_list(rows, 5))


class TestReadCsvLines(unittest.TestCase):

    def test_returns_node(self):
        result = read_csv_lines(testfile)
        self.assertIsInstance(result, Node)

    def test_first_row_country(self):
        result = read_csv_lines(testfile)
        self.assertEqual(result.value.country, 'USA')

    def test_correct_length(self):
        result = read_csv_lines(testfile)
        self.assertEqual(listlen(result), 5)


class TestListlen(unittest.TestCase):

    def test_none_returns_zero(self):
        self.assertEqual(listlen(None), 0)

    def test_full_file_length(self):
        result = read_csv_lines(testfile)
        self.assertEqual(listlen(result), 5)

    def test_single_node(self):
        row = parse_row(['USA', '2000', '5000.0', '17.5', '6000.0', '21.0', '7000.0', '24.5'])
        node = Node(value=row, next=None)
        self.assertEqual(listlen(node), 1)


class TestCompare(unittest.TestCase):

    def setUp(self):
        self.usa = parse_row(['USA', '2000', '5000.0', '17.5', '6000.0', '21.0', '7000.0', '24.5'])
        self.brazil = parse_row(['Brazil', '2015', '', '', '', '200.0', '2.5', '900.0'])

    def test_equal_country(self):
        self.assertTrue(compare(self.usa, 'country', 'equal', 'USA'))

    def test_equal_country_no_match(self):
        self.assertFalse(compare(self.usa, 'country', 'equal', 'Canada'))

    def test_less_than(self):
        self.assertTrue(compare(self.usa, 'year', 'less_than', 2010))

    def test_greater_than(self):
        self.assertTrue(compare(self.usa, 'year', 'greater_than', 1999))

    def test_none_field_returns_false(self):
        self.assertFalse(compare(self.brazil, 'electricity_and_heat_co2_emissions', 'equal', 0.0))

    def test_invalid_field_raises(self):
        with self.assertRaises(ValueError):
            compare(self.usa, 'population', 'equal', 'USA')

    def test_invalid_comparison_raises(self):
        with self.assertRaises(ValueError):
            compare(self.usa, 'year', 'between', 2000)

    def test_country_non_equal_raises(self):
        with self.assertRaises(ValueError):
            compare(self.usa, 'country', 'less_than', 'USA')


class TestFilterRows(unittest.TestCase):

    def setUp(self):
        self.data = read_csv_lines(testfile)

    def test_filter_by_country(self):
        result = filter_rows(self.data, 'country', 'equal', 'USA')
        self.assertEqual(listlen(result), 1)
        self.assertEqual(result.value.country, 'USA')

    def test_filter_no_matches(self):
        result = filter_rows(self.data, 'country', 'equal', 'Canada')
        self.assertIsNone(result)

    def test_filter_greater_than_year(self):
        result = filter_rows(self.data, 'year', 'greater_than', 2010)
        self.assertEqual(listlen(result), 2)  # Brazil (2015), India (2020)

    def test_filter_less_than_year(self):
        result = filter_rows(self.data, 'year', 'less_than', 2010)
        self.assertEqual(listlen(result), 2)  # USA (2000), China (2005)

    def test_filter_skips_none_fields(self):
        # Brazil has missing electricity fields, should be skipped
        result = filter_rows(self.data, 'electricity_and_heat_co2_emissions', 'greater_than', 0.0)
        countries = []
        node = result
        while node:
            countries.append(node.value.country)
            node = node.next
        self.assertNotIn('Brazil', countries)

    def test_filter_on_none_list(self):
        self.assertIsNone(filter_rows(None, 'country', 'equal', 'USA'))


if __name__ == '__main__':
    unittest.main()
