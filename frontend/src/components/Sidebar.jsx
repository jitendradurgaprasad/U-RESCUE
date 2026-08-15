function Sidebar() {

    return (

        <div
            className="glass"
            style={{

                position: "absolute",

                left: 25,

                top: 110,

                bottom: 25,

                width: 320,

                zIndex: 999,

                padding: 25

            }}
        >

            <h2>

                Prediction

            </h2>

            <br />

            <p>

                Click anywhere on the map.

            </p>

            <br />

            <hr />

            <br />

            <h3>

                Latitude

            </h3>

            <p>--</p>

            <br />

            <h3>

                Longitude

            </h3>

            <p>--</p>

            <br />

            <h3>

                Flood Risk

            </h3>

            <p
                style={{
                    color: "#22c55e"
                }}
            >
                Waiting...
            </p>

        </div>

    )

}

export default Sidebar;