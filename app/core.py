import json, os, uuid, threading, time, shutil
from typing import Dict, Any, Callable, List, Optional

class Observer:
    def __init__(self):
        self._subscribers = []
    def subscribe(self, fn: Callable):
        self._subscribers.append(fn)
    def notify(self, data):
        for fn in self._subscribers:
            fn(data)

class SimpleNoSQLHybrid:
    def __init__(self, storage_dir="data", blob_dir="data/blobs"):
        self._db: Dict[str, List[Dict[str, Any]]] = {}
        self._indexes: Dict[str, Dict[str, Dict[Any, List[Dict[str, Any]]]]] = {}
        self._observers: Dict[str, Observer] = {}
        self.storage_dir = storage_dir
        self.blob_dir = blob_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        os.makedirs(self.blob_dir, exist_ok=True)
        self._load_all_collections()
        self._ttl_thread = threading.Thread(target=self._run_ttl, daemon=True)
        self._ttl_thread.start()

    def _get_collection_path(self, collection):
        return os.path.join(self.storage_dir, f"{collection}.json")
    def _load_all_collections(self):
        for fname in os.listdir(self.storage_dir):
            if fname.endswith('.json'):
                col_name = fname[:-5]
                try:
                    with open(self._get_collection_path(col_name), 'r') as f:
                        self._db[col_name] = json.load(f)
                except Exception as e:
                    print(f"[WARN] Could not load {fname}: {e}")
        for cname in self._db:
            self._build_indexes(cname)
    def _save_collection(self, collection):
        path = self._get_collection_path(collection)
        tmp_path = path + ".tmp"
        try:
            with open(tmp_path, 'w') as f:
                json.dump(self._db[collection], f, indent=2)
            os.replace(tmp_path, path)
        except Exception as e:
            print(f"[ERROR] Saving {collection}: {e}")
    def _build_indexes(self, collection):
        self._indexes[collection] = {}
        for doc in self._db.get(collection, []):
            for key, value in doc.items():
                if key not in self._indexes[collection]:
                    self._indexes[collection][key] = {}
                if value not in self._indexes[collection][key]:
                    self._indexes[collection][key][value] = []
                self._indexes[collection][key][value].append(doc)
    def _notify_observers(self, collection, data):
        if collection in self._observers:
            self._observers[collection].notify(data)
    def create_collection(self, name):
        if name not in self._db:
            self._db[name] = []
            self._save_collection(name)
            self._observers[name] = Observer()
            self._indexes[name] = {}
    def drop_collection(self, name):
        if name in self._db:
            del self._db[name]
            self._indexes.pop(name, None)
            self._observers.pop(name, None)
            path = self._get_collection_path(name)
            if os.path.exists(path):
                os.remove(path)
    def ensure_index(self, collection, field):
        if collection not in self._db:
            return
        idx = self._indexes.setdefault(collection, {})
        idx[field] = {}
        for doc in self._db[collection]:
            v = doc.get(field)
            if v not in idx[field]:
                idx[field][v] = []
            idx[field][v].append(doc)
    def insert(self, collection, doc, partition_key=None, ttl=None):
        if collection not in self._db:
            self.create_collection(collection)
        doc = dict(doc)
        doc['_id'] = str(uuid.uuid4())
        if partition_key:
            doc['partition_key'] = partition_key
        if ttl:
            doc['_expires_at'] = time.time() + ttl
        self._db[collection].append(doc)
        self._save_collection(collection)
        self._build_indexes(collection)
        self._notify_observers(collection, {'action': 'insert', 'doc': doc})
        return doc['_id']

    # ADVANCED QUERY OPERATORS
    def _match_advanced(self, doc, query):
        # Supports: $or, $and, $gt, $lt, $gte, $lte, $ne, $in, $nin
        if not query:
            return True
        if "$or" in query:
            return any(self._match_advanced(doc, q) for q in query["$or"])
        if "$and" in query:
            return all(self._match_advanced(doc, q) for q in query["$and"])
        for k, v in query.items():
            if isinstance(v, dict):
                for op, opval in v.items():
                    docv = doc.get(k)
                    if op == "$gt":
                        if not (docv is not None and docv > opval): return False
                    elif op == "$lt":
                        if not (docv is not None and docv < opval): return False
                    elif op == "$gte":
                        if not (docv is not None and docv >= opval): return False
                    elif op == "$lte":
                        if not (docv is not None and docv <= opval): return False
                    elif op == "$ne":
                        if docv == opval: return False
                    elif op == "$in":
                        if docv not in opval: return False
                    elif op == "$nin":
                        if docv in opval: return False
            else:
                if str(doc.get(k)) != str(v): return False
        return True

    def find(self, collection, query=None, sort_by=None, partition_key=None, skip=0, limit=None):
        if collection not in self._db:
            return []
        docs = self._db[collection]
        if partition_key:
            docs = [doc for doc in docs if doc.get('partition_key') == partition_key]
        if query:
            docs = [doc for doc in docs if self._match_advanced(doc, query)]
        if sort_by:
            docs = sorted(docs, key=lambda d: d.get(sort_by))
        if skip:
            docs = docs[skip:]
        if limit is not None:
            docs = docs[:limit]
        return docs
    def update(self, collection, _id, update_fields):
        if collection not in self._db:
            return False
        for doc in self._db[collection]:
            if doc['_id'] == _id:
                doc.update(update_fields)
                self._save_collection(collection)
                self._build_indexes(collection)
                self._notify_observers(collection, {'action': 'update', 'doc': doc})
                return True
        return False
    def delete(self, collection, _id):
        if collection not in self._db:
            return False
        for idx, doc in enumerate(self._db[collection]):
            if doc['_id'] == _id:
                if 'blob_path' in doc and os.path.isfile(doc['blob_path']):
                    try:
                        os.remove(doc['blob_path'])
                    except Exception as ex:
                        print(f"[WARN] Could not remove blob: {ex}")
                del self._db[collection][idx]
                self._save_collection(collection)
                self._build_indexes(collection)
                self._notify_observers(collection, {'action': 'delete', 'doc': doc})
                return True
        return False
    def list_collections(self):
        return list(self._db.keys())
    def subscribe(self, collection, callback):
        if collection not in self._observers:
            self._observers[collection] = Observer()
        self._observers[collection].subscribe(callback)
    def _run_ttl(self):
        while True:
            for col in list(self._db.keys()):
                docs = self._db[col]
                to_delete = []
                now = time.time()
                for doc in docs:
                    if '_expires_at' in doc and doc['_expires_at'] < now:
                        to_delete.append(doc['_id'])
                for _id in to_delete:
                    self.delete(col, _id)
            time.sleep(5)
    def check_permission(self, user, action, collection):
        return True
    # EXPORT/IMPORT
    def export_collection(self, collection):
        if collection in self._db:
            return self._db[collection]
        return []
    def import_collection(self, collection, documents):
        if collection not in self._db:
            self.create_collection(collection)
        for doc in documents:
            if '_id' not in doc:
                doc['_id'] = str(uuid.uuid4())
            self._db[collection].append(doc)
        self._save_collection(collection)
        self._build_indexes(collection)
    # COMPACT (Rewrite JSON for space efficiency)
    def compact(self, collection):
        if collection in self._db:
            self._save_collection(collection)
