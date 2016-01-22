# -*- coding: utf-8 -*-

import repository
import sqlite3
import unittest

db_path = 'temp_hist.db'

class RepositoryTest(unittest.TestCase):

    def setUp(self):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('DELETE FROM czujnik')
        c.execute('DELETE FROM pomiar')
        c.execute('''INSERT INTO czujnik (id, serial_number, lokalizacja) VALUES(1, 1, 'Pok 11')''')
        c.execute('''INSERT INTO pomiar (id, czujnik_id, pomiar, data) VALUES(1, 1, 20, '2015-11-10')''')
        c.execute('''INSERT INTO pomiar (id, czujnik_id, pomiar, data) VALUES(2, 1, 10, '2015-12-30')''')
        conn.commit()
        conn.close()

    def tearDown(self):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('DELETE FROM czujnik')
        c.execute('DELETE FROM pomiar')
        conn.commit()
        conn.close()

    def testGetByIdCzujnik(self):
        czujnik = repository.PomiarRepository().getByCzujnik(1)
        self.assertIsInstance(czujnik, repository.Czujnik, "Objekt nie jest klasy Czujnik")

    def testGetByIdCzujnikNotFound(self):
        self.assertEqual(repository.PomiarRepository().getByCzujnik(22),
                None, "Powinno wyjść None")

    def testGetBysrednia(self):
        self.assertEqual(repository.PomiarRepository().sredniaCzujnika(1),15, "Powinno wyjść 15")

    def testDeleteNotFound(self):
        self.assertRaises(repository.RepositoryException,repository.PomiarRepository().delete,22)



if __name__ == "__main__":
    unittest.main()
