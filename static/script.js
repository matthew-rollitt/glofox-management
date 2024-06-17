function openEditPopup(userId, userName, email, membership, pauseweeks, status) {
    document.getElementById('userIdInput').value = userId;
    document.getElementById('userIdTitle').textContent = userId;
    document.getElementById('userNameTitle').textContent = userName;
    document.getElementById('nameInput').value = userName;
    document.getElementById('emailInput').value = email;
    document.getElementById('membership').value = membership;
    document.getElementById('editPopup').style.display = 'block';
    document.getElementById('pauseWeeks').value = pauseweeks;
    document.getElementById('status').value = status;
    console.log(status);
}

function cancelMembership(userId) {
    // Assuming you have the user's ID and a server endpoint to handle the cancellation
    fetch('/cancel-membership', {
        method: 'POST', // or 'PUT'
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ userId: userId }), // Send the user ID to the server
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Network response was not ok.');
    })
    .then(data => {
        console.log(data.message); // Assuming the server responds with a message
        alert('Membership cancelled successfully.');
        // Here you can add code to update the UI accordingly
    })
    .catch((error) => {
        console.error('There was a problem with the cancellation request:', error);
        alert('Failed to cancel membership. Please try again.');
    });
}


function closeEditPopup() {
    document.getElementById('editPopup').style.display = 'none';
}


function getGradient(ctx, startColor, endColor) {
    var gradient = ctx.createLinearGradient(0, 0, 0, ctx.canvas.height);
    gradient.addColorStop(0, startColor); // Start color
    gradient.addColorStop(1, endColor);   // End color (fully transparent)
    return gradient;
}


function filterByUsername() {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("searchUsername");
    filter = input.value.toUpperCase();
    table = document.getElementById("userTable");
    tr = table.getElementsByTagName("tr");
    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[0];
        if (td) {
            txtValue = td.textContent || td.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }       
    }
}
function pauseMembership(userId) {
    console.log('Pausing');
    console.log('Pausing membership for user:', userId);
    if (confirm('Are you sure you want to pause the membership?')) {
        fetch('/pausemembership', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ userId: userId })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            // Handle the response from the server
            location.reload(); // Refresh the page
        })
        .catch(error => {
            console.error('Error pausing membership:', error);
        });
    }
}

function sortTable(n) {
    var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    table = document.getElementById("userTable");
    switching = true;
    dir = "asc"; 
    while (switching) {
        switching = false;
        rows = table.rows;
        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("TD")[n];
            y = rows[i + 1].getElementsByTagName("TD")[n];
            if (dir == "asc") {
                if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                    shouldSwitch = true;
                    break;
                }
            } else if (dir == "desc") {
                if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            switchcount++;
        } else {
            if (switchcount == 0 && dir == "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
}
