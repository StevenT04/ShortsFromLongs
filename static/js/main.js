function copyToClipboard(chunkText) {
    // Unescape Unicode escape sequences
    const unescapedText = chunkText.replace(/\\u([\dA-F]{4})/gi, (match, grp) => {
        return String.fromCharCode(parseInt(grp, 16));
    }).replace(/\\n/g, "\n") // Unescape new lines
      .replace(/\\'/g, "'") // Unescape single quotes
      .replace(/\\"/g, '"') // Unescape double quotes
      .replace(/\\\\/g, '\\'); // Unescape backslashes

    navigator.clipboard.writeText(unescapedText).then(function() {
        console.log('Copying to clipboard was successful!');

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
        }, 2000); // Keep the message visible for 2 seconds before starting the fade out
    }, function(err) {
        console.error('Could not copy text: ', err);
    });
}
