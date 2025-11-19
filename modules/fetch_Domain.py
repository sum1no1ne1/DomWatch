import os
import shutil
from .config import supabase
from .screenshot_utils import take_screenshot
from .createpdf import pdfcreate
from .domain_utils import is_domain_valid_https_with_reason

def fetchDomain():
    try:
        print("Starting domain verification process...")

        # Get domains that are 'not verified'
        result = supabase.table('Domain_table').select('id', 'domain_name').eq('is_valid', 'not verified').execute()
        domains_to_check = result.data
        print(f"Found {len(domains_to_check)} domains to check.")

        # Verify HTTPS & update DB
        for entry in domains_to_check:
            domain_id = entry['id']
            domain_name = entry['domain_name']
            print(f"Checking: {domain_name}")

            is_valid, reason = is_domain_valid_https_with_reason(domain_name)
            
            if is_valid:
                supabase.table('Domain_table').update({
                    'is_valid': 'is working',
                    'verification_reason': reason
                }).eq('id', domain_id).execute()
            else:
                supabase.table('Domain_table').update({
                    'is_valid': 'not working',
                    'verification_reason': reason
                }).eq('id', domain_id).execute()

        # Fetch working / not working domains with reasons
        working_domains = supabase.table('Domain_table').select('domain_name').eq('is_valid', 'is working').execute().data
        not_working_domains = supabase.table('Domain_table').select('domain_name', 'verification_reason').eq('is_valid', 'not working').execute().data

        # Create screenshots folder
        folder_path = "screenshots"
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        os.makedirs(folder_path, exist_ok=True)

        # Take screenshots for all working domains
        print(f"Taking screenshots for {len(working_domains)} working domains...")
        for entry in working_domains:
            domain_name = entry['domain_name']
            print(take_screenshot(domain_name))

        # Create PDF from all screenshots
        pdf_result = pdfcreate()
        print(pdf_result)

        # Return the results
        return {
            "working_domains": [d['domain_name'] for d in working_domains],
            "not_working_domains": [
                {
                    "domain": d['domain_name'], 
                    "reason": d.get('verification_reason', 'Unknown error')
                } 
                for d in not_working_domains
            ]
        }

    except Exception as e:
        error_message = f"An error occurred during the fetch process: {e}"
        print(error_message)
        return {"error": error_message}