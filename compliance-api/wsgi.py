def create_wsgi_app():
    """Create and configure the WSGI application after monkey patching."""
    from compliance_api import create_app
    return create_app()


application = create_wsgi_app()

if __name__ == "__main__":
    # Local convenience only - never used by gunicorn (see docker-entrypoint.sh).
    # debug=False and a loopback-only bind keep the Werkzeug debugger (arbitrary
    # code execution via its interactive console) from ever being reachable.
    application.run(debug=False, host='127.0.0.1', port=3200)
