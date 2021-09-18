// --------------------------------------- Firebase configuration ---------------------------
var firebaseConfig = {
    apiKey: "AIzaSyBZRN-qaq0NluYrPUxg6l1m2ppmpVQt4-0",
    authDomain: "face-mask-detection-2021-8710d.firebaseapp.com",
    databaseURL: "https://face-mask-detection-2021-8710d-default-rtdb.firebaseio.com/",
    projectId: "face-mask-detection-2021-8710d",
    storageBucket: "face-mask-detection-2021-8710d.appspot.com",
    messagingSenderId: "78703109154",
    appId: "1:78703109154:web:11a0b3be7bee28a057567b",
    measurementId: "G-VDV219Y7T0"
};
firebase.initializeApp(firebaseConfig);

// --------------------------------------- Get current date ---------------------------
function convertTZ(date, tzString) {
    return new Date((typeof date === "string" ? new Date(date) : date).toLocaleString("en-US", { timeZone: tzString }));
}
const date = new Date();
var today = convertTZ(date, "Asia/Singapore");
// var todayDate = today.toISOString().split('T')[0];
// cahnge date format to YYYY-MM-DD
var todayDate = today.getFullYear() + '-' + ("0" + (today.getMonth() + 1)).slice(-2) + '-' + ("0" + today.getDate()).slice(-2);

// --------------------------------------- CHECK CURENT USER STATUS ---------------------------
firebase.auth().onAuthStateChanged((user) => {
    if (user) {
        console.log("curent user:" + user.uid);
        // --------------------------------------- Date picker ---------------------------------------
        firebase
            .database()
            .ref(user.uid + "/date")
            .on("value", (sanpshot) => {
                const dateArray = [];
                sanpshot.forEach(function (element) {
                    value = element.val();
                    dateArray.push(value)
                    console.log("Array:" + dateArray)
                    var input = document.getElementById("selectDate");
                    input.min = dateArray[0];
                    input.max = dateArray[dateArray.length - 1];
                });
            })

        // --------------------------------------- Load Image -------------------------------------
        var firebaseRef = firebase.database().ref(user.uid + "/" + todayDate);
        console.log("Today here: " + todayDate);

        firebaseRef.on("value", (sanpshot) => {
            var data = '';
            var counter = 0;
            document.querySelector('#historyTable').innerHTML = `<thead>
            <th>No</th>
            <th>Image</th>
            <th>Time</th>
        </thead>`
            // document.querySelector('#root').innerHTML = ``
            sanpshot.forEach(function (element) {
                counter += 1
                value = element.val();
                // console.log(value.image)
                data += '<tr>';
                data += '<td>' + counter + '</td>';
                data += `<td> <img src="../${value.image}" alt="No mask" width="200""></td>`;
                data += '<td>' + value.time + '</td>';
                data += '</tr>';
                // document.querySelector('#root').innerHTML += `<div>${value.image}</div>`
            });
            $('#historyTable').append(data);
        })
    } else {
        // no active user
        window.location.href = 'signin_signup.html';
        // alert("No Active user Found")
    }
})

// --------------------------------------- SIGN OUT ---------------------------
const auth = firebase.auth();
function signOut() {
    if (confirm('Are you sure you want to log out?')) {
        auth.signOut();
        console.log("sign out");
    } else {
        // Do nothing!
        console.log('Do nothing');
    }
}
// --------------------------------------- Enter button onClick ---------------------------
$('#submit').on('click', function () {
    var date = new Date($('#selectDate').val());
    if (date == "Invalid Date") {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            html: "Please select a date from calendar."
        })
    }
    else {
        // get the date
        var day = date.getDate();
        if (day < 10) {
            day = "0" + day;
        }

        var month = date.getMonth() + 1;
        if (month < 10) {
            month = "0" + month;
        }

        var year = date.getFullYear();
        var selectdate = [year, month, day].join('-');

        // get user id
        const user = auth.currentUser;
        userId = user.uid;
        // alert(userId)

        // update the history table
        document.getElementById("curentSelectedDate").innerHTML = "Curent selected date: <b>" + selectdate + "</b>";
        specificRecord(userId, selectdate)
    }
});

function specificRecord(uid, date) {
    console.log("update: " + date)
    var firebaseRef = firebase.database().ref(uid + "/" + date);

    firebaseRef.once("value", (sanpshot) => {
        var data = '';
        var counter = 0;
        document.querySelector('#historyTable').innerHTML = `<thead>
            <th>No</th>
            <th>Image</th>
            <th>Time</th>
        </thead>`
        // document.querySelector('#root').innerHTML = ``
        sanpshot.forEach(function (element) {
            counter += 1
            value = element.val();
            // console.log(value.image)
            data += '<tr>';
            data += '<td>' + counter + '</td>';
            data += `<td> <img src="../${value.image}" alt="No mask" width="200""></td>`;
            data += '<td>' + value.time + '</td>';
            data += '</tr>';
            // document.querySelector('#root').innerHTML += `<div>${value.image}</div>`
        });
        $('#historyTable').append(data);
    })
}


    // firebase
    //     .database()
    //     .ref("ehkIRTMmZubKIQZlYlbC9AT71wD3/13-Sep-2021")
    //     .on("value", (sanpshot) => {
    //         console.log(sanpshot.val());
    //     });