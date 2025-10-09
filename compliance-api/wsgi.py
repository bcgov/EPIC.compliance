def create_wsgi_app():
    """Create and configure the WSGI application after monkey patching."""
    # from gevent import monkey
    # monkey.patch_all()

    from compliance_api import create_app
    return create_app()


application = create_wsgi_app()

if __name__ == "__main__":
    application.run(debug=True, host='0.0.0.0', port=3200)
