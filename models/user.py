from models.base_model import BaseModel
from flask_login import UserMixin
import peewee as pw
import re


class User(UserMixin, BaseModel):
    username = pw.CharField(index=True, unique=True)
    email = pw.CharField(unique=True)
    hashed_password = pw.CharField(null = False)
    password = None
    profile_picture = pw.CharField(default='https://i.stack.imgur.com/l60Hf.png')
    phone_number = pw.IntegerField(default=None, null=True)
    is_admin = pw.BooleanField(default=False)

    
    def validate(self):
        duplicate_username = User.get_or_none(User.username == self.username)
        duplicate_email = User.get_or_none(User.email == self.email)

        if duplicate_username:
            self.errors.append('Username exists')

        if duplicate_email:
            self.errors.append('Email has been registered!')

        if len(self.username.strip())==0:
            self.errors.append('Username cannot be blank!')
        
        if len(self.email.strip())==0:
            self.errors.append('Email cannot be blank!')

        if re.match("\w+@\w+.\w+", self.email):
            pass
        else:
            self.errors.append('Email format is not correct!')

        if self.password == None:
            pass
        else:
            if len(self.password.strip())==0:
                self.errors.append('Password cannot be blank!')

            elif len(self.password.strip())<8:
                self.errors.append('Password need at least 8 characters!')
            
            elif any(letter.isupper() for letter in self.password) and any(letter.islower() for letter in self.password) and any(re.search("\W{1,}", letter) for letter in self.password):
                pass

            else:
                self.errors.append('Password must consists of at least one uppercase, one lowercase and one special character')
            
