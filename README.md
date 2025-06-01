🏡 Real Estate Management CLI App
📌 Function
Real Estate Management is a Command Line Interface (CLI) application designed to facilitate exploration and management of real estate listings. Users can browse, search, save, and interact with real estate properties. Additionally, the app supports agent registration, property listing, chat, feedback, and filtering features to enhance the user experience.

✨ Features
👤 User as Agent
Users can explore properties or register as agents to list properties themselves.

💬 Chat System
Users can chat within the platform, enabling direct communication with agents and other users.

⭐ Feedback System
Includes star ratings, textual feedback, and support for media attachments.

🔖 Explorer (Saved Listings)
Allows users to save listings for future exploration and reference.

🔍 Filtering & Sorting
Users can filter and sort listings by criteria like property type, price, location, etc.

⚙️ Installation
Follow these steps to install and run the application:

CLONE THE REPOSITORY

git clone https://github.com/Kipkoech854/Real-estate-management.git
cd Real-estate-management

SET UP THE ENVIRONMENT

pipenv install
pipenv shell

RUN THE APPLICATION

python cli_app.py
Interact via the CLI

Use numbers for menu choices.

Use names or IDs when prompted.

Additional commands and input instructions are provided through the CLI interface.

🧪 Usage
Once inside the CLI:

Navigate through menus using numbered options.

Input names, property IDs, or relevant text when prompted.

The application guides users clearly at every step.

🛠 Technologies Used
psycopg2 – PostgreSQL database integration

bcrypt – Secure password hashing

uuid – Unique ID generation

getpass – Secure password input

dotenv – Environment variable handling

random, string, json, datetime, os – Standard Python libraries

Project Modules:

Real_estate.ListingManager

explorer.Explorer

🛡 License
This project is licensed under the MIT License.

👥 Authors
Gideon Kipkoech

Brian Munene

Viktor Mugo

Derrick Masai

