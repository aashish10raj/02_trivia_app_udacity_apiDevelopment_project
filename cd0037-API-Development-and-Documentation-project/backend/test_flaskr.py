import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import *


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        # self.app = create_app()
        # self.client = self.app.test_client
        # # self.database_name = "trivia_test"
        # # self.database_path = "postgres://{}/{}".format(
        # #     'localhost:5432', self.database_name)
        # # setup_db(self.app, self.database_path)
        # self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://aashishraj:123@localhost:5432/trivia_test'
        # self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        # db.self.app=self.app
        # db.init_app(self.app)
        # db.create_all()
        # db.init_app(self.app)

        # with self.app.app_context():
        #     db.create_all()
        self.app = create_app(
            {
                "SQLALCHEMY_DATABASE_URI": "postgresql://aashishraj:123@localhost:5432/trivia_test"
            }
        )
        self.client = self.app.test_client
        # self.app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://aashishraj:123@localhost:5432/trivia_test'
        # self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        # db.init_app(self.app)
        # with self.app.app_context():
        #     db.create_all()


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
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))

    def test_404_sent_requesting_questions_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_404_sent_requesting_non_existing_category(self):
        res = self.client().get('/categories/9999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)

    def test_422_sent_deleting_non_existing_question(self):
        res = self.client().delete('/questions/a')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_add_question(self):
        """Tests question creation success"""
        newQuestion = {
            'question': 'what is your name?',
            'answer': 'Manal',
            'difficulty': 1,
            'category': 1
        }
        res = self.client().post('/questions', json=newQuestion)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)


    def test_422_add_question(self):
            new_question = {
                'question': 'new_question',
                'answer': 'new_answer',
                'category': 1
            }
            res = self.client().post('/questions', json=new_question)
            data = json.loads(res.data)

            self.assertEqual(res.status_code, 422)
            self.assertEqual(data["success"], False)
            self.assertEqual(data["message"], "unprocessable")

    def test_search_questions(self):
        search = {'searchTerm': 'What is'}
        res = self.client().post('/search', json=search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)


    def test_404_search_question(self):
        """Tests search questions failure 404"""

        # send post request with search term that should fail
        response = self.client().post('/questions',
                                      json={'searchTerm': 'abcdefghijk'})

        # load response data
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    def test_get_questions_per_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_get_questions_per_category(self):
        res = self.client().get('/categories/a/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_play_quiz(self):
        new_quiz_round = {'previous_questions': [],
                          'quiz_category': {'type': 'Entertainment', 'id': 5}}

        res = self.client().post('/quizzes', json=new_quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_play_quiz(self):
        new_quiz_round = {'previous_questions': []}
        res = self.client().post('/quizzes', json=new_quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()