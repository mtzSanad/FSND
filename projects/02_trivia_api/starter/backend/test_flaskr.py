import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        #self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        self.database_path = "postgres://postgres:postgres@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.testQuestion = {
            'question':'Question for test',
            'answer': 'test answer',
            'category' : '1',
            'difficulty' : '2'
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    #test getting categories
    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['total_categories'],6)

    #test getting categories failure 404 not found
    def test_get_categories_fail(self):
        response = self.client().get('/categories?page=1000')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code,404)
        self.assertEqual(data['error'],404)
        self.assertEqual(data['success'],False)

    #test getting questions
    def test_get_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertNotEqual(len(data['questions']),0)

    #test getting questions with paging
    def test_get_questions_paging(self):
        response = self.client().get('/questions?page=2')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertNotEqual(len(data['questions']),0)

    #test getting questions failure
    def test_get_questions_failure(self):
        response = self.client().get('/questions?page=1000')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code,404)
        self.assertEqual(data['error'],404)
        self.assertEqual(data['success'],False)

    #test delete question by getting count of existing question then insert a question make sure that counter increased by one after that delete the question
    #and finally check count again
    def test_delete_question(self):
        baseQuestionCount = Question.query.count()

        newQuestion = Question(question=self.testQuestion['question'],answer=self.testQuestion['answer'],category=self.testQuestion['category'],difficulty=self.testQuestion['difficulty'])

        newQuestion.insert()

        countAfterInsert = Question.query.count()

        #making sure that insert is success
        self.assertEqual(countAfterInsert,baseQuestionCount+1)

        #calling delete end point
        response = self.client().delete('/questions/{}'.format(newQuestion.id))

        data = json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['id'],newQuestion.id)

        countAfterDelete = Question.query.count()
        self.assertEqual(countAfterDelete,baseQuestionCount)

    #test  questions delete failure
    def test_delete_questions_failure(self):
        response = self.client().delete('/questions/100000')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code,404)
        self.assertEqual(data['error'],404)
        self.assertEqual(data['success'],False)

    #test creation endpoint
    def test_create_question(self):
        baseQuestionCount = Question.query.count()

        response = self.client().post('/questions',json=self.testQuestion)

        data = json.loads(response.data)

        questionCountAfterCreation = Question.query.count()

        #make sure that count increaed by 1
        self.assertEqual(questionCountAfterCreation,baseQuestionCount+1)

        #getting question from response id property
        createdQuestion = Question.query.filter_by(id=data['id']).one_or_none()


        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertIsNotNone(createdQuestion)

    #test  questions creation failure
    def test_create_questions_failure(self):
        response = self.client().post('/questions',json={'question':''})
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code,500)
        self.assertEqual(data['error'],500)
        self.assertEqual(data['success'],False)

    #test serch endpoint with matching
    def test_search_question(self):
        response = self.client().post('/questions',json={'searchTerm': 'what'})

        data = json.loads(response.data)


        self.assertEqual(response.status_code,200)
        self.assertEqual(data['total_questions'],8)
        self.assertGreater(len(data['questions']),0)


    #test serch endpoint without matching
    def test_search_question_no_match(self):
        response = self.client().post('/questions',json={'searchTerm': 'sdfsdfsdfsgdfgdfgsdfgsgfdgsfdgs'})

        data = json.loads(response.data)


        self.assertEqual(response.status_code,200)
        self.assertEqual(data['total_questions'],0)
        self.assertEqual(len(data['questions']),0)

    #test getting questions based on category
    def test_get_questions_by_category(self):
        response = self.client().get('/categories/6/questions')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['total_questions'],2)
        self.assertEqual(len(data['questions']),2)

    #test  questions category failure, sending post while required is get
    def test_get_questions_by_category_failure(self):
        response = self.client().post('/categories/1000/questions')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code,405)
        self.assertEqual(data['error'],405)
        self.assertEqual(data['success'],False)

    def test_play(self):
        response = self.client().post('/quizzes', json={'previous_questions':[],'quiz_category': {'type': 'Sports', 'id': '6'}})
        data = json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)

    def test_play_failure(self):
        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code,500)
        self.assertEqual(data['error'],500)
        self.assertEqual(data['success'],False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()