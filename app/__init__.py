import pandas as pd
from flask import Flask
app = Flask(__name__)



app.secret_key = "recipe_secret_key"
# Load the CSV file into a DataFrame
recipes_df = pd.read_csv('./recipes_dataset/recipes.csv')
