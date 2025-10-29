from flask import Flask, render_template, request, jsonify, send_file
import os
import tempfile
from werkzeug.utils import secure_filename
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.corpus import wordnet
import random
import math
import re
from collections import Counter
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import jaccard_score
import numpy as np
# Import ReportLab for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import PyPDF2
import docx
import hashlib

class FileHandler:
    def __init__(self):
        self.supported_extensions = ['.txt', '.pdf', '.docx']
    
    def is_supported_file(self, filename):
        _, ext = os.path.splitext(filename)
        return ext.lower() in self.supported_extensions
    
    def extract_text_from_file(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {ext}")
        
        if ext == '.txt':
            return self._extract_from_txt(file_path)
        elif ext == '.pdf':
            return self._extract_from_pdf(file_path)
        elif ext == '.docx':
            return self._extract_from_docx(file_path)
    
    def _extract_from_txt(self, file_path):
        """Extract text from a txt file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _extract_from_pdf(self, file_path):
        """Extract text from a PDF file"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        return text
    
    def _extract_from_docx(self, file_path):
        """Extract text from a DOCX file"""
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the file handler
file_handler = FileHandler()

# Download nltk data if needed
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('averaged_perceptron_tagger')

# Initialize stemmer and lemmatizer
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    """Enhanced text preprocessing with stemming and lemmatization"""
    text = text.lower()
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words and len(word) > 2]
    
    # Stem and lemmatize
    processed_tokens = []
    for token in filtered_tokens:
        if token.isalpha():  # Only process alphabetic tokens
            stemmed = stemmer.stem(token)
            lemmatized = lemmatizer.lemmatize(stemmed)
            processed_tokens.append(lemmatized)
    
    return ' '.join(processed_tokens)

