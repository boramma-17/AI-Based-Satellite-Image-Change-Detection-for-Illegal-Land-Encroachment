document.addEventListener("DOMContentLoaded", function () {

    const beforeInput = document.getElementById("beforeImage");
    const afterInput = document.getElementById("afterImage");

    const beforeDrop = document.getElementById("beforeDrop");
    const afterDrop = document.getElementById("afterDrop");

    const beforePreview = document.getElementById("beforePreview");
    const afterPreview = document.getElementById("afterPreview");

    const beforePreviewImage =
        document.getElementById("beforePreviewImage");

    const afterPreviewImage =
        document.getElementById("afterPreviewImage");

    const comparisonContainer =
        document.getElementById("comparisonContainer");

    const comparisonBefore =
        document.getElementById("comparisonBefore");

    const comparisonAfter =
        document.getElementById("comparisonAfter");

    const beforeLayer =
        document.getElementById("beforeLayer");

    const comparisonDivider =
        document.getElementById("comparisonDivider");

    const slider =
        document.getElementById("comparisonSlider");


    /* =========================================
       FILE PREVIEW
    ========================================= */

    beforeInput.addEventListener("change", function () {

        if (this.files.length > 0) {

            showPreview(
                this.files[0],
                "before"
            );

        }

    });


    afterInput.addEventListener("change", function () {

        if (this.files.length > 0) {

            showPreview(
                this.files[0],
                "after"
            );

        }

    });


    function showPreview(file, type) {

        if (!file.type.startsWith("image/")) {

            alert("Please select a valid image.");

            return;
        }


        const reader = new FileReader();


        reader.onload = function (event) {

            if (type === "before") {

                beforePreviewImage.src =
                    event.target.result;

                comparisonBefore.src =
                    event.target.result;

                beforeDrop.style.display =
                    "none";

                beforePreview.classList.add(
                    "show"
                );

            }


            if (type === "after") {

                afterPreviewImage.src =
                    event.target.result;

                comparisonAfter.src =
                    event.target.result;

                afterDrop.style.display =
                    "none";

                afterPreview.classList.add(
                    "show"
                );

            }


            updateComparisonState();

        };


        reader.readAsDataURL(file);
    }



    /* =========================================
       REMOVE IMAGE
    ========================================= */

    window.removeImage = function (type) {

        if (type === "before") {

            beforeInput.value = "";

            beforePreview.classList.remove(
                "show"
            );

            beforeDrop.style.display =
                "flex";

            comparisonBefore.src = "";

        }


        if (type === "after") {

            afterInput.value = "";

            afterPreview.classList.remove(
                "show"
            );

            afterDrop.style.display =
                "flex";

            comparisonAfter.src = "";

        }


        updateComparisonState();

    };



    /* =========================================
       DRAG & DROP
    ========================================= */

    setupDropZone(
        beforeDrop,
        beforeInput,
        "before"
    );

    setupDropZone(
        afterDrop,
        afterInput,
        "after"
    );


    function setupDropZone(
        dropZone,
        input,
        type
    ) {

        [
            "dragenter",
            "dragover"
        ].forEach(eventName => {

            dropZone.addEventListener(
                eventName,
                function (event) {

                    event.preventDefault();

                    dropZone.classList.add(
                        "dragging"
                    );

                }
            );

        });


        [
            "dragleave",
            "drop"
        ].forEach(eventName => {

            dropZone.addEventListener(
                eventName,
                function (event) {

                    event.preventDefault();

                    dropZone.classList.remove(
                        "dragging"
                    );

                }
            );

        });


        dropZone.addEventListener(
            "drop",
            function (event) {

                const files =
                    event.dataTransfer.files;

                if (!files.length) {
                    return;
                }

                input.files = files;

                showPreview(
                    files[0],
                    type
                );

            }
        );

    }



    /* =========================================
       COMPARISON SLIDER
    ========================================= */

    slider.addEventListener(
        "input",
        updateSlider
    );


    function updateSlider() {

        const value =
            slider.value;

        beforeLayer.style.width =
            value + "%";

        comparisonDivider.style.left =
            value + "%";

    }


    updateSlider();



    /* =========================================
       COMPARISON STATE
    ========================================= */

    function updateComparisonState() {

        const beforeExists =
            comparisonBefore.src !== "" &&
            comparisonBefore.src !==
            window.location.href;

        const afterExists =
            comparisonAfter.src !== "" &&
            comparisonAfter.src !==
            window.location.href;


        if (beforeExists && afterExists) {

            comparisonContainer.classList.add(
                "has-images"
            );

        } else {

            comparisonContainer.classList.remove(
                "has-images"
            );

        }

    }



    /* =========================================
       CURRENT LOCATION
    ========================================= */

    window.useCurrentLocation =
        function () {

            if (!navigator.geolocation) {

                alert(
                    "Geolocation is not supported by your browser."
                );

                return;
            }


            navigator.geolocation.getCurrentPosition(

                function (position) {

                    document.getElementById(
                        "latitude"
                    ).value =
                        position.coords.latitude.toFixed(6);


                    document.getElementById(
                        "longitude"
                    ).value =
                        position.coords.longitude.toFixed(6);


                    updateMap(
                        position.coords.latitude,
                        position.coords.longitude
                    );

                },


                function () {

                    alert(
                        "Unable to get your current location."
                    );

                }

            );

        };



    /* =========================================
       LEAFLET MAP
    ========================================= */

    let map;

    let marker;


    map = L.map(
        "detectionMap"
    ).setView(
        [20.5937, 78.9629],
        5
    );


    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            maxZoom: 19,

            attribution:
                "&copy; OpenStreetMap contributors"
        }
    ).addTo(map);



    function updateMap(
        latitude,
        longitude
    ) {

        const lat =
            parseFloat(latitude);

        const lng =
            parseFloat(longitude);


        if (
            Number.isNaN(lat) ||
            Number.isNaN(lng)
        ) {

            return;
        }


        map.setView(
            [lat, lng],
            15
        );


        if (marker) {

            marker.setLatLng(
                [lat, lng]
            );

        } else {

            marker = L.marker(
                [lat, lng]
            ).addTo(map);

        }


        marker.bindPopup(
            `
            <strong>GeoGuard AI Detection</strong>
            <br>
            Latitude: ${lat.toFixed(6)}
            <br>
            Longitude: ${lng.toFixed(6)}
            `
        ).openPopup();

    }



    /* =========================================
       LOCATION FIELD WATCH
    ========================================= */

    document.getElementById(
        "latitude"
    ).addEventListener(
        "change",
        updateLocationFromFields
    );


    document.getElementById(
        "longitude"
    ).addEventListener(
        "change",
        updateLocationFromFields
    );


    function updateLocationFromFields() {

        const latitude =
            document.getElementById(
                "latitude"
            ).value;

        const longitude =
            document.getElementById(
                "longitude"
            ).value;


        if (
            latitude &&
            longitude
        ) {

            updateMap(
                latitude,
                longitude
            );

        }

    }



    /* =========================================
       CENTER MAP
    ========================================= */

    window.centerMap =
        function () {

            const latitude =
                document.getElementById(
                    "latitude"
                ).value;

            const longitude =
                document.getElementById(
                    "longitude"
                ).value;


            if (
                latitude &&
                longitude
            ) {

                updateMap(
                    latitude,
                    longitude
                );

            } else {

                map.setView(
                    [20.5937, 78.9629],
                    5
                );

            }

        };



    /* =========================================
       RESET
    ========================================= */

    window.resetComparison =
        function () {

            document.getElementById(
                "comparisonForm"
            ).reset();


            removeImage("before");

            removeImage("after");


            document.getElementById(
                "changePercent"
            ).textContent = "—";


            document.getElementById(
                "encroachmentStatus"
            ).textContent = "Pending";


            document.getElementById(
                "confidence"
            ).textContent = "—";


            document.getElementById(
                "detectionId"
            ).textContent = "New";


            document.getElementById(
                "warningPanel"
            ).classList.remove(
                "show"
            );


            slider.value = 50;

            updateSlider();


            map.setView(
                [20.5937, 78.9629],
                5
            );


            if (marker) {

                map.removeLayer(marker);

                marker = null;

            }

        };



    /* =========================================
       DEMO RESULT FUNCTION
       ========================================= */

    window.showDetectionResult =
        function (
            changePercent,
            encroachment,
            confidence,
            detectionId
        ) {

            document.getElementById(
                "changePercent"
            ).textContent =
                Number(changePercent)
                    .toFixed(2) + "%";


            document.getElementById(
                "confidence"
            ).textContent =
                Number(confidence)
                    .toFixed(1) + "%";


            const status =
                document.getElementById(
                    "encroachmentStatus"
                );


            if (encroachment) {

                status.textContent =
                    "Detected";

                status.style.color =
                    "#ef4444";


                document.getElementById(
                    "warningPanel"
                ).classList.add(
                    "show"
                );

            } else {

                status.textContent =
                    "No Significant Change";

                status.style.color =
                    "#22c55e";

            }


            document.getElementById(
                "detectionId"
            ).textContent =
                "#" + detectionId;

        };



    /* =========================================
       FORM LOADING
    ========================================= */

    document.getElementById(
        "comparisonForm"
    ).addEventListener(
        "submit",
        function () {

            const button =
                document.getElementById(
                    "detectButton"
                );


            button.disabled = true;

            button.querySelector(
                "span:first-child"
            ).textContent =
                "Analyzing Images...";


            button.querySelector(
                ".arrow"
            ).textContent =
                "⟳";

        }
    );

});