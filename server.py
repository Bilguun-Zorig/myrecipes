from app import app

# import controllers
from app.controllers import user_controller, recipe_controller

if __name__ == "__main__":
    app.run(debug=True)