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
        response = self.client().get('/questions')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreater(data['total_questions'], 0)
        self.assertGreater(len(data['questions']), 0)
        self.assertGreater(len(data['categories']), 0)

    def test_requesting_questions_for_nonexistent_page(self):
        response = self.client().get('/questions?page=5000')
        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')

    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreater(len(data['categories']), 0)

    def test_request_for_nonexistent_category(self):
        response = self.client().get('/categories/800')
        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        response = self.client().delete('/questions/1')
        data = response.get_json()
        self.assertEqual(response.status_code, 422)
        self.assertFalse(data["success"])

    def test_deleting_nonexistent_question(self):
        response = self.client().delete('/questions/5678')
        data = response.get_json()

        self.assertEqual(response.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'unprocessable')

    def test_add_question(self):
        new_question = {
            'question': 'In which country do you live?',
            'answer': 'India',
            'difficulty': 5,
            'category': 3
        }
        response = self.client().post('/questions', json=new_question)
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
    def test_422_add_question(self):
        new_question = {
            'question': 'aashish',
            'answer': 'raj',
            'category': 3
        }
        response = self.client().post('/questions', json=new_question)
        data = response.get_json()

        self.assertEqual(response.status_code, 422)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "unprocessable")

    def test_search_questions(self):
        search = {'searchTerm': 'tesr'}
        response = self.client().post('/search', json=search)
        data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])

    def test_search_question_not_found(self):
        response = self.client().post('/questions', json={'searchTerm': 'xyz'})
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'resource not found')

    def test_get_questions_per_category(self):
        response = self.client().get('/categories/1/questions')
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreater(len(data['questions']), 0)
        self.assertGreater(data['total_questions'], 0)
        self.assertIsNotNone(data['current_category'])

    def test_404_get_questions_per_category(self):
        response = self.client().get('/categories/a/questions')
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "resource not found")

    def test_quiz(self):
        quiz_round = {
            'previous_questions': [],
            'quiz_category': {'type': 'Sports', 'id': 6}
        }
        response = self.client().post('/quizzes', json=quiz_round)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
    def test_404_quiz(self):
        quiz_round = {'previous_questions': []}
        response = self.client().post('/quizzes', json=quiz_round)
        data = response.get_json()
        self.assertEqual(response.status_code, 422)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "unprocessable")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()