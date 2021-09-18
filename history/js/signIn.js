// --------------------------------------- UI animation ---------------------------
const sign_in_btn = document.querySelector("#sign-in-btn");
const sign_up_btn = document.querySelector("#sign-up-btn");
const container = document.querySelector(".container");

sign_up_btn.addEventListener("click", () => {
    container.classList.add("sign-up-mode");
});

sign_in_btn.addEventListener("click", () => {
    container.classList.remove("sign-up-mode");
});

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

const auth = firebase.auth();

// --------------------------------------- SIGN UP ---------------------------
function signUp() {
    var email = document.getElementById("signUpEmail").value;
    var pass = document.getElementById("signUpPassword").value;
    var confirmPass = document.getElementById("signUpConfirmPassword").value;
    // (?=.*\d)          // should contain at least one digit
    // (?=.*[a-z])       // should contain at least one lower case
    // (?=.*[A-Z])       // should contain at least one upper case
    // [a-zA-Z0-9]{8,}   // should contain at least 8 from the mentioned characters
    // (?=.*[!@#$%^&*])  // should contain at least one special character
    var vpass = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*])(?=.*[^a-zA-Z0-9])(?!.*\s).{8,}$/;

    // check is empty
    if (email != "" && pass != "" && confirmPass != "") {
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
                    // sign up here
                    auth.createUserWithEmailAndPassword(email, pass).catch(function (error) {
                        // error occur
                        Swal.fire({
                            icon: 'error',
                            title: 'Oops...',
                            html: error.message
                        })
                    }).then(function (user) {
                        // is sign up
                        if (user) {
                            Swal.fire({
                                icon: 'success',
                                title: 'Welcome',
                                showConfirmButton: false,
                                timer: 1500
                            });
                        }
                    })
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

// --------------------------------------- SIGN IN ---------------------------
function signIn() {
    var email = document.getElementById("signInEmail").value;
    var pass = document.getElementById("signInPassword").value;
    //check is empty
    if (email != "" && pass != "") {
        // sign in here
        auth.signInWithEmailAndPassword(email, pass).catch(function (error) {
            // error occur
            Swal.fire({
                icon: 'error',
                title: 'Oops...',
                html: error.message
            })
        }).then(function (user) {
            //is sign in
            if (user) {
                Swal.fire({
                    icon: 'success',
                    title: 'Welcome',
                    showConfirmButton: false,
                    timer: 1500
                });
            }
        })
    } else {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: "All fields cannot be empty."
        });
    }
}

// --------------------------------------- CHECK CURENT USER STATUS ---------------------------
firebase.auth().onAuthStateChanged((user) => {
    if (user) {
        console.log("loged in");
        setTimeout(function () {
            window.location.href = 'history.html';
        }, 2000)

    } else {
        console.log("No Active user Found");
    }
});