function copyToClipboard(chunkText) {
    navigator.clipboard.writeText(chunkText).then(function() {
        console.log('Copying to clipboard was successful!');

        // Show copy confirmation
        const confirmation = document.getElementById('copyConfirmation');
        confirmation.style.display = 'block';
        setTimeout(() => {
            confirmation.style.display = 'none';
        }, 1000); // Display the message for 1 second
    }, function(err) {
        console.error('Could not copy text:', err);
    });
}
