// public/js/adblock_detector.js

// This global variable is used as a simple flag.
// If an adblocker blocks this entire script from loading,
// then 'window.mySiteAdScriptLoaded' will remain undefined.
window.mySiteAdScriptLoaded = true;

// Create a dummy <div> element that is designed to mimic common ad units.
// Adblockers often target specific class names, IDs, and dimensions.
var adDetectorDiv = document.createElement('div');

// Assign common ad-related IDs and classes.
// Adblocker filter lists often look for these.
adDetectorDiv.id = 'ad-detector-div';
adDetectorDiv.className = 'ad-banner adsbygoogle ad-placement';

// Apply styles to place the div off-screen and make it very small.
// This ensures it doesn't interfere with the normal page layout
// but is still subject to adblocker's cosmetic filters (e.g., hiding 1x1px "ads").
adDetectorDiv.style.position = 'absolute';
adDetectorDiv.style.top = '-9999px'; // Move it far off the top
adDetectorDiv.style.left = '-9999px'; // Move it far off the left
adDetectorDiv.style.height = '1px';  // Give it common ad dimensions
adDetectorDiv.style.width = '1px';   // Give it common ad dimensions
adDetectorDiv.style.overflow = 'hidden'; // Hide any potential content (though it's empty)
adDetectorDiv.style.visibility = 'hidden'; // Explicitly hide it

// Append the created div to the <body> of the document.
// This makes it part of the page's DOM, allowing adblockers to interact with it.
// We check for document.body to ensure the body element is available.
if (document.body) {
    document.body.appendChild(adDetectorDiv);
} else {
    // If body isn't ready yet (less common for scripts at end of body),
    // wait for DOMContentLoaded. However, placing the script at the end of body
    // usually ensures body is available.
    document.addEventListener('DOMContentLoaded', function() {
        document.body.appendChild(adDetectorDiv);
    });
}
