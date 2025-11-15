from .config import supabase
from .check_valid import check


def deleteDomain(domain):
    try:
        if check(domain):
            result = supabase.table('Domain_table').select('domain_name').eq('domain_name',domain).execute()
            if len(result.data)>0:
                supabase.table('Domain_table').delete().eq('domain_name',domain).execute()
                return f"{domain} deleted from db"
            else:    
                return f"{domain} is not  part of the db"
        else:
            return f"{domain} not a  valid Domain name"    
    except Exception as e:
        print(f"An error occurred while deleting domain: {e}")

# if __name__ == "__main__":
#     deleteDomain("www.bookmyshow.com")
