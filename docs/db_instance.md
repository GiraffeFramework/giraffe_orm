Create a database instance
```py
from giraffe_orm import GiraffeORM

db = GiraffeORM()
```

In order for Giraffe to discover your models, required for migrations, this 
instance must be discovereable. There are 3 methods applied to find your 
instance.

1. The instance is created inside a file named `app.py` or `main.py`.

2. An environment variable exists pointing to your instance

```shell
$env:GIRAFFE_APP = "src.database:db"
```

3. If you only use the CLI for migrations, you specify a flag

```shell
python -m giraffe_orm -A src.database:db migrate
```
