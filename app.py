from flask import Flask, render_template, request, jsonify, send_from_directory, send_file, redirect, session
import os
from datetime import datetime
import random
import json
from flask_compress import Compress
from flask_caching import Cache

app = Flask(__name__)

# Enable compression
Compress(app)

# Configure caching
cache = Cache(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
})

# Production configurations
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year
app.config['TEMPLATES_AUTO_RELOAD'] = False
app.config['COMPRESS_MIMETYPES'] = ['text/html', 'text/css', 'text/javascript', 'application/javascript']

# Secret key for session
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

# Load software data from software.json
def load_software_data():
    try:
        with open('software.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_software_data(data):
    with open('software.json', 'w') as f:
        json.dump(data, f, indent=4)

software_list = load_software_data()
download_counts = {s['id']: s.get('downloads', 0) for s in software_list}

@app.route('/')
def home():
    return render_template('index.html', software_list=software_list)

@app.route('/category/<category>')
def category(category):
    filtered_software = [s for s in software_list if s['category'].lower() == category.lower()]
    return render_template('index.html', software_list=filtered_software, category=category)

@app.route('/search')
@cache.cached(timeout=60, query_string=True)  # Cache results for 60 seconds
def search():
    try:
        # Get search parameters
        query = request.args.get('q', '').lower().strip()
        if not query:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'status': 'error',
                    'message': 'Please enter a search term'
                }), 400
            return redirect('/')

        if len(query) < 2:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'status': 'error',
                    'message': 'Please enter at least 2 characters'
                }), 400
            return render_template('index.html', error="Please enter at least 2 characters")

        # Search logic
        results = []
        for software in software_list:
            try:
                # Create searchable text from all relevant fields
                searchable_fields = [
                    software.get('name', '').lower(),
                    software.get('description', '').lower(),
                    software.get('category', '').lower(),
                    *[genre.lower() for genre in software.get('genre', [])],
                    software.get('version', '').lower(),
                    software.get('developer', '').lower()
                ]
                
                # Check if query matches any field
                if any(query in field for field in searchable_fields if field):
                    results.append(software)
                    continue

                # Check for exact matches in tags or keywords
                if any(query == tag.lower() for tag in software.get('genre', [])):
                    results.append(software)
                    continue

            except (AttributeError, TypeError) as e:
                app.logger.error(f"Error processing software entry: {e}")
                continue

        # Sort results by relevance (exact matches first, then partial matches)
        results.sort(key=lambda x: (
            query == x.get('name', '').lower(),  # Exact name matches first
            query in x.get('name', '').lower(),  # Partial name matches second
            query in x.get('category', '').lower(),  # Category matches third
            x.get('downloads', 0)  # Then by download count
        ), reverse=True)

        response_data = {
            'status': 'success',
            'results': results,
            'count': len(results)
        }

        # Return JSON response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(response_data)
        
        # Return template for regular requests
        return render_template('index.html', 
                             software_list=results, 
                             search_query=query,
                             result_count=len(results))

    except Exception as e:
        app.logger.error(f"Search error: {e}")
        error_response = {
            'status': 'error',
            'message': 'An error occurred while searching',
            'error': str(e)
        }
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(error_response), 500
        
        return render_template('index.html', 
                             error="An error occurred while searching. Please try again.",
                             search_query=query)

@app.route('/download/<software_id>')
def download(software_id):
    software = next((s for s in software_list if s['id'] == software_id), None)
    
    if software is None:
        return jsonify({'error': 'Software not found'}), 404
    # Increment download count
    download_counts[software_id] = download_counts.get(software_id, 0) + 1
    software['downloads'] = download_counts[software_id]
    save_software_data(software_list)
    
    # Get the download URL based on priority
    download_links = software.get('download_links', {})
    
    # Priority order for download links
    link_types = ['filecrypt', 'mega', 'gdrive', '1fichier', 'buzzheavier', 'megadb', 'official']
    
    for link_type in link_types:
        if link_type in download_links:
            return redirect(download_links[link_type])
    
    # Fallback to external_url if available
    if 'external_url' in software:
        return redirect(software['external_url'])
    
    return jsonify({'error': 'No download URL available'}), 404

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = file.filename
        file.save(os.path.join('uploads', filename))
        
        # Add new software to software_list
        new_software = {
            "id": filename.replace('.', '-'),
            "name": filename,
            "category": "Software",
            "version": "1.0",
            "size": "Unknown",
            "date_added": datetime.now().strftime("%Y-%m-%d"),
            "description": "Uploaded software",
            "filename": filename,
            "downloads": 0
        }
        software_list.append(new_software)
        download_counts[new_software['id']] = 0
        save_software_data(software_list)
        return jsonify({'message': 'File uploaded successfully'}), 200

@app.route('/files')
def list_files():
    files = []
    for filename in os.listdir('uploads'):
        files.append({'name': filename})
    return jsonify(files)

if __name__ == '__main__':
    # Use port from environment variable for production, default to 8080 for development
    port = int(os.environ.get('PORT', 8080))
    # Only enable debug mode in development
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
