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
    }
});

// --------------------------------------- Change password ---------------------------
function forgotPassword() {
    var email = document.getElementById("email").value;
    // check is empty
    if (email != "") {
        firebase.auth().sendPasswordResetEmail(email)
            .then(function () {
                // Password reset email sent.
                Swal.fire({
                    icon: 'success',
                    title: 'Verify your account',
                    html: "A verification email has been sent to " + email +
                        ". <br>Please check your mailbox to verify the account."
                });

            })
            .catch(function (error) {
                // Error occurred. Inspect error.code.
                console.log(error.message);
                Swal.fire({
                    icon: 'error',
                    title: 'Oops...',
                    text: error.message
                });
            });
    } else {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            position: "top",
            text: "Please enter your email address."
        })
    }
}
