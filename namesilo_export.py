import requests
import xml.etree.ElementTree as ET
import pandas as pd
import os

# Function to read the API key from a file called 'API.key' in the same directory
def get_api_key(file_name='API.key'):
    try:
        with open(file_name, 'r') as file:
            api_key = file.read().strip()
        return api_key
    except FileNotFoundError:
        print(f"Error: {file_name} not found.")
        return None

# NameSilo API endpoint to list registered domains
API_ENDPOINT = 'https://www.namesilo.com/api/listDomains'

def get_domains(api_key):
    # Define parameters for the API request
    params = {
        'version': '1',    # API version
        'type': 'xml',     # Response format
        'key': api_key,    # Your API key
    }
    
    # Send the API request
    response = requests.get(API_ENDPOINT, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the XML response
        root = ET.fromstring(response.content)
        
        # Extract domain and expiration information
        domains_info = []
        for domain_entry in root.findall('.//domain'):
            domain_name = domain_entry.text
            expiration_date = domain_entry.get('expires')
            
            if domain_name and expiration_date:
                domains_info.append({
                    'Domain': domain_name,
                    'Expiry Date': expiration_date
                })
        
        return domains_info
    else:
        print(f"Failed to fetch domains. Status code: {response.status_code}")
        return None

def save_to_excel(domains_info, file_name="domains_with_expiry.xlsx"):
    if len(domains_info) > 0:
        try:
            # Create a DataFrame from the domains_info list
            df = pd.DataFrame(domains_info)

            # Format the 'Expiry Date' column to DD/MM/YYYY
            df['Expiry Date'] = pd.to_datetime(df['Expiry Date']).dt.strftime('%d/%m/%Y')

            # Save the DataFrame to an Excel file
            df.to_excel(file_name, index=False)
            print(f"Domains and expiry dates saved to {file_name}")
        except Exception as e:
            print(f"Failed to save to Excel: {str(e)}")
    else:
        print("domains_info is empty, nothing to save.")

# Main execution block
if __name__ == '__main__':
    # Get the API key from 'API.key' file
    api_key = get_api_key()

    if api_key:
        # Get domains and their expiry dates
        domains_info = get_domains(api_key)
        
        # If domains are retrieved and not an empty list, save them to an Excel file
        if domains_info and len(domains_info) > 0:
            save_to_excel(domains_info)
        else:
            print("No domains to save.")
    else:
        print("No API key found. Exiting...")
