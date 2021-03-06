#!/usr/bin/env python3
import unittest

from netsuite.api.customer import (
    get_or_create_customer,
    get_customer
)
from netsuite.api.journal_entry import create_journal_entries
from netsuite.api.sale import (
    create_cashsale,
    create_salesorder
)

from netsuite.test_data import (
    data,
    prepare_customer_data,
)


class NetsuiteTestCase(unittest.TestCase):
    def test_customer(self):
        customer_data = prepare_customer_data(data)
        customer = get_or_create_customer(customer_data)
        self.assertEqual(customer.firstName, 'Joe')
        self.assertTrue(customer.email.endswith('gmail.com'))

    def test_cashsale(self):
        created, sale = create_cashsale(data)
        self.assertTrue(created)

    def test_salesorder(self):
        created, result = create_salesorder(data)
        self.assertTrue(created)

    def test_journal_entry(self):
        result = create_journal_entries(data.journal_entries)
        for external_id, status in result:
            self.assertIsNotNone(external_id)
            self.assertTrue(status)


if __name__ == "__main__":
     unittest.main()
