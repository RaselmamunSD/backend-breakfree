import json

with open('postman_collection.json', 'r') as f:
    data = json.load(f)

coach_folder = {
    'name': 'AI Coach & Fear Forecast',
    'item': [
        {
            'name': 'Chat - Start Session / Get Sessions',
            'request': {
                'method': 'GET',
                'header': [{'key': 'Authorization', 'value': 'Bearer {{access_token}}'}],
                'url': '{{base_url}}/api/coach/chat/'
            }
        },
        {
            'name': 'Chat - Start Session',
            'request': {
                'method': 'POST',
                'header': [{'key': 'Authorization', 'value': 'Bearer {{access_token}}'}, {'key': 'Content-Type', 'value': 'application/json'}],
                'url': '{{base_url}}/api/coach/chat/',
                'body': {'mode': 'raw', 'raw': '{}'}
            }
        },
        {
            'name': 'Chat - Send Message',
            'request': {
                'method': 'POST',
                'header': [{'key': 'Authorization', 'value': 'Bearer {{access_token}}'}, {'key': 'Content-Type', 'value': 'application/json'}],
                'url': '{{base_url}}/api/coach/chat/{{chat_session_id}}/message/',
                'body': {'mode': 'raw', 'raw': '{\n  "message": "Hello, I am feeling anxious today."\n}'}
            }
        },
        {
            'name': 'Fear Forecast - Create',
            'request': {
                'method': 'POST',
                'header': [{'key': 'Authorization', 'value': 'Bearer {{access_token}}'}, {'key': 'Content-Type', 'value': 'application/json'}],
                'url': '{{base_url}}/api/coach/fear-forecast/',
                'body': {'mode': 'raw', 'raw': '{\n  "fear": "I am afraid I will fail my exam",\n  "belief_strength": 80\n}'}
            }
        },
        {
            'name': 'Fear Forecast - Log Outcome',
            'request': {
                'method': 'POST',
                'header': [{'key': 'Authorization', 'value': 'Bearer {{access_token}}'}, {'key': 'Content-Type', 'value': 'application/json'}],
                'url': '{{base_url}}/api/coach/fear-forecast/{{forecast_id}}/log_outcome/',
                'body': {'mode': 'raw', 'raw': '{\n  "outcome": "I passed it!"\n}'}
            }
        }
    ]
}

data['item'].append(coach_folder)

with open('postman_collection.json', 'w') as f:
    json.dump(data, f, indent=2)
print('Success')
