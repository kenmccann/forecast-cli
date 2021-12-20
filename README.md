# forecast-cli
Command line tool for adding projects for Forecast via the API.

# Usage

## Available Arguments
```
$ python3 forecast-cli.py --help
usage: forecast-cli.py [-h] -a ACCOUNT -p PERSON -s SEGMENT [-r {EMEA,US,APAC}] -k KEY

Forecast IT API tool for creating projects and clients

optional arguments:
  -h, --help            show this help message and exit
  -a ACCOUNT, --account ACCOUNT
                        Account name as defined in Planhat
  -p PERSON, --person PERSON
                        Email of engineer or architect to assign to the project
  -s SEGMENT, --segment SEGMENT
                        Customer segment classification. Must be: Commercial, Enterprise, or Strategic
  -r {EMEA,US,APAC}, --region {EMEA,US,APAC}
                        Customer's region
  -k KEY, --key KEY     Your API key
```

## Example
```
$ python forecast-cli.py -a "ACME Corp" -p "some.user@aquasec.com" -s "Enterprise" -r "EMEA" -k <forecast_api_key>
```
