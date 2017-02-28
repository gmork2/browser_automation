import pytest

from utils.loading import import_string


class TestModuleImport:
    def test_import_string(self):
        cls = import_string('utils.loading.import_string')
        assert cls == import_string

        # Test exceptions raised
        with pytest.raises(ImportError):
            import_string('no_dots_in_path')
        msg = 'Module "utils" does not define a "unexistent" attribute'
        with pytest.raises(ImportError) as excinfo:
            import_string('utils.unexistent')
        assert msg in str(excinfo)

