from uuid import UUID, uuid4

from src.domain.id_generator import IdGenerator


class SystemUuidGenerator(IdGenerator):
    def generate(self) -> UUID:
        return uuid4()