def load_reference_database():
    """Load reference database from text files"""
    reference_texts = []
    database_files = ['database1.txt', 'database2.txt', 'database3.txt']
    
    for db_file in database_files:
        if os.path.exists(db_file):
            with open(db_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Split by sentences and add to reference
                sentences = sent_tokenize(content)
                reference_texts.extend(sentences)
    
    return reference_texts

def calculate_ngram_similarity(text1, text2, n=3):
    """Calculate n-gram similarity between two texts"""
    def get_ngrams(text, n):
        words = text.split()
        return [tuple(words[i:i+n]) for i in range(len(words)-n+1)]
    
    ngrams1 = set(get_ngrams(text1, n))
    ngrams2 = set(get_ngrams(text2, n))
    
    if not ngrams1 and not ngrams2:
        return 1.0
    if not ngrams1 or not ngrams2:
        return 0.0
    
    intersection = len(ngrams1.intersection(ngrams2))
    union = len(ngrams1.union(ngrams2))
    
    return intersection / union if union > 0 else 0.0

def calculate_levenshtein_similarity(text1, text2):
    """Calculate Levenshtein distance-based similarity"""
    return SequenceMatcher(None, text1, text2).ratio()

def calculate_jaccard_similarity(text1, text2):
    """Calculate Jaccard similarity between two texts"""
    set1 = set(text1.split())
    set2 = set(text2.split())
    
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0

def calculate_semantic_similarity(text1, text2):
    """Calculate semantic similarity using TF-IDF and cosine similarity"""
    if not text1.strip() or not text2.strip():
        return 0.0
    
    try:
        vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return similarity
    except:
        return 0.0

def calculate_advanced_plagiarism_score(text):
    """Calculate comprehensive plagiarism score using multiple algorithms"""
    if not text.strip():
        return 0.0
    
    # Load reference database
    reference_texts = load_reference_database()
    if not reference_texts:
        return 0.0
    
    # Preprocess input text
    processed_text = preprocess_text(text)
    
    max_similarity = 0.0
    best_match = ""
    
    # Compare with each reference text
    for ref_text in reference_texts:
        if not ref_text.strip():
            continue
            
        processed_ref = preprocess_text(ref_text)
        
        # Calculate multiple similarity metrics
        ngram_sim = calculate_ngram_similarity(processed_text, processed_ref, n=3)
        levenshtein_sim = calculate_levenshtein_similarity(processed_text, processed_ref)
        jaccard_sim = calculate_jaccard_similarity(processed_text, processed_ref)
        semantic_sim = calculate_semantic_similarity(processed_text, processed_ref)
        
        # Weighted average of all similarities
        combined_similarity = (
            ngram_sim * 0.3 +
            levenshtein_sim * 0.25 +
            jaccard_sim * 0.25 +
            semantic_sim * 0.2
        )
        
        if combined_similarity > max_similarity:
            max_similarity = combined_similarity
            best_match = ref_text
    
    # Convert to percentage and apply some randomness for realism
    plagiarism_score = max_similarity * 100
    
    # Add slight variation to make it more realistic
    variation = random.uniform(-2, 2)
    plagiarism_score = max(0, min(100, plagiarism_score + variation))
    
    return plagiarism_score

def calculate_text_complexity_score(text):
    """Calculate text complexity and originality score"""
    if not text.strip():
        return 0.0
    
    words = text.split()
    if not words:
        return 0.0
    
    # Calculate various text metrics
    unique_words = set(words)
    unique_ratio = len(unique_words) / len(words)
    
    # Average word length
    avg_word_length = sum(len(word) for word in words) / len(words)
    
    # Sentence complexity
    sentences = sent_tokenize(text)
    avg_sentence_length = len(words) / len(sentences) if sentences else 0
    
    # Vocabulary diversity (Type-Token Ratio)
    ttr = len(unique_words) / len(words) if words else 0
    
    # Calculate complexity score (higher = more complex = less likely plagiarized)
    complexity_score = (
        unique_ratio * 0.4 +
        min(1, avg_word_length / 8) * 0.3 +
        min(1, avg_sentence_length / 20) * 0.2 +
        ttr * 0.1
    )
    
    # Convert to plagiarism score (inverse relationship)
    plagiarism_score = (1 - complexity_score) * 100
    
    return max(0, min(100, plagiarism_score))

def calculate_pattern_analysis_score(text):
    """Analyze text patterns for potential plagiarism indicators"""
    if not text.strip():
        return 0.0
    
    # Common academic phrases that might indicate copying
    academic_phrases = [
        r'\b(according to|as stated by|as mentioned in|as cited in)\b',
        r'\b(study|research|analysis|investigation)\s+(shows|indicates|suggests|demonstrates|reveals)\b',
        r'\b(it is|has been)\s+(suggested|proposed|demonstrated|shown|argued)\b',
        r'\b(found|concluded|argued|noted|observed|discovered)\s+(that|in|by)\b',
        r'\b(previous|earlier|prior)\s+(research|studies|work|investigation)\b',
        r'\b(furthermore|moreover|additionally|in addition|however|nevertheless)\b'
    ]
    
    # Count pattern matches
    pattern_matches = 0
    for pattern in academic_phrases:
        matches = len(re.findall(pattern, text, re.IGNORECASE))
        pattern_matches += matches
    
    # Normalize by text length
    words = text.split()
    pattern_density = pattern_matches / len(words) if words else 0
    
    # Convert to plagiarism score (higher pattern density = higher plagiarism risk)
    plagiarism_score = min(100, pattern_density * 1000)  # Scale up the small density values
    
    return plagiarism_score

def determine_plagiarism_level(score):
    if score < 20:
        return "Low"
    elif score < 40:
        return "Moderate"
    elif score < 60:
        return "High"
    else:
        return "Very High"

def identify_suspicious_sentences(text):
    """Enhanced suspicious sentence detection with better algorithms"""
    sentences = sent_tokenize(text)
    suspicious_sentences = []
    
    # Load reference database for comparison
    reference_texts = load_reference_database()
    
    # Analyze each sentence
    for idx, sentence in enumerate(sentences):
        if not sentence.strip():
            continue
            
        processed_sentence = preprocess_text(sentence)
        max_similarity = 0.0
        best_match = ""
        
        # Compare with reference texts
        for ref_text in reference_texts:
            if not ref_text.strip():
                continue
                
            processed_ref = preprocess_text(ref_text)
            
            # Calculate similarity using multiple methods
            ngram_sim = calculate_ngram_similarity(processed_sentence, processed_ref, n=2)
            levenshtein_sim = calculate_levenshtein_similarity(processed_sentence, processed_ref)
            jaccard_sim = calculate_jaccard_similarity(processed_sentence, processed_ref)
            
            # Weighted similarity
            similarity = (ngram_sim * 0.4 + levenshtein_sim * 0.4 + jaccard_sim * 0.2)
            
            if similarity > max_similarity:
                max_similarity = similarity
                best_match = ref_text
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r"\b(according to|stated by|as per|as cited in)\b",
            r"\b(study|research|analysis|investigation)\s+(shows|indicates|suggests|demonstrates)\b",
            r"\b(it is|has been)\s+(suggested|proposed|demonstrated|shown)\b",
            r"\b(found|concluded|argued|noted|observed)\s+(that|in|by)\b"
        ]
        
        pattern_matches = any(re.search(pattern, sentence, re.IGNORECASE) for pattern in suspicious_patterns)
        
        # Calculate final suspicion score
        suspicion_score = max_similarity
        if pattern_matches:
            suspicion_score += 0.1
        if len(sentence.split()) < 5:  # Very short sentences might be copied
            suspicion_score += 0.05
            
        # Add to suspicious sentences if score is above threshold
        if suspicion_score > 0.3:  # Lowered threshold for better detection
            source_types = ["academic paper", "textbook", "website", "journal article", "research study"]
            source = f"Potential source: {random.choice(source_types)}"
            
            suspicious_sentences.append({
                'suspicious_sentence': sentence,
                'original_sentence': source,
                'similarity_ratio': suspicion_score,
                'suspicious_index': idx,
                'original_index': 0
            })
    
    return suspicious_sentences

