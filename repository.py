# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime

#
# Ścieżka połączenia z bazą danych
#
db_path = 'temp_hist.db'

#
# Wyjątek używany w repozytorium
#
class RepositoryException(Exception):
    def __init__(self, message, *errors):
        self.errors = errors
        Exception.__init__(self, message)

class Czujnik():
    """Klasa reprezentująca pojedyńczy czujnik temperatury
    """
    def __init__(self, id, serial_number, miejsce):
        self.id=id
        self.serial_number = serial_number
        self.miejsce = miejsce

    def __repr__(self):
        return "<Czujnik(id='%s', serial_number='%s', miejsce='%s')>" % (self.id, self.serial_number, self.miejsce)


class Pomiar():
    """Klasa reprezentująca pojedyńczy odczyt temperatury
    """
    def __init__(self, id, czujnik, pomiar, data):
        self.id=id
        self.czujnik=czujnik
        self.pomiar=pomiar
        self.data=data

    def __repr__(self):
        return "<Pomiar(Id='%s', Czujnik='%s', pomiar='%s', data='%s')>" % (self.id, self.czujnik, self.pomiar, self.data)


class Repository():
    def __init__(self):
        try:
            self.conn = self.get_connection()
        except Exception as e:
            raise RepositoryException('GET CONNECTION:', *e.args)
        self._complete = False

    # wejście do with ... as ...
    def __enter__(self):
        return self

    # wyjście z with ... as ...
    def __exit__(self, type_, value, traceback):
        self.close()

    def complete(self):
        self._complete = True

    def get_connection(self):
        return sqlite3.connect(db_path)

    def close(self):
        if self.conn:
            try:
                if self._complete:
                    self.conn.commit()
                else:
                    self.conn.rollback()
            except Exception as e:
                raise RepositoryException(*e.args)
            finally:
                try:
                    self.conn.close()
                except Exception as e:
                    raise RepositoryException(*e.args)



# repozytorium obiektow typu Invoice
#
class PomiarRepository(Repository):

        def getByCzujnik(self, id):
            """Pobierz czujnik o wskazanym id
            """
            try:
                c = self.conn.cursor()
                c.execute("SELECT * FROM czujnik WHERE id=?", (id,))
                cz_row = c.fetchone()
                if cz_row == None:
                    czujnik=None
                else:
                    czujnik = Czujnik(id=id, serial_number=cz_row[1], miejsce=cz_row[2])
            except Exception as e:
                print "invoice getByCzujnik error:", e
                raise RepositoryException('error getByCzujnik by id czujnik_id: %s' % str(id))
            return czujnik


        def getPomiar(self, id):
            """Pobierz pomiar o wskazanym id
            """
            try:
                c = self.conn.cursor()
                c.execute("SELECT p.*, c.* FROM pomiar p join czujnik c on p.czujnik_id=c.id WHERE p.id=?", (id,))
                row = c.fetchone()
                if row == None:
                    pomiar=None
                else:
                    pomiar = Pomiar(id=id, czujnik=Czujnik(id=row[4], serial_number=row[5], miejsce=row[6]), pomiar=row[2], data=row[3])
            except Exception as e:
                print "invoice getPomiar error:", e
                raise RepositoryException('error getPomiar by id: %s' % str(id))
            return pomiar

        def sredniaCzujnika(self, id):
            """Wyliczenie średniego pomiaru wartości czujnika
            """
            try:
                c = self.conn.cursor()
                c.execute("select avg(pomiar) from pomiar where czujnik_id =?", (id,))
            except Exception as e:
                print "błąd przy wyznaczaniu średniej temperatury czujnika", e
                raise RepositoryException('blad przy średniej dla id:%s' % str(id))
            return round(c.fetchone()[0],1)

        def add(self, pomiar):
            """Metoda dodaje pojedynczy pomiar temperatury do bazy danych.
            """
            try:
                c = self.conn.cursor()
                # sprawdz czy czujnik juz istnieje w bazie
                if self.getByCzujnik(id=pomiar.czujnik.id) == None:
                    # zapisz czujnik pomiaru
                    c.execute('INSERT INTO czujnik (id, serial_number, lokalizacja) VALUES(?, ?, ?)',(pomiar.czujnik.id, pomiar.czujnik.serial_number, pomiar.czujnik.miejsce))


            except Exception as e:
                print "czujnik add error:", e


            try:
                c = self.conn.cursor()
                # zapisz pomiar
                c.execute('INSERT INTO pomiar (id, czujnik_id, pomiar, data) VALUES(?, ?, ?, ?)',(pomiar.id, pomiar.czujnik.id, pomiar.pomiar, pomiar.data))


            except Exception as e:
                print "pomiar add error:", e

        def delete(self, czujnik):
            """Metoda usuwa czujnik wraz ze wszystkimi jego pomiarami
            """
            try:
                c = self.conn.cursor()
                # usuń pozycje
                c.execute('DELETE FROM pomiar WHERE czujnik_id=?', (czujnik.id,))
                # usuń nagłowek
                c.execute('DELETE FROM czujnik WHERE id=?', (czujnik.id,))

            except Exception as e:
                #print "invoice delete error:", e
                raise RepositoryException('error deleting czujnik %s' % str(e))


        def update(self, pomiar):
            """Metoda uaktualnia pojedynczy pomiar w bazie danych
            """
            try:
                c = self.conn.cursor()
                c.execute('update pomiar set czujnik_id=?, pomiar=?, data=? WHERE id=?', (pomiar.czujnik.id,pomiar.pomiar, pomiar.data, pomiar.id,))
            except Exception as e:
                raise RepositoryException('error updating pomiar %s' % str(e))


import numpy as np



AA= Czujnik(id=1, serial_number=00000001, miejsce='Pomieszczenie A')
AB= Czujnik(id=2, serial_number=00000002, miejsce='Pomieszczenie B')


#print(B.czujnik.id)


if __name__ == '__main__':
    try:
        with PomiarRepository() as repo:

            # usunięcie istniejących wpisów dla czujników A i B
            repo.delete(AA)
            repo.delete(AB)

            # dodanie nowych pomiarów do bazy
            repo.complete()
            for i in range(1,24) :
                if i%2 == 1 :
                    repo.add(Pomiar(id=i,czujnik=AA, pomiar=round(np.random.normal(15, 2, 1),1), data='2015-12-02'))
                else:
                    repo.add(Pomiar(id=i,czujnik=AB, pomiar=round(np.random.normal(17, 4, 1),1), data='2015-12-02'))
            repo.complete()

            # update przykladowego pomiaru
            #repo.update(pomiar=Pomiar(id=2,czujnik=A, pomiar=0, data='2015-12-01'))
            #repo.complete()

            #Odczyt przykładowego pomiaru i czujnika
            #print(repo.getByCzujnik(id=1))
            #print(repo.getPomiar(id=1))

            # obliczanie średniego poziomu temperatury dla czujników
            print('Średnia temperatura dla czujnika %s w pomiesczeniu %s wynosi %s' % (str(AA.serial_number), AA.miejsce, str(repo.sredniaCzujnika(id=AA.id))))

    except RepositoryException as e:
        print(e)
