from flask import Flask

app = Flask(__name__)

from src.views import fbudget
from src.views import pbudget
from src.views import user

app.register_blueprint(user.user_blueprint)
app.register_blueprint(fbudget.family_budgets_blieprint)
app.register_blueprint(pbudget.personal_budgets_blieprint)
