import vecs
from vecs import IndexMethod, IndexMeasure
import yaml
from pydantic import BaseModel
import string
import secrets


# Vector database metadata model
class VectorMetadataModel(BaseModel):
	doc_id: str
	paragraph_id: str


class VectorDatabase:
	def __init__(self, config_file, db_table):
		with open(config_file, 'r') as stream:
			data_loaded = yaml.safe_load(stream)
		self.db_table = db_table
		self.db_host = data_loaded['host']
		self.db_name = data_loaded['database_name']
		self.db_user = data_loaded['user']
		self.db_password = data_loaded['password']
		self.db_port = data_loaded['db_port']
		self.vector_dim = data_loaded['vector_dim']
		self._make_table()

	# Make table if needed
	def _make_table(self) -> None:
		vx = vecs.create_client(f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{int(self.db_port)}/{self.db_name}")
		vx.disconnect()

	@staticmethod
	def _key_gen() -> str:
		characters = string.ascii_letters + string.digits
		key_id = ''.join(secrets.choice(characters) for _ in range(16))

		return key_id

	# Insert a vector into database
	def insert_batch_vecs(self, embedding: list, doc_id: str, paragraph_id_list: list) -> None:
		vx = vecs.create_client(f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{int(self.db_port)}/{self.db_name}")
		docs = vx.get_or_create_collection(name=self.db_table, dimension=self.vector_dim)
		vectors = []

		for idx, value in enumerate(zip(embedding, paragraph_id_list)):
			vector_metadata = VectorMetadataModel(doc_id=doc_id, paragraph_id=value[1])
			vectors.append((self._key_gen(), value[0], vector_metadata.model_dump()))

		# Insert data
		docs.upsert(records=vectors)
		vx.disconnect()

	# Insert a vector into database
	def insert_vec(self, embedding: list, doc_id: str, paragraph_id: str) -> None:
		vx = vecs.create_client(f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{int(self.db_port)}/{self.db_name}")
		docs = vx.get_or_create_collection(name=self.db_table, dimension=self.vector_dim)

		# Validate metadata
		vector_metadata = VectorMetadataModel(doc_id=doc_id, paragraph_id=paragraph_id)

		# Insert data
		docs.upsert(records=[(self._key_gen(), embedding, vector_metadata.model_dump())])
		vx.disconnect()

	# Index the vector database using cosine similarity
	def make_cosine_index(self) -> None:
		vx = vecs.create_client(f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{int(self.db_port)}/{self.db_name}")
		docs = vx.get_or_create_collection(name=self.db_table, dimension=self.vector_dim)
		docs.create_index(method=IndexMethod.hnsw, measure=IndexMeasure.cosine_distance,)
		vx.disconnect()

	# Get the matches from the vector database using cosine similarity
	def get_matches(self, vector_search: list, n_results: int) -> list:
		vx = vecs.create_client(f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{int(self.db_port)}/{self.db_name}")
		docs = vx.get_or_create_collection(name=self.db_table, dimension=self.vector_dim)

		# Pull the results
		results = docs.query(
			data=vector_search,
			limit=n_results,
			measure="cosine_distance",
			include_value=True,
			include_metadata=True,
		)
		vx.disconnect()

		# Organise in descending order on similarity
		results = results[::-1]
		
		return results

	# Delete a collection (table)
	def delete_vecs(self) -> None:
		vx = vecs.create_client(f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{int(self.db_port)}/{self.db_name}")
		vx.delete_collection(self.db_table)
		vx.disconnect()
