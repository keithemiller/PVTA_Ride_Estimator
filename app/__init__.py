from .api import api as api_blueprint
app.register_blueprint(api_blueprint, url_prefix='/api')
