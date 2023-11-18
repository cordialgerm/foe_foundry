import React from 'react';
import './BackgroundImage.css';

function BackgroundImage({ img, children }) {
    const imageUrl = `url(img/${img})`
    const maskUrl = "url(mask/watercolor-mask.png)"
    return (
        <div style={{
            position: "relative",
            display: "flex",
            justifyContent: "center",
            height: "calc(100vh - 100px)",
        }}>
            <div className="backgroundImage" style={{
                backgroundImage: imageUrl,
                backgroundRepeat: "no-repeat",
                backgroundPosition: "center center",
                backgroundSize: "contain",
                width: "90%",
                height: "90%",
                position: "absolute",
                margin: "10px"
            }} />
            <div style={{
                display: "flex",
                alignItems: "flex-start",
                justifyContent: "flex-start",
                width: "100%",
                position: "relative",
            }}>
                {children}
            </div>
        </div>
    )
}

export function RandomBackgroundImage({ counter, children }) {
    const imageNames = getImageNames();
    const imageName = imageNames[counter % imageNames.length]
    return (
        <BackgroundImage img={imageName} children={children} />
    )
}

// Function to get image names dynamically
function getImageNames() {
    const context = require.context('../public/img', false, /\.(png|jpg|jpeg|gif|svg)$/);
    const imageNames = context.keys().map((key) => key.split('/').pop());
    return imageNames;
}
