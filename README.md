# Inspire-me 

This site's main focus is to allow users to browse a museum's collection by searching specific term. <br>

A search returns one random matching result, with the option to try again or go back and perform a new search. If a user has an account and is logged in, there is an option to save search results to their profile, along with the option to add notes about their thoughts and what it inspires them to create. Users are also able to save notes about future ideas on their own, with no associated search result. <br>

Users are only able to view their own saved results and notes.

****

Deployed at https://inspire-me-lrlz.onrender.com

****

Search functionality uses the Metropolitain Museum of Art API: https://metmuseum.github.io/ <br>

Python/Flask, PostgreSQL, SQLAlchemy, Jinja, HTML, WTForms, Bcrypt, minmimal Javascript, and Bootstrap for styling.

A full list of dependancies is included in requirements.txt <br>

*pip install -r requirements.txt*

#### Database Schema Diagram

![Entity Relationship Diagram](/inspireme-db-diagram.jpg)