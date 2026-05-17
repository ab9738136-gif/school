function validateForm() {
    var name = document.getElementById("name").value;
    if (name.trim() == "") {
        alert("कृपया सही नाम दर्ज करें।");
        return false;
    }
    alert("जानकारी बैकएंड सर्वर को भेजी जा रही है...");
    return true;
}
