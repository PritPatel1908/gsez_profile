document.addEventListener('DOMContentLoaded', function () {
    // Run setup for dynamic rows
    setupDynamicRows();

    // Setup camera capture for profile photo
    setupCameraCapture();

    // Initialize Bootstrap modals
    initializeModals();

    // Setup delete confirmation for all delete buttons/forms
    setupDeleteConfirmation();

    // Add event listener for dynamic content changes that might add new modals
    document.addEventListener('DOMNodeInserted', function (event) {
        // Check if the inserted node contains any modals
        if (event.target.querySelector && event.target.querySelector('.modal')) {
            // Re-initialize modals if new ones are added
            setTimeout(function () {
                initializeModals();
            }, 100); // Small delay to ensure DOM is fully updated
        }

        // Check if the inserted node contains delete buttons or forms
        if (event.target.querySelector &&
            (event.target.querySelector('button[type="submit"].btn-danger') ||
                event.target.querySelector('form[action*="delete"]'))) {
            // Re-setup delete confirmation
            setTimeout(function () {
                setupDeleteConfirmation();
            }, 100); // Small delay to ensure DOM is fully updated
        }
    });

    // Company name suggestions for previous employer
    const previousEmployerNameInput = document.getElementById('id_previous_employer_name');
    if (previousEmployerNameInput) {
        previousEmployerNameInput.addEventListener('input', function () {
            const query = this.value;
            if (query.length >= 2) {
                fetch(`/api/company-suggestions/?query=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        const datalist = document.getElementById('company-suggestions');
                        if (!datalist) {
                            const newDatalist = document.createElement('datalist');
                            newDatalist.id = 'company-suggestions';
                            document.body.appendChild(newDatalist);
                            previousEmployerNameInput.setAttribute('list', 'company-suggestions');
                        } else {
                            datalist.innerHTML = '';
                        }

                        data.forEach(company => {
                            const option = document.createElement('option');
                            option.value = company;
                            document.getElementById('company-suggestions').appendChild(option);
                        });
                    })
                    .catch(error => console.error('Error fetching company suggestions:', error));
            }
        });
    }

    // QR Code scanner for security personnel
    const scannerPreview = document.getElementById('scanner-preview');
    const scanButton = document.getElementById('scan-button');

    if (scannerPreview && scanButton) {
        scanButton.addEventListener('click', function () {
            // In a real application, you would use a library like instascan or html5-qrcode
            // For this demo, we'll simulate scanning by showing a form to enter user ID
            const userIdForm = document.createElement('div');
            userIdForm.innerHTML = `
                <form id="manual-scan-form" class="mt-3">
                    <div class="mb-3">
                        <label for="user_id" class="form-label">Enter User ID:</label>
                        <input type="text" class="form-control" id="user_id" name="user_id" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Submit</button>
                </form>
            `;

            scannerPreview.innerHTML = '';
            scannerPreview.appendChild(userIdForm);

            document.getElementById('manual-scan-form').addEventListener('submit', function (e) {
                e.preventDefault();
                const userId = document.getElementById('user_id').value;
                document.getElementById('scan-form').elements.user_id.value = userId;
                document.getElementById('scan-form').submit();
            });
        });
    }

    // Dynamic form fields for profile editing
    const addEmergencyContactBtn = document.getElementById('add-emergency-contact');
    if (addEmergencyContactBtn) {
        addEmergencyContactBtn.addEventListener('click', function () {
            const emergencyContactsContainer = document.getElementById('emergency-contacts-container');
            const contactCount = emergencyContactsContainer.children.length;

            const newContact = document.createElement('div');
            newContact.className = 'row mb-3';
            newContact.innerHTML = `
                <div class="col-md-5">
                    <input type="text" name="emergency_contact_name_${contactCount}" class="form-control" placeholder="Name">
                </div>
                <div class="col-md-5">
                    <input type="text" name="emergency_contact_number_${contactCount}" class="form-control" placeholder="Phone Number">
                </div>
                <div class="col-md-2">
                    <button type="button" class="btn btn-danger remove-contact">Remove</button>
                </div>
            `;

            emergencyContactsContainer.appendChild(newContact);

            // Add event listener to the remove button
            newContact.querySelector('.remove-contact').addEventListener('click', function () {
                emergencyContactsContainer.removeChild(newContact);
            });
        });
    }

    // Similar functionality for family members, previous employers, and qualifications
    // would be implemented in a similar way
});

// Function to preview profile image before upload
function previewProfileImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();

        reader.onload = function (e) {
            const previewImg = document.getElementById('previewPhoto');
            if (previewImg) {
                previewImg.src = e.target.result;
                previewImg.style.display = 'block';
            }

            // Hide current photo display if it exists
            const currentPhoto = document.getElementById('currentPhoto');
            if (currentPhoto) {
                currentPhoto.style.display = 'none';
            }
        }

        reader.readAsDataURL(input.files[0]);
    }
}

// Camera capture for profile photo
function setupCameraCapture() {
    const openCameraBtn = document.getElementById('openCameraBtn');

    const cameraModal = document.getElementById('cameraModal');
    const cameraFeed = document.getElementById('cameraFeed');
    const photoCanvas = document.getElementById('photoCanvas');
    const captureBtn = document.getElementById('captureBtn');
    const retakeBtn = document.getElementById('retakeBtn');
    const savePhotoBtn = document.getElementById('savePhotoBtn');
    const profilePhotoInput = document.querySelector('input[type="file"][name="profile_photo"]');
    const previewPhoto = document.getElementById('previewPhoto');

    // Skip if not on a page with camera functionality
    if (!openCameraBtn) {
        return;
    }

    let stream = null;
    let capturedImage = null;

    // Initialize Bootstrap modal if Bootstrap is available
    let modal = null;
    if (typeof bootstrap !== 'undefined') {
        modal = new bootstrap.Modal(cameraModal);
    }

    // Handle file input change for preview
    if (profilePhotoInput) {
        profilePhotoInput.addEventListener('change', function () {
            previewProfileImage(this);
        });
    }

    // Open camera modal and start camera
    openCameraBtn.addEventListener('click', function (e) {
        e.preventDefault(); // Prevent form submission

        // Reset UI
        if (captureBtn) captureBtn.style.display = 'block';
        if (retakeBtn) retakeBtn.style.display = 'none';
        if (savePhotoBtn) savePhotoBtn.style.display = 'none';
        if (cameraFeed) cameraFeed.style.display = 'block';

        // Open modal if Bootstrap is available, otherwise just show the camera container
        if (modal) {
            modal.show();
        } else {
            cameraModal.style.display = 'block';
        }

        // Add a timeout for camera initialization
        let cameraTimeout = setTimeout(function () {
            alert("Camera access timed out. Please check your camera permissions and try again.");
            if (modal) {
                modal.hide();
            } else if (cameraModal) {
                cameraModal.style.display = 'none';
            }
        }, 10000); // 10 seconds timeout

        // Add camera toggle option
        let useFrontCamera = true;

        // Create toggle button if it doesn't exist
        if (!document.getElementById('switchCameraBtn')) {
            const toggleBtn = document.createElement('button');
            toggleBtn.id = 'switchCameraBtn';
            toggleBtn.className = 'btn btn-sm btn-info mb-2';
            toggleBtn.innerHTML = '<i class="fas fa-sync"></i> Switch Camera';
            toggleBtn.style.display = 'none'; // Hide initially

            // Insert before video element
            if (cameraFeed && cameraFeed.parentNode) {
                cameraFeed.parentNode.insertBefore(toggleBtn, cameraFeed);
            }

            // Add click handler
            toggleBtn.addEventListener('click', function () {
                useFrontCamera = !useFrontCamera;

                // Stop current stream
                if (stream) {
                    stream.getTracks().forEach(track => track.stop());
                }

                // Restart camera with new facing mode
                startCamera();
            });
        }

        const switchCameraBtn = document.getElementById('switchCameraBtn');

        // Function to start camera with fallbacks
        function startCamera() {
            // Start camera
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                // Initial camera constraints
                const constraints = {
                    video: {
                        width: { ideal: 640 },
                        height: { ideal: 480 },
                        facingMode: useFrontCamera ? "user" : "environment"
                    }
                };

                // Try to access camera with these constraints
                navigator.mediaDevices.getUserMedia(constraints)
                    .then(function (mediaStream) {
                        // Clear the timeout as camera started successfully
                        clearTimeout(cameraTimeout);

                        stream = mediaStream;
                        if (cameraFeed) {
                            cameraFeed.srcObject = mediaStream;
                            cameraFeed.play()
                                .then(function () {
                                    // Show camera switch button once video is playing
                                    const switchBtn = document.getElementById('switchCameraBtn');
                                    if (switchBtn) {
                                        switchBtn.style.display = 'block';
                                    }
                                })
                                .catch(function (err) {
                                    alert("Error playing video: " + err.message);
                                });
                        }
                    })
                    .catch(function (err) {
                        clearTimeout(cameraTimeout);

                        // Provide more specific error messages
                        let errorMessage = "Could not access camera. ";

                        if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
                            errorMessage += "No camera detected on this device.";
                        } else if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                            errorMessage += "Camera permissions denied. Please allow camera access in your browser settings.";
                        } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
                            errorMessage += "Camera is already in use by another application.";
                        } else if (err.name === 'OverconstrainedError') {
                            errorMessage += "Camera constraints cannot be satisfied.";
                        } else if (err.name === 'TypeError') {
                            errorMessage += "No video track found.";
                        } else if (err.name === 'AbortError') {
                            errorMessage += "Camera initialization timed out. Try refreshing the page or using a different browser.";
                        } else {
                            errorMessage += err.message;
                        }

                        alert(errorMessage);

                        // Try simplified constraints if the initial attempt failed
                        if (err.name === 'AbortError' || err.name === 'OverconstrainedError') {
                            setTimeout(() => {
                                console.log("Trying simplified camera constraints...");
                                // Try with just basic video (no specific settings)
                                navigator.mediaDevices.getUserMedia({
                                    video: true
                                })
                                    .then(function (mediaStream) {
                                        stream = mediaStream;
                                        if (cameraFeed) {
                                            cameraFeed.srcObject = mediaStream;
                                            cameraFeed.play()
                                                .then(function () {
                                                    const switchBtn = document.getElementById('switchCameraBtn');
                                                    if (switchBtn) {
                                                        switchBtn.style.display = 'none'; // Hide switch button in fallback mode
                                                    }
                                                })
                                                .catch(function (err) {
                                                    alert("Error playing video in fallback mode: " + err.message);
                                                });
                                        }
                                    })
                                    .catch(function (err) {
                                        alert("Camera access failed even with simplified settings. Please check your device permissions.");
                                    });
                            }, 1000); // Wait 1 second before trying fallback
                        }
                    });
            } else {
                alert("Sorry, your browser doesn't support camera access. Please try using Chrome, Edge, or Firefox.");
            }
        }

        // Start camera on open
        startCamera();
    });

    // Capture photo button
    if (captureBtn) {
        captureBtn.addEventListener('click', function () {
            if (!cameraFeed || !photoCanvas) {
                return;
            }

            try {
                // Set canvas dimensions to match video feed
                photoCanvas.width = cameraFeed.videoWidth;
                photoCanvas.height = cameraFeed.videoHeight;
                // Draw current video frame to canvas
                const context = photoCanvas.getContext('2d');
                context.drawImage(cameraFeed, 0, 0, photoCanvas.width, photoCanvas.height);

                // Get image data as base64 string
                capturedImage = photoCanvas.toDataURL('image/jpeg');

                // Hide video and show buttons for retake/save
                cameraFeed.style.display = 'none';
                captureBtn.style.display = 'none';
                retakeBtn.style.display = 'block';
                savePhotoBtn.style.display = 'block';

                // Show captured image
                photoCanvas.style.display = 'block';
            } catch (err) {
                alert("Failed to capture image: " + err.message);
            }
        });
    }

    // Retake photo button
    if (retakeBtn) {
        retakeBtn.addEventListener('click', function () {
            // Reset UI for capturing
            cameraFeed.style.display = 'block';
            photoCanvas.style.display = 'none';
            captureBtn.style.display = 'block';
            retakeBtn.style.display = 'none';
            savePhotoBtn.style.display = 'none';
            capturedImage = null;
        });
    }

    // Save captured photo
    if (savePhotoBtn) {
        savePhotoBtn.addEventListener('click', function () {
            if (!capturedImage) {
                return;
            }

            try {
                // Convert base64 to blob
                const base64 = capturedImage.split(',')[1];
                const mime = capturedImage.split(',')[0].match(/:(.*?);/)[1];
                const binaryStr = atob(base64);
                const len = binaryStr.length;
                const arr = new Uint8Array(len);

                for (let i = 0; i < len; i++) {
                    arr[i] = binaryStr.charCodeAt(i);
                }

                const blob = new Blob([arr], { type: mime });

                // Create a File object from the Blob
                const filename = `camera_capture_${new Date().getTime()}.jpg`;
                const file = new File([blob], filename, { type: mime });

                // Check browser support for DataTransfer
                if (typeof DataTransfer === 'undefined') {
                    // Show preview directly
                    if (previewPhoto) {
                        previewPhoto.src = capturedImage;
                        previewPhoto.style.display = 'block';

                        // Hide current photo if exists
                        const currentPhoto = document.getElementById('currentPhoto');
                        if (currentPhoto) {
                            currentPhoto.style.display = 'none';
                        }
                    }
                } else {
                    // Use DataTransfer to create a FileLike object
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);

                    // Set the file to the input element
                    if (profilePhotoInput) {
                        try {
                            profilePhotoInput.files = dataTransfer.files;

                            // Trigger change event to update preview
                            const event = new Event('change', { bubbles: true });
                            profilePhotoInput.dispatchEvent(event);
                        } catch (err) {
                            // Fall back to direct preview
                            if (previewPhoto) {
                                previewPhoto.src = capturedImage;
                                previewPhoto.style.display = 'block';

                                // Hide current photo if exists
                                const currentPhoto = document.getElementById('currentPhoto');
                                if (currentPhoto) {
                                    currentPhoto.style.display = 'none';
                                }
                            }
                        }
                    }
                }

                // Update the hidden input with the captured image data
                try {
                    console.log('Updating hidden input for camera capture data');
                    let hiddenInput = document.getElementById('camera_capture_data');

                    if (hiddenInput) {
                        console.log('Found existing hidden input, updating value');
                        hiddenInput.value = capturedImage;
                        console.log('Hidden input value set successfully');
                    } else {
                        console.error('Hidden input element not found');
                        alert('There was an issue saving the captured image. Please try again or use file upload instead.');
                    }
                } catch (err) {
                    console.error('Error updating hidden input:', err);
                    alert('There was an issue saving the captured image. Please try again or use file upload instead.');
                }

                // Close modal
                if (modal) {
                    modal.hide();
                } else if (cameraModal) {
                    cameraModal.style.display = 'none';
                }

                // Stop camera stream
                stopCameraStream();
            } catch (err) {
                alert("Failed to save captured image: " + err.message);
            }
        });
    }

    // Close modal handler - stop camera stream
    if (cameraModal) {
        // Add event listener for Bootstrap modal
        cameraModal.addEventListener('hidden.bs.modal', function () {
            stopCameraStream();
        });

        // Also add handler for close button for non-Bootstrap scenarios
        const closeBtn = cameraModal.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function () {
                stopCameraStream();
                if (!modal) {
                    cameraModal.style.display = 'none';
                }
            });
        }
    }

    // Helper function to stop camera stream
    function stopCameraStream() {
        if (stream) {
            stream.getTracks().forEach(track => {
                track.stop();
            });
            stream = null;
        }
    }
}

// User form dynamic rows
function setupDynamicRows() {
    // Clear any existing event listeners to prevent duplicate handlers
    const clearExistingListeners = (buttonId) => {
        const button = document.getElementById(buttonId);
        if (button) {
            const newButton = button.cloneNode(true);
            button.parentNode.replaceChild(newButton, button);
            return newButton;
        }
        return null;
    };

    // Add Emergency Contact
    // const addEmergencyContactBtn = clearExistingListeners('addEmergencyContact');
    // if (addEmergencyContactBtn) {
    //     addEmergencyContactBtn.addEventListener('click', function () {
    //         const template = document.getElementById('emergencyContactTemplate');
    //         const container = document.getElementById('emergencyContactsContainer');

    //         // Check if the template exists
    //         if (!template || !container) return;

    //         const clone = template.content.cloneNode(true);

    //         // Add event listener to remove button
    //         const removeBtn = clone.querySelector('.remove-row');
    //         if (removeBtn) {
    //             removeBtn.addEventListener('click', function () {
    //                 this.closest('.emergency-contact-row').remove();
    //             });
    //         }

    //         container.appendChild(clone);
    //     });
    // }

    // Add Family Member
    // const addFamilyMemberBtn = clearExistingListeners('addFamilyMember');
    // if (addFamilyMemberBtn) {
    //     addFamilyMemberBtn.addEventListener('click', function () {
    //         const template = document.getElementById('familyMemberTemplate');
    //         const container = document.getElementById('familyMembersContainer');

    //         // Check if the template exists
    //         if (!template || !container) return;

    //         const clone = template.content.cloneNode(true);

    //         // Add event listener to remove button
    //         const removeBtn = clone.querySelector('.remove-row');
    //         if (removeBtn) {
    //             removeBtn.addEventListener('click', function () {
    //                 this.closest('.family-member-row').remove();
    //             });
    //         }

    //         container.appendChild(clone);
    //     });
    // }

    // Add Previous Employer
    // const addPreviousEmployerBtn = clearExistingListeners('addPreviousEmployer');
    // if (addPreviousEmployerBtn) {
    //     addPreviousEmployerBtn.addEventListener('click', function () {
    //         const template = document.getElementById('previousEmployerTemplate');
    //         const container = document.getElementById('previousEmployersContainer');

    //         // Check if the template exists
    //         if (!template || !container) return;

    //         const clone = template.content.cloneNode(true);

    //         // Add event listener to remove button
    //         const removeBtn = clone.querySelector('.remove-row');
    //         if (removeBtn) {
    //             removeBtn.addEventListener('click', function () {
    //                 this.closest('.previous-employer-row').remove();
    //             });
    //         }

    //         container.appendChild(clone);
    //     });
    // }

    // Add Qualification
    // const addQualificationBtn = clearExistingListeners('addQualification');
    // if (addQualificationBtn) {
    //     addQualificationBtn.addEventListener('click', function () {
    //         const template = document.getElementById('qualificationTemplate');
    //         const container = document.getElementById('qualificationsContainer');

    //         // Check if the template exists
    //         if (!template || !container) return;

    //         const clone = template.content.cloneNode(true);

    //         // Add event listener to remove button
    //         const removeBtn = clone.querySelector('.remove-row');
    //         if (removeBtn) {
    //             removeBtn.addEventListener('click', function () {
    //                 this.closest('.qualification-row').remove();
    //             });
    //         }

    //         container.appendChild(clone);
    //     });
    // }

    // Setup existing remove buttons for emergency contacts
    // document.querySelectorAll('.remove-contact').forEach(button => {
    //     button.addEventListener('click', function () {
    //         const index = this.getAttribute('data-index');
    //         const row = this.closest('tr');
    //         row.remove();

    //         // Add hidden input to track deleted item
    //         const input = document.createElement('input');
    //         input.type = 'hidden';
    //         input.name = 'deleted_contacts[]';
    //         input.value = index;

    //         const container = document.getElementById('deletedContactsContainer');
    //         if (container) {
    //             container.appendChild(input);
    //         }
    //     });
    // });

    // Setup existing remove buttons for family members
    // document.querySelectorAll('.remove-family-member').forEach(button => {
    //     button.addEventListener('click', function () {
    //         const index = this.getAttribute('data-index');
    //         const row = this.closest('tr');
    //         row.remove();

    //         // Add hidden input to track deleted item
    //         const input = document.createElement('input');
    //         input.type = 'hidden';
    //         input.name = 'deleted_family_members[]';
    //         input.value = index;

    //         const container = document.getElementById('deletedFamilyMembersContainer');
    //         if (container) {
    //             container.appendChild(input);
    //         }
    //     });
    // });

    // Setup existing remove buttons for previous employers
    // document.querySelectorAll('.remove-employer').forEach(button => {
    //     button.addEventListener('click', function () {
    //         const index = this.getAttribute('data-index');
    //         const row = this.closest('tr');
    //         row.remove();

    //         // Add hidden input to track deleted item
    //         const input = document.createElement('input');
    //         input.type = 'hidden';
    //         input.name = 'deleted_employers[]';
    //         input.value = index;

    //         const container = document.getElementById('deletedEmployersContainer');
    //         if (container) {
    //             container.appendChild(input);
    //         }
    //     });
    // });

    // Setup existing remove buttons for qualifications
    // document.querySelectorAll('.remove-qualification').forEach(button => {
    //     button.addEventListener('click', function () {
    //         const index = this.getAttribute('data-index');
    //         const row = this.closest('tr');
    //         row.remove();

    //         // Add hidden input to track deleted item
    //         const input = document.createElement('input');
    //         input.type = 'hidden';
    //         input.name = 'deleted_qualifications[]';
    //         input.value = index;

    //         const container = document.getElementById('deletedQualificationsContainer');
    //         if (container) {
    //             container.appendChild(input);
    //         }
    //     });
    // });
}

// Function to initialize Bootstrap modals
function initializeModals() {
    // Make sure Bootstrap is available
    if (typeof bootstrap === 'undefined') {
        console.warn('Bootstrap is not loaded, modal initialization skipped');
        return;
    }

    // Initialize all modals on the page without creating duplicate instances
    document.querySelectorAll('.modal').forEach(function (modalElement) {
        // Skip if already processed to avoid duplicate handlers
        if (modalElement.hasAttribute('data-initialized')) {
            return;
        }

        // Only initialize if not already initialized by Bootstrap
        if (!bootstrap.Modal.getInstance(modalElement)) {
            // Create modal with options to prevent unwanted behavior
            const modalInstance = new bootstrap.Modal(modalElement, {
                backdrop: true,     // Allow clicking outside to close
                keyboard: true      // Allow ESC key to close
            });

            // Mark as initialized
            modalElement.setAttribute('data-initialized', 'true');

            // Store the instance on the element for future reference
            modalElement._modalInstance = modalInstance;

            // Find all triggers for this modal
            const modalId = modalElement.id;
            if (modalId) {
                // Handle both data-bs-target and data-bs-toggle attributes
                const triggers = document.querySelectorAll(
                    `[data-bs-target="#${modalId}"], [data-bs-toggle="modal"][href="#${modalId}"]`
                );

                triggers.forEach(function (triggerElement) {
                    // Remove existing click listeners to prevent duplicates
                    const newTrigger = triggerElement.cloneNode(true);
                    triggerElement.parentNode.replaceChild(newTrigger, triggerElement);

                    // Add our custom handler
                    newTrigger.addEventListener('click', function (e) {
                        e.preventDefault();
                        e.stopPropagation();
                        modalInstance.show();
                    });
                });
            }
        }
    });
}

// Function to setup delete confirmation for all delete buttons/forms
function setupDeleteConfirmation() {
    // Get modal elements
    const deleteModal = document.getElementById('deleteConfirmModal');
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    const deleteMessage = document.getElementById('deleteConfirmMessage');

    // Skip if modal elements don't exist
    if (!deleteModal || !confirmBtn) {
        console.warn('Delete confirmation modal not found, using browser confirm instead');
        setupFallbackDeleteConfirmation();
        return;
    }

    // Create Bootstrap modal instance if Bootstrap is available
    let modal = null;
    if (typeof bootstrap !== 'undefined') {
        modal = new bootstrap.Modal(deleteModal);
    } else {
        console.warn('Bootstrap is not loaded, using browser confirm instead');
        setupFallbackDeleteConfirmation();
        return;
    }

    // Variable to store the callback function when delete is confirmed
    let confirmCallback = null;
    let currentForm = null;

    // Handle forms with delete action in URL
    document.querySelectorAll('form[action*="delete"]').forEach(form => {
        // Skip if already processed or has custom delete handler
        if (form.hasAttribute('data-delete-confirmation') || form.classList.contains('delete-user-form')) {
            return;
        }

        form.setAttribute('data-delete-confirmation', 'true');

        // Override the submit event
        form.addEventListener('submit', function (e) {
            console.log('Delete form submit intercepted');
            e.preventDefault();

            // Store reference to the current form
            currentForm = form;

            // Set the confirmation callback
            confirmCallback = () => {
                console.log('Submitting form after confirmation');
                // Submit the form directly without using preventDefault
                form.submit();
            };

            // Show the modal
            modal.show();
        });
    });

    // Handle forms with hidden input[name="action"][value="delete"]
    document.querySelectorAll('form').forEach(form => {
        // Skip if already processed or already handled by previous selector or has custom delete handler
        if (form.hasAttribute('data-delete-confirmation') ||
            form.getAttribute('action')?.includes('delete') ||
            form.classList.contains('delete-user-form')) {
            return;
        }

        // Check if the form has a hidden input with name="action" and value="delete"
        const deleteInput = form.querySelector('input[name="action"][value="delete"]');
        if (deleteInput) {
            console.log('Found form with delete action input:', form);
            form.setAttribute('data-delete-confirmation', 'true');

            // Override the submit event
            form.addEventListener('submit', function (e) {
                console.log('Delete form submit intercepted');
                e.preventDefault();

                // Store reference to the current form
                currentForm = form;

                // Set the confirmation callback
                confirmCallback = () => {
                    console.log('Submitting form after confirmation');
                    // Submit the form directly
                    form.submit();
                };

                // Show the modal
                modal.show();
            });
        }
    });

    // Handle delete buttons that are not in forms with delete action
    document.querySelectorAll('button.btn-danger:not([data-delete-confirmation]), a.btn-danger:not([data-delete-confirmation])').forEach(button => {
        // Skip if already processed or has custom delete handler
        if (button.hasAttribute('data-delete-confirmation') || button.classList.contains('delete-user-btn')) {
            return;
        }

        button.setAttribute('data-delete-confirmation', 'true');

        // Store the original click event
        const originalClick = button.onclick;

        // Override the click event
        button.addEventListener('click', function (e) {
            console.log('Delete button clicked');
            e.preventDefault();

            // Set the confirmation callback
            confirmCallback = () => {
                // Execute the original click handler if it exists
                if (originalClick) {
                    originalClick.call(this, e);
                }

                // If it's a link, navigate to the href
                if (button.tagName === 'A' && button.href) {
                    window.location.href = button.href;
                }

                // If it's in a form, submit the form
                const parentForm = button.closest('form');
                if (parentForm) {
                    parentForm.submit();
                }
            };

            // Show the modal
            modal.show();
        });
    });

    // Handle forms that target delete URLs
    document.querySelectorAll('form[method="get"][action*="delete"]').forEach(form => {
        // Skip if already processed
        if (form.hasAttribute('data-delete-confirmation')) {
            return;
        }

        form.setAttribute('data-delete-confirmation', 'true');

        // Override the submit event
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            // Store reference to the current form
            currentForm = form;

            // Set the confirmation callback
            confirmCallback = () => {
                form.submit();
            };

            // Show the modal
            modal.show();
        });
    });

    // Add click event to the confirm button in the modal
    confirmBtn.addEventListener('click', function () {
        console.log('Confirm button clicked');

        // Hide the modal
        modal.hide();

        // Execute the callback if it exists
        if (confirmCallback && typeof confirmCallback === 'function') {
            console.log('Executing confirmation callback with delay');

            // Use a small delay to allow modal to close
            setTimeout(() => {
                console.log('Executing callback now');
                confirmCallback();
                console.log('Callback executed');
                confirmCallback = null; // Reset the callback
                currentForm = null; // Reset the current form
            }, 300);
        } else {
            console.log('No confirmation callback found');
        }
    });

    // Reset callback when modal is dismissed
    deleteModal.addEventListener('hidden.bs.modal', function () {
        confirmCallback = null;
        currentForm = null;
    });
}

// Fallback function using browser's default confirm dialog
function setupFallbackDeleteConfirmation() {
    // Handle forms with delete action in URL
    document.querySelectorAll('form[action*="delete"]').forEach(form => {
        // Skip if already processed
        if (form.hasAttribute('data-delete-confirmation')) {
            return;
        }

        form.setAttribute('data-delete-confirmation', 'true');

        // Store the original submit event
        const originalSubmit = form.onsubmit;

        // Override the submit event
        form.onsubmit = function (e) {
            e.preventDefault();

            // Show confirmation dialog
            if (confirm('Are you sure you want to delete this record?')) {
                // If confirmed, remove our handler and submit
                form.onsubmit = originalSubmit;
                form.submit();
            }
        };
    });

    // Handle forms with hidden input[name="action"][value="delete"]
    document.querySelectorAll('form').forEach(form => {
        // Skip if already processed or already handled by previous selector
        if (form.hasAttribute('data-delete-confirmation') || form.getAttribute('action')?.includes('delete')) {
            return;
        }

        // Check if the form has a hidden input with name="action" and value="delete"
        const deleteInput = form.querySelector('input[name="action"][value="delete"]');
        if (deleteInput) {
            form.setAttribute('data-delete-confirmation', 'true');

            // Store the original submit event
            const originalSubmit = form.onsubmit;

            // Override the submit event
            form.onsubmit = function (e) {
                e.preventDefault();

                // Show confirmation dialog
                if (confirm('Are you sure you want to delete this record?')) {
                    // If confirmed, remove our handler and submit
                    form.onsubmit = originalSubmit;
                    form.submit();
                }
            };
        }
    });

    // Handle delete buttons that are not in forms with delete action
    document.querySelectorAll('button.btn-danger:not([data-delete-confirmation]), a.btn-danger:not([data-delete-confirmation])').forEach(button => {
        // Skip if already processed
        if (button.hasAttribute('data-delete-confirmation')) {
            return;
        }

        button.setAttribute('data-delete-confirmation', 'true');

        // Store the original click event
        const originalClick = button.onclick;

        // Override the click event
        button.onclick = function (e) {
            e.preventDefault();

            // Show confirmation dialog
            if (confirm('Are you sure you want to delete this record?')) {
                // If confirmed, execute the original click handler
                if (originalClick) {
                    originalClick.call(this, e);
                }

                // If it's a link, navigate to the href
                if (button.tagName === 'A' && button.href) {
                    window.location.href = button.href;
                }

                // If it's in a form, submit the form
                const parentForm = button.closest('form');
                if (parentForm) {
                    parentForm.submit();
                }
            }
        };
    });

    // Handle forms that target delete URLs
    document.querySelectorAll('form[method="get"][action*="delete"]').forEach(form => {
        // Skip if already processed
        if (form.hasAttribute('data-delete-confirmation')) {
            return;
        }

        form.setAttribute('data-delete-confirmation', 'true');

        // Override the submit event
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            // Set the confirmation callback
            confirmCallback = () => {
                form.submit();
            };

            // Show the modal
            modal.show();
        });
    });
} 