from app import db


class ModelMixin(object):

    def save(self, commit=True):
        # Save this model to the database.
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self):
        """delete the DB entity

        Returns:
            db.Model: the entity
        """
        db.session.delete(self)
        db.session.commit()
        return self

# Add your own utility classes and functions here.
