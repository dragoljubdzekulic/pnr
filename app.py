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

    # Handle record locator (first line)
    pnr_info['record_locator'] = lines[0]
    logging.debug(f"Record Locator: {pnr_info['record_locator']}")

    # Handle passenger name (second line)
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
        
        # Validate if first name exists
        pnr_info['passenger_name']['first_name'] = first_name_and_title[0].strip() if len(first_name_and_title) > 0 else ''
        
        # Validate if title exists
        pnr_info['passenger_name']['title'] = first_name_and_title[1].strip() if len(first_name_and_title) > 1 else ''

    # Handle itinerary (remaining lines)
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
            r'(\d{4})?\s*'                # Departure time (optional, might be incomplete)
            r'(\d{4})?\s*'                # Arrival time (optional, might be incomplete)
            r'(.*)?'                      # Extra info (optional)
        )
        match = re.match(pattern, line)
        if not match:
            logging.warning(f"Skipping line due to insufficient parts: {line}")
            continue

        route = match.group(7)
        departure_location = route[:3] if route else ''
        arrival_location = route[3:] if route else ''

        # Ensure departure and arrival times have valid values
        departure_time = match.group(9)
        arrival_time = match.group(10)
        
        # Handle missing or incomplete times (e.g., 235 should be 0235)
        if departure_time and len(departure_time) < 4:
            departure_time = departure_time.zfill(4)
        if arrival_time and len(arrival_time) < 4:
            arrival_time = arrival_time.zfill(4)

        segment_info = {
            'segment_number': match.group(1) if match.group(1) else '',
            'airline_code': match.group(2) if match.group(2) else '',
            'flight_number': match.group(3) if match.group(3) else '',
            'cabin_class': match.group(4) if match.group(4) else '',
            'date': match.group(5) if match.group(5) else '',
            'day': match.group(6) if match.group(6) else '',
            'route': route if route else '',
            'departure_location': departure_location,
            'arrival_location': arrival_location,
            'status': match.group(8) if match.group(8) else '',
            'departure_time': departure_time if departure_time else '',
            'arrival_time': arrival_time if arrival_time else '',
            'extra_info': match.group(11).strip() if match.group(11) else ''
        }

        pnr_info['itinerary'].append(segment_info)

    return pnr_info
