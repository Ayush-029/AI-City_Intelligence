// ==========================================
// AI CITY INTELLIGENCE
// Traffic Prediction Frontend
// ==========================================

const API_URL = "http://127.0.0.1:8000";


// ==========================================
// PREDICT TRAFFIC
// ==========================================

async function predictTraffic() {

    const button = document.querySelector(".predict-btn");
    const buttonText = document.getElementById("btnText");

    // -------------------------------
    // Get values from form
    // -------------------------------

    const temp = Number(document.getElementById("temp").value);
    const rain = Number(document.getElementById("rain").value);
    const snow = Number(document.getElementById("snow").value);
    const clouds = Number(document.getElementById("clouds").value);
    const hour = Number(document.getElementById("hour").value);
    const day = Number(document.getElementById("day").value);
    const month = Number(document.getElementById("month").value);
    const weekend = Number(document.getElementById("weekend").value);


    // ==========================================
    // VALIDATION
    // ==========================================

    if (
        Number.isNaN(temp) ||
        Number.isNaN(rain) ||
        Number.isNaN(snow) ||
        Number.isNaN(clouds) ||
        Number.isNaN(hour) ||
        Number.isNaN(day) ||
        Number.isNaN(month) ||
        Number.isNaN(weekend)
    ) {
        alert("Please fill all fields.");
        return;
    }


    if (hour < 0 || hour > 23) {
        alert("Hour must be between 0 and 23.");
        return;
    }

    if (clouds < 0 || clouds > 100) {
        alert("Cloud cover must be between 0 and 100.");
        return;
    }


    // ==========================================
    // REQUEST DATA
    // ==========================================

    const data = {

        temp: temp,

        rain_1h: rain,

        snow_1h: snow,

        clouds_all: clouds,

        hour: hour,

        day_of_week: day,

        month: month,

        is_weekend: weekend

    };


    // ==========================================
    // LOADING STATE
    // ==========================================

    button.disabled = true;

    buttonText.textContent = "Analyzing Traffic...";


    try {

        // ======================================
        // CALL FASTAPI
        // ======================================

        const response = await fetch(
            `${API_URL}/predict`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(data)
            }
        );


        const result = await response.json();


        // ======================================
        // API ERROR
        // ======================================

        if (!response.ok) {

            console.error("API Error:", result);

            alert(
                "Prediction failed.\n\n" +
                JSON.stringify(result, null, 2)
            );

            return;
        }


        // ======================================
        // UPDATE DASHBOARD
        // ======================================

        updateDashboard(result);


    } catch (error) {

        console.error("Connection Error:", error);

        alert(
            "Cannot connect to FastAPI.\n\n" +
            "Make sure the API server is running."
        );

    } finally {

        button.disabled = false;

        buttonText.textContent = "Predict Traffic";

    }

}



// ==========================================
// UPDATE DASHBOARD
// ==========================================

function updateDashboard(result) {

    const trafficElement =
        document.getElementById("traffic");

    const congestionElement =
        document.getElementById("congestion");

    const riskElement =
        document.getElementById("risk");

    const periodElement =
        document.getElementById("period");

    const recommendationElement =
        document.getElementById("recommendation");

    const riskBar =
        document.getElementById("riskBar");


    // ======================================
    // TRAFFIC
    // ======================================

    trafficElement.textContent =
        Number(result.predicted_traffic_volume)
            .toLocaleString();


    // ======================================
    // CONGESTION
    // ======================================

    congestionElement.textContent =
        result.congestion_level;


    // ======================================
    // RISK
    // ======================================

    riskElement.textContent =
        `${result.risk_score}%`;


    // ======================================
    // TIME PERIOD
    // ======================================

    periodElement.textContent =
        result.time_period;


    // ======================================
    // RISK BAR
    // ======================================

    riskBar.style.width =
        `${result.risk_score}%`;


    // ======================================
    // AI RECOMMENDATION
    // ======================================

    recommendationElement.textContent =
        result.recommendation;


    // ======================================
    // CONGESTION COLOR
    // ======================================

    updateCongestionStyle(
        result.congestion_level
    );

}



// ==========================================
// CONGESTION STYLE
// ==========================================

function updateCongestionStyle(level) {

    const element =
        document.getElementById("congestion");


    if (level === "LOW") {

        element.style.color = "#25d695";

    }

    else if (level === "MEDIUM") {

        element.style.color = "#ffb547";

    }

    else if (level === "HIGH") {

        element.style.color = "#ff5c6c";

    }

}



// ==========================================
// API HEALTH CHECK
// ==========================================

