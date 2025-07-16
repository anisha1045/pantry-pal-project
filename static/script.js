function call_hello() {
    fetch('/hello')
    .then(response => response.text())
    .then(data => {
        console.log(data);
        alert(data); // or update your page
    });
}