
from .check_valid import check
from .config import supabase


def addDomain(domain):
    
     if check(domain):
        result = supabase.table('Domain_table').select('domain_name').eq('domain_name', domain).execute()
        if len(result.data)>0:
            return f"{domain} already exists in db"
        else:    
            supabase.table('Domain_table').insert({'domain_name':domain}).execute()
            return f"{domain} added to the db"
     else:
          return f"{domain} not a  valid Domain name"


# if __name__ == "__main__":
#     addDomain("www.bookmyshow.com")
