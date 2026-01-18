// ==================== CONFIGURATION ====================
const API_BASE = '/api';
let selectedUserId = null;

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tab switching
    setupTabNavigation();
    
    // Initialize upload tab switching
    setupUploadTabs();
    
    // Initialize forms
    setupForms();
    
    // Load initial data
    loadUsers();
    loadUsersForPhotoSelection();
    
    // Setup file preview
    setupFilePreview();
});

// ==================== TAB NAVIGATION ====================
function setupTabNavigation() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            
            // Remove active class from all
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Add active class to current
            btn.classList.add('active');
            document.getElementById(tabId + '-tab').classList.add('active');
        });
    });
}

function setupUploadTabs() {
    const uploadTabBtns = document.querySelectorAll('.upload-tab-btn');
    const uploadTabContents = document.querySelectorAll('.upload-tab-content');
    
    uploadTabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-upload-tab');
            
            // Remove active class from all
            uploadTabBtns.forEach(b => b.classList.remove('active'));
            uploadTabContents.forEach(c => c.classList.remove('active'));
            
            // Add active class to current
            btn.classList.add('active');
            document.getElementById(tabId + 'UploadTab').classList.add('active');
        });
    });
}

// ==================== FORM SETUP ====================
function setupForms() {
    // Create User Form
    const createUserForm = document.getElementById('createUserForm');
    if (createUserForm) {
        createUserForm.addEventListener('submit', handleCreateUser);
    }
    
    // Edit User Form
    const editUserForm = document.getElementById('editUserForm');
    if (editUserForm) {
        editUserForm.addEventListener('submit', handleEditUser);
    }
    
    // Upload Single Photo Form
    const uploadSingleForm = document.getElementById('uploadSingleForm');
    if (uploadSingleForm) {
        uploadSingleForm.addEventListener('submit', handleUploadSinglePhoto);
    }
    
    // Upload Multiple Photos Form
    const uploadMultipleForm = document.getElementById('uploadMultipleForm');
    if (uploadMultipleForm) {
        uploadMultipleForm.addEventListener('submit', handleUploadMultiplePhotos);
    }
    
    // Upload Camera Photo Form
    const uploadCameraForm = document.getElementById('uploadCameraForm');
    if (uploadCameraForm) {
        uploadCameraForm.addEventListener('submit', handleUploadCameraPhoto);
    }
}

// ==================== FILE PREVIEW ====================
function setupFilePreview() {
    const singlePhotoFile = document.getElementById('singlePhotoFile');
    const multiplePhotoFiles = document.getElementById('multiplePhotoFiles');
    
    if (singlePhotoFile) {
        singlePhotoFile.addEventListener('change', function() {
            previewFile(this, 'singlePreview', true);
        });
    }
    
    if (multiplePhotoFiles) {
        multiplePhotoFiles.addEventListener('change', function() {
            previewFile(this, 'multiplePreview', false);
        });
    }
}

function previewFile(input, containerId, isSingle) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    if (isSingle && input.files.length > 0) {
        const file = input.files[0];
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.className = 'preview-img';
            container.appendChild(img);
        };
        reader.readAsDataURL(file);
    } else if (!isSingle) {
        Array.from(input.files).forEach((file, index) => {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                const div = document.createElement('div');
                div.className = 'preview-item';
                
                const img = document.createElement('img');
                img.src = e.target.result;
                img.className = 'preview-img';
                
                const removeBtn = document.createElement('button');
                removeBtn.type = 'button';
                removeBtn.className = 'preview-remove';
                removeBtn.innerHTML = '×';
                removeBtn.onclick = function(event) {
                    event.preventDefault();
                    removeFileFromInput(input, index);
                };
                
                div.appendChild(img);
                div.appendChild(removeBtn);
                container.appendChild(div);
            };
            reader.readAsDataURL(file);
        });
    }
}

function removeFileFromInput(input, index) {
    const dataTransfer = new DataTransfer();
    
    Array.from(input.files).forEach((file, i) => {
        if (i !== index) {
            dataTransfer.items.add(file);
        }
    });
    
    input.files = dataTransfer.files;
    previewFile(input, 'multiplePreview', false);
}

