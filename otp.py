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
    player = "OTP"

    for row in readCSV:
        if line_count == 0:
            line_count += 1
        else:
            print(row)
            route_type = row[3]
            case = row[0]
            origin = row[1]
            destination = row[2]
            departure_time = datetime.datetime.now()
            date = departure_time.strftime('%m-%d-%Y')
            time = departure_time.strftime('%I:%M%p')
            # sobrescrevendo o tempo na variável departure_time pq já usei e agora quero em outro formato
            departure_time = departure_time.strftime('%m-%d-%Y %H:%M')
            mode = "TRANSIT,WALK"
            transferPenalty = "0"
            arriveBy = "false"
            numItineraries = "5"

            with urllib.request.urlopen("http://dev-otp.quicko.com.br:8080/otp/routers/default/plan?"
                                        "fromPlace=" + origin +
                                        "&toPlace=" + destination +
                                        "&time=" + time +
                                        "&date=" + date +
                                        "&mode=" + mode +
                                        "&arriveBy=" + arriveBy +
                                        "&pathComparator=duration"
                                        "&transferPenalty=" + transferPenalty +
                                        "&numItineraries=" + numItineraries) as url:
                string = url.read()
                payload = json.loads(string)

                requestParameters = payload["requestParameters"]
                plan = payload["plan"]
                itineraries = plan["itineraries"]

                itinerary_id = 0
                for itinerary in itineraries:
                    legs = itinerary["legs"]
                    itinerary_duration = itinerary["duration"]

                    fares = itinerary["fare"]
                    fare = fares["fare"]
                    regular = fare["regular"]
                    itinerary_id += 1

                    leg_id = 0
                    for leg in legs:
                        leg_id += 1

                        responses.append([route_type, case, origin + ";" + destination, departure_time, player, itinerary_id,
                                          leg_id, int(leg["duration"]), leg["mode"], leg["route"], regular["cents"], itinerary_duration])

# filename = player + "_output_" + str(departure_time.timestamp()) + ".csv"
with open("output.csv", mode='a', newline='\n') as output:
    writeCSV = csv.writer(output, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writeCSV.writerows(responses)
