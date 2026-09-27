import inspect

class MyClass:
    def method_one(self):
        pass

    def method_two(self, arg):
        pass

    @classmethod
    def class_method(cls):
        pass

    @staticmethod
    def static_method():
        pass

    def _private_method(self):
        pass

    my_attribute = 10

def get_method_names(cls):
    """
    Returns a list of names of methods defined within a given class.
    """
    method_names = []
    for name, obj in inspect.getmembers(cls):
        if inspect.isfunction(obj) or inspect.ismethod(obj):
            # Exclude built-in methods (those starting with '__')
            if not name.startswith('__'):
                method_names.append(name)
    return method_names

# Get method names for MyClass
methods = get_method_names(MyClass)
print(methods)