// ==================== USERS MANAGEMENT ====================
async function loadUsers() {
    try {
        const response = await fetch(`${API_BASE}/users`);
        const users = await response.json();
        
        const container = document.getElementById('usersContainer');
        
        if (users.length === 0) {
            container.innerHTML = '<div class="loading">No users found. Create your first user!</div>';
            return;
        }
        
        container.innerHTML = users.map(user => `
            <div class="user-card">
                <div class="user-info">
                    <h3>${escapeHtml(user.name)}</h3>
                    <p>📧 ${escapeHtml(user.email)}</p>
                    <p>🆔 ID: ${user.id}</p>
                </div>
                <div class="user-actions">
                    <button class="btn btn-primary btn-small" onclick="openEditUserModal(${user.id}, '${escapeHtml(user.name)}', '${escapeHtml(user.email)}')">
                        ✏️ Edit
                    </button>
                    <button class="btn btn-danger btn-small" onclick="deleteUser(${user.id})">
                        🗑️ Delete
                    </button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        showMessage('usersContainer', 'Error loading users: ' + error.message, 'error');
        console.error('Error:', error);
    }
}

async function handleCreateUser(e) {
    e.preventDefault();
    
    const name = document.getElementById('userName').value.trim();
    const email = document.getElementById('userEmail').value.trim();
    const messageEl = document.getElementById('createUserMessage');
    
    if (!name || !email) {
        showMessage(messageEl, 'Please fill in all fields', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(messageEl, `✅ User "${data.name}" created successfully!`, 'success');
            document.getElementById('createUserForm').reset();
            loadUsers();
            loadUsersForPhotoSelection();
            setTimeout(() => messageEl.classList.remove('show'), 3000);
        } else {
            showMessage(messageEl, '❌ Error: ' + data.message, 'error');
        }
    } catch (error) {
        showMessage(messageEl, 'Error creating user: ' + error.message, 'error');
    }
}

function openEditUserModal(userId, userName, userEmail) {
    document.getElementById('editUserId').value = userId;
    document.getElementById('editUserName').value = userName;
    document.getElementById('editUserEmail').value = userEmail;
    document.getElementById('editUserModal').classList.add('show');
    document.getElementById('editUserMessage').classList.remove('show');
}

function closeEditUserModal() {
    document.getElementById('editUserModal').classList.remove('show');
}

async function handleEditUser(e) {
    e.preventDefault();
    
    const userId = document.getElementById('editUserId').value;
    const name = document.getElementById('editUserName').value.trim();
    const email = document.getElementById('editUserEmail').value.trim();
    const messageEl = document.getElementById('editUserMessage');
    
    if (!name || !email) {
        showMessage(messageEl, 'Please fill in all fields', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(messageEl, `✅ User updated successfully!`, 'success');
            loadUsers();
            loadUsersForPhotoSelection();
            setTimeout(() => {
                closeEditUserModal();
            }, 1000);
        } else {
            showMessage(messageEl, '❌ Error: ' + data.message, 'error');
        }
    } catch (error) {
        showMessage(messageEl, 'Error updating user: ' + error.message, 'error');
    }
}

async function deleteUser(userId) {
    if (!confirm('Are you sure you want to delete this user and all their photos?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/users/${userId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('✅ User deleted successfully!');
            loadUsers();
            loadUsersForPhotoSelection();
        } else {
            alert('❌ Error deleting user');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// ==================== PHOTOS MANAGEMENT ====================
async function loadUsersForPhotoSelection() {
    try {
        const response = await fetch(`${API_BASE}/users`);
        const users = await response.json();
        
        const select = document.getElementById('photoUserId');
        select.innerHTML = '<option value="">-- Select User --</option>';
        
        users.forEach(user => {
            const option = document.createElement('option');
            option.value = user.id;
            option.textContent = `${user.name} (${user.email})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

function onUserSelected() {
    selectedUserId = document.getElementById('photoUserId').value;
    
    if (selectedUserId) {
        document.getElementById('uploadSection').style.display = 'block';
        document.getElementById('photosSection').style.display = 'block';
        loadUserPhotos();
    } else {
        document.getElementById('uploadSection').style.display = 'none';
        document.getElementById('photosSection').style.display = 'none';
        document.getElementById('photosContainer').innerHTML = '<div class="loading">No user selected</div>';
    }
}

async function loadUserPhotos() {
    if (!selectedUserId) return;
    
    try {
        const response = await fetch(`${API_BASE}/photos/${selectedUserId}`);
        const photos = await response.json();
        
        const container = document.getElementById('photosContainer');
        
        if (photos.length === 0) {
            container.innerHTML = '<div class="loading" style="grid-column: 1/-1;">No photos yet. Upload one to get started!</div>';
            return;
        }
        
        container.innerHTML = photos.map(photo => `
            <div class="photo-card">
                <img src="${API_BASE}/photos/${selectedUserId}/${photo.id}/view" 
                     alt="${escapeHtml(photo.filename)}" 
                     class="photo-image"
                     onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22300%22 height=%22200%22%3E%3Crect fill=%22%23f3f4f6%22 width=%22300%22 height=%22200%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 fill=%22%236b7280%22 font-size=%2216%22%3EImage Not Found%3C/text%3E%3C/svg%3E'">
                <div class="photo-info">
                    <h3>${escapeHtml(photo.filename)}</h3>
                    <div class="photo-details">
                        <p>📏 ${photo.width}×${photo.height}px</p>
                        <p>📅 ${new Date(photo.created_at).toLocaleString()}</p>
                    </div>
                    <div class="photo-actions">
                        <a href="${API_BASE}/photos/${selectedUserId}/${photo.id}/view" target="_blank">👁️ View</a>
                        <a href="#" class="delete" onclick="deletePhoto(event, ${selectedUserId}, ${photo.id})">🗑️ Delete</a>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        const container = document.getElementById('photosContainer');
        showMessage(container, 'Error loading photos: ' + error.message, 'error');
        console.error('Error:', error);
    }
}

async function handleUploadSinglePhoto(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('singlePhotoFile');
    const messageEl = document.getElementById('singleUploadMessage');
    
    if (!fileInput.files.length) {
        showMessage(messageEl, 'Please select a photo', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    try {
        const response = await fetch(`${API_BASE}/photos/${selectedUserId}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(messageEl, `✅ Photo uploaded successfully!`, 'success');
            document.getElementById('uploadSingleForm').reset();
            document.getElementById('singlePreview').innerHTML = '';
            loadUserPhotos();
            setTimeout(() => messageEl.classList.remove('show'), 3000);
        } else {
            showMessage(messageEl, '❌ Error: ' + data.message, 'error');
        }
    } catch (error) {
        showMessage(messageEl, 'Error uploading photo: ' + error.message, 'error');
    }
}

async function handleUploadMultiplePhotos(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('multiplePhotoFiles');
    const messageEl = document.getElementById('multipleUploadMessage');
    
    if (!fileInput.files.length) {
        showMessage(messageEl, 'Please select at least one photo', 'error');
        return;
    }
    
    const formData = new FormData();
    Array.from(fileInput.files).forEach(file => {
        formData.append('files[]', file);
    });
    
    try {
        const response = await fetch(`${API_BASE}/photos/${selectedUserId}/upload/multiple`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const successCount = data.files.length;
            const errorCount = data.errors ? data.errors.length : 0;
            let message = `✅ ${successCount} photo(s) uploaded successfully!`;
            if (errorCount > 0) {
                message += ` (${errorCount} failed)`;
            }
            showMessage(messageEl, message, 'success');
            document.getElementById('uploadMultipleForm').reset();
            document.getElementById('multiplePreview').innerHTML = '';
            loadUserPhotos();
            setTimeout(() => messageEl.classList.remove('show'), 3000);
        } else {
            showMessage(messageEl, '❌ Error: ' + data.message, 'error');
        }
    } catch (error) {
        showMessage(messageEl, 'Error uploading photos: ' + error.message, 'error');
    }
}

async function deletePhoto(e, userId, photoId) {
    e.preventDefault();
    
    if (!confirm('Are you sure you want to delete this photo?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/photos/${userId}/${photoId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('✅ Photo deleted successfully!');
            loadUserPhotos();
        } else {
            alert('❌ Error deleting photo');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// ==================== UTILITY FUNCTIONS ====================
function showMessage(elementOrId, message, type) {
    const element = typeof elementOrId === 'string' 
        ? document.getElementById(elementOrId) 
        : elementOrId;
    
    if (!element) return;
    
    element.textContent = message;
    element.className = `message show ${type}`;
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Close modals when clicking outside
window.addEventListener('click', function(event) {
    const editModal = document.getElementById('editUserModal');
    if (event.target === editModal) {
        closeEditUserModal();
    }
});

// ==================== CAMERA CAPTURE ====================
let cameraStream = null;
let capturedImageBlob = null;

async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { 
                facingMode: 'user',
                width: { ideal: 1280 },
                height: { ideal: 720 }
            },
            audio: false
        });
        
        const video = document.getElementById('cameraStream');
        video.srcObject = stream;
        cameraStream = stream;
        
        video.style.display = 'block';
        document.getElementById('captureContainer').style.display = 'flex';
        document.getElementById('startCameraBtn').style.display = 'none';
        document.getElementById('stopCameraBtn').style.display = 'block';
        video.classList.add('recording');
        
        // Ensure video plays
        video.onloadedmetadata = function() {
            video.play();
        };
    } catch (error) {
        showMessage(
            document.getElementById('cameraUploadMessage'),
            '❌ Camera Error: ' + (error.name === 'NotAllowedError' 
                ? 'Camera permission denied' 
                : error.message),
            'error'
        );
    }
}

function stopCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }
    
    const video = document.getElementById('cameraStream');
    video.style.display = 'none';
    document.getElementById('captureContainer').style.display = 'none';
    document.getElementById('startCameraBtn').style.display = 'block';
    document.getElementById('stopCameraBtn').style.display = 'none';
    video.classList.remove('recording');
}

function capturePhoto() {
    const video = document.getElementById('cameraStream');
    const canvas = document.getElementById('captureCanvas');
    const ctx = canvas.getContext('2d');
    
    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw video frame to canvas
    ctx.drawImage(video, 0, 0);
    
    // Convert to blob
    canvas.toBlob(function(blob) {
        capturedImageBlob = blob;
        
        // Show preview
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('cameraPreview');
            preview.innerHTML = `
                <img src="${e.target.result}" alt="Captured Photo">
                <p style="color: #6b7280; font-size: 14px;">Photo captured successfully!</p>
            `;
            document.getElementById('uploadCameraForm').style.display = 'block';
        };
        reader.readAsDataURL(blob);
        
        showMessage(
            document.getElementById('cameraUploadMessage'),
            '✅ Photo captured! Ready to upload',
            'success'
        );
    }, 'image/jpeg', 0.95);
}

