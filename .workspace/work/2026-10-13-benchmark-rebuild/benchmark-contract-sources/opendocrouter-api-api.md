# Parse

Types:

```python
from opendocrouter.types import ParseRecord, ParseDeleteResponse
```

Methods:

- <code title="post /v1/parse">client.parse.<a href="./src/opendocrouter/resources/parse.py">create</a>(\*\*<a href="src/opendocrouter/types/parse_create_params.py">params</a>) -> <a href="./src/opendocrouter/types/parse_record.py">ParseRecord</a></code>
- <code title="delete /v1/parse/{id}">client.parse.<a href="./src/opendocrouter/resources/parse.py">delete</a>(id) -> <a href="./src/opendocrouter/types/parse_delete_response.py">ParseDeleteResponse</a></code>
- <code title="get /v1/parse/{id}">client.parse.<a href="./src/opendocrouter/resources/parse.py">get</a>(id, \*\*<a href="src/opendocrouter/types/parse_get_params.py">params</a>) -> <a href="./src/opendocrouter/types/parse_record.py">ParseRecord</a></code>

# Uploads

Types:

```python
from opendocrouter.types import Upload
```

Methods:

- <code title="post /v1/uploads">client.uploads.<a href="./src/opendocrouter/resources/uploads.py">create</a>() -> <a href="./src/opendocrouter/types/upload.py">Upload</a></code>

# Credits

Types:

```python
from opendocrouter.types import Credits
```

Methods:

- <code title="get /v1/credits">client.credits.<a href="./src/opendocrouter/resources/credits.py">get</a>() -> <a href="./src/opendocrouter/types/credits.py">Credits</a></code>

# Models

Types:

```python
from opendocrouter.types import ModelListResponse
```

Methods:

- <code title="get /v1/models">client.models.<a href="./src/opendocrouter/resources/models.py">list</a>() -> <a href="./src/opendocrouter/types/model_list_response.py">ModelListResponse</a></code>
