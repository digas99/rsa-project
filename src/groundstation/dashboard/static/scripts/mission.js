let map = L.map('map');
let coordinates = [];
let polygon = null;
let missions = null;

// const ATTRIBUTION = `
// 	<a href="https://www.mapbox.com/about/maps/">© Mapbox </a> |
// 	<a href="http://www.openstreetmap.org/copyright">© OpenStreetMap </a> |
// 	<a href="https://www.mapbox.com/map-feedback/" target="_blank"><strong>Improve this map</strong></a>
// `;
const ATTRIBUTION = `
	<a href="https://www.google.com/maps">© Google Maps </a> |
`;

let baseLayer = L.tileLayer(tileUrl, {
	maxZoom: 21,
    attribution: ATTRIBUTION
}).addTo(map);

const center = [40.63454619621909, -8.660199650809899];

map.setView(center, 20);

map.addEventListener('contextmenu', e => {
	const lat = e.latlng.lat;
	const lng = e.latlng.lng;

	updateCoordinatesList(lat, lng);
	addPointToMap(lat, lng);
	updatePolygon();
});

const addPointToMap = (lat, lng) => {
	L.marker([lat, lng]).addTo(map);
}

const updatePolygon = () => {
	if (coordinates.length < 3) {
		return;
	}

	if (polygon)
		map.removeLayer(polygon);

	polygon = L.polygon(coordinates, {color: 'red'}).addTo(map);
}

const updateCoordinatesList = (lat, lng) => {
	coordinates.push([lat, lng]);

	const list = document.querySelector(".coords");

	const li = document.createElement("li");
	li.innerHTML = `Lat: ${lat}, Lng: ${lng}`;
	list.appendChild(li);
}

document.addEventListener("click", e => {
	if (e.target.closest("button")) {
		let data;
		switch (e.target.id) {
			case "reset-map":
				coordinates = [];
				map.eachLayer(layer => {
					if (layer instanceof L.Marker)
						map.removeLayer(layer);
				});

				if (polygon)
					map.removeLayer(polygon);
				document.querySelector(".coords").innerHTML = "";
				break;
			
			case "generate-mission":
				if (coordinates.length < 2) {
					alert("You need at least 2 points to generate a mission");
					return;
				}

				const drones = Array.from(document.querySelectorAll(".drone-info input"))
					.map(input => input.value);

				if (drones.some(drone => drone === "")) {
					alert("Please state the name of both drones");
					return;
				}

				switchLoading("Generating mission...");

				data = {
					coordinates,
					drones
				};

				fetch("/generate", {
					method: "POST",
					headers: {
						"Content-Type": "application/json"
					},
					body: JSON.stringify(data)
				}).then(res => res.json())
				.then(data => {
					console.log(data);

					selectStep(2);

					// Add image of the plot
					const image = new Image();
					image.src = 'data:image/jpeg;base64,' + data.image;
					const plot = document.querySelector(".step[data-index='2'] .content .plot");
					plot.appendChild(image);

					// Add mission map
					const missionMap = L.map('mission-map');
					L.tileLayer(tileUrl, {
						maxZoom: 22,
						attribution: ATTRIBUTION
					}).addTo(missionMap);
					
					missionMap.setView(data.center, 21);

					// Add polygons to the map
					data.polygons.forEach(polygon => {
						// create polygon
						L.polygon(polygon, {color: 'green'}).addTo(missionMap);

						// add polygon points
						polygon.forEach(point => {
							L.marker(point).addTo(missionMap);
						});
					});

					// Handle station info
					missions = data.missions;
					handleStationInfo(missions);

					switchLoading();
				});
				break;
			case "send-mission":
				const stationURL = document.querySelector(".station input").value;
				if (!stationURL) {
					alert("Please state the station URL");
					return;
				}

				const selectedDrones = getSelectedDrones();
				data = {
					"station": stationURL,
					"drones": selectedDrones,
				};

				switchLoading("Sending mission...");

				fetch("/mission", {
					method: "POST",
					headers: {
						"Content-Type": "application/json"
					},
					body: JSON.stringify(data)
				}).then(res => res.json())
				.then(data => {
					console.log(data);
					switchLoading();

					if (data.error) {
						alert(data.error);
						return;
					}
					
					selectStep(3);
				});

				break;
		}
	}

	if (e.target.closest(".step .title")) {
		const step = e.target.closest(".step").dataset.index;
		selectStep(step);
	}
});