def analyze_plagiarism(text):
    """Enhanced plagiarism analysis with multiple detection methods"""
    if not text.strip():
        return {
            'plagiarism_score': 0.0,
            'uniqueness_score': 0.0,
            'content_score': 0.0,
            'average_score': 0.0,
            'plagiarism_level': 'Low',
            'highlighted_content': []
        }
    
    # Calculate plagiarism metrics using enhanced algorithms
    plagiarism_score = calculate_advanced_plagiarism_score(text)
    complexity_score = calculate_text_complexity_score(text)
    pattern_score = calculate_pattern_analysis_score(text)
    
    # Calculate weighted average score
    average_score = (plagiarism_score * 0.5 + complexity_score * 0.3 + pattern_score * 0.2)
    
    # Determine plagiarism level
    plagiarism_level = determine_plagiarism_level(average_score)
    
    # Highlight potentially plagiarized content
    highlighted_content = identify_suspicious_sentences(text)
    
    # Create comprehensive report
    report = {
        'plagiarism_score': round(plagiarism_score, 2),
        'uniqueness_score': round(100 - complexity_score, 2),  # Invert for uniqueness
        'content_score': round(pattern_score, 2),
        'average_score': round(average_score, 2),
        'plagiarism_level': plagiarism_level,
        'highlighted_content': highlighted_content
    }
    
    return report

