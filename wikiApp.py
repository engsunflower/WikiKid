from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
import openai   
import creds
import wikipedia

app = Flask(__name__)
CORS(
    app,
    resources={r"/process": {"origins": "http://127.0.0.1:5000"}},
)

@app.route('/')
def index():
    return render_template('homepage.html')

@app.route('/process',methods=['GET','POST'])
def process():
    print("CHECK - Received a post request.")
    try:
        # retrieving the user's input(wikipedia article name)
        article_name = request.form.get('article_name')
        if not article_name:
            return jsonify({'error': "article name missing"})

        page = wikipedia.page(article_name)
        page_content = page.content

        openai.api_key = creds.apiKey

        def generate_chunks():
            for chunk in openai.ChatCompletion.create(
                model="gpt-4", 
                messages=[
                    {"role": "system", "content": "Simplify text for 4th grader. Skip comments on formatting, references, links."},
                    {"role": "user", "content": page_content}
                ],
                stream=True,
            ):
                content = chunk["choices"][0].get("delta", {}).get("content")
                if content is not None:
                    yield content

        return Response(generate_chunks(), content_type='text/plain')

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
