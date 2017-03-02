def get_runner(test_runner_class=None):
    if not test_runner_class:
        test_runner_class = 'core.test.runner.HTMLTestRunner'

    test_path = test_runner_class.split('.')
    # Allow for Python 2.5 relative paths
    if len(test_path) > 1:
        test_module_name = '.'.join(test_path[:-1])
    else:
        test_module_name = '.'
    test_module = __import__(test_module_name, {}, {}, test_path[-1])
    test_runner = getattr(test_module, test_path[-1])
    return test_runner

