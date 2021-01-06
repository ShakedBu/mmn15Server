class Message:
    def __init__(self, m_id, to_client, from_client, m_type, content):
        self.id = m_id
        self.to_client = to_client
        self.from_client = from_client
        self.type = m_type
        self.content = content
