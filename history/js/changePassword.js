// --------------------------------------- Firebase configuration ---------------------------
var firebaseConfig = {
    apiKey: "",
    authDomain: "",
    databaseURL: "",
    projectId: "",
    storageBucket: "",
    messagingSenderId: "",
    appId: "",
    measurementId: ""
};
firebase.initializeApp(firebaseConfig);

// --------------------------------------- CHECK CURENT USER STATUS ---------------------------
firebase.auth().onAuthStateChanged((user) => {
    if (user) {
        console.log("loged in");
    } else {
        console.log("No Active user Found");
        window.location.href = 'signIn_signUp.html';
    }
})

// --------------------------------------- CHANGE PASSWORD ---------------------------
function changePassword() {
    var pass = document.getElementById("password").value;
    var confirmPass = document.getElementById("confirmPassword").value;
    // (?=.*\d)          // should contain at least one digit
    // (?=.*[a-z])       // should contain at least one lower case
    // (?=.*[A-Z])       // should contain at least one upper case
    // [a-zA-Z0-9]{8,}   // should contain at least 8 from the mentioned characters
    // (?=.*[!@#$%^&*])  // should contain at least one special character
    var vpass = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*])(?=.*[^a-zA-Z0-9])(?!.*\s).{8,}$/;

    // check is empty
    if (pass != "" && confirmPass != "") {
        // compare password
        if (pass != confirmPass) {
            Swal.fire({
                icon: 'error',
                title: 'Oops...',
                text: "Passwords doesn't match"
            });
        } else {
            // check password length
            if (pass.length < 8) {
                Swal.fire({
                    icon: 'error',
                    title: 'Oops...',
                    text: "Password must have at least 8 characters"
                });
            } else {
                //check password format
                if (!pass.match(vpass)) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Oops...',
                        html: "<p>Passwords should contain: <br> -at least one digit" +
                            "<br> -at least one lower case <br> -at least one upper case" +
                            "<br> -at least one special character</p>"
                    });
                } else {
                    // change password here --------------------------------------------------------------
                    var auth = firebase.auth().currentUser;
                    auth.updatePassword(pass).then(function () {
                        // Update successful.
                        console.log("Update successful.");
                        Swal.fire({
                            icon: 'success',
                            title: 'Password Changed!',
                            text: "Your password has been changed successfully.",
                            showConfirmButton: false,
                            timer: 1500
                        });
                        setTimeout(function () {
                            window.location.href = 'history.html';
                        }, 2000)
                    }).catch(function (error) {
                        // An error happened.
                        console.log(error.message);
                        Swal.fire({
                            icon: 'error',
                            title: 'Oops...',
                            text: error.message
                        });
                    });
                }
            }
        }
    } else {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: "All fields cannot be empty."
        });
    }
}

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
