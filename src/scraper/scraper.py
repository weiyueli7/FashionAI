
from apify_client import ApifyClient
import pandas as pd
from io import StringIO
import requests
from dotenv import load_dotenv
import os
import sys
import aiohttp
import asyncio
from google.cloud import secretmanager
from apify import Actor
from aiohttp import ClientTimeout

# Load the .env file
load_dotenv()

# Setting up Environment Variables
meta_data_folder = os.getenv('SCRAPED_METADATA')
images_folder = os.getenv('SCRAPED_RAW_IMAGES')

men_file_name = os.getenv('MEN_FILE_NAME')
women_file_name = os.getenv('WOMEN_FILE_NAME')

id_col_name = os.getenv('COLUMN_ID_NAME')
image_url_col = os.getenv('URL_IMAGE')
bad_urls_men_file_name = os.getenv('BAD_URLS_MEN')
bad_urls_women_file_name = os.getenv('BAD_URLS_WOMEN')

scrape_data = os.getenv('SCRAP_IMAGES')

# Initialize the ApifyClient with your API token
client = secretmanager.SecretManagerServiceClient()
response = client.access_secret_version(
    request={"name": os.getenv('APIFY_GCP_SECRET_ACCESS')}
    )
secret_value = "apify_api_fmyOzdUdJa6NnRysW2LKPGccavak5R3YiHro"
client = ApifyClient(secret_value)

os.environ['APIFY_TOKEN'] = secret_value

num_items_to_download = int(os.getenv('MAX_ITEMS'))


def get_items_seed(url):
    # Prepare the Actor input for each page
    run_input = {
        "startUrls": [{"url": url}],
        "maxRequestsPerCrawl": num_items_to_download/2,
        "proxy": {
            "useApifyProxy": True,
            # This specifies using the residential proxy group
            "apifyProxyGroups": ["RESIDENTIAL"],
        },
        "maxConcurrency": 10,
    }

    # Run the Actor and wait for it to finish
    run = client.actor("mKTnbkisJ8BAiIbsP").call(run_input=run_input)

    dataset_id = run["defaultDatasetId"]

    # Fetch and print Actor results from the run's dataset (if there are any)
    # for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    #     print(item)
    # Fetch Actor results from the run's dataset
    # all_items.append(item)
    # API URL to get the dataset in CSV format
    api_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?format=csv"

    # Fetch the CSV file
    response = requests.get(api_url)

    # Decode the byte string to UTF-8 and remove BOM
    # The 'utf-8-sig' will handle the BOM
    decoded_data = response.content.decode('utf-8-sig')

    # Use StringIO to treat the decoded string as a file-like object
    csv_data = StringIO(decoded_data)
    df = pd.read_csv(csv_data)
    return df

# Function to asynchronously download a single image using Apify proxy
async def download_image(session, url, image_name, bad_urls, id, proxy_url):
    # Check if the image already exists locally to skip downloading
    if os.path.exists(image_name):
        print(f"{image_name} already exists, skipping download.")
        return

    try:
        # Fetch the image using Apify's proxy service
        async with session.get(url, proxy=proxy_url, timeout=ClientTimeout(total=600)) as response:
            if response.status == 200:
                # Save the image
                with open(image_name, 'wb') as f:
                    f.write(await response.read())
                print(f"Photo successfully downloaded as {image_name}")
            else:
                # Log the failed download
                print(
                    f"Failed to download {image_name}. Status code: {response.status}")
                bad_urls.append(
                    {'url': url, 'id': id, 'error': f'Failed with status code {response.status}'})
    except Exception as e:
        # Log any exceptions
        print(f"Error downloading {url}: {e}")
        bad_urls.append({'url': url, 'id': id, 'error': str(e)})

# Function to download multiple images asynchronously and return a DataFrame of failed downloads
async def download_images(urls_df, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    bad_urls = []  # List to store information about failed downloads

    # Set up Apify proxy configuration to use residential proxies
    async with Actor:
        proxy_configuration = await Actor.create_proxy_configuration(
            groups=['RESIDENTIAL']  # Use Apify's residential proxies
        )
        proxy_url = await proxy_configuration.new_url()  # Get the proxy URL
        proxies = {
            'http': proxy_url,
            'https': proxy_url,
        }

        # Create an aiohttp session with a limited connection pool
        # Limit to 30 concurrent connections per host
        connector = aiohttp.TCPConnector(limit_per_host=30)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            for i, row in urls_df.iterrows():
                url = row.get(image_url_col)
                if url:
                    # Construct the image name based on the id column
                    image_name = os.path.join(
                        output_folder, f"image_{row.get(id_col_name)}.jpg")
                    # Schedule the download task, passing the proxy_url
                    tasks.append(download_image(
                        session, url, image_name, bad_urls, row.get(id_col_name), proxy_url))
                else:
                    print(f"URL missing in row {i + 1}")
                    bad_urls.append({'url': 'Missing', 'id': row.get(
                        id_col_name), 'error': 'No URL provided'})

            # Await the completion of all tasks
            await asyncio.gather(*tasks)

    # Convert bad_urls list to a Pandas DataFrame and return it
    if bad_urls:
        bad_urls_df = pd.DataFrame(bad_urls)
        print(f"Bad URLs collected: {len(bad_urls_df)}")
        return bad_urls_df
    else:
        # Return an empty DataFrame if no errors
        return pd.DataFrame(columns=['url', 'id', 'error'])

if __name__ == '__main__':
    try:
        df_men = pd.read_csv(os.path.join(meta_data_folder, men_file_name))
        bad_image_metadata_men = asyncio.run(download_images(
            df_men, os.path.join(images_folder, os.path.splitext(men_file_name)[0])))
        print("Images saved for men")
        bad_image_metadata_men.to_csv(os.path.join(
            meta_data_folder, bad_urls_men_file_name), index=False)

        print("Images files were saved")
        sys.exit(0)

    except Exception as e:
        # Catch any exception and print the error message
        print(f"Error: {e}", file=sys.stderr)  # Print the error to stderr
        # Exit with an error code 1 to indicate failure
        sys.exit(1)
