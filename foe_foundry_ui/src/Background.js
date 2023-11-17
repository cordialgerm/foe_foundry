import React from 'react';

function BackgroundImage({ img, children }) {
    const imageUrl = `url(img/${img})`
    return (
        <div style={{ backgroundImage: imageUrl, backgroundRepeat: "no-repeat", backgroundPosition: "center center", backgroundSize: "cover" }}>
            {children}
        </div>
    )
}

export function RandomBackgroundImage({ counter, children }) {
    const imageNames = getImageNames();
    console.log(imageNames);
    console.log(imageNames.length)
    console.log(counter)
    const imageName = imageNames[counter % imageNames.length]
    console.log(imageName)
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
