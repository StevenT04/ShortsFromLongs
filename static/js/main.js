function copyToClipboard(chunkText) {

    const decodedText = decodeURIComponent(JSON.parse('"' + chunkText.replace(/\"/g, '\\"') + '"'));
    navigator.clipboard.writeText(decodedText).then(function() {

        // Get the confirmation alert element
        const confirmation = document.getElementById('copyConfirmation');
        
        // Make sure the element is visible and fully opaque before starting the fade out
        confirmation.style.display = 'block';
        confirmation.style.opacity = '1';
        
        // Hide the confirmation message after 1 second with a fade out
        setTimeout(() => {
            // Start the fade out by reducing the opacity
            confirmation.style.opacity = '0';

            // After the fade out duration, set display to none
            setTimeout(() => {
                confirmation.style.display = 'none';
            }, 500); // Set this to match your CSS transition duration
        }, 2000); // Keep the message visible for 1 second before starting the fade out
    }, function(err) {
        console.error('Could not copy text: ', err);
    });
}

