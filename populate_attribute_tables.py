#import psycopg2
import json
import urllib

# Read the files
url = "http://api.census.gov/data/2015/acs5/variables.json"
response = urllib.urlopen(url)
data = json.loads(response.read())
acs_keys = data['variables'].keys()
sample_data = data['variables'][acs_keys[0]]

 
