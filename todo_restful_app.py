import sys
from backend.app import app


if __name__ == '__main__':
    args = sys.argv
    app.run(host='0.0.0.0', port=8081, debug=True if '--debug' in args else False)

