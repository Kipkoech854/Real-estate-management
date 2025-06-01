import psycopg2
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

class ChatSystem:
    def __init__(self, conn, current_user_id):
        self.conn = conn
        self.current_user_id = current_user_id

    def list_user_chats(self):
        """this is a function to load chats of a particular user"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, u1.username AS contact_name
                FROM conversations c
                JOIN users u1 ON (CASE 
                    WHEN c.participant_1 = %s THEN c.participant_2
                    ELSE c.participant_1 END) = u1.id
                WHERE c.participant_1 = %s OR c.participant_2 = %s
            """, (self.current_user_id, self.current_user_id, self.current_user_id))
            return cur.fetchall()  # [(conversation_id, contact_name), ...]

    def get_or_create_conversation(self, user1_id, user2_username):
        """this is a function to initialize or get a conversation instance from the database"""
        with self.conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = %s", (user2_username,))
            row = cur.fetchone()
            if not row:
                print("User not found.")
                return None
            user2_id = row[0]
            ids = sorted([user1_id, user2_id])

            cur.execute("""
                SELECT id FROM conversations 
                WHERE participant_1 = %s AND participant_2 = %s
            """, (ids[0], ids[1]))
            row = cur.fetchone()
            if row:
                return row[0]

            conversation_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO conversations (id, participant_1, participant_2)
                VALUES (%s, %s, %s)
            """, (conversation_id, ids[0], ids[1]))
            self.conn.commit()
            return conversation_id

    def send_message(self, conversation_id, sender_id, message, attachments=None):
        """this is the function that sends the message typed in by the user"""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO chats (
                    id, conversation_id, sender_id, message, attachments
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                str(uuid.uuid4()),
                conversation_id,
                sender_id,
                message,
                json.dumps(attachments) if attachments else None
            ))
            self.conn.commit()
    
    def get_chat_messages(self, conversation_id):
        """this is a function to get all chats with all the other people the user has"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT u.username, c.message, c.created_at
                FROM chats c
                JOIN users u ON u.id = c.sender_id
                WHERE c.conversation_id = %s
                ORDER BY c.created_at ASC
            """, (conversation_id,))
            chats = cur.fetchall()
            return chats

    def cli_interface(self):
        """this is a function to run the user interface"""
        while True:
            print("\n=== Your Conversations ===")
            chats = self.list_user_chats()
            if not chats:
                print("No chats found.")
                print("1. Start New Chat")
                print("2. Exit")
                choice = input("Select option: ").strip()
                if choice == '1':
                    name = input("Recipient username: ").strip()
                    if not name:
                        print("Recipient name is required.")
                        continue
                    conversation_id = self.get_or_create_conversation(self.current_user_id, name)
                    if conversation_id:
                        message = input("Message: ").strip()
                        attachments = input("Attachments (optional): ").strip()
                        self.send_message(conversation_id, self.current_user_id, message, attachments or None)
                elif choice == '2':
                    break
                else:
                    print("Invalid option.")
            else:
                for idx, (cid, contact_name) in enumerate(chats, 1):
                    print(f"{idx}. {contact_name}")
                choice = input("Open chat (enter number or 'n' for new, 'q' to quit): ").strip()
                if choice.lower() == 'n':
                    name = input("Recipient username: ").strip()
                    conversation_id = self.get_or_create_conversation(self.current_user_id, name)
                    if conversation_id:
                        message = input("Message: ").strip()
                        attachments = input("Attachments (optional): ").strip()
                        self.send_message(conversation_id, self.current_user_id, message, attachments or None)
                elif choice.lower() == 'q':
                    break
                elif choice.isdigit() and 1 <= int(choice) <= len(chats):
                    selected_chat = chats[int(choice) - 1]
                    messages = self.get_chat_messages(selected_chat[0])
                    print(f"\n=== Chat with {selected_chat[1]} ===")
                    for username, message, created in messages:
                        print(f"[{created}] {username}: {message}")
                    print("------------------------------")
                    new_msg = input("Send a new message (leave blank to go back): ").strip()
                    if new_msg:
                        self.send_message(selected_chat[0], self.current_user_id, new_msg)
                else:
                    print("Invalid selection.")
    

    def run(self):
        self.cli_interface()

if __name__ == "__main__":
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        print("Connected to database successfully.")
        current_user_id = input("Enter your user ID: ").strip()
        try:
            uuid.UUID(current_user_id)
        except ValueError:
            print("Invalid UUID. Please provide a valid user ID.")
            exit()
    except psycopg2.Error as e:
        print(f"Database connection failed: {e}")    
    app = ChatSystem(conn, current_user_id)
    app.run()        