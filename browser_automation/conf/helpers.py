import os
import logging


logger = logging.getLogger(__name__)

def get_default_config_dir(filename=None):
    import platform

    if platform.system in ('Windows', 'Microsoft'):
        def save_config_path(resource):
            app_data_path = os.environ.get('APPDATA')
            if not app_data_path:
                import _winreg
                hkey = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
                                       'Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders')
                app_data_reg = _winreg.QueryValueEx(hkey, 'AppData')
                app_data_path = app_data_reg[0]
                _winreg.CloseKey(hkey)
            return os.path.join(app_data_path, resource)
