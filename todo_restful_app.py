from backend.app import app


if __name__ == '__main__':
    global name
    import sys
    name = sys.argv[1]
    app.run(host='0.0.0.0', port=9000)

