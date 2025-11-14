import os
from .config import supabase
from .screenshot_utils import  take_screenshot
from .domain_utils import is_domain_valid_https
from .sendmail import sendemail
from .createpdf import pdfcreate
import shutil

def fetchDomain():
    print("Starting domain verification process...")
    try:
        result = supabase.table('Domain_table').select('id', 'domain_name').eq('is_valid', 'not verified').execute()
        domains_to_check = result.data

        print(f"Found {len(domains_to_check)} domains to check.")
        for entry in domains_to_check:
            domain_id = entry['id']
            domain_name = entry['domain_name']
            print(f"Checking: {domain_name}")

            if is_domain_valid_https(domain_name):
                print(f"   - {domain_name} is valid (HTTPS + valid SSL + reachable).")
                supabase.table('Domain_table').update({'is_valid': 'is working'}).eq('id', domain_id).execute()
            else:
                print(f"   - {domain_name} is NOT valid.")
                supabase.table('Domain_table').update({'is_valid': 'not working'}).eq('id', domain_id).execute()

        result_working = supabase.table('Domain_table').select('domain_name').eq('is_valid', 'is working').execute()
        result_not_working = supabase.table('Domain_table').select('domain_name').eq('is_valid', 'not working').execute()
        working_domains = result_working.data
        not_working_domains= result_not_working.data

        dir_path = "screenshots"

        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
        
        os.makedirs(dir_path, exist_ok=True)

        print(f"Found {len(working_domains)} domains marked as 'is working'. Taking screenshots...")
        for entry in working_domains:
            domain_name = entry['domain_name']
            take_screenshot_result = take_screenshot(domain_name) 
            print(take_screenshot_result) 

        print(f'screenshots found at location: {dir_path} \n proceeding to create a pdf')
        pdf_result = pdfcreate() 
        print(pdf_result) 

        print("sending pdf to required users.")
        email_result = sendemail(working_domains,not_working_domains) 
        print(email_result) 

        print("Process completed.")
        return "Domain verification, screenshot capture, PDF creation, and email sending completed successfully!"

    except Exception as e:
        error_message = f"An error occurred during the fetch process: {str(e)}"
        print(error_message) 
        return error_message
