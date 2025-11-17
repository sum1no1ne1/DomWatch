import os
import shutil
from .config import supabase
from .screenshot_utils import take_screenshot
from .createpdf import pdfcreate
from .sendmail import sendemail
from .domain_utils import is_domain_valid_https

BATCH_SIZE = 5  # Adjust based on memory capacity

def fetchDomain():
    print("Starting domain verification process...")
    try:
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
        dir_path = "screenshots"
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        os.makedirs(dir_path, exist_ok=True)

        print(f"Processing {len(working_domains)} working domains in batches...")

        # Batch processing
        for i in range(0, len(working_domains), BATCH_SIZE):
            batch = working_domains[i:i+BATCH_SIZE]
            print(f"Processing batch {i//BATCH_SIZE + 1}: {[d['domain_name'] for d in batch]}")

            for entry in batch:
                domain_name = entry['domain_name']
                print(take_screenshot(domain_name))

            # Create PDF for this batch
            pdf_result = pdfcreate()
            print(pdf_result)

            # Optionally send email per batch
            email_result = sendemail(batch, not_working_domains)
            print(email_result)

            # Clear screenshots to free memory
            for f in os.listdir(dir_path):
                if f.endswith(".png") or f.endswith(".pdf"):
                    os.remove(os.path.join(dir_path, f))

        print("Domain verification, screenshot capture, PDF creation, and email sending completed successfully!")
        return "Process completed successfully."

    except Exception as e:
        error_message = f"An error occurred during the fetch process: {e}"
        print(error_message)
        return error_message
