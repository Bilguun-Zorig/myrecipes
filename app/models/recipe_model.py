from app import app, recipes_df
from app.config.mysqlconnection import connectToMySQL
import json

class Recipe:
    db = 'recipe_generator'
    
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.ingredient = data['ingredient']
        self.step = data['step']
        self.nutrition = data['nutrition']
        self.description = data['description']
        self.cook_time = data['cook_time']
        self.image_url = data.get('image_url')
        self.user_first_name = data.get('first_name')
        self.user_last_name = data.get('last_name')
        self.user_user_id = data.get('user_id')
        self.num_likes = data.get('num_likes', None)
        
        
    @classmethod
    def get_all_recipes_by_user_id(cls, id):
        query = """
            SELECT recipes.*, users.first_name, users.last_name, 
                (SELECT COUNT(*) FROM user_likes_recipes WHERE recipe_id = recipes.id) AS num_likes
            FROM recipes
            LEFT JOIN users ON users.id = recipes.user_id
            WHERE users.id = %(id)s
        """
        
        # results = connectToMySQL(cls.db).query_db(query, {'id': id})
        # return [cls(data) for data in results]
        results = connectToMySQL(cls.db).query_db(query, {'id': id})
        recipes = []
        for data in results:
            recipe = cls(data)
            recipe.ingredient = cls.format_ingredients(recipe.ingredient)  # Ensure ingredients are formatted
            recipes.append(recipe)
        return recipes

    @staticmethod
    def filter_recipes_by_ingredients_and_category(ingredients, category):
        def recipe_match(recipe_ingredients, recipe_tags):
            return all(ingredient in recipe_ingredients.lower() for ingredient in ingredients) and category in recipe_tags.lower()
        filtered_recipes = recipes_df[recipes_df.apply(lambda row: recipe_match(row['ingredients'], row['tags']), axis=1)]
        return filtered_recipes.to_dict(orient='records')
    
    @staticmethod
    def filter_recipes_by_ids(ids):
        return recipes_df[recipes_df['id'].isin(map(int, ids))].to_dict(orient='records')
    
    @classmethod
    def save_recipe(cls, data):
        query = """
            INSERT INTO recipes (name, ingredient, step, nutrition, description, cook_time, image_url, user_id)
            VALUES (%(name)s, %(ingredient)s, %(step)s, %(nutrition)s, %(description)s, %(cook_time)s, %(image_url)s, %(user_id)s)
        """
        return connectToMySQL(cls.db).query_db(query, data)
    
    
    @classmethod
    def get_all_users_recipes(cls):
        query = """
            SELECT * , (
                        SELECT
                        COUNT(*)
                        FROM user_likes_recipes
                        WHERE recipe_id = recipes.id
                    ) as num_likes
            FROM recipes
            LEFT JOIN users ON users.id = recipes.user_id
        """
        
        # return [cls(data) for data in connectToMySQL(cls.db).query_db(query)]
        results = connectToMySQL(cls.db).query_db(query)
        return results 
    
    @classmethod
    def get_one_recipe_by_id(cls, id):
        
        query = """
            SELECT * , (
                        SELECT
                        COUNT(*)
                        FROM user_likes_recipes
                        WHERE recipe_id = recipes.id
                    ) as num_likes
            FROM recipes
            LEFT JOIN users ON users.id = recipes.user_id
            WHERE 
                recipes.id=%(id)s
        """
        results = connectToMySQL(cls.db).query_db(query, { 'id': id })

        return cls(results[0]) if results else None
    
    @classmethod
    def update_recipe(cls, data):
        if not data.get('image_url'):
            data['image_url'] = None 
        query = """
            UPDATE
                recipes
            SET
                name=%(name)s,
                ingredient=%(ingredient)s,
                step=%(step)s,
                nutrition=%(nutrition)s,
                description=%(description)s,
                cook_time=%(cook_time)s,
                image_url=%(image_url)s
            WHERE
                id=%(id)s
        """

        return connectToMySQL(cls.db).query_db(query, data)
    
    @classmethod
    def delete_recipe(cls, id):
        query = """
            DELETE
            FROM recipes 
            WHERE id = %(id)s
        """
        return connectToMySQL(cls.db).query_db(query, { 'id': id })
    
    @classmethod
    def add_like(cls, recipe_id, user_id):
        query ="""
            INSERT INTO
                user_likes_recipes
            (recipe_id, user_id)
            VALUES
            (%(recipe_id)s, %(user_id)s)   
        """
        result = connectToMySQL(cls.db).query_db(query, {"recipe_id":recipe_id, "user_id": user_id})
        return result
    
    @staticmethod
    def safe_parse(string):
        try:
            parsed_list = json.loads(string)
        except json.JSONDecodeError:
            string = string.strip("[]").replace("'", "")
            parsed_list = [item.strip() for item in string.split(",")]
        return parsed_list

    @staticmethod
    def format_string(string):
        parsed_list = Recipe.safe_parse(string)
        return ', '.join([str(item).strip() for item in parsed_list])

    @staticmethod
    def format_ingredients(ingredients_string):
        return Recipe.format_string(ingredients_string)

    @staticmethod
    def format_steps(steps_string):
        return Recipe.format_string(steps_string)

    @staticmethod
    def format_nutrition(nutrition_string):
        return Recipe.format_string(nutrition_string)
    

    def __str__(self):
        return (f"Recipe: {self.name}\n"
                f"Ingredients: {self.ingredient}\n"
                f"Steps: {self.step}\n"
                f"Nutrition: {self.nutrition}\n"
                f"Description: {self.description}\n"
                f"Cook Time: {self.cook_time}\n")
