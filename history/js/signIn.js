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

function signUp() {
    var email = document.getElementById("signUpEmail");
    var pass = document.getElementById("signUpPassword");

    const promise = auth.createUserWithEmailAndPassword(email.value, pass.value);
    promise.catch(e => alert(e.message));

    alert("Sign up");
}

function signIn() {
    var email = document.getElementById("signInEmail");
    var pass = document.getElementById("signInPassword");

    const promise = auth.signInWithEmailAndPassword(email.value, pass.value);
    promise.catch(e => alert(e.message));
    if (user) {
        alert("sign in");
        var uid = user.uid;
        window.location.href = 'history.html?id=' + uid;
    }
}

function signOut() {
    auth.signOut();
    alert("Sign out!");
}

//active user to homepage
firebase.auth().onAuthStateChanged((user) => {
    if (user) {
        var uid = user.uid;
        window.location.href = 'history.html?id=' + uid;
    } else {
        // alert("No Active user Found")
    }
})