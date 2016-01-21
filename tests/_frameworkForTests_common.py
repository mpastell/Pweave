class ParametricTestsMetaclass(type):
    def __new__(mcl, name, bases, attrs):
        try:
            tests = attrs['__tests']
            testGenerator = attrs['__testGenerator']

        except KeyError:
            pass

        else:
            del attrs['__tests']
            del attrs['__testGenerator']

            for name, params in tests.items():
                args, kwargs = params
                attrs['test' + name] = testGenerator(*args, **kwargs)

        return type.__new__(mcl, name, bases, attrs)