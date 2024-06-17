from flask import Flask, json, jsonify, render_template, request, session, redirect, url_for
import firebase_admin
from firebase_admin import credentials, auth, firestore
from datetime import datetime, timedelta
from jsonify import convert
from faker import Faker


import random
fake = Faker()

# Initialize Flask app
app = Flask(__name__)
with open('/Users/admin/go/Code/glofox-management/firebase/secret.json', 'r') as file:
    secret_data = json.load(file)
    app.secret_key = secret_data.get('flask', '')

# Initialize Firebase
cred = credentials.Certificate('/Users/admin/go/Code/glofox-management/firebase/femmanagment-firebase-adminsdk-x7yr6-c361ab0e3b.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/get-users', methods=['GET'])
def get_users():
    status = request.args.get('status', default=None, type=str)
    users_ref = db.collection('Users')
    if status:
        query_ref = users_ref.where('status', '==', status)
    else:
        query_ref = users_ref
    users = query_ref.stream()
    users_list = []
    for user in users:
        user_dict = user.to_dict()
        users_list.append({
            'MembershipID': user_dict.get('MembershipID'),
            'name': user_dict.get('name'),
            'membership': user_dict.get('membership'),
            'email': user_dict.get('email'),
            'status': user_dict.get('status')  # Ensure 'status' field exists in Firestore documents
        })

    return jsonify(users_list)

def add_users_to_firestore(num_users):
    for _ in range(num_users):
        # Generate random user data
        name = fake.name()
        new_user = {
            'MembershipID': random.randint(1, 300),
            'name': name,
            'membership': random.choice(['Like', 'Love', 'Talk']),
            'email': name.replace(' ', '').lower() + '@example.com',
            'created_at': datetime.now(),
            'pauseWeeks': 0,
            'status': 'Active'
        }
        
        # Check if the user already exists in the database
        users_ref = db.collection('Users').where('MembershipID', '==', new_user['MembershipID']).stream()
        if not any(users_ref):
            # Add the new user to the 'Users' collection
            db.collection('Users').add(new_user)
            print(f"Added new user: {new_user}")
        else:
            print(f"User {new_user['name']} already exists.")

