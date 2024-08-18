function fetchSensorData() {
    fetch('/sensor_data')
        .then(response => response.json())
        .then(data => {
            document.getElementById('moisture').innerText = data.moisture;
        });
}

function fetchChickenStatuses() {
    fetch('/chicken_status')
        .then(response => response.json())
        .then(data => {
            console.log(data);
            document.getElementById('flu-detected').innerText = data.flu_chickens;
            document.getElementById('total-detected').innerText = data.chickens_detected;
            if (data.flu_chickens > 0) {
                document.getElementById('notification').innerText = `WASPADA TERDAPAT AYAM YANG TERDETEKSI TERJANGKIT FLU BURUNG!`;
                document.getElementById('notification').style.display = 'block';
            } else {
                document.getElementById('notification').style.display = 'none';
            }
        });
}
setInterval(fetchSensorData, 500); 
setInterval(fetchChickenStatuses, 500);  
