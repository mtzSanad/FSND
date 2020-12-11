import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

'''
Pagination helper method
'''
def pagenate(request,selection):
      page = request.args.get('page',1,type=int)
      start = (page-1) * QUESTIONS_PER_PAGE
      end = start + QUESTIONS_PER_PAGE

      #formating objects as json
      selectionAsArray = [ obj.format() for obj in selection]

      #limiting array size
      return selectionAsArray[start:end]

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories',methods=['GET'])
  def all_categories():
        categories = Category.query.all();

        current_categories = pagenate(request,categories)

        if len(current_categories) == 0:
              abort(404)
        
        #getting categories as json id:type for react
        categoriesAsJson= {}
        for category in current_categories:
              categoriesAsJson[category['id']] = category['type']
              

        return jsonify({
          'success':True,
          'categories':categoriesAsJson,
          'total_categories':len(current_categories)
        })


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions',methods=['GET'])
  def questions():
        #getting questions      
        questions = Question.query.all()
        current_questions = pagenate(request,questions)

        if len(current_questions) == 0:
              abort(404)
        
        #getting categories and extracting category array from json
        categories = Category.query.all();

        categoriesAsJson= {}
        for category in categories:
              categoriesAsJson[category.id] = category.type
        
        return jsonify({ 
          'success':True,    
          'questions': current_questions,
          'total_questions': len(questions),
          'categories': categoriesAsJson,
          'current_category': categories[0].format()
        }) 
        

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>',methods=['DELETE'])
  def deleteQuestion(id):
        question = Question.query.get(id)

        if question == None:
              abort(404)

        question.delete()

        return jsonify({
              'success':True,
              'id':id
        })


  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions',methods=['POST'])
  def createAndSearchQuestion():
        #This method will handle search and create questions

        #getting request json param for create or search
        body = request.get_json()


        #Method is called for search not creation
        searchTerm = body.get('searchTerm')
        if searchTerm:
              filtedQuestion = Question.query.filter(Question.question.ilike('%'+searchTerm+'%')).all()
              if(len(filtedQuestion)>1):
                    return jsonify({
                        'questions':pagenate(request,filtedQuestion),
                        'total_questions':len(filtedQuestion),
                        'current_category': filtedQuestion[0].category
                    })
              else:
                    return jsonify({
                        'questions':pagenate(request,filtedQuestion),
                        'total_questions':0,
                        'current_category': ''
                    })

        if body.get('question') == '':
              abort(500)

        #if no searchTerm, creating question object using json data
        question = Question(question = body.get('question'), answer=body.get('answer'), category=body.get('category'), difficulty=body.get('difficulty'))
        
        #saving the question
        question.insert()
        
        return jsonify({ 
          'success': True,
          'question': question.format(),
          'id': question.id
        }) 


  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  #since the front end utilize /questions with POST method for search also, this method is implemented with create question

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:categoryId>/questions')
  def questionsByCategory(categoryId):
        #getting questions of category while handling pagination
        questionsOfCategory = Question.query.filter(Question.category==categoryId).all()

        if len(questionsOfCategory)==0:
              abort(404)

        return jsonify({
              'success':True,
              'questions': pagenate(request,questionsOfCategory),
              'total_questions': len(questionsOfCategory),
              'current_category': questionsOfCategory[0].category
        })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes',methods=['POST'])
  def quizzes():
        #getting previous question to be avoided and quiz category
        body = request.get_json()
        previousQuestions = body.get('previous_questions')
        quizCategory = body.get('quiz_category')
        quizQuestions={}
        randomQuestion={}
            
        if body.get('quiz_category') == None:
              abort(500)
              
        #in case of selecting all in category the id is zero,then we should remove category filter
        if quizCategory['id'] == 0:
              quizQuestions = Question.query.filter(Question.id.notin_(previousQuestions)).all()
        else:
              #getting for the selected category and not in previous questions
              quizQuestions = Question.query.filter(Question.category==quizCategory['id'],Question.id.notin_(previousQuestions)).all()

        #Getting random question
        if len(quizQuestions)>0:
              randomQuestion = quizQuestions[random.randrange(0, len(quizQuestions)-1)].format() 
        else:
              randomQuestion = {}

        return jsonify({
              'success':True,
              'question':randomQuestion
        })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
        return jsonify({
            "success": False, 
            "error": 400,
            "message": "Bad Request"
        }), 400

  @app.errorhandler(401)
  def unatuthorized(error):
        return jsonify({
            "success": False, 
            "error": 401,
            "message": "Unauthorized"
        }), 401

  @app.errorhandler(404)
  def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "Not found"
        }), 404

  @app.errorhandler(405)
  def methodNotAllowed(error):
        return jsonify({
            "success": False, 
            "error": 405,
            "message": "Method Not Allowed"
        }), 405


  @app.errorhandler(500)
  def internalServerError(error):
        return jsonify({
            "success": False, 
            "error": 500,
            "message": "Internal Server Error"
        }), 500
  
  return app

    