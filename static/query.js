async function submitQuery() {
    const query = document.getElementById("query").value;
    const response = await fetch('/generate_response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({query})
    });

    if (response.ok) {
        const result = await response.json();
        console.log("Backend result:", result);
        document.getElementById('response').innerText = result.response || 'No response available';

    } else {
        document.getElementById('response').innerText = "Error : unable to retreive a response";
    }
}

