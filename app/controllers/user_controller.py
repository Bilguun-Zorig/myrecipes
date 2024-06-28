from app import app
from flask import Flask, render_template, session, redirect, request, flash
from flask_bcrypt import Bcrypt

from app.models.user_model import User

bcrypt = Bcrypt(app)

@app.route('/')
def get_generate_recipe_form():
    from app.models.recipe_model import Recipe
    all_recipes = Recipe.get_all_users_recipes()
    
    # Group recipes by user
    user_recipes = {}
    for recipe in all_recipes:
        user_id = recipe['user_id']
        # print("RECIPE ID ", recipe['id'])
        if user_id not in user_recipes:
            user_recipes[user_id] = {
                'user_first_name': recipe['first_name'],
                'user_last_name': recipe['last_name'],
                'recipes': []
            }
        user_recipes[user_id]['recipes'].append({
            'name': recipe['name'],
            'num_likes': recipe['num_likes'],
            'image_url': recipe['image_url'],
            'id': recipe['id'],
            'ingredient': recipe['ingredient'],
            'step': recipe['step'],
            'nutrition': recipe['nutrition'],
            'description': recipe['description'],
            'cook_time': recipe['cook_time']
        })
    
    return render_template('/ingredient_and_recipe/generate_recipe.html', user_recipes=user_recipes)

@app.route('/user/login')
def user_login():
    return render_template('/user/login.html')

@app.route('/user/register')
def user_register():
    return render_template('/user/register.html')

@app.route('/user/register', methods = ['POST'])
def register():
    
    form = request.form 
    
    data = {
            "first_name": form["first_name"],
            "last_name": form["last_name"],
            "email_address": form["email_address"],
            "password": form["password"],
        }
    
    if User.validate_registration(form):
        User.register_user(data)
        return redirect('/user/login')
    return redirect('/user/register')

@app.route('/user/login', methods=["POST"])
def login():
    form = request.form
    user = User.get_by_email(form.get('email_address'))
    
    if not user or not bcrypt.check_password_hash(user.password, form['password']):
        flash("Invalid Credentials", 'login')
        return redirect('/user/login')
    
    session['user_id'] = user.id
    print("USER ID ", session['user_id'])
    
    return redirect('/')
    
@app.route('/user/logout')
def logout():
    session.clear()
    return redirect('/user/login')