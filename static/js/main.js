function copyToClipboard(chunkText, checkboxId) {
    // Unescape Unicode escape sequences and other escape characters
    const unescapedText = chunkText.replace(/\\u([\dA-F]{4})/gi, (match, grp) => {
        return String.fromCharCode(parseInt(grp, 16));
    }).replace(/\\n/g, "\n")
      .replace(/\\'/g, "'")
      .replace(/\\"/g, '"')
      .replace(/\\\\/g, '\\');

    navigator.clipboard.writeText(unescapedText).then(function() {
        console.log('Copying to clipboard was successful!');

        // Check the corresponding checkbox
        const checkbox = document.getElementById(checkboxId);
        if (checkbox) {
            checkbox.checked = true;
        }

        // Show confirmation message
        const confirmation = document.getElementById('copyConfirmation');
        confirmation.style.display = 'block';
        confirmation.style.opacity = '1';
        
        // Hide the confirmation message after a delay with fade out
        setTimeout(() => {
            confirmation.style.opacity = '0';
            setTimeout(() => {
                confirmation.style.display = 'none';
            }, 500);
        }, 2000);
    }, function(err) {
        console.error('Could not copy text: ', err);
    });
}
