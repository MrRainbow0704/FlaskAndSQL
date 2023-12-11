import mysql.connector as mysql
import sqlite3 as sqlite
from typing import Literal
from pathlib import Path


class MySQL:
    def db_connect(
        DbHostName: str,
        DbHostPort: int,
        DbUserName: str,
        DbUserPassword: str,
        DbName: str,
    ) -> mysql.MySQLConnection | Literal[False]:
        """Crea e restituisce una connessione a un database già esistente.

        Args:
            DbHostName (str): IP del database.
            DbHostPort (int): Porta del database.
            DbUserName (str): Username con il quale loggare.
            DbUserPassword (str): Password con la quale loggare.
            DbName (str): Nome del database a cui connettersi.

        Returns:
            mysql.MySQLConnection: Connessione al database selezionato.
        """

        # Prova a stabilire una connessione con il database, se fallisce restituisce False
        connection = False
        try:
            connection = mysql.connect(
                host=DbHostName,
                port=DbHostPort,
                user=DbUserName,
                passwd=DbUserPassword,
                database=DbName,
            )
        except mysql.Error as err:
            print(f"Error: '{err}'")

        return connection

    def create_db(
        DbHostName: str,
        DbUserPort: int,
        DbUserName: str,
        DbUserPassword: str,
        DbName: str,
    ) -> mysql.MySQLConnection | Literal[False]:
        """Crea un database e restituisce la connessione a esso.
        ATTENZIONE DbName è vulnerabile a iniezioni SQL! Sanificalo.

        Args:
            DbHostName (str): IP del database.
            DbHostPort (int): Porta del database.
            DbUserName (str): Username con il quale loggare.
            DbUserPassword (str): Password con la quale loggare.
            DbName (str): Nome del database da creare.

        Returns:
            mysql.MySQLConnection | Literal[False]: Connessione al database selezionato, false se fallisce.
        """

        # Prova a creare una connessione a un database senza specificare la tabella.
        # Se va a buon fine, crea la tabella richiesta e restituisci una connessione al database
        # altrimenti restituisci false
        try:
            conn = mysql.connect(
                host=DbHostName, port=DbUserPort, user=DbUserName, passwd=DbUserPassword
            )
        except mysql.Error as err:
            print(f"Error: '{err}'")
            return False
        else:
            MySQL.SQL_query(conn, "CREATE DATABASE IF NOT EXISTS `%s`;" % DbName)
            return MySQL.db_connect(
                DbHostName, DbUserPort, DbUserName, DbUserPassword, DbName
            )

    def SQL_query(
        conn: mysql.MySQLConnection,
        sqlString: str,
        sqlParam: tuple | dict = None,
    ) -> list[dict[str, str] | None] | None | Literal[False]:
        """Fa una richiesta al database e restituisce la risposta. Tutti i parametri vengono sanificati automaticamente.

        Args:
            conn (mysql.MySQLConnection): Una connessione al database.
            sqlString (str): IL comando da eseguire. Usa %s come placeholder o
                            %(var)s se sqlParam è un dizionario con una chiave "val".
            sqlParam (tuple | dict, optional): Parametri da associare al comando. Defaults to None.

        Returns:
            list[dict[str, str] | None] | None | False : Le/la righe/a restituite/a dalla
                                    richiesta, False se la richiesta fallisce.
        """

        if sqlParam is None:
            sqlParam = ()

        cur = conn.cursor(dictionary=True)

        # Esegui la query aggiornando il database se necessario
        # Se la query fallisce, fa il rollback e restituisce False
        try:
            cur.execute(sqlString, sqlParam)
            if (
                sqlString.count("INSERT")
                or sqlString.count("UPDATE")
                or sqlString.count("DELETE")
            ):
                conn.commit()
        except mysql.Error as err:
            conn.rollback()
            return f"Error: '{err}\nParameteri: {sqlString=} {sqlParam=}'"
        
        # Ottieni i risultati della query svuotando anche il buffer
        try:
            res = cur.fetchall()
        except mysql.Error as err:
            print(f"Error: '{err}'")
            res = []

        # Chiudi il cursore e restituisci il risultato della query
        cur.reset()
        cur.close()
        return res


class SQLite:
    def db_connect(DbPath: str | Path) -> sqlite.Connection | Literal[False]:
        """Crea e restituisce una connessione a un database esistente o non.

        Args:
            DbPath (str | Path): Percorso del database.

        Returns:
            sqlite.Connection: Connessione al database selezionato.
        """
        connection = False
        try:
            connection = sqlite.connect(DbPath, check_same_thread=False)
        except sqlite.Error as err:
            print(f"Error: '{err}'")
        return connection

    def SQL_query(
        conn: sqlite.Connection,
        sqlString: str,
        sqlParam: tuple | dict = None,
    ) -> list[dict[str, str] | None] | None | Literal[False]:
        """Fa una richiesta al database e restituisce la risposta. Tutti i parametri vengono sanificati automaticamente.

        Args:
            conn (sqlite.Connection): Una connessione al database.
            sqlString (str): IL comando da eseguire. Usa %s come placeholder o
                            %(var)s se sqlParam è un dizionario con una chiave "val".
            sqlParam (tuple | dict, optional): Parametri da associare al comando. Defaults to None.

        Returns:
            list[dict[str, str] | None] | None | Literal[False]: : Le/la righe/a restituite/a dalla
                                    richiesta, False se la richiesta fallisce.
        """

        if sqlParam is None:
            sqlParam = ()
        conn.row_factory = sqlite.Row
        cur = conn.cursor()

        # Esegui la query aggiornando il database se necessario
        # Se la query fallisce, fa il rollback e restituisce False
        try:
            cur.execute(sqlString, sqlParam)
            if (
                sqlString.count("INSERT")
                or sqlString.count("UPDATE")
                or sqlString.count("DELETE")
            ):
                conn.commit()
        except sqlite.Error as err:
            conn.rollback()
            return f"Error: '{err}\nParameteri: {sqlString=} {sqlParam=}'"

        # Ottieni i risultati della query svuotando anche il buffer
        try:
            res = [list(row) for row in cur.fetchall()]
        except sqlite.Error as err:
            print(f"Error: '{err}'")
            res = []

        # Chiudi il cursore e restituisci il risultato della query
        cur.close()
        return res
