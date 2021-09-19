from uvicorn import run

if __name__ == '__main__':
    run('backend.app:app', host='0.0.0.0', port=9000)

