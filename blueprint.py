from user_module.user_routes import user_blueprint  # User module
from staff_module.staff_details import staff_module  # Staff module
from worker_module.worker_details import worker_module  # Worker module

def register_blueprints(app):
    app.register_blueprint(user_blueprint, url_prefix='/user_module')  # User module
    app.register_blueprint(staff_module, url_prefix='/staff')  # Staff module
    app.register_blueprint(worker_module, url_prefix='/worker')  # Worker module