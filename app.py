from flask import Flask, request, jsonify
import re

app = Flask(__name__)

def remove_double_spaces(text):
    # Replace multiple spaces with a single space
    return re.sub(' +', ' ', text)

def is_cabin_class(value):
    # Define the expected cabin class values
    expected_classes = {'F', 'J', 'C', 'Y', 'W', 'S'}
    return value in expected_classes

def parse_pnr(pnr_data):
    lines = [line.strip() for line in pnr_data.strip().split('\n') if line.strip()]
    pnr_info = {
        'record_locator': '',
        'passenger_name': {
            'last_name': '',
            'first_name': '',
            'title': ''
        },
        'itinerary': []
    }

    if lines:
        pnr_info['record_locator'] = lines[0]
        passenger_name_line = lines[1].strip()
        if passenger_name_line:
            name_parts = passenger_name_line.split('/')
            last_name = name_parts[0].strip()
            if last_name.startswith('1.1'):
                last_name = last_name[3:].strip()  # Strip '1.1' from the last name
            pnr_info['passenger_name']['last_name'] = last_name
            first_name_and_title = name_parts[1].split(' ')
            pnr_info['passenger_name']['first_name'] = first_name_and_title[0].strip()
            if len(first_name_and_title) > 1:
                pnr_info['passenger_name']['title'] = first_name_and_title[1].strip()

        for line in lines[2:]:
            parts = line.split()
            if len(parts) < 5:
                continue  # Skip if there are not enough parts to process

            segment_number = parts[0]
            airline_code = parts[1]
            flight_number = parts[2]

            # Initialize default values
            cabin_class = ''
            status = ''
            date = ''
            day_of_week = ''
            route = ''
            departure_time = ''
            arrival_time = ''
            extra_info = ''

            # Adapt based on the length of parts and expected positions
            if len(parts) > 4 and is_cabin_class(parts[3]):
                cabin_class = parts[3]
                date = parts[4]
                if len(parts) > 5:
                    route = parts[5]
                if len(parts) > 6:
                    departure_time = parts[6]
                if len(parts) > 7:
                    arrival_time = parts[7]
                if len(parts) > 8:
                    extra_info = ' '.join(parts[8:])
            else:
                date = parts[3]
                if len(parts) > 4:
                    route = parts[4]
                if len(parts) > 5:
                    departure_time = parts[5]
                if len(parts) > 6:
                    arrival_time = parts[6]
                if len(parts) > 7:
                    extra_info = ' '.join(parts[7:])

            itinerary_info = {
                'segment_number': segment_number,
                'airline_code': airline_code,
                'flight_number': flight_number,
                'cabin_class': cabin_class,
                'date': date,
                'route': route,
                'status': status,
                'departure_location': route[:3] if route else '',
                'arrival_location': route[3:] if route else '',
                'departure_time': departure_time,
                'arrival_time': arrival_time,
                'extra_info': extra_info
            }
            pnr_info['itinerary'].append(itinerary_info)

    return pnr_info

@app.route('/parse_pnr', methods=['POST'])
def parse_pnr_endpoint():
    pnr_data = request.get_json().get('pnr_data', '')
    if not pnr_data:
        return jsonify({'error': 'PNR data is required'}), 400

    try:
        # Remove double spaces
        cleaned_pnr_data = remove_double_spaces(pnr_data)
        
        # Parse the cleaned PNR data
        parsed_pnr = parse_pnr(cleaned_pnr_data)
        
        # Include the cleaned PNR data in the response
        response = {
            'parsed_pnr': parsed_pnr,
            'removedoublespacestext': cleaned_pnr_data
        }
        
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
