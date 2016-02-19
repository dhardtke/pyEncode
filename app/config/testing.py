SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
TESTING = True
PRESERVE_CONTEXT_ON_EXCEPTION = False
# disable CSRF checking when testing to allow form-validation testing
WTF_CSRF_ENABLED = False
