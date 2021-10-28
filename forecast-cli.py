import requests
import argparse

lifecycle_template_commercial = 0
lifecycle_template_strategic = 0
lifecycle_template_enterprise = 0

parser = argparse.ArgumentParser(description='Forecast IT API tool for creating projects and clients')
parser.add_argument('-a', '--account', help='Account name as defined in Planhat', required=True)
parser.add_argument('-p', '--person', help='Email of engineer or architect to assign to the project', required=True)
parser.add_argument('-s', '--segment', help='Customer segment classification.  Must be: Commercial, Enterprise, or Strategic', required=True)
parser.add_argument("-r", "--region", choices=["EMEA", "US", "APAC"], help="Customer's region")
parser.add_argument('-k', '--key', help='Your API key', required=True)
args = parser.parse_args()
target_account = args.account
target_person = args.person
target_segment = args.segment
target_template = 0
target_region = args.region
api_key = args.key


def get_template_ids():
    proj_list = get_projects()
    for proj in proj_list:
        if proj['name'] == 'Customer lifecycle template (Commercial)':
            global lifecycle_template_commercial
            lifecycle_template_commercial = proj['id']
            continue
        if proj['name'] == 'Customer lifecycle template (Strategic)':
            global lifecycle_template_strategic
            lifecycle_template_strategic = proj['id']
            continue
        if proj['name'] == 'Customer lifecycle template (Enterprise)':
            global lifecycle_template_enterprise
            lifecycle_template_enterprise = proj['id']
            continue


def create_project(type, name, person):
    headers = {
        'X-FORECAST-API-KEY': api_key
    }
    payload = {}

    if target_template != 0:
        url = "https://api.forecast.it/api/v1/projects/duplicate/" + str(target_template)
    else:
        print("ERROR: Invalid template")
        exit(1)
    client_id = get_client_by_name(name)
    if client_id:
        # Client definition already exists.
        payload = {
            'name': name + " Lifecycle",
            'client': client_id
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 201:
            new_project = response.json()
            print("Created \"" + new_project['name'] + "\" with type \'" + target_segment + "\'.")
            print("ID: " + str(new_project['id']))
            # Now set the new project into "Running" Stage.
            url = "https://api.forecast.it/api/v1/projects/" + str(new_project['id'])
            payload = {
                'stage': 'RUNNING'
            }
            response = requests.request("PUT", url, headers=headers, data=payload)
    else:
        # Client definition does not exist.
        new_client_id = create_client(name)
        payload = {
            'name': name + " Lifecycle",
            'client': new_client_id
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 201:
            new_project = response.json()
            print("Created \"" + new_project['name'] + "\" with type \'" + target_segment + "\'.")
            print("ID: " + str(new_project['id']))
            client_id = new_client_id

    # Now set the new project into "Running" Stage.
    url = "https://api.forecast.it/api/v1/projects/" + str(new_project['id'])
    payload = {
        'stage': 'RUNNING'
    }
    # If region was specified, add appropriate label.
    if args.region:
        existing_labels = new_project['labels']
        existing_labels.append(get_label_id(target_region))
        payload['labels'] = existing_labels
    response = requests.request("PUT", url, headers=headers, data=payload)

    # Now add the engineer to the project.
    add_person_to_project(new_project['id'], person)

    # Now add the engineer to the project tasks.
    for task in get_project_tasks(new_project['id']):
        add_person_to_task(new_project['id'], task['id'], person)


def get_label_id(region):
    url = "https://api.forecast.it/api/v1/labels"
    payload = {}
    headers = {
        'X-FORECAST-API-KEY': api_key
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        labels = response.json()
        for label in labels:
            if region.upper() + "_Region" == label['name']:
                return label['id']

    return None


def add_person_to_project(project_id, person):
    url = "https://api.forecast.it/api/v1/projects/" + str(project_id) + "/team"
    payload = {
        'person_id': person['id'],
        'project_role': person['role']
    }
    headers = {
        'X-FORECAST-API-KEY': api_key
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 201:
        team_member = response.json()
        return team_member['person_id']
    else:
        print("ERROR: Unable to modify project team")
        exit(1)


def add_person_to_task(project, task_id, person):
    url = "https://api.forecast.it/api/v2/tasks/" + str(task_id)
    payload = {
        'assigned_persons': [person['id']]
    }
    headers = {
        'X-FORECAST-API-KEY': api_key
    }

    response = requests.request("PUT", url, headers=headers, json=payload)
    if response.status_code == 200:
        updated_task = response.json()
        return updated_task
    else:
        print("ERROR: Unable update task. " + response.text)

    return None


def get_project_tasks(project):
    url = "https://api.forecast.it/api/v2/projects/" + str(project) + "/tasks"
    payload = {}
    headers = {
        'X-FORECAST-API-KEY': api_key
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        tasks = response.json()
        return tasks
    else:
        print("ERROR: Unable to get tasks.")

    return None


def create_client(name):
    url = "https://api.forecast.it/api/v1/clients"
    payload = {
        'name': name
    }
    headers = {
        'X-FORECAST-API-KEY': api_key
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 201:
        new_client = response.json()
        return new_client['id']
    else:
        print("ERROR: Client creation failed")
        exit(1)


def get_client_by_name(name):
    url = "https://api.forecast.it/api/v1/clients"
    payload = {}
    headers = {
        'X-FORECAST-API-KEY': api_key
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    clients = response.json()

    for client in clients:
        if client['name'].lower() == name.lower():
            return client['id']

    return None


def get_projects():
    url = "https://api.forecast.it/api/v1/projects"
    payload = {}
    headers = {
        'X-FORECAST-API-KEY': api_key
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    projects = response.json()

    return projects


def get_person_id(email):
    url = "https://api.forecast.it/api/v1/persons"
    payload = {}
    headers = {
        'X-FORECAST-API-KEY': api_key
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    people = response.json()

    for per in people:
        if not per['email']:
            continue
        if email.lower() == per['email'].lower():
            return { 'id': per['id'], 'role': per['default_role'] }

    return None


def set_template():
    global lifecycle_template_commercial, lifecycle_template_enterprise, lifecycle_template_strategic, target_template
    if target_segment.lower() == 'Commercial'.lower():
        target_template = lifecycle_template_commercial
        return True
    elif target_segment.lower() == 'Enterprise'.lower():
        target_template = lifecycle_template_enterprise
        return True
    elif target_segment.lower() == 'Strategic'.lower():
        target_template = lifecycle_template_strategic
        return True
    else:
        print("ERROR: Invalid target segment")
        exit(1)


if __name__ == '__main__':
    get_template_ids()
    set_template()
    person_id = get_person_id(target_person)
    create_project(target_template, target_account, person_id)
