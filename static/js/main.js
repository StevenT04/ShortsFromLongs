document.addEventListener("DOMContentLoaded", function(){
    // Hide the toast initially
    var toastElList = [].slice.call(document.querySelectorAll('.toast'));
    var toastList = toastElList.map(function(toastEl) {
        return new bootstrap.Toast(toastEl); // Initialize Bootstrap toasts
    });

    // Example: to hide a toast, you'd now use toastList[0].hide() assuming you have at least one toast.
});

function copyToClipboard(chunkText) {
    navigator.clipboard.writeText(chunkText).then(function() {
        console.log('Copying to clipboard was successful!');
        // Show Bootstrap toast for copy confirmation without jQuery
        var toastElement = document.getElementById('copyConfirmation');
        var toast = new bootstrap.Toast(toastElement);
        toast.show();
    }, function(err) {
        console.error('Could not copy text:', err);
    });
}
