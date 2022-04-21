
import unittest, psycopg2

from plume.pg.computer import datetime_parser
from plume.pg.tests.connection import ConnectionString

class ComputerTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Création de la connexion PG.
        
        """
        cls.connection_string = ConnectionString()
    
    def test_datetime_parser(self):
        """Sérialisation textuelle des dates-heures renvoyées par PostgreSQL.
        
        """
        conn = psycopg2.connect(ComputerTestCase.connection_string)
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT '2022-04-20 16:46:35.487888+02'::timestamp with time zone")
                result = cur.fetchall()
        conn.close()
        cr = datetime_parser(*result[0])
        self.assertEqual(cr.str_value, '20/04/2022 16:46:35')

if __name__ == '__main__':
    unittest.main()

