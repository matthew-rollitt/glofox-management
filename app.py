from flask import Flask, json, jsonify, render_template, request, session, redirect, url_for
from firebase_admin import credentials, firestore
import firebase_admin


app = Flask(__name__)
with open('/Users/admin/go/Code/glofox-management/firebase/secret.json', 'r') as file:
    secret_data = json.load(file)
    app.secret_key = secret_data.get('flask', '')

# Initialize Firebase
cred = credentials.Certificate('/Users/admin/go/Code/glofox-management/firebase/femmanagment-firebase-adminsdk-x7yr6-c361ab0e3b.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def get_user(user_id):
    return db.collection('Users').where('MembershipID', '==', user_id).get()


# Error handler for Firestore operations
def handle_firestore_error(error):
    return jsonify({"error": str(error)}), 500

# Routes
@app.route('/get-users', methods=['GET'])
def get_users():
    try:
        status = request.args.get('status')
        users_ref = db.collection('Users')
        query_ref = users_ref.where('status', '==', status) if status else users_ref
        users = [user.to_dict() for user in query_ref.stream()]
        return jsonify(users), 200
    except Exception as e:
        return handle_firestore_error(e)

@app.route('/get-weekly-users', methods=['GET'])
def get_weekly_users():
    try:
        weekly_users_ref = db.collection('WeeklyUsers')
        weekly_users = [doc.to_dict() for doc in weekly_users_ref.stream()]
        return jsonify(weekly_users), 200
    except Exception as e:
        return handle_firestore_error(e)

@app.route('/pausemembership', methods=['POST'])
def pause_membership():
    try:
        data = request.get_json()
        user_id = int(data['userId'].strip())
        user_ref = get_user(user_id)
        
        if not user_ref:
            return jsonify({"message": "No user found with the specified MembershipID."}), 404
        
        for user_doc in user_ref:
            user_data = user_doc.to_dict()
            user_data['status'] = 'Active' if user_data['status'] == 'Paused' else 'Paused'
            user_doc.reference.update(user_data)
        
        return jsonify({"message": "Membership status updated successfully."}), 200
    except Exception as e:
        return handle_firestore_error(e)

@app.route('/cancel-membership', methods=['POST'])
def cancel_membership():
    try:
        data = request.get_json()
        user_id = int(data['userId'].strip())
        user_ref = get_user(user_id)
    
        for user_doc in user_ref:
            user_data = user_doc.to_dict()
            user_data['status'] = 'Cancelled'
            user_doc.reference.update(user_data)
        
        return jsonify({"message": "Membership status updated successfully."}), 200
    except Exception as e:
        return handle_firestore_error(e)


@app.route('/')
def index():
    try:
        users_ref = db.collection('Users')
        users = [doc.to_dict() for doc in users_ref.stream()]
        weekly_users_ref = db.collection('WeeklyUsers')
        weekly_users = [doc.to_dict() for doc in weekly_users_ref.stream()]
        current_week_users = weekly_users[-1]['total_users']
        last_week = weekly_users[-2]['total_users']
        last_month_users = weekly_users[-5]['total_users']
        percent_change_week = round(((current_week_users - last_week) / last_week) * 100, 2)
        percent_change_month = round(((current_week_users - last_month_users) / last_month_users) * 100, 2)

        return render_template('index.html', users=users,
                                current_week_users=current_week_users,
                                last_month_users=last_month_users,
                                percent_change_week=percent_change_week,
                                percent_change_month=percent_change_month)
    except Exception as e:
        return handle_firestore_error(e)

@app.route('/update-membership', methods=['POST'])
def update_membership():
    try:
        user_id = int(request.form.get('userId').strip())
        user_ref = get_user(user_id)
        
        if not user_ref:
            return jsonify({"message": "No user found with the specified MembershipID."}), 404
        
        user_data = user_ref[0].to_dict()
        user_data['email'] = request.form.get('email').strip()
        user_data['name'] = request.form.get('name')
        user_data['membership'] = request.form.get('membership')
        user_data['pauseWeeks'] = request.form.get('pauseWeeks')
        
        status = request.form.get('status')
        if status == 'suspend':
            user_data['status'] = 'Suspended'
        elif status == 'reactivate':
            user_data['status'] = 'Active'
        
        user_ref[0].reference.update(user_data)
        return redirect(url_for('index'))
    
    except Exception as e:
        return handle_firestore_error(e)

if __name__ == '__main__':
    app.run(debug=True)
