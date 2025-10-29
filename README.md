# AI-Based Plagiarism Checker

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green)](https://palletsprojects.com/p/flask/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](https://opensource.org/licenses/MIT)

A sophisticated Python-based plagiarism detection system that uses Natural Language Processing (NLP) techniques to analyze text for potential plagiarism. This web application provides both text-based and file-based plagiarism checking capabilities with advanced AI algorithms for accurate detection.

## Table of Contents
- [Features](#features)
- [Technical Stack](#technical-stack)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Supported File Formats](#supported-file-formats)
- [How It Works](#how-it-works)
- [Limitations](#limitations)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Multiple Input Methods**:
  - Direct text input through web interface
  - File upload support (TXT, PDF, DOCX)
- **Advanced Analysis**:
  - TF-IDF based similarity detection
  - N-gram analysis for pattern matching
  - Content uniqueness scoring
  - Statistical analysis of text patterns
  - Levenshtein distance calculations
  - Semantic similarity using cosine similarity
- **Comprehensive Reporting**:
  - Multiple similarity metrics (Cosine, Jaccard, N-gram)
  - Plagiarism level assessment (Low, Moderate, High, Very High)
  - Highlighted suspicious content with potential sources
  - Visual charts and graphs for better understanding
  - Downloadable detailed PDF reports

## Technical Stack

- **Backend**: Python Flask
- **NLP Libraries**: NLTK, scikit-learn, NumPy
- **File Processing**: PyPDF2, python-docx
- **Frontend**: HTML, CSS, JavaScript with Bootstrap 5
- **Visualization**: Chart.js for data visualization
- **PDF Generation**: ReportLab for report generation

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Semester-Project-II
   ```
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Download required NLTK data (done automatically on first run):
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger')"
   ```

## Usage

1. Start the Flask application:
   ```bash
   python app.py
   ```
2. Open your web browser and navigate to `http://localhost:5000`
3. Choose between:
   - Text input: Paste your text directly (minimum 50 words recommended)
   - File upload: Upload a document (TXT, PDF, or DOCX)
4. View the analysis results including:
   - Overall plagiarism score
   - Detailed metrics visualization
   - Suspicious content highlights
5. Download the detailed PDF report for documentation

## API Endpoints

The application provides the following RESTful API endpoints:

- `GET /` - Serve the main web interface
- `POST /check-text` - Analyze text submitted via form data
- `POST /check-files` - Analyze uploaded files
- `GET /download-report/<path:report_path>` - Download generated PDF reports

## Supported File Formats

- Text files (.txt)
- PDF documents (.pdf)
- Microsoft Word documents (.docx)

**Note**: Maximum file size is 16MB for optimal performance.

## How It Works

The plagiarism detection system uses multiple algorithms to analyze text:

1. **Text Preprocessing**: Text is cleaned, tokenized, and normalized
2. **Feature Extraction**: TF-IDF vectors are created for comparison
3. **Similarity Calculation**: Multiple metrics are used:
   - Cosine similarity for semantic analysis
   - Jaccard similarity for set-based comparison
   - N-gram analysis for pattern matching
   - Levenshtein distance for string similarity
4. **Scoring**: Weighted average of all metrics determines final score
5. **Reporting**: Results are presented with visualizations and detailed analysis

## Limitations

- Maximum file size: 16MB
- Currently optimized for English text
- Processing time may vary based on document length
- Accuracy depends on reference database coverage

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is open-source and available under the MIT License.

## Acknowledgments

- Thanks to the NLTK and scikit-learn communities for their excellent libraries
- Inspired by academic integrity tools and plagiarism detection research

