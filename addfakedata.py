import random
from faker import Faker
from datetime import datetime, timedelta
from firebase_init import initialize_firebase, db


fake = Faker()

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