# Call the function to add 80 random users
#add_users_to_firestore(80)
@app.route('/get-weekly-users', methods=['GET'])
def get_weekly_users():
    try:
        # Fetch weekly users data from Firestore
        weekly_users_ref = db.collection('WeeklyUsers')
        weekly_users_docs = weekly_users_ref.stream()

        weekly_users = []
        for doc in weekly_users_docs:
            data = doc.to_dict()
            weekly_users.append({
                'week_start': data['week_start'],
                'week_end': data['week_end'],
                'membership_counts': data['membership_counts'],
                'paused_memberships': data['paused_memberships'],
                'total_users': data['total_users']
            })

        return jsonify(weekly_users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

users = [
    {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "membership": "Love",
        "pauseweeks": 0,
        "status": "active"
    },
    # Add more user data as needed
]

@app.route('/pausemembership', methods=['POST'])
def pause_membership():
    try:
        data = request.get_json()
        user_id = data['userId'].strip()
        print("userId: " + user_id)
        user_ref = db.collection('Users').where('MembershipID', '==', int(user_id)).get()
        
        # Check if user with the given MembershipID exists
        if user_ref:
            for user_doc in user_ref:
                user_data = user_doc.to_dict()
                # Check if the account is already paused
                if user_data['status'] == 'Paused':
                    # Set the account status to 'Active'
                    user_data['status'] = 'Active'
                else:
                    # Set the account status to 'Paused'
                    user_data['status'] = 'Paused'
                user_doc.reference.update(user_data)
                print("Membership status updated successfully.")
            return jsonify({"message": "Membership status updated successfully."}), 200
        else:
            print("No user found with the specified MembershipID.")
            return jsonify({"message": "No user found with the specified MembershipID."}), 404

    except Exception as e:
        print(f"Error updating membership status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/cancel-membership', methods=['POST'])
def cancel_membership():
    try:
        data = request.get_json()
        user_id = data['userId'].strip()
        print("userId: " + user_id)
        user_ref = db.collection('Users').where('MembershipID', '==', int(user_id)).get()
        
        # Check if user with the given MembershipID exists
        if user_ref:
            for user_doc in user_ref:
                user_data = user_doc.to_dict()
                user_data['status'] = 'Cancelled'
                user_doc.reference.update(user_data)
                print("Membership status cancelled successfully.")
            return jsonify({"message": "Membership status updated successfully."}), 200
        else:
            print("No user found with the specified MembershipID.")
            return jsonify({"message": "No user found with the specified MembershipID."}), 404
    except Exception as e:
        print(f"Error updating membership status: {e}")
        return jsonify({"error": str(e)}), 500



def add_weekly_to_firestore(num_weeks):
    try:
        total_users = 48  # Set the initial total users count to 40
        membership_counts = {'Like': 0, 'Love': 0, 'Talk': 0}

        for i in range(num_weeks):
            # Generate random user data for the week
            week_start = datetime.now() - timedelta(days=(7 * (num_weeks - i)))
            week_end = datetime.now() - timedelta(days=(7 * (num_weeks - i - 1)))
            paused_memberships = []

            # Decide if we are adding new members or losing one member
            new_members = random.randint(1, 5)
            total_users += new_members

            for _ in range(new_members):
                membership = random.choice(['Like', 'Love', 'Talk'])
                membership_counts[membership] += 1

            if random.random() < 0.2:
                paused_memberships.append(membership)

            # Add the membership counts to the 'WeeklyUsers' collection
            db.collection('WeeklyUsers').add({
                'week_start': week_start.strftime('%Y-%m-%d'),
                'week_end': week_end.strftime('%Y-%m-%d'),
                'membership_counts': membership_counts.copy(),
                'paused_memberships': paused_memberships.copy(),
                'total_users': total_users
            })
            print("Added membership counts and paused memberships.")
    except Exception as e:
        print(f"Error adding weekly users: {e}")


# Call the function to add 14 weeks of data
#add_weekly_to_firestore(14)

@app.route('/')
def index():
    try:
        users_ref = db.collection('Users')
        users = [doc.to_dict() for doc in users_ref.stream()]
        return render_template('index.html', users=users)
    except Exception as e:
        return f'Error loading users: {e}', 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Add your authentication logic here (e.g., Firebase Authentication)
        session['user'] = request.form['user']
        return redirect(url_for('profile'))
    return render_template('login.html')



@app.route('/update-membership', methods=['POST'])
def update_membership():
    print("Updating membership")
    try:
        new_membership = request.form.get('membership')
        new_email = request.form.get('email').strip()
        new_name = request.form.get('name')
        user_id = request.form.get('userId').strip()
        pause_weeks = request.form.get('pauseWeeks')  # Get the pauseWeeks value
        status = request.form.get('status')  # Get the status value

        print(user_id)
        user_ref = db.collection('Users').where('MembershipID', '==', int(user_id)).get()
        # Check if user with the given MembershipID exists
        if user_ref:
            for user_doc in user_ref:
                print(user_doc.to_dict())
                user_data = user_doc.to_dict()
                user_data['email'] = new_email
                user_data['name'] = new_name
                user_data['membership'] = new_membership
                user_data['pauseWeeks'] = pause_weeks  # Add the pauseWeeks to the user data

                # Update the user status based on the selected option
                if status == 'suspend':
                    user_data['status'] = 'Suspended'
                elif status == 'reactivate':
                    user_data['status'] = 'Active'

                # Save the updated data back to Firestore
                user_doc.reference.update(user_data)

            print("User updated successfully.")
        else:
            print("No user found with the specified MembershipID.")

        return redirect(url_for('index'))

    except Exception as e:
        print(f"Error updating membership: {e}")
        return f'Error updating membership: {e}', 500


def aggregate_membership_data():
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)  # Last two months
        week_data = []

        for week_start in range(0, 60, 7):
            current_week_start = start_date + timedelta(days=week_start)
            current_week_end = current_week_start + timedelta(days=6)
            users_ref = db.collection('Users').where('created_at', '>=', current_week_start).where('created_at', '<=', current_week_end).stream()
            membership_counts = {'Like': 0, 'Love': 0, 'Talk': 0}

            for user in users_ref:
                user_data = user.to_dict()
                membership_counts[user_data['membership']] += 1

            week_data.append({
                'week_start': current_week_start.strftime('%Y-%m-%d'),
                'week_end': current_week_end.strftime('%Y-%m-%d'),
                'membership_counts': membership_counts
            })

        # Store the aggregated data in a new Firestore collection
        for week in week_data:
            db.collection('WeeklyMembershipData').add(week)
            print(f"Added week data: {week}")

    except Exception as e:
        print(f"Error aggregating membership data: {e}")

# Uncomment this to run the aggregation function
# aggregate_membership_data()

if __name__ == '__main__':
    app.run(debug=True)
