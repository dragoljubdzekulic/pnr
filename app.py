from flask import Flask, request, jsonify

app = Flask(__name__)

def parse_pnr(pnr_data):
    lines = pnr_data.strip().split('\n')
    pnr_info = {
        'record_locator': '',
        'passenger_name': {
            'last_name': '',
            'first_name': '',
            'title': ''
        },
        'itinerary': []
    }

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if pnr_info['record_locator'] == '':
            pnr_info['record_locator'] = line
        elif line[0].isdigit() and line[1] == '.':
            name_parts = line[3:].split('/')
            pnr_info['passenger_name']['last_name'] = name_parts[0]
            first_name_and_title = name_parts[1].split(' ')
            pnr_info['passenger_name']['first_name'] = first_name_and_title[0]
            if len(first_name_and_title) > 1:
                pnr_info['passenger_name']['title'] = first_name_and_title[1]
        else:
            itinerary_parts = line.split()
            flight_details = itinerary_parts[1]
            flight_number = itinerary_parts[2]
            cabin_class = itinerary_parts[3]
            date = itinerary_parts[4]
            route = itinerary_parts[5]
            departure_location = route[:3]
            arrival_location = route[3:]
            status = itinerary_parts[6]
            departure_time = itinerary_parts[7]
            arrival_time = itinerary_parts[8]
            extra_info = ' '.join(itinerary_parts[9:]) if len(itinerary_parts) > 9 else ''
           
            itinerary_info = {
                'airline_code': flight_details,
                'flight_number': flight_number,
                'cabin_class': cabin_class,
                'date': date,
                'departure_location': departure_location,
                'arrival_location': arrival_location,
                'status': status,
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
        parsed_pnr = parse_pnr(pnr_data)
        return jsonify(parsed_pnr)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
