import pytest
from sqlalchemy.exc import IntegrityError
from app import app
from models import db, Recipe, User

class TestRecipe:
    '''Recipe model tests'''

    def create_user(self, username="TestUser"):
        user = User(username=username)
        user.password_hash = "test123"  # triggers setter
        db.session.add(user)
        db.session.commit()
        return user

    def test_has_attributes(self):
        '''Recipe has title, instructions, minutes_to_complete.'''

        with app.app_context():
            db.session.query(Recipe).delete()
            db.session.query(User).delete()
            db.session.commit()

            user = self.create_user()

            recipe = Recipe(
                title="Delicious Shed Ham",
                instructions="""Or kind rest bred with am shed then. In""" +
                    """ raptures building an bringing be. Elderly is detract""" +
                    """ tedious assured private so to visited. Do travelling""" +
                    """ companions contrasted it. Mistress strongly remember""" +
                    """ up to. Ham him compass you proceed calling detract.""" +
                    """ Better of always missed we person mr. September""" +
                    """ smallness northward situation few her certainty""" +
                    """ something.""",
                minutes_to_complete=60,
                user_id=user.id
            )

            db.session.add(recipe)
            db.session.commit()

            new_recipe = Recipe.query.filter_by(title="Delicious Shed Ham").first()

            assert new_recipe.title == "Delicious Shed Ham"
            assert new_recipe.minutes_to_complete == 60
            assert new_recipe.user_id == user.id

    def test_requires_title(self):
        '''Recipe requires a title.'''

        with app.app_context():
            db.session.query(Recipe).delete()
            db.session.query(User).delete()
            db.session.commit()

            user = self.create_user("User2")

            recipe = Recipe(
                instructions="Long enough instructions to pass..." * 2,
                minutes_to_complete=30,
                user_id=user.id
            )

            with pytest.raises(IntegrityError):
                db.session.add(recipe)
                db.session.commit()

    def test_requires_50_plus_char_instructions(self):
        '''Instructions must be 50+ characters.'''

        with app.app_context():
            db.session.query(Recipe).delete()
            db.session.query(User).delete()
            db.session.commit()

            user = self.create_user("User3")

            with pytest.raises(ValueError):
                recipe = Recipe(
                    title="Short Instructions",
                    instructions="Too short to pass.",
                    minutes_to_complete=15,
                    user_id=user.id
                )
                db.session.add(recipe)
                db.session.commit()
