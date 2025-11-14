
from .config import supabase


def readDomain():
    try:
      
        result = supabase.table('Domain_table').select("*").execute()
        
      
        if not result.data:
            return "No domains found in the table."
        else:
            for response in result.data:
                print(f"ID: {response['id']}")
                print(f"Domain: {response['domain_name']}")
                print(f"Created At: {response['created_at']}")
                print(f"Is_Valid: {response['is_valid']}")
                
   
        return result
    except Exception as e:
        print(f"An error occurred while reading domains from the database: {e}")

        class ErrorResult:
            def __init__(self):
                self.data = []
        return ErrorResult()

# if __name__ == "__main__":
#     result_obj = readDomain()
#     print(f"Fetched {len(result_obj.data)} domains via return.")