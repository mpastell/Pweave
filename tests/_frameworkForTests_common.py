class ParametricTestsMetaclass(type):
    def __new__(mcl, name, bases, attrs):
        try:
            tests = attrs['_tests']
            testGenerator = attrs['_testGenerator']

        except KeyError:
            pass

        else:
            del attrs['_tests']
            del attrs['_testGenerator']

            for name, params in tests.items():
                args, kwargs = params
                methodName = 'test' + name
                attrs[methodName] = testGenerator(methodName, *args, **kwargs)

        return type.__new__(mcl, name, bases, attrs)