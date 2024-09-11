from flask import Flask, request, jsonify
import re
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

def remove_double_spaces(text):
    # Replace multiple spaces with a single space
    return re.sub(r' +', ' ', text)

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

    if not lines:
        raise ValueError("PNR data is empty")

    pnr_info['record_locator'] = lines[0]
    logging.debug(f"Record Locator: {pnr_info['record_locator']}")

    passenger_name_line = lines[1].strip()
    if passenger_name_line:
        name_parts = passenger_name_line.split('/')
        if len(name_parts) < 2:
            raise ValueError("Invalid passenger name format")

        last_name = name_parts[0].strip()
        if last_name.startswith('1.1'):
            last_name = last_name[3:].strip()  # Strip '1.1' from the last name

        pnr_info['passenger_name']['last_name'] = last_name
        first_name_and_title = name_parts[1].split(' ')
        pnr_info['passenger_name']['first_name'] = first_name_and_title[0].strip()
        if len(first_name_and_title) > 1:
            pnr_info['passenger_name']['title'] = first_name_and_title[1].strip()

    for line in lines[2:]:
        pattern = (
            r'(\d+)\s+'                   # Segment number
            r'([A-Z]{2})\s+'              # Airline code
            r'(\d+)\s+'                   # Flight number
            r'([FJCYWS])?\s*'             # Cabin class (optional)
            r'(\d{2}[A-Z]{3})\s+'         # Date
            r'([A-Z])?\s*'                # Day (optional)
            r'([A-Z]{6})\s+'              # Route
            r'(\w{2,3}\d*)?\s*'           # Status (optional)
            r'(\d{4})\s+'                 # Departure time
            r'(\d{4})\s*'                 # Arrival time
            r'(.*)'                       # Extra info (optional)
        )
        match = re.match(pattern, line)
        if not match:
            logging.warning(f"Skipping line due to insufficient parts: {line}")
            continue

        route = match.group(7)
        departure_location = route[:3]
        arrival_location = route[3:]

        segment_info = {
            'segment_number': match.group(1),
            'airline_code': match.group(2),
            'flight_number': match.group(3),
            'cabin_class': match.group(4) if match.group(4) else '',
            'date': match.group(5),
            'day': match.group(6) if match.group(6) else '',
            'route': route,
            'departure_location': departure_location,
            'arrival_location': arrival_location,
            'status': match.group(8) if match.group(8) else '',
            'departure_time': match.group(9),
            'arrival_time': match.group(10),
            'extra_info': match.group(11).strip() if match.group(11) else ''
        }

        pnr_info['itinerary'].append(segment_info)

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
            'cleaned_pnr_data': cleaned_pnr_data
        }
        
        return jsonify(response)
    except ValueError as ve:
        logging.error(f"ValueError: {ve}")
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        logging.error(f"Exception: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
