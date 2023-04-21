// run with deno run --allow-read --allow-net journeys.js

const getStations = async () => {
    let stations = [];
    let url = "https://iot.hamburg.de/v1.0/Things?$filter=Datastreams/properties/serviceName%20eq%20%27HH_STA_StadtRad%27&$orderby=id&$count=true&$expand=Locations";
    let resp = await fetch(url);
    let json = await resp.json();
    let nextLink = json["@iot.nextLink"];

    stations = json.value;
    console.log(nextLink)
    console.log(typeof stations)

    while (nextLink) {
        resp = await fetch(nextLink);
        json = await resp.json();
        nextLink = json["@iot.nextLink"];

        stations.push(...json.value);
        console.log(nextLink);
    }
    console.log("done")
    console.log(stations.length)

    // Deno.writeTextFile("stations.json", JSON.stringify(stations));
    // return (stationId) => {
    //     for (const station of stations) {
    //         if (station.properties.stationsNummer === stationId) {
    //             return station;
    //         }
    //     }

    //     return null;
    // }
    return stations;
};

const stations = await getStations();


const text = await Deno.readTextFile("./Hamburg_2021.csv");

const csvlines = text.split("\n");

const file = {
    journeys: [],
    stations: {}
}

for (const line of csvlines.slice(1)) {
    const [from, start, to, end] = line.split(",");
    if (from != to && typeof start !== 'undefined' && start.startsWith("2021-04-21")) {
        file.journeys.push([from, to]);
    }
}

for (const station of stations) {
    const coords = station.Locations[0].location.geometry.coordinates;
    if (file.stations[station.properties.stationsNummer]) {
        console.log("ALARM", station.properties.stationsNummer, station.description);
    }
    file.stations[station.properties.stationsNummer] = coords;
}

Deno.writeTextFile("journeys.json", JSON.stringify(file));
