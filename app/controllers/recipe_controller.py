from app import app, recipes_df
from flask import Flask, render_template, session, redirect, request, flash

from app.models.recipe_model import Recipe


@app.route('/user/all/recipes')
def my_recipes():
    if 'user_id' not in session:
        return redirect('/user/login')
    user_id = session['user_id']
    recipes = Recipe.get_all_recipes_by_user_id(user_id)
    for recipe in recipes:
        recipe.ingredient = Recipe.format_ingredients(recipe.ingredient)
        recipe.step = Recipe.format_steps(recipe.step)
        recipe.nutrition = Recipe.format_nutrition(recipe.nutrition)
    return render_template('/ingredient_and_recipe/my_recipes.html', recipes = recipes, logged_in=user_id)


@app.route('/generate/recipe', methods=['POST'])
def generate_recipe():
    # Clear previous generated recipes in session
    session.pop('generated_recipe_ids', None)
    
    ingredients = request.form.get('ingredients')
    category = request.form.get('category')

    if ingredients and category:
        ingredients_list = [ingredient.strip().lower() for ingredient in ingredients.split()]
        recipes = Recipe.filter_recipes_by_ingredients_and_category(ingredients_list, category)
        recipe_ids = [recipe['id'] for recipe in recipes]

        # Store only the recipe IDs in the session
        session['generated_recipe_ids'] = recipe_ids
        print(f"Session updated with new recipe IDs: {session['generated_recipe_ids']}")
        return redirect('/show_recipes')

    flash("Please enter ingredients and select a category to generate recipes.")
    return redirect('/generate_recipe_form')


@app.route('/show_recipes')
def show_recipes():
    recipe_ids = session.get('generated_recipe_ids', [])
    recipes = Recipe.filter_recipes_by_ids(recipe_ids)
    for recipe in recipes:
        recipe['ingredients'] = Recipe.format_ingredients(recipe['ingredients'])
        recipe['steps'] = Recipe.format_steps(recipe['steps'])
        recipe['nutrition'] = Recipe.format_nutrition(recipe['nutrition'])
    logged_in = 'user_id' in session
    return render_template('ingredient_and_recipe/show_recipes.html', recipes=recipes, logged_in=logged_in)


@app.route('/generate_recipe_form')
def generate_recipe_form():
    all_recipes = Recipe.get_all_users_recipes()
    user_recipes = {}
    for recipe in all_recipes:
        user_id = recipe['user_id']
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
            'ingredient': Recipe.format_ingredients(recipe['ingredient']),
            'step': Recipe.format_steps(recipe['step']),
            'nutrition': Recipe.format_nutrition(recipe['nutrition']),
            'description': recipe['description'],
            'cook_time': recipe['cook_time']
        })
    return render_template('/ingredient_and_recipe/generate_recipe.html', user_recipes=user_recipes)


@app.route('/generate/one/recipe/<int:id>')
def generate_one_recipe(id):
    # Retrieve the recipe details from the DataFrame
    recipe_row = recipes_df.loc[recipes_df['id'] == id]
    print(f"Looking for recipe with ID: {id}, found: {not recipe_row.empty}")
    
    if not recipe_row.empty:
        recipe = recipe_row.iloc[0].to_dict()
        recipe['ingredients'] = Recipe.format_ingredients(recipe['ingredients'])
        recipe['steps'] = Recipe.format_steps(recipe['steps'])
        recipe['nutrition'] = Recipe.format_nutrition(recipe['nutrition'])
        logged_in = 'user_id' in session
        return render_template('ingredient_and_recipe/show_one_recipe.html', recipe=recipe, logged_in=logged_in)
    
    flash("Recipe not found.")
    return redirect('/')


@app.route('/user/save/recipes', methods=['POST'])
def save_selected_recipes():
    if 'user_id' not in session:
        flash("You need to log in to save recipes.")
        return redirect('/generate/recipe')

    selected_recipe_ids = request.form.getlist('selected_recipes')
    print("!!!! SELECTED RECIPE ", selected_recipe_ids)
    if selected_recipe_ids:
        recipes_data = Recipe.filter_recipes_by_ids(selected_recipe_ids)
        print("!!!! Recipe data ", recipes_data)
        for recipe_data in recipes_data:
            Recipe.save_recipe({
                'name': recipe_data['name'],
                'ingredient': recipe_data['ingredients'],
                'step': recipe_data['steps'],
                'nutrition': recipe_data['nutrition'],
                'description': recipe_data['description'],
                'cook_time': recipe_data['minutes'],
                'image_url': None,
                'user_id': session['user_id']
            })

    flash("Selected recipes have been saved.")
    return redirect('/user/all/recipes')


@app.route('/user/recipes/<int:id>')
def get_user_recipes(id):
    user_all_recipe = Recipe.get_all_recipes_by_user_id(id)
    user_first_name = user_all_recipe[0].user_first_name
    # print("!!!! User Recipes", user_first_name)
    return render_template('/ingredient_and_recipe/users_recipes.html', user_all_recipe=user_all_recipe, first_name = user_first_name)

@app.route('/user/recipe/add')
def get_add_recipe_form():
    if not 'user_id' in session:
        return redirect('/')
    return render_template("/ingredient_and_recipe/add_recipe.html")

@app.route('/user/recipe/add', methods=['POST'])
def get_add_new_recipe_by_user():
    if not 'user_id' in session:
        return redirect('/')
    Recipe.save_recipe({
        **request.form,
        'user_id': session['user_id'],
        'image_url': request.form['image_url']
    })
    return redirect('/user/all/recipes')

@app.route('/user/recipe/update/<int:recipe_id>')
def get_update_recipe_form(recipe_id):
    if not 'user_id' in session:
        return redirect('/')
    return render_template("/ingredient_and_recipe/update_recipe.html", recipe = Recipe.get_one_recipe_by_id(recipe_id))

@app.route('/user/recipe/update', methods=["POST"])
def update_recipe():
    if not 'user_id' in session:
        return redirect('/')
    Recipe.update_recipe(request.form)
    return redirect('/user/all/recipes')


@app.route('/user/recipe/delete/<int:id>')
def delete_chore(id):
    Recipe.delete_recipe(id)
    return redirect('/user/all/recipes')

@app.route('/user/recipes/like/<int:recipe_id>')
def like_recipe(recipe_id):
    if not 'user_id' in session:
        return redirect('/')
    
    Recipe.add_like(recipe_id, int(session['user_id']))
    # return redirect('/')
    return redirect(request.referrer)


@app.route('/user/recipe/<int:id>')
def get_one_recipe(id):
    recipe = Recipe.get_one_recipe_by_id(id)
    recipe.ingredient = Recipe.format_ingredients(recipe.ingredient)
    recipe.step = Recipe.format_steps(recipe.step)
    recipe.nutrition = Recipe.format_nutrition(recipe.nutrition)
    return render_template("/ingredient_and_recipe/one_recipe.html", recipe=recipe)