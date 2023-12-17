import psycopg2
import yaml


class DocumentDB:
    def __init__(self, config_file):
        with open(config_file, 'r') as stream:
            data_loaded = yaml.safe_load(stream)
        self._para_table = data_loaded['paragraph_table']
        self._database_name = data_loaded['database_name']
        self._user = data_loaded['user']
        self._password = data_loaded['password']
        self._host = data_loaded['host']
        self._conn = None
        self._create_database()

    # Connect to the database and return the connection
    def _connect_db(self):
        self._conn = psycopg2.connect(
            dbname=self._database_name, 
            user=self._user, 
            password=self._password, 
            host=self._host
        )
        return self._conn.cursor()

    # Create the tables if needed
    def _create_database(self) -> None:
        cursor = self._connect_db()
        cursor.execute('''CREATE TABLE IF NOT EXISTS {} (
                    id SERIAL PRIMARY KEY,
                    doc_name TEXT,
                    doc_id TEXT,
                    chunk_method TEXT
                )'''.format(self._para_table))
        self._conn.commit()
        self._conn.close()

    # Add a document to the database
    def add_document(self, doc_name: str, doc_id: str, chunk_method: str) -> None:
        cursor = self._connect_db()
        cursor.execute("INSERT INTO {} (doc_name, doc_id, chunk_method) VALUES (%s, %s, %s)".format(self._para_table), (doc_name, doc_id, chunk_method))
        self._conn.commit()
        self._conn.close()

    # Return all the documents
    def get_docs(self) -> list:
        cursor = self._connect_db()
        cursor.execute("SELECT * FROM {}".format(self._para_table))
        result = cursor.fetchall()
        self._conn.close()

        return result

    # Delete a document
    def delete_document(self, doc_id: str) -> None:
        cursor = self._connect_db()
        cursor.execute("DELETE FROM {} WHERE doc_id = %s".format(self._para_table), (doc_id,))
        self._conn.commit()
        self._conn.close()


