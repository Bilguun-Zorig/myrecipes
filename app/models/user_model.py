import re
from app import app
from flask import flash
from app.config.mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'[a-zA-Z]')
PASSWORD_REGEX = re.compile(r'^(?=.*[A-Z])(?=.*[0-9]).{8,}$')

bcrypt = Bcrypt(app)


class User:
    
    db = 'recipe_generator'
    
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email_address = data['email_address']
        self.password = data['password']
        
        
    @classmethod
    def register_user(cls, data):
        
        data['password'] = bcrypt.generate_password_hash(data['password'])
        
        query = """
            INSERT INTO 
                users
            (first_name, last_name, email_address, password)
            VALUES
            (%(first_name)s, %(last_name)s, %(email_address)s, %(password)s)
        """
        
        return connectToMySQL(cls.db).query_db(query, data)
        
    
    @classmethod
    def get_by_email(cls, email_address):
        query = """
            SELECT 
                *
            FROM
                users
            WHERE 
                email_address = %(email_address)s
        """
        results = connectToMySQL(cls.db).query_db(query, {'email_address':email_address})

        # if not results:
        #     return None
        return cls(results[0]) if results else None
    
    @classmethod
    def get_one_by_id(cls, id):
        
        query = """
            SELECT 
                *
            FROM 
                users
            WHERE 
                users.id=%(id)s
                ;
        """

        results = connectToMySQL(cls.db).query_db(query, { 'id': id })
        
        #check the result if you get error or not
        if not results:
            return None
        
        user = cls(results[0])

        return user 
    
    
    @staticmethod
    def validate_registration(registration_form):
        is_valid = True 
        
        #? check if user exist
        if User.get_by_email(registration_form['email_address']):
            is_valid = False
            flash("Email address already exists.", "email_address")
        #? Check first name and last name
        if len(registration_form['first_name']) < 3:
            is_valid = False
            flash("First name must be at least 3 characters.", "first_name")
            
        if not NAME_REGEX.match(registration_form['first_name']):
            is_valid = False
            flash("Name must contain only letters", "first_name")
            
        if len(registration_form['last_name']) < 3:
            is_valid = False
            flash("Last name must be at least 3 characters.", "last_name")
        
        if not NAME_REGEX.match(registration_form['last_name']):
            is_valid = False
            flash("Name must contain only letters", "last_name")
        
        #? Check password length
        if not PASSWORD_REGEX.match(registration_form['password']):
            flash("Invalid password format, and must be 8 characters, contain at least 1 uppercase letter, and at least 1 number", "password")
            is_valid = False
            
        
        #? Compare password and confirm password
        if registration_form['password'] != registration_form['confirm_password']:
            is_valid = False
            flash("Password must match.", "confirm_password")
        
        #? Check email
        if len(registration_form['email_address']) == 0:
            flash('Email is required', 'email_address')
            is_valid = False
        if not EMAIL_REGEX.match(registration_form['email_address']): 
            flash("Invalid email address!", 'email_address')
            is_valid = False

        if is_valid:
            flash('Thanks for registering', 'registration')
        
        return is_valid
