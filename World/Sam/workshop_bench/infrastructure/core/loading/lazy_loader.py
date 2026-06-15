import threading

class LazyProperty:
    __slots__ = ('func', 'lock', 'name')
    def __init__(self, func):
        self.func = func
        self.lock = threading.Lock()
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        with self.lock:
            if self.name not in instance.__dict__:
                instance.__dict__[self.name] = self.func(instance)
            return instance.__dict__[self.name]