from os.path import join, dirname, abspath, exists
import json
__CONF_FILE_NAME__ = 'backend.json'
__CONF_FILE_PATH__ = join(dirname(dirname(abspath(__file__))), 'conf', __CONF_FILE_NAME__)


class Config:
    @staticmethod
    def get(value):
        data = None
        try:
            if exists(__CONF_FILE_PATH__):
                with open(file=__CONF_FILE_PATH__) as file:
                    data = json.load(file)
                    return data[value]
            return False
        except Exception as e:
            raise Exception(f'Key not in file `{__CONF_FILE_PATH__}`')