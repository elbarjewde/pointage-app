
navigator.geolocation.getCurrentPosition(
    (position) => {
        const coords = position.coords;
        const latitude = coords.latitude;
        const longitude = coords.longitude;
        const streamlitMsg = {
            "latitude": latitude.toString(),
            "longitude": longitude.toString()
        };
        window.parent.postMessage({isStreamlitMessage: true, type: "streamlit:setComponentValue", value: streamlitMsg}, "*");
    },
    (error) => {
        console.error("خطأ في تحديد الموقع:", error);
    }
);