document.addEventListener("change", e => {
	if (e.target.closest(".station input")) {
		handleStationInfo(missions);
	}
});

const selectStep = step => {
	const steps = document.querySelectorAll(".step");
	steps.forEach(s => {
		if (s.dataset.index !== step) {
			s.querySelector(".content").style.display = "none";
		}
	});

	const currentStep = document.querySelector(`.step[data-index='${step}']`);
	currentStep.querySelector(".content").style.removeProperty("display");
}

const switchLoading = text => {
	const loading = document.querySelector(".loading");
	if (loading.style.display === "none") {
		loading.style.removeProperty("display");
		
		if (text)
			loading.querySelector(".popup").innerText = text;
	}
	else
		loading.style.display = "none";
}

let stationPing = null;

const handleStationInfo = missions => {
	const droneNames = document.querySelectorAll(".drones .name");
	missions.forEach((mission, index) => {
		droneId = mission.drone;
		droneNames[index].innerText = droneId;
	});

	const stationInfo = document.querySelector(".station-info");
	const stationURL = stationInfo.querySelector(".station input").value;

	if (stationURL) {
		// Clear any existing interval to avoid multiple intervals running at the same time
		if (stationPing) {
			clearInterval(stationPing);
		}

		// Function to ping the station URL
		const pingStation = (drones) => {
			const body = {
				"station": stationURL,
				drones
			};

			fetch("/station", {
				method: "POST",
				headers: {
					"Content-Type": "application/json"
				},
				body: JSON.stringify(body)
			}).then(response => response.json())
			.then(data => {
				console.log(data);
				if (data && !data.error) {
					// update station status
					updateStatus(0, true);

					// update drone status
					const drones = getSelectedDrones().map(drone => drone.name);
					const availableDrones = data;
					drones.forEach((drone, index) => {
						updateStatus(index + 1, availableDrones.includes(drone));
					});
				}
				else {
					// update station status
					[0, 1, 2].forEach(index => updateStatus(index, false));
				}
			});
		};

		pingStation(getSelectedDrones().map(drone => drone.name));

		stationPing = setInterval(() => pingStation(getSelectedDrones().map(drone => drone.name)), 1000);
	}

	// add mission files
	droneNames.forEach(name => {
		const drone = name.innerText;
		const mission = missions.find(m => m.drone === drone);
		updateMissionFile(drone, mission.content);
	});
}

const getSelectedDrones = () => {
	const drones = Array.from(document.querySelectorAll(".drones > div"));
	const data = [];
	drones.forEach(drone => {
		data.push({
			name: drone.querySelector(".name").innerText,
			server: drone.querySelector(".drone-server input").value
		})
	});
	return data;
}

const updateStatus = (index, online) => {
	const status = document.querySelectorAll(".status")[index];
	status.classList.remove("offline", "online");
	status.classList.add(online ? "online" : "offline");
}

const updateMissionFile = (drone, content) => {
	const drones = Array.from(document.querySelectorAll(".drones .name"));
	const index = drones.findIndex(d => d.innerText === drone);
	const missionFile = document.querySelectorAll(".drone-mission")[index];
	const lines = content.split("\n");
	missionFile.innerHTML = "";
	lines.forEach(line => {
		const li = document.createElement("div");
		li.innerText = line;
		missionFile.appendChild(li);
	});
}

// handle url parameters
const urlParams = new URLSearchParams(window.location.search);
const step = urlParams.get("step");
if (step) {
	selectStep(step);
}

// Connect to the MQTT broker
url = window.location.href;
const client = mqtt.connect('ws://' + url.split('/')[2] + ':9005');

client.on('connect', function () {
    console.log('Connected to MQTT broker');

    // Subscribe to the topics /counter/device1 and /counter/device2
	client.subscribe('/counter/device1', function (err) {
		if (!err) {
			console.log('Subscribed to /counter/device1');
		}
	});
	client.subscribe('/counter/device2', function (err) {
		if (!err) {
			console.log('Subscribed to /counter/device2');
		}
	});
});

client.on('message', function (topic, message) {
	const counters = document.querySelectorAll(".count");
	if (topic === '/counter/device1') {
		const counter = JSON.parse(message.toString())["people"];
		counters[0].innerText = counter;
	}
	if (topic === '/counter/device2') {
		const counter = JSON.parse(message.toString())["people"];
		counters[1].innerText = counter;
	}
});

client.on('error', function (error) {
    console.error('Connection error:', error);
});