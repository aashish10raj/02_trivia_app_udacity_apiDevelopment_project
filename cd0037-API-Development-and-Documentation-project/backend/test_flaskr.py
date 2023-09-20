import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

from flaskr import create_app
from models import *


load_dotenv()
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT")
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
database_name= os.environ.get("DB_TEST_NAME")

db_uri = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{database_name}"
class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""

        self.app = create_app(
            {
                "SQLALCHEMY_DATABASE_URI": db_uri
            }
        )
        self.client = self.app.test_client



        # sample question for use in tests
        self.new_question = {
            'question': 'Which four states make up the 4 Corners region of the US?',
            'answer': 'Colorado, New Mexico, Arizona, Utah',
            'difficulty': 3,
            'category': '3'
        }

        # binds the app to the current context
        # with self.app.app_context():
        #     self.db = SQLAlchemy()
        #     self.db.init_app(self.app)
        #     # create all tables
        #     self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass


    def test_get_paginated_questions(self):
        result = self.client().get('/questions')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_requesting_questions_for_nonexistent_page(self):
        result = self.client().get('/questions?page=1000')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_categories(self):
        result = self.client().get('/categories')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_request_for_nonexistent_category(self):
        result = self.client().get('/categories/9999')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        result = self.client().delete('/questions/1')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 422)
        self.assertEqual(data["success"], False)

    def test_deleting_nonexistent_question(self):
        result = self.client().delete('/questions/1')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_add_question(self):
        """Tests question creation success"""
        newQuestion = {
            'question': 'In which country do you live?',
            'answer': 'India',
            'difficulty': 5,
            'category': 3
        }
        result = self.client().post('/questions', json=newQuestion)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data["success"], True)


    def test_422_add_question(self):
            new_question = {
                'question': 'aashish',
                'answer': 'raj',
                'category': 3
            }
            result = self.client().post('/questions', json=new_question)
            data = json.loads(result.data)

            self.assertEqual(result.status_code, 422)
            self.assertEqual(data["success"], False)
            self.assertEqual(data["message"], "unprocessable")

    def test_search_questions(self):
        search = {'searchTerm': 'tesr'}
        res = self.client().post('/search', json=search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)


    def test_search_question_not_found(self):
        """Tests search questions failure 404"""

        # send post request with search term that should fail
        response = self.client().post('/questions',
                                      json={'searchTerm': 'xyz'})

        data = json.loads(response.data)
        # check response status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    def test_get_questions_per_category(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_get_questions_per_category(self):
        response = self.client().get('/categories/a/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_play_quiz(self):
        new_quiz_round = {'previous_questions': [],
                          'quiz_category': {'type': 'Sports', 'id': 6}}

        response = self.client().post('/quizzes', json=new_quiz_round)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_play_quiz(self):
        new_quiz_round = {'previous_questions': []}
        response = self.client().post('/quizzes', json=new_quiz_round)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()