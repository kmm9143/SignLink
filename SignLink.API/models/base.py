# DESCRIPTION:  This script defines the base class for all SQLAlchemy ORM models in the project.
#               The `Base` object serves as the foundation for all model classes, enabling
#               declarative mapping between Python classes and database tables. All ORM models
#               should inherit from this `Base` to ensure proper metadata management and schema generation.
# LANGUAGE:     PYTHON
# SOURCE(S):    [1] SQLAlchemy Documentation. (n.d.). ORM Declarative Mapping. Retrieved October 4, 2025, from https://docs.sqlalchemy.org/en/20/orm/declarative_mapping.html
#               [2] SQLAlchemy Documentation. (n.d.). ORM Quick Start. Retrieved October 4, 2025, from https://docs.sqlalchemy.org/en/20/orm/quickstart.html

# -------------------------------------------------------------------
# Step 1: Import required SQLAlchemy module for declarative base
# -------------------------------------------------------------------
from sqlalchemy.ext.declarative import declarative_base                 # Base class factory for declarative ORM models

# -------------------------------------------------------------------
# Step 2: Initialize declarative base class for all ORM models
# -------------------------------------------------------------------
Base = declarative_base()                                               # Shared base class for all SQLAlchemy model definitions