# pymockREST

### Methods
|Method	|Path|	Action|	Parameters|	Headers|
|GET|	/v1|	Main endpoint and returns API's status.|	-|	-|
|POST|	/v1/login	|Logs into the API.|	username: String password: String	|Content-Type: application/json|
|GET	|/v1/users	|Returns all users.	|-	|-|
|GET	|/v1/users/:id|	Returns a user with the given ID.|	-|	-|
|POST	|/v1/users|	Creates a new user.	|username: String password: String name: String email: String|	Content-Type: application/json|
|DELETE|	/v1/users/:id|	Deletes a user.|	-|	Authorization: Token|
|PATCH|	/v1/users/:id|	Updates user's information.|	Fields in /v1/login	|Authorization: Token|
|GET	|/v1/posts|	Returns all blog posts.	|-	|-|
|GET	|/v1/posts/:id|	Returns a blog post with the given ID.|	-	|-|
|POST	|/v1/posts|	Creates a new blog post.	|title: String content: String tags: String	|Authorization: Token
Content-Type: application/json|
|DELETE	|/v1/posts/:id|	Deletes a blog post.|	-	|Authorization: Token|
|PATCH|	/v1/posts/:id	|Updates a blog post.	|Fields in /v1/posts	|Authorization: Token
Content-Type: application/json|
