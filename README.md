# sql2func

Run SQL as a function!

## Example

```python
from dataclasses import dataclass
from typing import List

import mariadb
from sql2func import SqlContext, select
from sql2func.dbapi2 import Connection


@dataclass
class Foobar:
    """
    Foobar data class
    """
    fb_id: int
    foo: str
    bar: str


@select(statement='''
SELECT fb_id, foo, bar
FROM tbl_foobar
WHERE foo = {{ foo }}
''')
def select_foobars(foo: str) -> List[Foobar]:
    pass


@update(statement='''
UPDATE tbl_foobar
SET bar = {{ bar }}
WHERE fb_id = {{ fb_id }}
''')
def update_foobar(fb_id: int, bar: str) -> int:
    pass


def connect_to_db() -> Connection:
    return mariadb.connect(
        host='localhost',
        user='db_user',
        password='db_password',
        database='db_name'
    )


def _main():
    with SqlContext(connector=connect_to_db):
        # All SQLs in this context will be run via one DB connection.
        # Run select.
        for result in select_foobars(foo='foo'):
            print(result)
        # Run update.
        update_foobar(fb_id=1, bar='blabla')
    # DB connection will be closed after SqlContext exited.


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
