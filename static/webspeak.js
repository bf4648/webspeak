function reconnect() {
    setTimeout(connect, 5000);
}

function status(status) {
    var statuselement = document.getElementById('status');
    statuselement.innerHTML = status;
}

function connect() {
    websock = new WebSocket("ws://" + window.location.host);
    websock.onopen = function(event) {
	status('Waiting for first request');
    }

    websock.onmessage = function(event) {
	var data = JSON.parse(event.data);
	status('Last spoke: ' + data['speak']);
	console.log(data['speak']);
	var u = new SpeechSynthesisUtterance();
	u.text = data['speak'];
	u.lang = 'en-US';
	u.rate = 0.7;
	console.log(u);
	window.speechSynthesis.speak(u);
    }

    websock.onerror = function(event) {
	console.log('Error');
	status('ERROR');
    }

    websock.onclose = function(event) {
	console.log('Closed');
	status('Reconnecting...');
	reconnect();
    }
}

connect();
