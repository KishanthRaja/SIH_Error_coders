from flask import Flask, request, render_template, jsonify
import pandas as pd
import datetime

app = Flask(__name__)

# Load dataset
df = pd.read_csv('bus_schedule_dataset.csv')

# Dictionaries to store driver and conductor shift info
shift_info = {}
route_allocation = {}
allocated_details = {}  # To store allocated details
driver_list = ['ganesh','siva','parvathi']
conductor_list = ['ganesh','siva','parvathi']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/allocate', methods=['POST'])
def allocate():
    driver_name = request.form.get('driver_name')
    conductor_name = request.form.get('conductor_name')

    if driver_name.lower() not in driver_list:
        return jsonify({'status':'error','message':'Driver name not in Directory.'})
    
    if conductor_name.lower() not in conductor_list:
        return jsonify({'status':'error','message':'Conductor name not in Directory.'})
    
    # Check if driver or conductor exists and if their shift is over
    def check_shift(name):
        if name.lower() in shift_info:
            shift_end = shift_info[name]['end_time']
            if datetime.datetime.now() > shift_end:
                return True
            else:
                return f"{name} shift ends by {shift_end.strftime('%H:%M')}"
        return True

    driver_check = check_shift(driver_name)
    conductor_check = check_shift(conductor_name)

    if isinstance(driver_check, str):
        return jsonify({'status': 'error', 'message': driver_check})
    if isinstance(conductor_check, str):
        return jsonify({'status': 'error', 'message': conductor_check})

    # Find an available shift
    for _, row in df.iterrows():
        route_number = row['Route Number']
        if route_number not in route_allocation:
            # Allocate shift
            shift_info[driver_name.lower()] = {'shift': row['Shift Hours'], 'end_time': datetime.datetime.now() + datetime.timedelta(hours=12)}
            shift_info[conductor_name.lower()] = {'shift': row['Shift Hours'], 'end_time': datetime.datetime.now() + datetime.timedelta(hours=12)}
            route_allocation[route_number] = {'driver': driver_name, 'conductor': conductor_name}

            # Save allocated details
            allocated_details[route_number] = {
                'driver': driver_name,
                'conductor': conductor_name,
                'route_stops': row['Route Stops'],
                'route_timings': row['Route Timings']
            }

            return jsonify({
                'status': 'success',
                'route_number': route_number,
                'route_stops': row['Route Stops'],
                'route_timings': row['Route Timings']
            })

    return jsonify({'status': 'error', 'message': 'No available routes for allocation.'})

@app.route('/show_schedule', methods=['GET'])
def show_schedule():
    return jsonify(allocated_details)

if __name__ == '__main__':
    app.run(debug=True)