async function checkAPIStatus() {

    try {

        const response = await fetch(
            `${API_URL}/health`
        );


        if (response.ok) {

            console.log(
                "✅ FastAPI connection successful"
            );

        }

    } catch (error) {

        console.warn(
            "⚠️ FastAPI is not running"
        );

    }

}


// ==========================================
// PAGE LOAD
// ==========================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        checkAPIStatus();

    }
);

function setButtonLoading(buttonId, isLoading, loadingText, defaultText) {
    const button = document.getElementById(buttonId);
    button.disabled = isLoading;
    button.textContent = isLoading ? loadingText : defaultText;
}

async function updateAPIStatus() {
    const statusText = document.getElementById("apiStatusText");
    const statusDetail = document.getElementById("apiStatusDetail");
    const statusDot = document.getElementById("apiStatusDot");

    try {
        const response = await fetch(`${API_URL}/health`);
        if (!response.ok) throw new Error("API is unavailable");
        statusText.textContent = "API Online";
        statusDetail.textContent = "Four intelligence modules ready";
        statusDot.style.background = "#25d695";
    } catch (error) {
        statusText.textContent = "API Offline";
        statusDetail.textContent = "Start FastAPI to predict";
        statusDot.style.background = "#ff5c6c";
    }
}

document.addEventListener("DOMContentLoaded", updateAPIStatus);

async function predictAQI() {
    const city = document.getElementById("aqiCity").value;
    const datetime = document.getElementById("aqiDatetime").value;

    const fields = {
        "PM2.5": document.getElementById("pm25").value,
        "PM10": document.getElementById("pm10").value,
        "NO": document.getElementById("no").value,
        "NO2": document.getElementById("no2").value,
        "NOx": document.getElementById("nox").value,
        "NH3": document.getElementById("nh3").value,
        "CO": document.getElementById("co").value,
        "SO2": document.getElementById("so2").value,
        "O3": document.getElementById("o3").value
    };

    if (!city || !datetime || Object.values(fields).some(value => value === "")) {
        alert("Please fill all air-quality fields.");
        return;
    }

    const data = {
        city: city,
        datetime: datetime,
        "PM2.5": Number(fields["PM2.5"]),
        "PM10": Number(fields["PM10"]),
        "NO": Number(fields["NO"]),
        "NO2": Number(fields["NO2"]),
        "NOx": Number(fields["NOx"]),
        "NH3": Number(fields["NH3"]),
        "CO": Number(fields["CO"]),
        "SO2": Number(fields["SO2"]),
        "O3": Number(fields["O3"])
    };

    const resultElement = document.getElementById("aqiResult");
    setButtonLoading("aqiPredictButton", true, "Analyzing Air Quality...", "Predict Air Quality");
    resultElement.className = "prediction-result";
    resultElement.textContent = "Analyzing air quality...";

    try {
        const response = await fetch(`${API_URL}/air-quality/predict`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "AQI prediction failed.");
        }

        resultElement.className = "prediction-result";

if (result.aqi_category === "Good") {
    resultElement.classList.add("aqi-good");
} else if (result.aqi_category === "Satisfactory" || result.aqi_category === "Moderate") {
    resultElement.classList.add("aqi-warning");
} else {
    resultElement.classList.add("aqi-danger");
}
        resultElement.innerHTML = `
            <strong>Predicted AQI: ${result.predicted_aqi}</strong><br>
            Category: ${result.aqi_category}<br>
            Risk score: ${result.risk_score}%
        `;
    } catch (error) {
        console.error(error);
        resultElement.textContent = `Error: ${error.message}`;
    } finally {
        setButtonLoading("aqiPredictButton", false, "", "Predict Air Quality");
    }
}

