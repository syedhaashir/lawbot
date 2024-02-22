import PyPDF2
import google.generativeai as genai
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

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

# Function to process user input
def process_input(user_input, pdf_text):
    try:
        keywords = extract_keywords(user_input)
        print("Detected Keywords:", keywords)

        keyword_results = search_keywords(pdf_text, keywords)

        # Extract sentences around keyword locations and print the extracted text
        sentences = extract_sentences(pdf_text, keyword_results)
        for keyword, sentence_list in sentences.items():
            print(f"\nExtracted Text for Keyword '{keyword}':")
            for _, _, sentence in sentence_list:
                print(sentence)

        # Concatenate extracted sentences
        concatenated_sentences = ' '.join(sentence for keyword, sentence_list in sentences.items() for _, _, sentence in sentence_list)

        # Generate AI response based on the user input and extracted information
        prompt = f"Read the below text and extract a summarized answer for this according to: {user_input} Try to answer and write a summarized answer according to the provided date (if any), point number (if any), or anything that specifically refers to that statement from the given text:\n\n{concatenated_sentences}"
        response = model.generate_content(prompt)

        print("\nAI Response:")
        print(response.text)
    except Exception:
        print("May you have a lovely day!")

# Function to extract relevant keywords using NLTK
def extract_keywords(text):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    keywords = [word.lower() for word in word_tokens if word.isalnum() and word.lower() not in stop_words]
    return keywords

# Path to the PDF file
pdf_path = r"C:\Users\Yousuf Traders\OneDrive\Desktop\gsoc\abd code\constitution of pakistan.pdf"
# Read text from PDF
pdf_text = read_pdf(pdf_path)

# Function to interactively ask questions or input text
def interact_with_ai(pdf_text):
    while True:
        user_input = input("Enter your question or text (type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        else:
            process_input(user_input, pdf_text)

# Interact with AI
interact_with_ai(pdf_text)