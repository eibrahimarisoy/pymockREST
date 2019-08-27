# pymockREST

PyMock is a simple mock REST API written with Flask. 

### Methods
| Method | Path | Action | Parameters | Headers |
| ------ | ------ | ------ | ------ | ------ |
|GET|	/api|	Main endpoint and returns API's status.|	-|	-|
|POST|	/api/login	|Logs into the API.|	username: String password: String	|Content-Type: application/json|
|GET	|/api/users	|Returns all users.	|-	|-|
|GET	|/api/users/:id|	Returns a user with the given ID.|	-|	-|
|POST	|/api/users|	Creates a new user.	|username: String password: String name: String email: String|	Content-Type: application/json|
|DELETE|	/api/users/:id|	Deletes a user.|	-|	Authorization: Token|
|PATCH|	/api/users/:id|	Updates user's information.|	Fields in /api/login	|Authorization: Token|
|GET	|/api/posts|	Returns all blog posts.	|-	|-|
|GET	|/api/posts/:id|	Returns a blog post with the given ID.|	-	|-|
|POST	|/api/posts|	Creates a new blog post.	|title: String content: String tags: String	|Authorization: Token Content-Type: application/json|
|DELETE	|/api/posts/:id|	Deletes a blog post.|	-	|Authorization: Token|
|PATCH|	/api/posts/:id	|Updates a blog post.	|Fields in /api/posts	|Authorization: Token Content-Type: application/json|
