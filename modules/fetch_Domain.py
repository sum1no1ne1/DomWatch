import os
import shutil
from .config import supabase
from .screenshot_utils import take_screenshot
from .createpdf import pdfcreate
from .sendmail import sendemail
from .domain_utils import is_domain_valid_https

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

            if is_domain_valid_https(domain_name):
                print(f"   - {domain_name} is valid.")
                supabase.table('Domain_table').update({'is_valid': 'is working'}).eq('id', domain_id).execute()
            else:
                print(f"   - {domain_name} is NOT valid.")
                supabase.table('Domain_table').update({'is_valid': 'not working'}).eq('id', domain_id).execute()

        # Fetch working / not working domains
        working_domains = supabase.table('Domain_table').select('domain_name').eq('is_valid', 'is working').execute().data
        not_working_domains = supabase.table('Domain_table').select('domain_name').eq('is_valid', 'not working').execute().data

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

        # Send email with PDF and domain lists
        email_result = sendemail(working_domains, not_working_domains)
        print(email_result)

        return "Domain verification, screenshot capture, PDF creation, and email sending completed successfully."

    except Exception as e:
        error_message = f"An error occurred during the fetch process: {e}"
        print(error_message)
        return error_message

