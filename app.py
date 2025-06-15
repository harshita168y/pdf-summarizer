from flask import Flask, request, render_template
import os
import PyPDF2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def summarize_text(text, max_sentences=3):
    import re
    from collections import Counter
    from heapq import nlargest

    sentences = re.split(r'(?<=[.!?]) +', text)
    words = re.findall(r'\w+', text.lower())
    word_freq = Counter(words)
    ranking = {sent: sum(word_freq[word.lower()] for word in sent.split()) for sent in sentences}
    summary = ' '.join(nlargest(max_sentences, ranking, key=ranking.get))
    return summary

@app.route('/', methods=['GET', 'POST'])
def index():
    summary = ''
    message = ''
    if request.method == 'POST':
        if 'file' not in request.files:
            message = 'No file part'
        else:
            file = request.files['file']
            if file.filename == '':
                message = 'No selected file'
            else:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                text = extract_text_from_pdf(file_path)
                summary = summarize_text(text)
                message = 'Summary generated successfully!'
    return render_template('index.html', summary=summary, message=message)

if __name__ == '__main__':
    app.run(debug=True)
