from app import app, csrf
# from grocery_api.utils.google_oauth import oauth


# oauth.init_app(app)
#  API Routes
from grocery_api.blueprints.users.views import users_api_blueprint
from grocery_api.blueprints.sessions.views import sessions_api_blueprint
from grocery_api.blueprints.cuisines.views import cuisines_api_blueprint
from grocery_api.blueprints.ingredients.views import ingredients_api_blueprint
from grocery_api.blueprints.carts.views import carts_api_blueprint
from grocery_api.blueprints.payments.views import payments_api_blueprint
from grocery_api.blueprints.orders.views import orders_api_blueprint

app.register_blueprint(users_api_blueprint, url_prefix='/api/v1/users')
app.register_blueprint(sessions_api_blueprint, url_prefix='/api/v1/sessions')
app.register_blueprint(cuisines_api_blueprint, url_prefix='/api/v1/cuisines')    
app.register_blueprint(ingredients_api_blueprint, url_prefix='/api/v1/ingredients')
app.register_blueprint(carts_api_blueprint, url_prefix='/api/v1/carts')       
app.register_blueprint(payments_api_blueprint, url_prefix='/api/v1/payments')   
app.register_blueprint(orders_api_blueprint, url_prefix='/api/v1/orders')
                                  
csrf.exempt(users_api_blueprint)
csrf.exempt(sessions_api_blueprint) 
csrf.exempt(cuisines_api_blueprint)
csrf.exempt(ingredients_api_blueprint)
csrf.exempt(carts_api_blueprint)
csrf.exempt(payments_api_blueprint)
csrf.exempt(orders_api_blueprint)