async function predictWaste() {
    const city = document.getElementById("wasteCity").value;
    const wasteType = document.getElementById("wasteType").value;
    const disposalMethod = document.getElementById("disposalMethod").value;

    const numericValues = {
        recycling_rate: document.getElementById("recyclingRate").value,
        population_density: document.getElementById("populationDensity").value,
        municipal_efficiency_score: document.getElementById("municipalEfficiency").value,
        awareness_campaigns_count: document.getElementById("campaignCount").value,
        landfill_capacity_tons: document.getElementById("landfillCapacity").value,
        waste_reduction_initiatives: document.getElementById("wasteInitiatives").value,
        industrial_symbiosis_index: document.getElementById("industrialIndex").value,
        community_participation_score: document.getElementById("communityScore").value,
        green_technology_adoption: document.getElementById("greenTechnology").value,
        recycling_infrastructure_rating: document.getElementById("infrastructureRating").value
    };

    if (
        !city ||
        !wasteType ||
        !disposalMethod ||
        Object.values(numericValues).some(value => value === "")
    ) {
        alert("Please fill all waste-management fields.");
        return;
    }

    const data = {
        city: city,
        waste_type: wasteType,
        disposal_method: disposalMethod,
        recycling_rate: Number(numericValues.recycling_rate),
        population_density: Number(numericValues.population_density),
        municipal_efficiency_score: Number(
            numericValues.municipal_efficiency_score
        ),
        awareness_campaigns_count: Number(
            numericValues.awareness_campaigns_count
        ),
        landfill_capacity_tons: Number(
            numericValues.landfill_capacity_tons
        ),
        waste_reduction_initiatives: Number(
            numericValues.waste_reduction_initiatives
        ),
        industrial_symbiosis_index: Number(
            numericValues.industrial_symbiosis_index
        ),
        community_participation_score: Number(
            numericValues.community_participation_score
        ),
        green_technology_adoption: Number(
            numericValues.green_technology_adoption
        ),
        recycling_infrastructure_rating: Number(
            numericValues.recycling_infrastructure_rating
        )
    };

    const resultElement = document.getElementById("wasteResult");

    setButtonLoading("wastePredictButton", true, "Analyzing Waste...", "Predict Waste Management");
    resultElement.className = "prediction-result";
    resultElement.textContent = "Analyzing waste-management data...";

    try {
        const response = await fetch(`${API_URL}/waste/predict`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Waste prediction failed.");
        }

        if (result.collection_priority === "LOW") {
            resultElement.classList.add("aqi-good");
        } else if (result.collection_priority === "MEDIUM") {
            resultElement.classList.add("aqi-warning");
        } else {
            resultElement.classList.add("aqi-danger");
        }

        resultElement.innerHTML = `
            <strong>
                Predicted Waste:
                ${result.predicted_waste_tons_per_day.toLocaleString()} tons/day
            </strong><br>
            Collection Priority: ${result.collection_priority}<br>
            Recommendation: ${result.recommendation}<br>
            <small>${result.model_note}</small>
        `;
    } catch (error) {
        console.error(error);
        resultElement.textContent = `Error: ${error.message}`;
    } finally {
        setButtonLoading("wastePredictButton", false, "", "Predict Waste Management");
    }
}

async function predictTransport() {
    const city = document.getElementById("transportCity").value;

    const numericValues = {
        year_start: document.getElementById("transportYear").value,
        daily_trips: document.getElementById("dailyTrips").value,
        daily_trip_length_km: document.getElementById("tripLength").value,
        total_buses: document.getElementById("totalBuses").value,
        bus_terminals: document.getElementById("busTerminals").value,
        bus_stands: document.getElementById("busStands").value,
        bus_stops: document.getElementById("busStops").value
    };

    if (!city || Object.values(numericValues).some(value => value === "")) {
        alert("Please fill all transport fields.");
        return;
    }

    const data = {
        city: city,
        year_start: Number(numericValues.year_start),
        daily_trips: Number(numericValues.daily_trips),
        daily_trip_length_km: Number(
            numericValues.daily_trip_length_km
        ),
        total_buses: Number(numericValues.total_buses),
        bus_terminals: Number(numericValues.bus_terminals),
        bus_stands: Number(numericValues.bus_stands),
        bus_stops: Number(numericValues.bus_stops)
    };

    const resultElement = document.getElementById("transportResult");

    setButtonLoading("transportPredictButton", true, "Analyzing Transport...", "Predict Transport Demand");
    resultElement.className = "prediction-result";
    resultElement.textContent = "Analyzing transport demand...";

    try {
        const response = await fetch(`${API_URL}/transport/predict`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Transport prediction failed.");
        }

        if (result.crowd_level === "LOW") {
            resultElement.classList.add("aqi-good");
        } else if (result.crowd_level === "MEDIUM") {
            resultElement.classList.add("aqi-warning");
        } else {
            resultElement.classList.add("aqi-danger");
        }

        resultElement.innerHTML = `
            <strong>
                Predicted Daily Passengers:
                ${result.predicted_daily_passengers.toLocaleString()}
            </strong><br>
            Crowd Level: ${result.crowd_level}<br>
            Recommendation: ${result.recommendation}
        `;
    } catch (error) {
        console.error(error);
        resultElement.textContent = `Error: ${error.message}`;
    } finally {
        setButtonLoading("transportPredictButton", false, "", "Predict Transport Demand");
    }
}
