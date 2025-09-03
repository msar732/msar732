# Database router for read replicas
class DatabaseRouter:
    """
    A router to control all database operations on models
    """
    
    def db_for_read(self, model, **hints):
        """Suggest the database to read from."""
        return 'default'  # Can be extended for read replicas
    
    def db_for_write(self, model, **hints):
        """Suggest the database to write to."""
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if models are in the same app."""
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that certain apps' models get created on the right database."""
        return True