<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>fillaDb Blog</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://fonts.googleapis.com/css?family=Inter:400,700&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary: #1976d2;
      --accent: #39b77e;
      --bg: #f6fafd;
      --card: #fff;
      --text: #222;
      --muted: #9fb9d0;
    }
    * { box-sizing: border-box; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'Inter', Arial, sans-serif;
      margin: 0;
      min-height: 100vh;
    }
    header {
      background: var(--card);
      box-shadow: 0 2px 12px rgba(25, 118, 210, 0.08);
      display: flex;
      align-items: center;
      padding: 1rem 2.2rem;
      justify-content: space-between;
    }
    .logo {
      display: flex;
      align-items: center;
      gap: 1rem;
    }
    .logo img {
      width: 48px;
      height: 48px;
    }
    .logo span {
      font-size: 2rem;
      font-weight: 700;
      color: var(--primary);
      letter-spacing: 1px;
    }
    nav a {
      margin-left: 1.2rem;
      text-decoration: none;
      color: var(--primary);
      font-weight: 600;
      font-size: 1rem;
    }
    nav a:hover { color: var(--accent); }
    .container {
      max-width: 820px;
      margin: 2.8rem auto 0 auto;
      padding: 0 1.1rem;
    }
    .blog-title {
      font-size: 2.2rem;
      color: var(--primary);
      margin-bottom: 0.25rem;
      letter-spacing: 1px;
      text-align: center;
    }
    .blog-desc {
      text-align: center;
      color: var(--muted);
      margin-bottom: 2.1rem;
      font-size: 1.08rem;
    }
    .posts {
      display: grid;
      gap: 2rem;
      grid-template-columns: 1fr;
    }
    .post {
      background: var(--card);
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(25,118,210,0.09);
      padding: 2rem 1.4rem 1.5rem 1.4rem;
      display: flex;
      flex-direction: column;
      transition: transform 0.08s;
    }
    .post:hover { transform: translateY(-4px) scale(1.01);}
    .post-title {
      font-size: 1.25rem;
      color: var(--primary);
      font-weight: bold;
      margin-bottom: 0.7rem;
    }
    .post-meta {
      color: var(--muted);
      font-size: 0.92rem;
      margin-bottom: 0.8rem;
    }
    .post-summary {
      color: #444;
      font-size: 1rem;
      margin-bottom: 0.6rem;
      white-space: pre-line;
    }
    .read-more {
      align-self: flex-end;
      background: linear-gradient(90deg, var(--primary) 60%, var(--accent) 100%);
      color: #fff;
      font-weight: 600;
      border: none;
      border-radius: 6px;
      padding: 0.45rem 1.1rem;
      text-decoration: none;
      transition: background 0.2s;
    }
    .read-more:hover {
      background: linear-gradient(90deg, #1565c0 60%, #219150 100%);
      color: #fff;
    }
    footer {
      text-align: center;
      margin: 2.8rem 0 1.2rem 0;
      color: var(--muted);
      font-size: 1rem;
    }
    @media (min-width: 700px) {
      .posts { grid-template-columns: 1fr 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <div class="logo">
      <img src="fillaDb-logo.png" alt="fillaDb Logo">
      <span>fillaDb</span>
    </div>
    <nav>
      <a href="#">Blog</a>
      <a href="#">Docs</a>
      <a href="#">GitHub</a>
    </nav>
  </header>
  <div class="container">
    <div class="blog-title">The fillaDb Blog</div>
    <div class="blog-desc">Technical news, practical guides, and ideas for making the most of your NoSQL engine.</div>
    <div class="posts">

      <div class="post">
        <div class="post-title">🔎 What is fillaDb? Technical Overview</div>
        <div class="post-meta">by Arnold Lartey · June 2025</div>
        <div class="post-summary">
          fillaDb is a modern, lightweight NoSQL database server for Python, built for flexibility and ease of integration. 
          Inspired by LiteDB, CosmosDB, Cassandra, and Firebase, fillaDb provides a schemaless JSON document store, fast in-memory operations with persistent JSON storage, built-in support for files and binary data, and a friendly admin UI. 
          Features include partitioning, TTL for expiring data, advanced query operators, dynamic indexing, import/export, and compaction. 
          All data is accessible via a secure REST API, and the admin dashboard enables low-code configuration and live document browsing.
        </div>
      </div>

      <div class="post">
        <div class="post-title">🌟 Benefits of fillaDb for Developers & Teams</div>
        <div class="post-meta">by 3D PLUS GH Team · June 2025</div>
        <div class="post-summary">
          • Instantly embeddable in any Python project—no dependencies on external services.
          • Schemaless document store: rapidly evolve your data model with no migrations.
          • Store files, images, and binary blobs directly alongside records.
          • Advanced query support: find, filter, sort, and paginate with MongoDB-like flexibility.
          • Built-in admin dashboard for non-technical users to manage data visually.
          • API-level authentication for security; tokens and passwords can be changed in the UI.
          • Small, fast, and zero-config by default—perfect for prototyping, internal tools, and small production apps.
        </div>
      </div>

      <div class="post">
        <div class="post-title">🔧 Use Cases: When and Why to Choose fillaDb</div>
        <div class="post-meta">by Arnold Lartey · June 2025</div>
        <div class="post-summary">
          • Rapid prototyping for SaaS or microservice backends.
          • Internal dashboards, reporting, or admin panels where developers want NoSQL speed and flexibility without server ops.
          • IoT, research, and edge deployments where lightweight, self-contained storage is essential.
          • Secure storage of user files (avatars, uploads, logs) with metadata in the same API/database.
          • Training and education—use fillaDb to demonstrate database concepts or rapid app development.
        </div>
      </div>

    </div>
  </div>
  <footer>
    &copy; 2025 Arnold Lartey · 3D PLUS GH · Powered by <b>fillaDb</b>
  </footer>
</body>
</html>
