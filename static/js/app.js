document.addEventListener('DOMContentLoaded', function() {

    // Check if we're on the homepage by checking the current path
    if (window.location.pathname === '/') {

        // Handle form submission for uploading assignments
        const uploadForm = document.getElementById("upload-form");
        const uploadedImageContainer = document.getElementById("uploaded-image-container");
        const questionSection = document.getElementById("question-section");  // Add reference to the question section
        let filePath = "";  // This will hold the path of the uploaded image

        // Check if the upload form exists
        if (!uploadForm) {
            console.error("Upload form element not found!");
            return;
        }

        uploadForm.addEventListener("submit", function (event) {
            event.preventDefault(); // Prevent default form submission

            const formData = new FormData(uploadForm);
            fetch("/", {
                method: "POST",
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("Assignment uploaded successfully! File path: " + data.file_path);
                    filePath = data.file_path; // Store the file path returned from the server
                    // Show the question form after upload
                    if (uploadedImageContainer) {
                        uploadedImageContainer.style.display = "block";  // Show the container
                    }
                    if (questionSection) {
                        questionSection.style.display = "block";  // Show the question textarea
                    } else {
                        console.error("Question section not found!");
                    }
                } else {
                    alert("Error uploading file: " + data.error);
                }
            })
            .catch(error => alert("Error: " + error));
        });

        // Handle form submission for asking questions about the image
        const questionForm = document.getElementById("question-form");
        const responseContainer = document.getElementById("response-container");

        // Check if question form exists
        if (!questionForm || !responseContainer) {
            console.error("Question form or response container not found!");
            return;
        }

        questionForm.addEventListener("submit", function (event) {
            event.preventDefault(); // Prevent form submission

            const question = document.getElementById("question").value;
            if (!question.trim()) {
                alert("Please enter a question.");
                return;
            }

            // Send the question and file path to the backend to get the response
            fetch("/ask_image_question", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    question: question,
                    file_path: filePath  // Send the file path to the backend
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.response) {
                    responseContainer.innerHTML = "<strong>Answer:</strong> " + data.response;
                } else {
                    responseContainer.innerHTML = "<strong>Error:</strong> " + data.error;
                }
            })
            .catch(error => {
                responseContainer.innerHTML = "<strong>Error:</strong> " + error;
            });
        });
    }

});
