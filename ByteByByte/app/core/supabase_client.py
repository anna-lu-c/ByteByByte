# supabase_client.py
# Заглушка для будущей интеграции с Supabase

class SupabaseClient:
    def __init__(self):
        self.url = ""
        self.key = ""
    
    def sign_up(self, email, password):
        # TODO: реализовать
        return {"user": None, "error": "Not implemented"}
    
    def sign_in(self, email, password):
        # TODO: реализовать
        return {"user": None, "error": "Not implemented"}
    
    def get_profile(self, user_id):
        return None
    
    def sync_progress(self, user_id, progress_data):
        pass

# Глобальный экземпляр
supabase = SupabaseClient()
