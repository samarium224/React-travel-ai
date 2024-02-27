from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from haversine import haversine
from thesis_with_lat_lon import find_nearest_hotels, place_coordinates,  convert_to_numeric, predict_top_12_place_ids, map_place_id_to_name, model  # Adjust this import

app = Flask(__name__)
CORS(app)

@app.route('/plan-itinerary', methods=['POST'])
def plan_itinerary():
    try:
        data = request.json
        gender = data['gender']
        season = data['season']
        with_whom = data['with_whom']
        budget = data['budget']
        num_days = int(data['num_days'])

        features = {"Gender": gender, "DayOrder": 1, "Season": season, "With": with_whom, "Budget": budget}
        numeric_features = convert_to_numeric(features)
        input_df = pd.DataFrame([numeric_features], columns=['Gender', 'DayOrder', 'Season', 'With', 'Budget'])

        top_place_ids = predict_top_12_place_ids(input_df)
        ref_point = (24.8903, 91.8715)

        places_with_distances = []
        for place_id in top_place_ids:
            place_coord = place_coordinates[place_id]
            distance = haversine(ref_point, place_coord)
            place_name = map_place_id_to_name(place_id)
            places_with_distances.append((place_name, distance))

        places_with_distances.sort(key=lambda x: x[1])

        itinerary = {}
        for day_order in range(1, num_days + 1):
            start_index = (day_order - 1) * 4
            end_index = start_index + 4
            itinerary[f"Day {day_order}"] = [{
                "place": place,
                "distance": f"{distance:.2f} km"
            } for place, distance in places_with_distances[start_index:end_index]]

        
        first_place_id = top_place_ids[0]  # Adjust based on your logic to get the first predicted place ID
        first_place_coord = place_coordinates[first_place_id]
        nearest_hotels = find_nearest_hotels(first_place_coord, 2)  # Getting two nearest hotels

        itinerary_with_hotels = itinerary
        itinerary_with_hotels['Nearest Hotels'] = nearest_hotels

        return jsonify({"itinerary": itinerary_with_hotels})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

       

if __name__ == "__main__":
    app.run(debug=True)