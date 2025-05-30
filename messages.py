def mark_messages_read(self, chat_id, user_id):
    """Mark all unread messages in a chat as read for the user"""
    try:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE chats
                SET read = TRUE
                WHERE chat_id = %s AND user_id = %s AND read = FALSE
                """,
                (chat_id, user_id)
            )
            self.conn.commit()
            print("✅Messages marked as read.")
    except psycopg2.Error as e:
        self.conn.rollback()
        print(f"❌Database Error: {e}")


def chat_interface(self, current_user_id):
    chat_id = input("Enter chat ID: ").strip()
    self.mark_messages_read(chat_id, current_user_id)
    
    messages = self.get_chat_messages(chat_id)
    for msg in messages:
        sender, text, attachments, is_read, time = msg
        print(f"[{time.strftime('%H:%M')}] {sender}: {text}")
    
    while True:
        msg = input("You: ")
        if msg.lower() == "exit":
            break
        self.send_message(
            user_id=self.get_agency_user_id(chat_id),
            chat_id=chat_id,
            sender_id=current_user_id,
            message=msg
        )


def get_chat_messages(self, chat_id):
    """Retrieve all messages for a specific chat"""
    try:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT sender_id, message, attachments, read, created_at
                FROM chats
                WHERE chat_id = %s
                ORDER BY created_at ASC
                """,
                (chat_id,)
            )
            return cur.fetchall()
    except psycopg2.Error as e:
        print(f"❌Database Error: {e}")
        return []

for msg in self.get_chat_messages(chat_id):
    sender, text, attachments, is_read, time = msg
    print(f"[{time.strftime('%Y-%m-%d %H:%M')}] {sender}: {text}")
    if attachments:
        print(f"  Attachments: {attachments}")



def send_message(self, user_id, chat_id, sender_id, message, attachments=None):
    """Insert a message into the chats table"""
    try:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO chats (
                    id, user_id, chat_id, sender_id, message, attachments
                ) VALUES (
                    %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    str(uuid.uuid4()),
                    user_id,
                    chat_id,
                    sender_id,
                    message,
                    json.dumps(attachments) if attachments else None
                )
            )
            self.conn.commit()
            print("✅Message sent successfully.")
            return True
    except psycopg2.Error as e:
        self.conn.rollback()
        print(f"❌Database Error: {e}")
        return False


























    def list_user_chats(self, user_id):
    with self.conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, u1.username AS contact_name
            FROM conversations c
            JOIN users u1 ON (CASE 
                WHEN c.participant_1 = %s THEN c.participant_2
                ELSE c.participant_1 END) = u1.id
            WHERE c.participant_1 = %s OR c.participant_2 = %s
        """, (user_id, user_id, user_id))
        return cur.fetchall()  # [(conversation_id, contact_name), ...]
    
    


    def get_or_create_conversation(self, user1_id, user2_id):
    with self.conn.cursor() as cur:
        ids = sorted([user1_id, user2_id])  # Ensure uniqueness
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
    if not chat in chats:
        print("\n=== no chats ===")
        print("1. Make New chat")
        print("2. go back")


        choice = input("Select option: ").strip()
        if choice == '1':
            name = input("name : ").strip() 
            if name:
                get_or_create_conversation(self.current_user_id, name)
                message = input("message : ").strip()
                attachments = input("attatchments : ").strip()
            else:
                print("receipient name needed to send message")
                if message or attachments:
                    send_message(get_or_create_conversation(), self.current_user_id, message, attachments)
                else:
                    print('message or attatchment to be sent needed')
        else if choice =='2':
            break
    else:
         print("\n=== chats ===")
         list_user_chats(self.current_user_id)
         openchat = input("open chat : ").strip()
         conver
         if input:
            get_chat_messages()