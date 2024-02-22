from flask import Flask, render_template, request, jsonify
import PyPDF2
import google.generativeai as genai
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

app = Flask(__name__)

# Set your API key here
GOOGLE_API_KEY = "AIzaSyBFJ1K8XvM6vlVxNa4iCFcLyQq7mGKfAl8"
genai.configure(api_key=GOOGLE_API_KEY)

# Download NLTK resources
nltk.download('stopwords')
nltk.download('punkt')


# Function to read text from PDF
def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text


# Function to search for keywords in the PDF text and find their locations
def search_keywords(text, keywords):
    keyword_results = {}
    for keyword in keywords:
        pattern = re.compile(r'\b{}\b'.format(re.escape(keyword)), re.IGNORECASE)
        matches = re.finditer(pattern, text)
        keyword_results[keyword] = [(match.start(), match.end()) for match in matches]
    return keyword_results


# Function to extract sentences around the keyword locations
def extract_sentences(text, keyword_results, sentence_window=100):
    sentences = {}
    for keyword, locations in keyword_results.items():
        sentences[keyword] = []
        for start, end in locations:
            start_index = max(text.rfind('.', 0, start - sentence_window), 0)
            end_index = min(text.find('.', end + sentence_window), len(text))
            sentence = text[start_index:end_index].strip()
            sentences[keyword].append((start_index, end_index, sentence))
    return sentences


# Initialize GenerativeModel
model = genai.GenerativeModel('gemini-pro')


# Function to extract relevant keywords using NLTK
def extract_keywords(text):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    keywords = [word.lower() for word in word_tokens if word.isalnum() and word.lower() not in stop_words]
    return keywords


@app.route('/')
def index():
    return render_template('index.html')  # Render the HTML template



# Function to extract article numbers from text
def extract_article_numbers(text):
    article_numbers = re.findall(r'Article\s+(\d+)', text)
    return ['Article ' + num for num in article_numbers]

# In the '/ask_ai' route handler
@app.route('/ask_ai', methods=['POST'])
def ask_ai():
    try:
        user_input = request.json['prompt']
        pdf_path = r"C:\Users\Abdullah\Desktop\Constitution\Constitution of Pakistan.pdf"  # Update with the path to your PDF file
        pdf_text = read_pdf(pdf_path)

        keywords = extract_keywords(user_input)
        keyword_results = search_keywords(pdf_text, keywords)

        sentences = extract_sentences(pdf_text, keyword_results)
        concatenated_sentences = ' '.join(
            sentence for keyword, sentence_list in sentences.items() for _, _, sentence in sentence_list)

        article_numbers = extract_article_numbers(pdf_text)

        # Create a prompt with placeholders for each sentence
        prompt = prompt =f"{concatenated_sentences} /n Read the above given text in the pdf file and cosider it as an information through which you have to answer the below question. Generate the answer completely according to the given text and it should be in detailed form.The answer sould be bulleted where sentences are starting./{user_input}"

        for index, (_, sentence_list) in enumerate(sentences.items(), start=1):
            for _, _, sentence in sentence_list:
                prompt += f"{index}. {sentence}\n\n"  # Adding each sentence as a bullet point

        response = model.generate_content(prompt)

        return jsonify({'status': 'success', 'response': response.text, 'article_numbers': article_numbers})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
