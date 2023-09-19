import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import collections
collections.Iterable = collections.abc.Iterable
import random
from backend.models import  *

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_question = questions[start:end]

    return current_question

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://aashishraj:123@localhost:5432/trivia'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    if test_config is not None:
        app.config.from_mapping(test_config)
    db.init_app(app)
    CORS(app, supports_credentials=True)

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Headers", "GET, POST, PATCH, DELETE, OPTION")
        return response

    with app.app_context():
        db.create_all()


    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def retrieve_categories():
        categories = Category.query.order_by(Category.type).all()

        if len(categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': {category.id: category.type for category in categories}
        })

    @app.route('/questions')
    def get_questions():
    # Get all the questions and paginate
        selection = Question.query.all()
        total_questions = len(selection)
        current_questions = paginate_questions(request, selection)

        # Get all categories
        categories = Category.query.all()
        categories_dict = {category.id: category.type for category in categories}

        # Abort 404 if no questions
        if len(current_questions) == 0:
            abort(404)

        # Return the response
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': total_questions,
            'categories': categories_dict
        })
    @app.route("/questions/<question_id>", methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except:
            abort(422)

    # @app.route("/questions", methods=['POST'])
    # def post_question():
    #     body = request.get_json()
    #
    #     if (body.get('searchTerm')):
    #         search_term = body.get('searchTerm')
    #
    #         # searching the db with the entered search term
    #         selection = Question.query.filter(
    #             Question.question.ilike(f'%{search_term}%')).all()
    #
    #         # 404 if no results found
    #         if (len(selection) == 0):
    #             abort(404)
    #
    #         # paginate the results
    #         paginated = paginate_questions(request, selection)
    #
    #
    #         return jsonify({
    #             'success': True,
    #             'questions': paginated,
    #             'total_questions': len(Question.query.all())
    #         })
    #     # if no search term, create new question
    #     else:
    #         # load data from body
    #         new_question = body.get('question')
    #         new_answer = body.get('answer')
    #         new_difficulty = body.get('difficulty')
    #         new_category = body.get('category')
    #
    #         # ensure all fields have data
    #         if ((new_question is None) or (new_answer is None)
    #                 or (new_difficulty is None) or (new_category is None)):
    #             abort(422)
    #
    #         try:
    #             # create and insert new question
    #             question = Question(question=new_question, answer=new_answer,
    #                                 difficulty=new_difficulty, category=new_category)
    #             question.insert()
    #
    #             # get all questions and paginate
    #             selection = Question.query.order_by(Question.id).all()
    #             current_questions = paginate_questions(request, selection)
    #
    #             # return data to view
    #             return jsonify({
    #                 'success': True,
    #                 'created': question.id,
    #                 'question_created': question.question,
    #                 'questions': current_questions,
    #                 'total_questions': len(Question.query.all())
    #             })
    #
    #         except:
    #             abort(422)

    @app.route("/questions", methods=['POST'])
    def post_question():
        body = request.get_json()

        if 'searchTerm' in body:
            search_term = body['searchTerm']

            # Searching the db with the entered search term
            selection = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

            # Return 404 if no results found
            if len(selection) == 0:
                abort(404)

            # Paginate the results
            paginated = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions': paginated,
                'total_questions': len(Question.query.all())
            })
        else:
            # Load data from body
            new_question = body.get('question')
            new_answer = body.get('answer')
            new_difficulty = body.get('difficulty')
            new_category = body.get('category')

            # Ensure all fields have data
            if not all([new_question, new_answer, new_difficulty, new_category]):
                abort(422)

            try:
                # Create and insert new question
                question = Question(
                    question=new_question,
                    answer=new_answer,
                    difficulty=new_difficulty,
                    category=new_category
                )
                question.insert()

                # Get all questions and paginate
                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                # Return data to view
                return jsonify({
                    'success': True,
                    'created': question.id,
                    'question_created': question.question,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })

            except:
                abort(422)


    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):

        try:
            questions = Question.query.filter(
                Question.category == str(category_id)).all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions],
                'total_questions': len(questions),
                'current_category': category_id
            })
        except:
            abort(404)

# generating random question for the quiz
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():

        try:

            body = request.get_json()

            if not ('quiz_category' in body and 'previous_questions' in body):
                abort(422)

            category = body.get('quiz_category')
            previous_questions = body.get('previous_questions')

            if category['type'] == 'click':
                available_questions = Question.query.filter(
                    Question.id.notin_((previous_questions))).all()
            else:
                available_questions = Question.query.filter_by(
                    category=category['id']).filter(Question.id.notin_((previous_questions))).all()

            new_question = available_questions[random.randrange(
                0, len(available_questions))].format() if len(available_questions) > 0 else None

            return jsonify({
                'success': True,
                'question': new_question
            })
        except:
            abort(422)
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400



    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host="localhost", port=8000, debug=True)

