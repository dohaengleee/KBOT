class MultiDBRouter(object):
    def __init__(self):
        self.model_list = ['api_admin', 'lab2ai_article', 'baseball', 'minor_baseball', 'real_minor_baseball']

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to auth_db.
        """
        if model._meta.app_label in self.model_list:
            return model._meta.app_label

        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to auth_db.
        """
        if model._meta.app_label in self.model_list:
            return model._meta.app_label

        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        if obj1._meta.app_label in self.model_list or \
                obj2._meta.app_label in self.model_list:
            return True

        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth app only appears in the 'auth_db'
        database.
        """
        if app_label == 'api_admin':
            return db in self.model_list
        elif db == 'default':
            return True

        return None