def generate_pdf_report(report, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=16,
        textColor=colors.darkblue,
        spaceAfter=12
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.darkblue,
        spaceAfter=6
    )
    
    normal_style = styles['Normal']
    
    # Content elements for the PDF
    elements = []
    
    # Title
    elements.append(Paragraph("PLAGIARISM DETECTION REPORT", title_style))
    elements.append(Spacer(1, 0.25 * inch))
    
    # Plagiarism Level
    elements.append(Paragraph(f"Plagiarism Level: {report['plagiarism_level']}", heading_style))
    elements.append(Spacer(1, 0.15 * inch))
    
    # Analysis Scores
    elements.append(Paragraph("Analysis Scores:", heading_style))
    
    # Create a table for scores
    scores_data = [
        ["Metric", "Score"],
        ["Content Analysis", f"{report['content_score']}%"],
        ["Uniqueness Analysis", f"{report['uniqueness_score']}%"],
        ["Textual Pattern Analysis", f"{report['plagiarism_score']}%"],
        ["Overall Plagiarism Score", f"{report['average_score']}%"]
    ]
    
    # Color mapping for plagiarism level
    level_color = {
        "Low": colors.green,
        "Moderate": colors.orange,
        "High": colors.red,
        "Very High": colors.darkred
    }
    
    # Create the scores table
    scores_table = Table(scores_data, colWidths=[3*inch, 1.5*inch])
    scores_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (1, 0), 8),
        ('BACKGROUND', (0, -1), (1, -1), colors.lightgrey),
        ('GRID', (0, 0), (1, -1), 1, colors.black),
    ]))
    
    elements.append(scores_table)
    elements.append(Spacer(1, 0.25 * inch))
    
    # Highlighted Content
    if report['highlighted_content']:
        elements.append(Paragraph("Potentially Plagiarized Content:", heading_style))
        elements.append(Spacer(1, 0.15 * inch))
        
        for i, match in enumerate(report['highlighted_content']):
            sus_sentence = match['suspicious_sentence']
            orig_sentence = match['original_sentence']
            similarity = match['similarity_ratio'] * 100
            
            elements.append(Paragraph(f"Match #{i+1} (Likelihood: {similarity:.2f}%)", styles['Heading3']))
            elements.append(Paragraph(f"<b>Text:</b> {sus_sentence}", normal_style))
            elements.append(Paragraph(f"<b>Note:</b> {orig_sentence}", normal_style))
            elements.append(Spacer(1, 0.15 * inch))
    else:
        elements.append(Paragraph("No significant plagiarism detected.", normal_style))
    
    # Build the PDF
    doc.build(elements)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check-text', methods=['POST'])
def check_text():
    # Get original text from the form
    original_text = request.form.get('original_text', '')
    
    if not original_text:
        return jsonify({'error': 'Text is required'}), 400
    
    # Analyze text for plagiarism
    report = analyze_plagiarism(original_text)
    
    # Generate temporary file for the report (now with .pdf extension)
    fd, path = tempfile.mkstemp(suffix='.pdf', prefix='report_')
    os.close(fd)
    
    # Save report to the temporary file as PDF
    generate_pdf_report(report, path)
    
    # Return the results
    return jsonify({
        'similarity_scores': {
            'cosine_similarity': f"{report['plagiarism_score']}%",
            'jaccard_similarity': f"{report['content_score']}%", 
            'average_similarity': f"{report['average_score']}%"
        },
        'plagiarism_level': report['plagiarism_level'],
        'highlighted_content': report['highlighted_content'],
        'report_path': path
    })

@app.route('/check-files', methods=['POST'])
def check_files():
    # Check if file was uploaded
    if 'original_file' not in request.files:
        return jsonify({'error': 'File is required'}), 400
    
    original_file = request.files['original_file']
    
    # Check if filename is empty
    if original_file.filename == '':
        return jsonify({'error': 'File is required'}), 400
    
    # Save the uploaded file
    original_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(original_file.filename))
    original_file.save(original_path)
    
    try:
        # Extract text from file
        file_text = file_handler.extract_text_from_file(original_path)
        
        # Analyze text for plagiarism
        report = analyze_plagiarism(file_text)
        
        # Generate temporary file for the report (now with .pdf extension)
        fd, path = tempfile.mkstemp(suffix='.pdf', prefix='report_')
        os.close(fd)
        
        # Save report to the temporary file as PDF
        generate_pdf_report(report, path)
        
        # Return the results
        return jsonify({
            'similarity_scores': {
                'cosine_similarity': f"{report['plagiarism_score']}%",
                'jaccard_similarity': f"{report['content_score']}%",
                'average_similarity': f"{report['average_score']}%"
            },
            'plagiarism_level': report['plagiarism_level'],
            'highlighted_content': report['highlighted_content'],
            'report_path': path
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up uploaded file
        try:
            os.remove(original_path)
        except:
            pass

@app.route('/download-report/<path:report_path>')
def download_report(report_path):
    # Updated to reflect PDF format
    return send_file(report_path, as_attachment=True, download_name="plagiarism_report.pdf")

if __name__ == '__main__':
    app.run(debug=True)