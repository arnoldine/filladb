import os, uuid, time
from flask import (
    Flask, request, jsonify, send_file, session, redirect, url_for, render_template
)
from .core import SimpleNoSQLHybrid
from .auth import (
    token_required, get_api_token, set_api_token,
    get_admin_password, set_admin_password
)

db = SimpleNoSQLHybrid(storage_dir="data", blob_dir="data/blobs")
BLOB_DIR = db.blob_dir

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("FILLADB_SECRET", "filladb_secret")

    # --- API ROUTES ---

    @app.route('/collections', methods=['GET'])
    @token_required
    def list_collections():
        return jsonify({'collections': db.list_collections()})

    @app.route('/collections/<col>', methods=['POST'])
    @token_required
    def create_collection(col):
        db.create_collection(col)
        return jsonify({'message': f"Collection '{col}' created."}), 201

    @app.route('/collections/<col>', methods=['DELETE'])
    @token_required
    def drop_collection(col):
        db.drop_collection(col)
        return jsonify({'message': f"Collection '{col}' dropped."})

    @app.route('/collections/<col>/ensureindex', methods=['POST'])
    @token_required
    def ensure_index(col):
        data = request.json or {}
        field = data.get("field")
        if not field:
            return jsonify({"error": "Missing field"}), 400
        db.ensure_index(col, field)
        return jsonify({"message": f"Index on '{field}' ensured for '{col}'."})

    @app.route('/collections/<col>/export', methods=['GET'])
    @token_required
    def export_collection(col):
        docs = db.export_collection(col)
        return jsonify({'documents': docs})

    @app.route('/collections/<col>/import', methods=['POST'])
    @token_required
    def import_collection(col):
        data = request.json or {}
        documents = data.get("documents", [])
        if not isinstance(documents, list):
            return jsonify({"error": "Invalid documents format"}), 400
        db.import_collection(col, documents)
        return jsonify({"message": f"Imported {len(documents)} documents into '{col}'."})

    @app.route('/collections/<col>/compact', methods=['POST'])
    @token_required
    def compact_collection(col):
        db.compact(col)
        return jsonify({"message": f"Collection '{col}' compacted."})

    @app.route('/<col>/insert', methods=['POST'])
    @token_required
    def insert(col):
        data = request.json or {}
        partition_key = data.get('partition_key')
        ttl = data.get('ttl')
        doc = data.get('document')
        if not doc:
            return jsonify({'error': 'Missing "document" field'}), 400
        doc_id = db.insert(col, doc, partition_key=partition_key, ttl=ttl)
        return jsonify({'_id': doc_id}), 201

    @app.route('/<col>/find', methods=['POST'])
    @token_required
    def find(col):
        data = request.json or {}
        query = data.get('query', {})
        partition_key = data.get('partition_key')
        sort_by = data.get('sort_by')
        skip = int(data.get('skip', 0))
        limit = data.get('limit', None)
        if limit is not None:
            limit = int(limit)
        result = db.find(col, query, sort_by=sort_by, partition_key=partition_key, skip=skip, limit=limit)
        return jsonify({'results': result})

    @app.route('/<col>/update/<doc_id>', methods=['PUT'])
    @token_required
    def update(col, doc_id):
        data = request.json or {}
        fields = data.get('fields', {})
        if db.update(col, doc_id, fields):
            return jsonify({'message': 'Updated.'})
        return jsonify({'error': 'Document not found.'}), 404

    @app.route('/<col>/delete/<doc_id>', methods=['DELETE'])
    @token_required
    def delete(col, doc_id):
        if db.delete(col, doc_id):
            return jsonify({'message': 'Deleted.'})
        return jsonify({'error': 'Document not found.'}), 404

    # --- FILE UPLOAD/DOWNLOAD ---
    @app.route('/<col>/upload', methods=['POST'])
    @token_required
    def upload_blob(col):
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        file = request.files['file']
        filename = os.path.basename(file.filename)
        blob_id = str(uuid.uuid4())
        ext = os.path.splitext(filename)[1]
        blob_filename = f"{blob_id}{ext}"
        filepath = os.path.join(BLOB_DIR, blob_filename)
        file.save(filepath)
        doc = {
            'filename': filename,
            'blob_path': filepath,
            'content_type': file.content_type,
            'size': os.path.getsize(filepath),
            'uploaded_at': time.time(),
            '_id': blob_id
        }
        db.insert(col, doc)
        return jsonify({'_id': blob_id, 'message': 'File uploaded successfully.'}), 201

    @app.route('/<col>/download/<blob_id>', methods=['GET'])
    @token_required
    def download_blob(col, blob_id):
        result = db.find(col, {'_id': blob_id})
        if not result:
            return jsonify({'error': 'Blob not found'}), 404
        blob_doc = result[0]
        if not os.path.exists(blob_doc['blob_path']):
            return jsonify({'error': 'File not found on server'}), 404
        return send_file(blob_doc['blob_path'],
                         mimetype=blob_doc.get('content_type', 'application/octet-stream'),
                         as_attachment=True,
                         download_name=blob_doc['filename'])

    @app.route('/about', methods=['GET'])
    def about():
        return jsonify({
            'product': "fillaDb",
            'developer': "Arnold Lartey",
            'company': "3D PLUS GH",
            'contact': "arnold.lartey@3dplusgh.com"
        })

    # --- ADMIN PAGES ---

    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        error = ''
        if request.method == 'POST':
            pwd = request.form.get('password', '')
            if pwd == get_admin_password():
                session['admin_auth'] = True
                return redirect(url_for('admin'))
            else:
                error = "Incorrect password."
        return render_template("admin_login.html", error=error)

    @app.route('/admin/logout', methods=['POST'])
    def admin_logout():
        session.pop('admin_auth', None)
        return redirect(url_for('admin_login'))

    @app.route('/admin', methods=['GET', 'POST'])
    def admin():
        if 'admin_auth' not in session:
            return redirect(url_for('admin_login'))
        message = ""
        error = ""
        token_value = get_api_token()
        tab = request.args.get('tab', 'dashboard')
        selected_col = request.args.get('col', '')
        docs = []
        columns = []
        # --- Handle API token change ---
        if request.method == 'POST' and request.form.get('action') == 'change_token':
            new_token = request.form.get('new_token', '').strip()
            if new_token:
                set_api_token(new_token)
                token_value = new_token
                message = "API token updated successfully!"
        # --- Handle password change ---
        if request.method == 'POST' and request.form.get('action') == 'change_pass':
            current = request.form.get('current_pass', '').strip()
            newpass = request.form.get('new_pass', '').strip()
            conf = request.form.get('confirm_pass', '').strip()
            if current != get_admin_password():
                error = "Current password is incorrect."
            elif not newpass or len(newpass) < 5:
                error = "New password too short."
            elif newpass != conf:
                error = "New passwords do not match."
            else:
                set_admin_password(newpass)
                message = "Admin password changed successfully!"
        # --- Collections & docs ---
        collections = db.list_collections()
        if selected_col in collections:
            docs = db.find(selected_col)
            columns = sorted({k for doc in docs for k in doc.keys()})
        return render_template("admin_panel.html",
            token_value=token_value, message=message, error=error,
            tab=tab, collections=collections, docs=docs,
            selected_col=selected_col, columns=columns
        )

    return app