async function handleUploadCameraPhoto(e) {
    e.preventDefault();
    
    if (!selectedUserId) {
        showMessage(
            document.getElementById('cameraUploadMessage'),
            '❌ Please select a user first',
            'error'
        );
        return;
    }
    
    if (!capturedImageBlob) {
        showMessage(
            document.getElementById('cameraUploadMessage'),
            '❌ No photo captured yet',
            'error'
        );
        return;
    }
    
    const formData = new FormData();
    formData.append('file', capturedImageBlob, `camera_${Date.now()}.jpg`);
    
    try {
        const response = await fetch(`${API_BASE}/photos/${selectedUserId}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(
                document.getElementById('cameraUploadMessage'),
                '✅ Photo uploaded successfully!',
                'success'
            );
            capturedImageBlob = null;
            document.getElementById('cameraPreview').innerHTML = '';
            document.getElementById('uploadCameraForm').style.display = 'none';
            loadUserPhotos();
        } else {
            showMessage(
                document.getElementById('cameraUploadMessage'),
                '❌ Error: ' + (data.message || 'Upload failed'),
                'error'
            );
        }
    } catch (error) {
        showMessage(
            document.getElementById('cameraUploadMessage'),
            '❌ Error: ' + error.message,
            'error'
        );
    }
}

