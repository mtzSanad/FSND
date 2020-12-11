# Full Stack Trivia API Backend
This project is aimed for Udacity Advanced Web Development learners to test their understanding of creating/testing/documenting end points API. This project initalization is created by Udacity https://github.com/udacity/FSND and learners should do most of the work on __init__.py and test_flasker.py to create and test end points for a pre developed front end.

This project is fun to play small trivia where you can create questions and select the difficuluty and category of you questions, later on you can select a specific category to play and test you knowledge in a fun way.

Project main features:-

1- Create question.

2- Display list of question by category.

3- Search with question term.

4- Delete question.

5- Play the game and have fun :).

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## API Documentation

### GET '/categories'
- Fetch question categories this method use pagination of 10 category by page.
- Request Arguments: None
- Returns: Json object that contains 'categories' property that hold categories as JSON as key value pair, where id is the key and category name is the value.
```
$curl http://127.0.0.1:5000/categories

      {
        'success':True,
        'categories':{
          '1' : "Science",
          '2' : "Art",
          '3' : "Geography",
          '4' : "History",
          '5' : "Entertainment",
          '6' : "Sports"
        },
        'total_categories':6
      }
```

### GET '/questions'
- Fetch questions this method use pagination of 10 quesiton by page.
- Request Arguments: None
- Returns: Json object that contains questions and categories data.

```
$curl http://127.0.0.1:5000/questions

{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "current_category": {
    "id": 1,
    "type": "Science"
  },
  "questions": [
    {
      "answer": "Apollo 13",
      "category": 5,
      "difficulty": 4,
      "id": 2,
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    },
    {
      "answer": "Tom Cruise",
      "category": 5,
      "difficulty": 4,
      "id": 4,
      "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
    },
    {
      "answer": "Edward Scissorhands",
      "category": 5,
      "difficulty": 3,
      "id": 6,
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    },
    {
      "answer": "Brazil",
      "category": 6,
      "difficulty": 3,
      "id": 10,
      "question": "Which is the only team to play in every soccer World Cup tournament?"
    },
    {
      "answer": "Uruguay",
      "category": 6,
      "difficulty": 4,
      "id": 11,
      "question": "Which country won the first ever soccer World Cup in 1930?"
    },
    {
      "answer": "George Washington Carver",
      "category": 4,
      "difficulty": 2,
      "id": 12,
      "question": "Who invented Peanut Butter?"
    },
    {
      "answer": "Lake Victoria",
      "category": 3,
      "difficulty": 2,
      "id": 13,
      "question": "What is the largest lake in Africa?"
    },
    {
      "answer": "The Palace of Versailles",
      "category": 3,
      "difficulty": 3,
      "id": 14,
      "question": "In which royal palace would you find the Hall of Mirrors?"
    },
    {
      "answer": "Agra",
      "category": 3,
      "difficulty": 2,
      "id": 15,
      "question": "The Taj Mahal is located in which Indian city?"
    },
    {
      "answer": "Escher",
      "category": 2,
      "difficulty": 1,
      "id": 16,
      "question": "Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
    }
  ],
  "success": true,
  "total_questions": 21
}
```

### DELETE '/questions/<int:id>'
- Delete only one question.
- Request Arguments: question id to be deleted.
- Returns: Json object that contains deleted id.

```
$curl -X DELETE http://127.0.0.1:5000//questions/1
  {
    'success':True,
    'id':1
  }
```

### POST '/questions'
- This end point is resposible on creating a new question or searching for question based on query parameter sent.
- In case question object is sent in request body, then it is create a new question.
- In case 'searchTerm' is sent as request body parameter then searching for question is performed.

Question creation case
```
$curl -X POST  http://127.0.0.1:5000/questions -H "Content-Type: application/json" -d '{ "question": "Test question?", "answer": "test", "difficulty": 1, "category": "1" }'

{
  "id": 30,
  "question": {
    "answer": "test",
    "category": 1,
    "difficulty": 1,
    "id": 30,
    "question": "Test question?"
  },
  "success": true
}
```

Question search case
```
$curl -X POST  http://127.0.0.1:5000/questions -H "Content-Type: application/json" -d '{ "searchTerm":  "test" }'

{
  "current_category": 1,
  "questions": [
    {
      "answer": "test",
      "category": 1,
      "difficulty": 1,
      "id": 30,
      "question": "Test question?"
    }
  ],
  "total_questions": 1
}
```

### GET '/categories/<int:categoryId>/questions'
- Fetch questions for specific category.
- Request Arguments: categoryId
- Returns: Json object that contains questions.

```
$ curl http://127.0.0.1:5000/categories/1/questions
{
  "current_category": 1,
  "questions": [
    {
      "answer": "The Liver",
      "category": 1,
      "difficulty": 4,
      "id": 20,
      "question": "What is the heaviest organ in the human body?"
    },
    {
      "answer": "Alexander Fleming",
      "category": 1,
      "difficulty": 3,
      "id": 21,
      "question": "Who discovered penicillin?"
    },
    {
      "answer": "Blood",
      "category": 1,
      "difficulty": 4,
      "id": 22,
      "question": "Hematology is a branch of medicine involving the study of what?"
    },
    {
      "answer": "",
      "category": 1,
      "difficulty": 1,
      "id": 27,
      "question": ""
    },
    {
      "answer": "fgdfgdfg",
      "category": 1,
      "difficulty": 1,
      "id": 28,
      "question": "ssdfs"
    },
    {
      "answer": "test",
      "category": 1,
      "difficulty": 1,
      "id": 30,
      "question": "Test question?"
    }
  ],
  "success": true,
  "total_questions": 6
}
```

### POST '/quizzes'
- This end point is where you can play the game.
- Request Arguments: question category and it is zero if no specific category is selected and list of previous asked questions.
- Returns: random qustion not in previous asked questions.

```
$ curl -X POST http://127.0.0.1:5000/quizzes -H "Content-Type: application/json" -d '{"previous_questions": [1,2], "quiz_category": {"type": "ALL", "id": 0}}'
{
  "question": {
    "answer": "Brazil",
    "category": 6,
    "difficulty": 3,
    "id": 10,
    "question": "Which is the only team to play in every soccer World Cup tournament?"
  },
  "success": true
}
```


## Testing
There are 14 test that handles all end point success and failure crietria. To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

## Author
Moataz Sanad made the required TODO's in this project mainly on  __init__.py and test_flasker.py, the project is developed by Udacity for learning purpose.
Original repository https://github.com/udacity/FSND/tree/master/projects/02_trivia_api/starter
