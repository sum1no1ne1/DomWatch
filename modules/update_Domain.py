
from .config import supabase
from .check_valid import check


def updateDomain(old,new):
    try:
        if check(new):
            result = supabase.table('Domain_table').select('domain_name').eq('domain_name', old).execute()
            if len(result.data)>0:
                supabase.table('Domain_table').update({'domain_name':new, 'is_valid':'not verified'}).eq('domain_name',old).execute()
            else:    
                return f"{old} is not  part of the db"
        else:   
            return f"{new} not a  valid Domain name" 
    except Exception as e:
        print(f"An error occurred while updating domain: {e}")

# if __name__ == "__main__":
#     updateDomain("www.bookmyshow.zorg","www.bookmyshow.com")   