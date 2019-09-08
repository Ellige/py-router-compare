import datetime
import urllib.request
import json
import csv

responses = []

try:
    f = open('output.csv')
    f.close()
except FileNotFoundError:
    print('File does not exist')
    responses.append(["route_type", "case", "origin_destination", "departure_time", "player", "itinerary", "leg",
                      "duration_leg", "modal", "line", "fare", "itinerary_duration"])

with open('input.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=';')
    line_count = 0
    itinerary_id = 0
    leg_id = 0
    player = "Google"

    for row in readCSV:
        if line_count == 0:
            line_count += 1
        else:
            print(row)
            route_type = row[3]
            case = row[0]
            origin = row[1]
            destination = row[2]
            mode = "transit"
            alternatives = "true"
            departure_time = "now"
            key = "AIzaSyCbMkR5Pa3RN60Dp8d6abdcZQ3F5pIv914"

            with urllib.request.urlopen("https://maps.googleapis.com/maps/api/directions/json?" +
                                        "key=" + key +
                                        "&origin=" + origin +
                                        "&destination=" + destination +
                                        "&mode=" + mode +
                                        "&language=pt-BR" +
                                        "&departure_time=" + departure_time +
                                        "&alternatives=" + alternatives) as url:
                string = url.read()
                payload = json.loads(string)

                departure_time = datetime.datetime.now()
                departure_time = departure_time.strftime('%m-%d-%Y %H:%M')

                routes = payload["routes"]
                itinerary_id = 0
                for route in routes:
                    try:
                        fare = route["fare"]
                    except KeyError:
                        continue

                    cents = float(fare["value"])*100

                    legs = route["legs"]
                    itinerary_id += 1

                    leg_id = 0
                    for leg in legs:
                        itinerary_duration = leg["duration"]
                        itinerary_duration = itinerary_duration["value"]
                        steps = leg["steps"]
                        for step in steps:
                            duration = step["duration"]
                            duration = duration["value"]
                            leg_id += 1

                            try:
                                transit_details = step["transit_details"]
                            except KeyError:
                                transit_details = {"line": {"short_name": "", "vehicle": {"type": "WALK"}}}

                            line = transit_details["line"]
                            short_name = line["short_name"]
                            vehicle = line["vehicle"]
                            mode = vehicle["type"]
                            if mode == "HEAVY_RAIL":
                                mode = "RAIL"

                            responses.append([route_type, case, origin + ";" + destination, departure_time, player,
                                              itinerary_id, leg_id, duration, mode, short_name, int(cents), itinerary_duration])

# filename = player + "_output_" + str(departure_time.timestamp()) + ".csv"
with open("output.csv", mode='a', newline='\n') as output:
    writeCSV = csv.writer(output, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writeCSV.writerows(responses)
