# sql2func

Execute SQL as a function, and convert result to object.

## Example

```python
from dataclasses import dataclass
from typing import List

import mariadb
from sql2func import SqlContext, select
from sql2func.dbapi2 import Connection


def connect_to_db() -> Connection:
    return mariadb.connect(
        host='localhost',
        user='db_user',
        password='db_password',
        database='db_name'
    )


@dataclass
class Result:
    a: str
    b: str

@select(statement='''
SELECT a,b
FROM table
WHERE key = {{ key }}
''')
def query_result(key: str) -> List[Result]:
    pass


def _main():
    with SqlContext(connector=connect_to_db):
        for result in query_result(key='foo'):
            print(result)


if __name__ == '__main__':
    _main()
```


## Install

```bash
# Install release version
pip install sql2funcs

# Install develop version
pip install git+https://github.com/deadblue/sql2func.git@develop
```
