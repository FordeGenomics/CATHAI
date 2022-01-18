#!/bin/bash

flask shell <<EOF
from app.models import User
print("Checking state...")
try:
    User.query.first()
    print("Good!")
except:
    print("Setting up DB and defaults")
    import manager
    manager.recreate_db()
    manager.setup_prod()
    print("Done")

EOF

