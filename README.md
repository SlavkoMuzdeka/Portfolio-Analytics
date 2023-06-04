# Portfolio Analytics

## Project Motivation
The project aims to simplify portfolio management and provide users with a comprehensive platform to track their investments and asset price history efficiently. By centralizing portfolio and asset data, the project seeks to alleviate the complexities and manual efforts associated with monitoring and analyzing investment performance.
Through intuitive data visualization and insights, the project empowers users to make informed decisions based on historical trends, enabling them to optimize their investment strategies.
The motivation behind the project is to create a personalized experience, tailoring the platform to individual preferences and allowing users to set alerts and notifications aligned with their investment goals.
The project's motivation stems from the belief that accessible and user-friendly tools are essential to democratize financial information and make it comprehensible for investors of all levels of expertise.
Ultimately, the project's continuous improvement and incorporation of user feedback aim to refine the platform's functionality and provide a reliable and trusted resource for portfolio management.

## Getting started

The project adheres to the PEP 8 style guide and follows common best practices, including:

* Variable and function names are clear.
* Endpoints are logically named.
* Code is commented appropriately.
* Secrets are stored as environment variables.

### Key Dependencies & Platforms

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

- [PostgreSQL](https://www.postgresql.org/) this project is integrated with a popular relational database PostgreSQL, though other relational databases can be used with a little effort.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Auth0](https://auth0.com/docs/) is the authentication and authorization system we'll use to handle users with different roles with more secure and easy ways

- [Heroku](https://www.heroku.com/what) is the cloud platform used for deployment

### Running Locally

#### Installing Dependencies

##### Python 3.11

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

##### Virtual Environment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virtual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

Once you have your virtual environment setup and running, install dependencies by running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

#### Database Setup
With Postgres running, restore a database using the `capstone.psql` file provided. In terminal run:

```bash
createdb capstone
psql -U <username> -d <database_name> -f capstone.psql
```

#### Running Tests
To run the tests, in one terminal run:
```bash
python app.py
```

In another terminal run:
```bash
python test_app.py
```

#### Auth0 Setup

You need to setup an Auth0 account.
Environment variables needed: (setup.sh)

```bash
export AUTH0_DOMAIN='<your_auth0_domain>'
export ALGORITHMS='<your_algorithms>'
export API_AUDIENCE='<your_api_audience>'
```

##### Roles

Create two roles for users under `Users & Roles` section in Auth0

* User (which represent readers)
	* Can read/get information about portfolio and asset price history
* Admin
	* All permissions a User has and…
	* Add, update and delete a portfolio and asset price history

##### Permissions

Following permissions should be created under created API settings.

* `get:portfolios`
* `get:asset_price_histories`
* `post:portfolios`
* `patch:asset_price_histories`
* `delete:portfolios`

##### Set JWT Tokens in `auth_config.json`

Use the following link to create users and sign them in. This way, you can generate 

```
https://{{YOUR_DOMAIN}}/authorize?audience={{API_IDENTIFIER}}&response_type=token&client_id={{YOUR_CLIENT_ID}}&redirect_uri={{YOUR_CALLBACK_URI}}
```

#### Launching The App

1. Initialize and activate a virtualenv:

    ```bash
    # Creating a virtual environment

    # Unix/maxOS
    python3 -m venv env_capstone

    # Windows
    python -m venv env_capstone

    # Activating a virtual environment

    # Unix/maxOS
    source env_capstone/bin/activate

    # Windows
    .\env_capstone\Scripts\activate

    ```

2. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Configure database path to connect local postgres database in `models.py`
    
    ```python
    DATABASE_PATH = "postgresql://{}:{}@{}/{}".format(
    DATABASE_USER, DATABASE_PASS, DATABASE_HOST, DATABASE_NAME
    )
    ```       

4. Setup the environment variables for Auth0 under `setup.sh` running:
	```bash
	source ./setup.sh 
	```

5.  To run the server locally, execute:

    ```bash
    python app.py
    ```

## API Documentation

### Models
There are two models:
* Portfolio
	* asset_class_desc
	* weight
    * benchmark_desc
	* sort_id
    * bloomberg_qry
* AssetPriceHistory
	* asset_type
	* price
	* date
    * portfolio_id

### Error Handling

Errors are returned as JSON objects in the following format:
```json
{
    "success": False, 
    "error": 400,
    "message": "bad request"
}
```
The API will return three error types when requests fail:
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Resource Not Found
- 405: Method Not Allowed
- 422: Not Processable 
- 500: Internal Server Error

#### GET /portfolios 
* Get all portfolios

* Require `get:portfolios` permission

* **Example Request:** `curl 'http://localhost:8080/portfolios'`

* **Expected Result:**
    ```json
    {
        "portfolios": [
            {
                "asset_class_desc": "some_asset_class_desc",
                "benchmark_desc": "some_benchmark_desc",
                "bloomberg_qry": "some_bloomberg_qry",
                "id": 478,
                "sort_id": 445,
                "weight": 23.3
            }
        ],
        "success": true
    }
    ```

#### GET /asset_price_histories 
* Get all asset price histories

* Requires `get:asset_price_histories` permission

* **Example Request:** `curl 'http://localhost:8080/asset_price_histories'`

* **Expected Result:**
    ```json
    {
        "asset_price_histories": [
            {
                "asset_type": "some_asset_type",
                "date": "02-03-2019",
                "id": 309,
                "portfolio_id": 478,
                "price": 23.3
            }
        ],
        "success": true
    }
    ```

#### POST /portfolios
* Creates a new portfolio.

* Requires `post:portfolios` permission

* Requires the asset class description, weight, benchmark description, sort id and bloomberg query.

* **Example Request:** (Create)
    ```bash
	curl --location --request POST 'http://localhost:8080/portfolios' \
		--header 'Content-Type: application/json' \
		--data-raw '{
			"asset_class_desc": "Description",
			"weight": 22,
            "benchmark_desc":"Benchmark description",
            "sort_id": 1,
            "bloomberg_qry":"new_query"
		}'
    ```

* **Example Response:**
    ```bash
	{
		"success": true
	}
    ```

#### PATCH /asset_price_histories/<int:id>/edit
* Updates the asset price history where <asset_price_histories_id> is the existing asset price history id

* Require `patch:asset_price_histories` permission

* Responds with a 404 error if <asset_price_histories_id> is not found

* Update the corresponding fields for AssetPriceHistory with id <asset_price_histories_id>

* **Example Request:** 
	```json
    curl --location --request PATCH 'http://localhost:8080/asset_price_histories/309/edit' \
		--header 'Content-Type: application/json' \
		--data-raw '{
			"asset_type": "some_asset_type_edited",
            "date": "02-04-2019",
            "portfolio_id": 478,
            "price": 24.3
        }'
  ```

* **Example Response:**
    ```json
	{
        "success": true,
        "updated": 309
    }
    ```

#### DELETE /portfolios/<int:id>
* Deletes the portfolio with given id 

* Require `delete:portfolios` permission

* **Example Request:** `curl --request DELETE 'http://localhost:8080/portfolios/1'`

* **Example Response:**
    ```json
	{
		"deleted": 1,
		"success": true
    }
    ```

