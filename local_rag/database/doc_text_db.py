import psycopg2
import yaml


class DocumentTextDB:
    def __init__(self, config_file):
        with open(config_file, 'r') as stream:
            data_loaded = yaml.safe_load(stream)
        self._para_table = data_loaded['doc_text_table']
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
                    paragraph_id TEXT,
                    paragraph TEXT
                )'''.format(self._para_table))
        self._conn.commit()
        self._conn.close()

    # Add a document to the database
    def add_bulk_documents(self, data_in: list) -> None:
        cursor = self._connect_db()
        cursor.executemany("INSERT INTO {} (doc_name, doc_id, paragraph_id, paragraph) VALUES (%s, %s, %s, %s)".format(self._para_table), data_in)
        self._conn.commit()
        self._conn.close()

    # Return all the documents
    def get_big_from_small(self, paragraph_id: str) -> str:
        cursor = self._connect_db()
        cursor.execute("SELECT * FROM {} WHERE paragraph_id = %s".format(self._para_table), (paragraph_id,))
        result = cursor.fetchone()

        self._conn.close()

        return result[4]

    # Delete a document
    def delete_document(self, doc_id: str) -> None:
        cursor = self._connect_db()
        cursor.execute("DELETE FROM {} WHERE doc_id = %s".format(self._para_table), (doc_id,))
        self._conn.commit()
        self._conn.close()


