
from typing import TypeVar, Type, Dict, Protocol, runtime_checkable

T = TypeVar("T")

@runtime_checkable
class Service(Protocol):
    pass

class ServiceRegistry:
    _services: Dict[Type[Service], Service] = {}

    @classmethod
    def register(cls, protocol: Type[Service], instance: Service):
        cls._services[protocol] = instance

    @classmethod
    def get(cls, protocol: Type[T]) -> T:
        return cls._services.get(protocol) # type: ignore