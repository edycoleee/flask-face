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
    checkModelStatus();
    checkPredictionModelStatus();
    
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
    
    uploadTabBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tabId = btn.getAttribute('data-upload-tab');
            
            // Find parent container to scope the tab switching
            const parentCard = btn.closest('.card');
            if (!parentCard) return;
            
            // Remove active class from siblings only
            const siblingBtns = parentCard.querySelectorAll('.upload-tab-btn');
            const siblingContents = parentCard.querySelectorAll('.upload-tab-content');
            
            siblingBtns.forEach(b => b.classList.remove('active'));
            siblingContents.forEach(c => c.classList.remove('active'));
            
            // Add active class to current
            btn.classList.add('active');
            
            // Activate corresponding content
            const targetContent = parentCard.querySelector(`#${tabId}Tab`);
            if (targetContent) {
                targetContent.classList.add('active');
            }
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
    
    // Training Form
    const trainingForm = document.getElementById('trainingForm');
    if (trainingForm) {
        trainingForm.addEventListener('submit', startTraining);
    }
    
    // Prediction Upload Form
    const predictUploadForm = document.getElementById('predictUploadForm');
    if (predictUploadForm) {
        predictUploadForm.addEventListener('submit', handlePredictUpload);
    }
    
    // Prediction Camera Form
    const predictCameraForm = document.getElementById('predictCameraForm');
    if (predictCameraForm) {
        predictCameraForm.addEventListener('submit', handlePredictCamera);
    }
    
    // Verification Email Form
    const verifyEmailForm = document.getElementById('verifyEmailForm');
    if (verifyEmailForm) {
        verifyEmailForm.addEventListener('submit', handleEmailLookup);
    }
    
    // Verification Upload Form
    const verifyUploadForm = document.getElementById('verifyUploadForm');
    if (verifyUploadForm) {
        verifyUploadForm.addEventListener('submit', handleVerifyUpload);
    }
    
    // Verification Camera Form
    const verifyCameraForm = document.getElementById('verifyCameraForm');
    if (verifyCameraForm) {
        verifyCameraForm.addEventListener('submit', handleVerifyCamera);
    }
}

// ==================== FILE PREVIEW ====================
function setupFilePreview() {
    const singlePhotoFile = document.getElementById('singlePhotoFile');
    const multiplePhotoFiles = document.getElementById('multiplePhotoFiles');
    const predictPhotoFile = document.getElementById('predictPhotoFile');
    
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
    
    if (predictPhotoFile) {
        predictPhotoFile.addEventListener('change', function() {
            previewFile(this, 'predictUploadPreview', true);
        });
    }
    
    const verifyPhotoFile = document.getElementById('verifyPhotoFile');
    if (verifyPhotoFile) {
        verifyPhotoFile.addEventListener('change', function() {
            previewFile(this, 'verifyUploadPreview', true);
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
                    <p>🔑 Password: ${escapeHtml(user.password)}</p>
                    <p>🆔 ID: ${user.id}</p>
                </div>
                <div class="user-actions">
                    <button class="btn btn-primary btn-small" onclick="openEditUserModal(${user.id}, '${escapeHtml(user.name)}', '${escapeHtml(user.email)}', '${escapeHtml(user.password)}')">
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
    const password = document.getElementById('userPassword').value.trim();
    const messageEl = document.getElementById('createUserMessage');
    
    if (!name || !email || !password) {
        showMessage(messageEl, 'Please fill in all fields', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email, password })
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

function openEditUserModal(userId, userName, userEmail, userPassword) {
    document.getElementById('editUserId').value = userId;
    document.getElementById('editUserName').value = userName;
    document.getElementById('editUserEmail').value = userEmail;
    document.getElementById('editUserPassword').value = userPassword;
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
    const password = document.getElementById('editUserPassword').value.trim();
    const messageEl = document.getElementById('editUserMessage');
    
    if (!name || !email || !password) {
        showMessage(messageEl, 'Please fill in all fields', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email, password })
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

// Check browser support for getUserMedia
function getGetUserMediaFunction() {
    const navigator_obj = navigator;
    navigator_obj.getUserMedia = navigator_obj.getUserMedia || 
                                  navigator_obj.webkitGetUserMedia || 
                                  navigator_obj.mozGetUserMedia || 
                                  navigator_obj.msGetUserMedia;
    
    // Modern approach - use mediaDevices
    if (navigator_obj.mediaDevices && navigator_obj.mediaDevices.getUserMedia) {
        return navigator_obj.mediaDevices.getUserMedia.bind(navigator_obj.mediaDevices);
    }
    // Fallback for older browsers
    else if (navigator_obj.getUserMedia) {
        return function(constraints) {
            return new Promise((resolve, reject) => {
                navigator_obj.getUserMedia(constraints, resolve, reject);
            });
        };
    }
    // No support
    else {
        return null;
    }
}

// Camera state management
let isStreaming = false;
let capturedImageData = null;

// Fungsi untuk membuka kamera
async function openCamera() {
    try {
        // Clear previous errors
        hideCameraError();
        
        // Cek apakah browser mendukung getUserMedia
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            showCameraError(
                '❌ Browser tidak mendukung akses kamera atau halaman tidak aman. ' +
                'Pastikan menggunakan HTTPS atau localhost untuk mengakses kamera.'
            );
            return;
        }
        
        // Request camera with optimal settings
        const constraints = {
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            },
            audio: false
        };
        
        let stream;
        try {
            stream = await navigator.mediaDevices.getUserMedia(constraints);
        } catch (constraintError) {
            // Fallback to basic video if detailed constraints fail
            console.log('Detailed constraints not supported, trying basic video...');
            stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        }
        
        const video = document.getElementById('cameraStream');
        
        if (video) {
            video.srcObject = stream;
            cameraStream = stream;
            isStreaming = true;
            
            // Show video container and controls
            document.getElementById('videoContainer').style.display = 'block';
            document.getElementById('captureContainer').style.display = 'flex';
            document.getElementById('startCameraBtn').style.display = 'none';
            document.getElementById('stopCameraBtn').style.display = 'inline-block';
            
            // Clear previous preview
            document.getElementById('cameraPreview').innerHTML = '';
            document.getElementById('uploadCameraForm').style.display = 'none';
            capturedImageData = null;
            
            // Ensure video plays
            video.onloadedmetadata = () => {
                video.play().catch(err => {
                    console.error('Play error:', err);
                    showCameraError('❌ Gagal memutar video kamera: ' + err.message);
                });
            };
            
            showMessage(
                document.getElementById('cameraUploadMessage'),
                '✅ Kamera berhasil dibuka. Posisikan wajah Anda dan klik "Ambil Foto"',
                'success'
            );
        }
    } catch (err) {
        let errorMessage = '❌ Tidak dapat mengakses kamera: ';
        
        if (err.name === 'NotAllowedError') {
            errorMessage += 'Izin akses kamera ditolak. Silakan izinkan akses kamera di pengaturan browser.';
        } else if (err.name === 'NotFoundError') {
            errorMessage += 'Kamera tidak ditemukan. Pastikan perangkat memiliki kamera.';
        } else if (err.name === 'NotReadableError') {
            errorMessage += 'Kamera sedang digunakan aplikasi lain. Tutup aplikasi tersebut dan coba lagi.';
        } else if (err.name === 'OverconstrainedError') {
            errorMessage += 'Kamera tidak mendukung resolusi yang diminta.';
        } else if (err.name === 'TypeError') {
            errorMessage += 'Akses kamera gagal. Gunakan HTTPS atau localhost.';
        } else {
            errorMessage += err.message || 'Terjadi kesalahan tidak diketahui';
        }
        
        showCameraError(errorMessage);
        console.error('Error accessing camera:', err);
    }
}

// Fungsi untuk menutup kamera
function closeCamera() {
    if (cameraStream) {
        // Stop all tracks
        const tracks = cameraStream.getTracks();
        tracks.forEach(track => track.stop());
        cameraStream = null;
    }
    
    const video = document.getElementById('cameraStream');
    
    if (video && video.srcObject) {
        video.srcObject = null;
    }
    
    // Hide video and controls
    document.getElementById('videoContainer').style.display = 'none';
    document.getElementById('captureContainer').style.display = 'none';
    document.getElementById('startCameraBtn').style.display = 'inline-block';
    document.getElementById('stopCameraBtn').style.display = 'none';
    
    // Reset state
    isStreaming = false;
    
    showMessage(
        document.getElementById('cameraUploadMessage'),
        '',
        ''
    );
}

// Fungsi untuk capture gambar
function captureImage() {
    if (!isStreaming) {
        showMessage(
            document.getElementById('cameraUploadMessage'),
            '❌ Kamera belum aktif. Silakan buka kamera terlebih dahulu.',
            'error'
        );
        return;
    }
    
    const video = document.getElementById('cameraStream');
    const canvas = document.getElementById('captureCanvas');
    
    if (!canvas || !video) {
        showCameraError('❌ Element kamera tidak ditemukan');
        return;
    }
    
    const context = canvas.getContext('2d');
    
    // Check if video is ready
    if (video.readyState !== video.HAVE_ENOUGH_DATA) {
        showMessage(
            document.getElementById('cameraUploadMessage'),
            '❌ Kamera belum siap. Tunggu sebentar dan coba lagi.',
            'error'
        );
        return;
    }
    
    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Validate dimensions
    if (canvas.width === 0 || canvas.height === 0) {
        showMessage(
            document.getElementById('cameraUploadMessage'),
            '❌ Stream kamera tidak valid. Coba tutup dan buka kamera lagi.',
            'error'
        );
        return;
    }
    
    // Draw video frame to canvas
    context.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );
    
    // Get image data as base64
    const imageData = canvas.toDataURL('image/png');
    capturedImageData = imageData;
    
    // Convert to blob for upload
    canvas.toBlob(
        function(blob) {
            if (!blob) {
                showMessage(
                    document.getElementById('cameraUploadMessage'),
                    '❌ Gagal mengambil foto. Silakan coba lagi.',
                    'error'
                );
                return;
            }
            
            capturedImageBlob = blob;
            
            // Show preview
            const preview = document.getElementById('cameraPreview');
            preview.innerHTML = `
                <div class="captured-image-container">
                    <img src="${imageData}" alt="Foto yang diambil" class="captured-image">
                    <p class="capture-success">✅ Foto berhasil diambil!</p>
                </div>
            `;
            
            // Show upload form
            document.getElementById('uploadCameraForm').style.display = 'block';
            
            // Optionally hide video to save resources
            // document.getElementById('videoContainer').style.display = 'none';
            // document.getElementById('captureContainer').style.display = 'none';
            
            showMessage(
                document.getElementById('cameraUploadMessage'),
                '✅ Foto siap diupload! Klik "Upload Foto" atau "Ambil Ulang"',
                'success'
            );
        },
        'image/jpeg',
        0.95 // Quality 95%
    );
}

async function handleUploadCameraPhoto(e) {
    e.preventDefault();
    
    if (!selectedUserId) {
        showMessage(
            document.getElementById('cameraUploadMessage'),
            '❌ Silakan pilih user terlebih dahulu',
            'error'
        );
        return;
    }
    
    if (!capturedImageBlob) {
        showMessage(
            document.getElementById('cameraUploadMessage'),
            '❌ Belum ada foto yang diambil',
            'error'
        );
        return;
    }
    
    const formData = new FormData();
    formData.append('file', capturedImageBlob, `camera_${Date.now()}.jpg`);
    
    try {
        showMessage(
            document.getElementById('cameraUploadMessage'),
            '⏳ Mengupload foto...',
            'info'
        );
        
        const response = await fetch(`${API_BASE}/photos/${selectedUserId}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(
                document.getElementById('cameraUploadMessage'),
                '✅ Foto berhasil diupload!',
                'success'
            );
            
            // Clean up
            capturedImageBlob = null;
            capturedImageData = null;
            document.getElementById('cameraPreview').innerHTML = '';
            document.getElementById('uploadCameraForm').style.display = 'none';
            
            // Close camera
            closeCamera();
            
            // Reload photos
            loadUserPhotos();
        } else {
            showMessage(
                document.getElementById('cameraUploadMessage'),
                '❌ Error: ' + (data.message || 'Upload gagal'),
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

// Fungsi untuk mengambil foto ulang
function retakePhoto() {
    // Clear captured image
    capturedImageBlob = null;
    capturedImageData = null;
    
    // Clear preview
    document.getElementById('cameraPreview').innerHTML = '';
    document.getElementById('uploadCameraForm').style.display = 'none';
    
    // Show video and capture button again
    document.getElementById('videoContainer').style.display = 'block';
    document.getElementById('captureContainer').style.display = 'flex';
    
    showMessage(
        document.getElementById('cameraUploadMessage'),
        'ℹ️ Posisikan wajah Anda dan ambil foto lagi',
        'info'
    );
}

// Helper functions untuk error handling
function showCameraError(message) {
    const errorEl = document.getElementById('cameraErrorMessage');
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.style.display = 'block';
    }
    
    showMessage(
        document.getElementById('cameraUploadMessage'),
        message,
        'error'
    );
}

function hideCameraError() {
    const errorEl = document.getElementById('cameraErrorMessage');
    if (errorEl) {
        errorEl.style.display = 'none';
        errorEl.textContent = '';
    }
}


// ==================== TRAINING SECTION ====================

// Start training
async function startTraining(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    
    const trainingData = {
        epochs: parseInt(formData.get('epochs')),
        batch_size: parseInt(formData.get('batch_size')),
        validation_split: parseFloat(formData.get('validation_split')),
        continue_training: formData.get('continue_training') === 'true'
    };
    
    const messageEl = document.getElementById('trainingMessage');
    const startBtn = document.getElementById('startTrainingBtn');
    const progressCard = document.getElementById('trainingProgressCard');
    const resultsCard = document.getElementById('trainingResultsCard');
    
    // Show progress, hide results
    progressCard.style.display = 'block';
    resultsCard.style.display = 'none';
    
    // Disable button
    startBtn.disabled = true;
    startBtn.innerHTML = '⏳ Training...';
    
    // Update progress
    updateProgress(0, 'Initializing training...');
    
    try {
        showMessage(messageEl, '🚀 Training started...', 'info');
        updateProgress(10, 'Loading dataset...');
        
        const response = await fetch(`${API_BASE}/training/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(trainingData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            updateProgress(100, 'Training completed!');
            showMessage(messageEl, '✅ ' + data.message, 'success');
            displayTrainingResults(data.data);
            resultsCard.style.display = 'block';
            
            // Refresh model status
            setTimeout(() => {
                checkModelStatus();
            }, 1000);
        } else {
            updateProgress(0, 'Training failed');
            showMessage(messageEl, '❌ Error: ' + (data.message || 'Training failed'), 'error');
            progressCard.style.display = 'none';
        }
    } catch (error) {
        updateProgress(0, 'Training failed');
        showMessage(messageEl, '❌ Error: ' + error.message, 'error');
        progressCard.style.display = 'none';
    } finally {
        startBtn.disabled = false;
        startBtn.innerHTML = '🚀 Start Training';
    }
}

// Update progress bar
function updateProgress(percent, text) {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    if (progressFill) {
        progressFill.style.width = percent + '%';
        progressFill.textContent = percent + '%';
    }
    
    if (progressText) {
        progressText.textContent = text;
    }
}

// Display training results
function displayTrainingResults(stats) {
    const resultsContainer = document.getElementById('trainingResults');
    
    if (!stats) {
        resultsContainer.innerHTML = '<p>No results available</p>';
        return;
    }
    
    const accuracyClass = stats.test_accuracy >= 0.9 ? 'success' : 
                         stats.test_accuracy >= 0.7 ? 'warning' : 'danger';
    
    resultsContainer.innerHTML = `
        <div class="result-item">
            <div class="label">Test Accuracy</div>
            <div class="value ${accuracyClass}">${(stats.test_accuracy * 100).toFixed(2)}%</div>
        </div>
        <div class="result-item">
            <div class="label">Test Loss</div>
            <div class="value">${stats.test_loss.toFixed(4)}</div>
        </div>
        <div class="result-item">
            <div class="label">Training Time</div>
            <div class="value">${stats.training_time_minutes} min</div>
        </div>
        <div class="result-item">
            <div class="label">Epochs Trained</div>
            <div class="value">${stats.epochs_trained}</div>
        </div>
        <div class="result-item">
            <div class="label">Total Images</div>
            <div class="value">${stats.num_data}</div>
        </div>
        <div class="result-item">
            <div class="label">Number of Users</div>
            <div class="value">${stats.num_classes}</div>
        </div>
    `;
    
    // Add detailed metrics table
    if (stats.class_labels && stats.class_labels.length > 0) {
        resultsContainer.innerHTML += `
            <div style="grid-column: 1 / -1;">
                <h3 style="margin: 20px 0 10px 0;">📊 Recognized Users</h3>
                <p style="color: #6b7280; margin-bottom: 15px;">
                    Model trained to recognize: ${stats.class_labels.join(', ')}
                </p>
            </div>
        `;
    }
}

// Check model status
async function checkModelStatus() {
    const statusContainer = document.getElementById('modelStatus');
    
    try {
        statusContainer.innerHTML = '<div class="loading">Loading...</div>';
        
        const response = await fetch(`${API_BASE}/training/status`);
        const data = await response.json();
        
        if (response.ok && data.data) {
            displayModelStatus(data.data);
        } else {
            statusContainer.innerHTML = '<p style="color: #ef4444;">Failed to load model status</p>';
        }
    } catch (error) {
        statusContainer.innerHTML = '<p style="color: #ef4444;">Error: ' + error.message + '</p>';
    }
}

// Display model status
function displayModelStatus(status) {
    const statusContainer = document.getElementById('modelStatus');
    
    const statusBadge = status.model_available 
        ? '<span class="status-badge available">✅ Model Available</span>'
        : '<span class="status-badge unavailable">❌ No Model</span>';
    
    let statusHTML = `
        <div class="status-grid">
            <div class="status-item">
                <div class="label">Model Status</div>
                <div class="value">${statusBadge}</div>
            </div>
    `;
    
    if (status.model_available && status.accuracy_metrics) {
        const metrics = status.accuracy_metrics;
        const accuracyClass = metrics.test_accuracy >= 0.9 ? 'success' : 
                             metrics.test_accuracy >= 0.7 ? 'warning' : 'danger';
        
        statusHTML += `
            <div class="status-item">
                <div class="label">Test Accuracy</div>
                <div class="value ${accuracyClass}">${(metrics.test_accuracy * 100).toFixed(2)}%</div>
            </div>
            <div class="status-item">
                <div class="label">Epochs Trained</div>
                <div class="value">${metrics.epochs_trained}</div>
            </div>
            <div class="status-item">
                <div class="label">Last Updated</div>
                <div class="value">${new Date(metrics.timestamp).toLocaleString()}</div>
            </div>
        `;
        
        statusHTML += `</div>`;
        
        // Add detailed metrics table
        statusHTML += `
            <table class="metric-table">
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Training Accuracy</td>
                        <td class="metric-value">${(metrics.training_accuracy * 100).toFixed(2)}%</td>
                    </tr>
                    <tr>
                        <td>Training Loss</td>
                        <td class="metric-value">${metrics.training_loss.toFixed(4)}</td>
                    </tr>
                    <tr>
                        <td>Validation Accuracy</td>
                        <td class="metric-value">${(metrics.validation_accuracy * 100).toFixed(2)}%</td>
                    </tr>
                    <tr>
                        <td>Validation Loss</td>
                        <td class="metric-value">${metrics.validation_loss.toFixed(4)}</td>
                    </tr>
                    <tr>
                        <td>Test Accuracy</td>
                        <td class="metric-value">${(metrics.test_accuracy * 100).toFixed(2)}%</td>
                    </tr>
                    <tr>
                        <td>Test Loss</td>
                        <td class="metric-value">${metrics.test_loss.toFixed(4)}</td>
                    </tr>
                </tbody>
            </table>
        `;
    } else {
        statusHTML += `</div>
            <p style="margin-top: 20px; color: #6b7280;">
                No trained model available. Start training to create a new model.
            </p>
        `;
    }
    
    statusContainer.innerHTML = statusHTML;
}

// ==================== PREDICTION FUNCTIONS ====================

// Check Prediction Model Status
async function checkPredictionModelStatus() {
    const statusContainer = document.getElementById('predictionModelStatus');
    
    try {
        statusContainer.innerHTML = '<div class="loading">Checking model status...</div>';
        
        const response = await fetch(`${API_BASE}/face/model-info`);
        const result = await response.json();
        
        if (result.status === 'success' && result.data.loaded) {
            const info = result.data;
            statusContainer.innerHTML = `
                <div class="status-grid">
                    <div class="status-item status-success">
                        <div class="label">Status</div>
                        <div class="value">✅ Model Ready</div>
                    </div>
                    <div class="status-item">
                        <div class="label">Number of Classes</div>
                        <div class="value">${info.num_classes}</div>
                    </div>
                    <div class="status-item">
                        <div class="label">Test Accuracy</div>
                        <div class="value">${(info.accuracy * 100).toFixed(2)}%</div>
                    </div>
                    <div class="status-item">
                        <div class="label">Trained Users</div>
                        <div class="value">${info.classes.join(', ')}</div>
                    </div>
                </div>
            `;
        } else {
            statusContainer.innerHTML = `
                <div class="status-grid">
                    <div class="status-item status-error">
                        <div class="label">Status</div>
                        <div class="value">❌ Model Not Found</div>
                    </div>
                </div>
                <p style="margin-top: 15px; color: #6b7280;">
                    Please train the model first in the Training tab.
                </p>
            `;
        }
    } catch (error) {
        console.error('Error checking prediction model status:', error);
        statusContainer.innerHTML = `
            <div class="error">
                ❌ Failed to check model status: ${error.message}
            </div>
        `;
    }
}

// Handle Predict Upload
async function handlePredictUpload(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('predictPhotoFile');
    const messageDiv = document.getElementById('predictUploadMessage');
    const resultsCard = document.getElementById('predictionResultsCard');
    const resultsDiv = document.getElementById('predictionResults');
    
    if (!fileInput.files || fileInput.files.length === 0) {
        messageDiv.innerHTML = '<div class="error">❌ Please select a photo</div>';
        return;
    }
    
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        messageDiv.innerHTML = '<div class="loading">🔍 Analyzing face...</div>';
        resultsCard.style.display = 'none';
        
        const response = await fetch(`${API_BASE}/face/predict`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            messageDiv.innerHTML = '<div class="success">✅ Prediction successful!</div>';
            displayPredictionResults(result.data);
            
            // Reset form
            fileInput.value = '';
            document.getElementById('predictUploadPreview').innerHTML = '';
        } else {
            messageDiv.innerHTML = `<div class="error">❌ ${result.message}</div>`;
        }
    } catch (error) {
        console.error('Error predicting:', error);
        messageDiv.innerHTML = `<div class="error">❌ Prediction failed: ${error.message}</div>`;
    }
}

// Handle Predict Camera
async function handlePredictCamera(e) {
    e.preventDefault();
    
    const messageDiv = document.getElementById('predictCameraMessage');
    const resultsCard = document.getElementById('predictionResultsCard');
    const canvas = document.getElementById('predictCaptureCanvas');
    
    if (!predictCapturedImageData) {
        showMessage(
            messageDiv,
            '❌ Belum ada foto yang diambil',
            'error'
        );
        return;
    }
    
    try {
        showMessage(messageDiv, '🔍 Menganalisis wajah...', 'info');
        resultsCard.style.display = 'none';
        
        // Convert canvas to blob
        canvas.toBlob(async (blob) => {
            if (!blob) {
                showMessage(messageDiv, '❌ Gagal memproses gambar', 'error');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', blob, 'camera_predict.jpg');
            
            const response = await fetch(`${API_BASE}/face/predict`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                showMessage(messageDiv, '✅ Prediksi berhasil!', 'success');
                displayPredictionResults(result.data);
                
                // Clean up
                predictCapturedImageData = null;
                document.getElementById('predictCameraPreview').innerHTML = '';
                document.getElementById('predictCameraForm').style.display = 'none';
                
                // Close camera
                closePredictCamera();
            } else {
                showMessage(messageDiv, '❌ ' + (result.message || 'Prediksi gagal'), 'error');
            }
        }, 'image/jpeg', 0.95);
        
    } catch (error) {
        console.error('Error predicting:', error);
        showMessage(messageDiv, '❌ Error: ' + error.message, 'error');
    }
}

// Fungsi untuk mengambil foto ulang prediction
function retakePredictPhoto() {
    // Clear captured image
    predictCapturedImageData = null;
    
    // Clear preview
    document.getElementById('predictCameraPreview').innerHTML = '';
    document.getElementById('predictCameraForm').style.display = 'none';
    
    // Show video and capture button again
    document.getElementById('predictVideoContainer').style.display = 'block';
    document.getElementById('predictCaptureContainer').style.display = 'flex';
    
    showMessage(
        document.getElementById('predictCameraMessage'),
        'ℹ️ Posisikan wajah Anda dan ambil foto lagi',
        'info'
    );
}

// Helper functions untuk error handling prediction camera
function showPredictCameraError(message) {
    const errorEl = document.getElementById('predictCameraErrorMessage');
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.style.display = 'block';
    }
    
    showMessage(
        document.getElementById('predictCameraMessage'),
        message,
        'error'
    );
}

function hidePredictCameraError() {
    const errorEl = document.getElementById('predictCameraErrorMessage');
    if (errorEl) {
        errorEl.style.display = 'none';
        errorEl.textContent = '';
    }
}

// ==================== VERIFICATION SECTION (1:1) ====================

// State for verification
let verifyUserId = null;
let verifyUserName = null;
let verifyUserEmail = null;
let verifyCameraStream = null;
let isVerifyStreaming = false;
let verifyCapturedImageData = null;

// Handle Email Lookup
async function handleEmailLookup(e) {
    e.preventDefault();
    
    const email = document.getElementById('verifyEmail').value.trim();
    const messageEl = document.getElementById('emailLookupMessage');
    const userInfoDisplay = document.getElementById('userInfoDisplay');
    const verifyFaceSection = document.getElementById('verifyFaceSection');
    
    if (!email) {
        showMessage(messageEl, '❌ Silakan masukkan email', 'error');
        return;
    }
    
    try {
        showMessage(messageEl, '🔍 Mencari user...', 'info');
        
        // Lookup user by email
        const response = await fetch(`${API_BASE}/users`);
        const users = await response.json();
        
        const user = users.find(u => u.email.toLowerCase() === email.toLowerCase());
        
        if (user) {
            verifyUserId = user.id;
            verifyUserName = user.name;
            verifyUserEmail = user.email;
            
            // Display user info
            document.getElementById('foundUserId').textContent = user.id;
            document.getElementById('foundUserName').textContent = user.name;
            document.getElementById('foundUserEmail').textContent = user.email;
            
            userInfoDisplay.style.display = 'block';
            verifyFaceSection.style.display = 'block';
            
            showMessage(messageEl, '✅ User ditemukan! Silakan lanjut ke Step 2', 'success');
            
            // Scroll to face verification section
            verifyFaceSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } else {
            userInfoDisplay.style.display = 'none';
            verifyFaceSection.style.display = 'none';
            verifyUserId = null;
            showMessage(messageEl, '❌ User dengan email tersebut tidak ditemukan', 'error');
        }
    } catch (error) {
        console.error('Error looking up user:', error);
        showMessage(messageEl, '❌ Error: ' + error.message, 'error');
    }
}

// Handle Verify Upload
async function handleVerifyUpload(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('verifyPhotoFile');
    const messageEl = document.getElementById('verifyUploadMessage');
    
    if (!verifyUserId) {
        showMessage(messageEl, '❌ Silakan lookup email terlebih dahulu (Step 1)', 'error');
        return;
    }
    
    if (!fileInput.files || fileInput.files.length === 0) {
        showMessage(messageEl, '❌ Silakan pilih foto', 'error');
        return;
    }
    
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('user_id', verifyUserId);
    formData.append('file', file);
    
    try {
        showMessage(messageEl, '🔍 Memverifikasi wajah...', 'info');
        
        const response = await fetch(`${API_BASE}/auth/login-face-verify`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showMessage(messageEl, '✅ Verifikasi berhasil!', 'success');
            displayVerificationResults(result.data, true);
            
            // Reset form
            fileInput.value = '';
            document.getElementById('verifyUploadPreview').innerHTML = '';
        } else {
            showMessage(messageEl, '❌ ' + (result.message || 'Verifikasi gagal'), 'error');
            displayVerificationResults(result.data, false);
        }
    } catch (error) {
        console.error('Error verifying:', error);
        showMessage(messageEl, '❌ Error: ' + error.message, 'error');
    }
}

// Camera functions for verification
async function openVerifyCamera() {
    try {
        hideVerifyCameraError();
        
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            showVerifyCameraError(
                '❌ Browser tidak mendukung akses kamera atau halaman tidak aman. ' +
                'Pastikan menggunakan HTTPS atau localhost untuk mengakses kamera.'
            );
            return;
        }
        
        const constraints = {
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            },
            audio: false
        };
        
        let stream;
        try {
            stream = await navigator.mediaDevices.getUserMedia(constraints);
        } catch (constraintError) {
            console.log('Detailed constraints not supported, trying basic video...');
            stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        }
        
        const video = document.getElementById('verifyCameraStream');
        
        if (video) {
            video.srcObject = stream;
            verifyCameraStream = stream;
            isVerifyStreaming = true;
            
            document.getElementById('verifyVideoContainer').style.display = 'block';
            document.getElementById('verifyCaptureContainer').style.display = 'flex';
            document.getElementById('startVerifyCameraBtn').style.display = 'none';
            document.getElementById('stopVerifyCameraBtn').style.display = 'inline-block';
            
            document.getElementById('verifyCameraPreview').innerHTML = '';
            document.getElementById('verifyCameraForm').style.display = 'none';
            verifyCapturedImageData = null;
            
            video.onloadedmetadata = () => {
                video.play().catch(err => {
                    console.error('Play error:', err);
                    showVerifyCameraError('❌ Gagal memutar video kamera: ' + err.message);
                });
            };
            
            showMessage(
                document.getElementById('verifyCameraMessage'),
                '✅ Kamera berhasil dibuka. Posisikan wajah Anda dan klik "Ambil Foto"',
                'success'
            );
        }
    } catch (err) {
        let errorMessage = '❌ Tidak dapat mengakses kamera: ';
        
        if (err.name === 'NotAllowedError') {
            errorMessage += 'Izin akses kamera ditolak. Silakan izinkan akses kamera di pengaturan browser.';
        } else if (err.name === 'NotFoundError') {
            errorMessage += 'Kamera tidak ditemukan. Pastikan perangkat memiliki kamera.';
        } else if (err.name === 'NotReadableError') {
            errorMessage += 'Kamera sedang digunakan aplikasi lain. Tutup aplikasi tersebut dan coba lagi.';
        } else if (err.name === 'OverconstrainedError') {
            errorMessage += 'Kamera tidak mendukung resolusi yang diminta.';
        } else if (err.name === 'TypeError') {
            errorMessage += 'Akses kamera gagal. Gunakan HTTPS atau localhost.';
        } else {
            errorMessage += err.message || 'Terjadi kesalahan tidak diketahui';
        }
        
        showVerifyCameraError(errorMessage);
        console.error('Error accessing camera:', err);
    }
}

function closeVerifyCamera() {
    if (verifyCameraStream) {
        const tracks = verifyCameraStream.getTracks();
        tracks.forEach(track => track.stop());
        verifyCameraStream = null;
    }
    
    const video = document.getElementById('verifyCameraStream');
    
    if (video && video.srcObject) {
        video.srcObject = null;
    }
    
    document.getElementById('verifyVideoContainer').style.display = 'none';
    document.getElementById('verifyCaptureContainer').style.display = 'none';
    document.getElementById('startVerifyCameraBtn').style.display = 'inline-block';
    document.getElementById('stopVerifyCameraBtn').style.display = 'none';
    
    isVerifyStreaming = false;
    
    showMessage(
        document.getElementById('verifyCameraMessage'),
        '',
        ''
    );
}

function captureVerifyImage() {
    if (!isVerifyStreaming) {
        showMessage(
            document.getElementById('verifyCameraMessage'),
            '❌ Kamera belum aktif. Silakan buka kamera terlebih dahulu.',
            'error'
        );
        return;
    }
    
    const video = document.getElementById('verifyCameraStream');
    const canvas = document.getElementById('verifyCaptureCanvas');
    
    if (!canvas || !video) {
        showVerifyCameraError('❌ Element kamera tidak ditemukan');
        return;
    }
    
    const context = canvas.getContext('2d');
    
    if (video.readyState !== video.HAVE_ENOUGH_DATA) {
        showMessage(
            document.getElementById('verifyCameraMessage'),
            '❌ Kamera belum siap. Tunggu sebentar dan coba lagi.',
            'error'
        );
        return;
    }
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    if (canvas.width === 0 || canvas.height === 0) {
        showMessage(
            document.getElementById('verifyCameraMessage'),
            '❌ Stream kamera tidak valid. Coba tutup dan buka kamera lagi.',
            'error'
        );
        return;
    }
    
    context.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );
    
    const imageData = canvas.toDataURL('image/png');
    verifyCapturedImageData = imageData;
    
    const preview = document.getElementById('verifyCameraPreview');
    preview.innerHTML = `
        <div class="captured-image-container">
            <img src="${imageData}" alt="Foto yang diambil" class="captured-image">
            <p class="capture-success">✅ Foto berhasil diambil!</p>
        </div>
    `;
    
    document.getElementById('verifyCameraForm').style.display = 'block';
    
    showMessage(
        document.getElementById('verifyCameraMessage'),
        '✅ Foto siap diverifikasi! Klik "Verify Face" atau "Ambil Ulang"',
        'success'
    );
}

async function handleVerifyCamera(e) {
    e.preventDefault();
    
    const messageDiv = document.getElementById('verifyCameraMessage');
    const canvas = document.getElementById('verifyCaptureCanvas');
    
    if (!verifyUserId) {
        showMessage(messageDiv, '❌ Silakan lookup email terlebih dahulu (Step 1)', 'error');
        return;
    }
    
    if (!verifyCapturedImageData) {
        showMessage(messageDiv, '❌ Belum ada foto yang diambil', 'error');
        return;
    }
    
    try {
        showMessage(messageDiv, '🔍 Memverifikasi wajah...', 'info');
        
        canvas.toBlob(async (blob) => {
            if (!blob) {
                showMessage(messageDiv, '❌ Gagal memproses gambar', 'error');
                return;
            }
            
            const formData = new FormData();
            formData.append('user_id', verifyUserId);
            formData.append('file', blob, 'camera_verify.jpg');
            
            const response = await fetch(`${API_BASE}/auth/login-face-verify`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                showMessage(messageDiv, '✅ Verifikasi berhasil!', 'success');
                displayVerificationResults(result.data, true);
                
                // Clean up
                verifyCapturedImageData = null;
                document.getElementById('verifyCameraPreview').innerHTML = '';
                document.getElementById('verifyCameraForm').style.display = 'none';
                
                closeVerifyCamera();
            } else {
                showMessage(messageDiv, '❌ ' + (result.message || 'Verifikasi gagal'), 'error');
                displayVerificationResults(result.data, false);
            }
        }, 'image/jpeg', 0.95);
        
    } catch (error) {
        console.error('Error verifying:', error);
        showMessage(messageDiv, '❌ Error: ' + error.message, 'error');
    }
}

function retakeVerifyPhoto() {
    verifyCapturedImageData = null;
    
    document.getElementById('verifyCameraPreview').innerHTML = '';
    document.getElementById('verifyCameraForm').style.display = 'none';
    
    document.getElementById('verifyVideoContainer').style.display = 'block';
    document.getElementById('verifyCaptureContainer').style.display = 'flex';
    
    showMessage(
        document.getElementById('verifyCameraMessage'),
        'ℹ️ Posisikan wajah Anda dan ambil foto lagi',
        'info'
    );
}

function showVerifyCameraError(message) {
    const errorEl = document.getElementById('verifyCameraErrorMessage');
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.style.display = 'block';
    }
    
    showMessage(
        document.getElementById('verifyCameraMessage'),
        message,
        'error'
    );
}

function hideVerifyCameraError() {
    const errorEl = document.getElementById('verifyCameraErrorMessage');
    if (errorEl) {
        errorEl.style.display = 'none';
        errorEl.textContent = '';
    }
}

// Display Verification Results
function displayVerificationResults(data, isSuccess) {
    const resultsCard = document.getElementById('verificationResultsCard');
    const resultsDiv = document.getElementById('verificationResults');
    
    let html = '';
    
    if (isSuccess && data.match) {
        // Success - Face Matched
        html = `
            <div class="verification-success">
                <div class="success-icon">✅</div>
                <h3>Verifikasi Berhasil!</h3>
                <p class="success-message">Wajah cocok dengan user yang diklaim</p>
            </div>
            
            <div class="verification-details">
                <div class="detail-card">
                    <div class="detail-label">User ID</div>
                    <div class="detail-value">${data.user_id}</div>
                </div>
                <div class="detail-card">
                    <div class="detail-label">Nama</div>
                    <div class="detail-value">${data.name}</div>
                </div>
                <div class="detail-card">
                    <div class="detail-label">Email</div>
                    <div class="detail-value">${data.email}</div>
                </div>
                <div class="detail-card">
                    <div class="detail-label">Confidence</div>
                    <div class="detail-value confidence-high">${data.confidence}%</div>
                </div>
            </div>
            
            <div class="token-info">
                <h4>🔑 Authentication Token</h4>
                <div class="token-box">
                    <code>${data.token}</code>
                </div>
                <p class="token-expires">Expires: ${new Date(data.expires_at).toLocaleString()}</p>
            </div>
        `;
    } else if (data.match === false) {
        // Failed - Face Does Not Match
        html = `
            <div class="verification-failed">
                <div class="error-icon">❌</div>
                <h3>Verifikasi Gagal</h3>
                <p class="error-message">Wajah TIDAK cocok dengan user yang diklaim</p>
            </div>
            
            <div class="verification-details mismatch">
                <div class="detail-card error">
                    <div class="detail-label">Claimed User ID</div>
                    <div class="detail-value">${data.claimed_user_id}</div>
                </div>
                <div class="detail-card warning">
                    <div class="detail-label">Detected User ID</div>
                    <div class="detail-value">${data.predicted_user_id}</div>
                </div>
                <div class="detail-card">
                    <div class="detail-label">Detection Confidence</div>
                    <div class="detail-value">${data.confidence}%</div>
                </div>
            </div>
            
            <div class="security-warning">
                <p>⚠️ <strong>Security Alert:</strong> Foto yang diupload terdeteksi sebagai user lain.</p>
                <p>Kemungkinan:</p>
                <ul>
                    <li>Foto yang diupload bukan milik user yang diklaim</li>
                    <li>Percobaan impersonation/penipuan</li>
                    <li>Email yang diinput salah</li>
                </ul>
            </div>
        `;
    } else if (data.confidence && data.required_confidence) {
        // Failed - Low Confidence
        html = `
            <div class="verification-failed">
                <div class="error-icon">⚠️</div>
                <h3>Confidence Terlalu Rendah</h3>
                <p class="error-message">Wajah cocok, tapi confidence di bawah threshold</p>
            </div>
            
            <div class="verification-details">
                <div class="detail-card warning">
                    <div class="detail-label">Confidence</div>
                    <div class="detail-value confidence-low">${data.confidence}%</div>
                </div>
                <div class="detail-card">
                    <div class="detail-label">Required Minimum</div>
                    <div class="detail-value">${data.required_confidence}%</div>
                </div>
            </div>
            
            <div class="security-warning">
                <p>💡 <strong>Saran:</strong></p>
                <ul>
                    <li>Gunakan foto dengan pencahayaan yang lebih baik</li>
                    <li>Pastikan wajah terlihat jelas dan tidak blur</li>
                    <li>Posisikan wajah menghadap kamera</li>
                    <li>Hindari foto dengan background yang berantakan</li>
                </ul>
            </div>
        `;
    }
    
    resultsDiv.innerHTML = html;
    resultsCard.style.display = 'block';
    
    // Scroll to results
    resultsCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Display Prediction Results
function displayPredictionResults(data) {
    const resultsCard = document.getElementById('predictionResultsCard');
    const resultsDiv = document.getElementById('predictionResults');
    
    let html = `
        <div class="prediction-main">
            <div class="prediction-header">
                <h3>🎯 Identified User</h3>
            </div>
            <div class="prediction-user">
                <div class="user-avatar">${data.name.charAt(0).toUpperCase()}</div>
                <div class="user-details">
                    <div class="user-name">${data.name}</div>
                    <div class="user-email">${data.email}</div>
                    <div class="user-id">User ID: ${data.user_id}</div>
                </div>
                <div class="confidence-badge">
                    <div class="confidence-label">Confidence</div>
                    <div class="confidence-value">${data.confidence}%</div>
                </div>
            </div>
        </div>
        
        <div class="prediction-alternatives">
            <h4>📊 All Predictions (Top 3)</h4>
            <table class="prediction-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>User ID</th>
                        <th>Name</th>
                        <th>Confidence</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    data.all_predictions.forEach((pred, index) => {
        const isTop = index === 0;
        html += `
            <tr class="${isTop ? 'top-prediction' : ''}">
                <td>${index + 1}</td>
                <td>${pred.user_id}</td>
                <td>${pred.name}</td>
                <td>
                    <div class="confidence-bar-container">
                        <div class="confidence-bar" style="width: ${pred.confidence}%"></div>
                        <span class="confidence-text">${pred.confidence}%</span>
                    </div>
                </td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    resultsDiv.innerHTML = html;
    resultsCard.style.display = 'block';
    
    // Scroll to results
    resultsCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Camera functions for prediction
let predictCameraStream = null;
let isPredictStreaming = false;
let predictCapturedImageData = null;

// Fungsi untuk membuka kamera prediction
async function openPredictCamera() {
    try {
        // Clear previous errors
        hidePredictCameraError();
        
        // Cek apakah browser mendukung getUserMedia
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            showPredictCameraError(
                '❌ Browser tidak mendukung akses kamera atau halaman tidak aman. ' +
                'Pastikan menggunakan HTTPS atau localhost untuk mengakses kamera.'
            );
            return;
        }
        
        // Request camera with optimal settings
        const constraints = {
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            },
            audio: false
        };
        
        let stream;
        try {
            stream = await navigator.mediaDevices.getUserMedia(constraints);
        } catch (constraintError) {
            console.log('Detailed constraints not supported, trying basic video...');
            stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        }
        
        const video = document.getElementById('predictCameraStream');
        
        if (video) {
            video.srcObject = stream;
            predictCameraStream = stream;
            isPredictStreaming = true;
            
            // Show video container and controls
            document.getElementById('predictVideoContainer').style.display = 'block';
            document.getElementById('predictCaptureContainer').style.display = 'flex';
            document.getElementById('startPredictCameraBtn').style.display = 'none';
            document.getElementById('stopPredictCameraBtn').style.display = 'inline-block';
            
            // Clear previous preview
            document.getElementById('predictCameraPreview').innerHTML = '';
            document.getElementById('predictCameraForm').style.display = 'none';
            predictCapturedImageData = null;
            
            // Ensure video plays
            video.onloadedmetadata = () => {
                video.play().catch(err => {
                    console.error('Play error:', err);
                    showPredictCameraError('❌ Gagal memutar video kamera: ' + err.message);
                });
            };
            
            showMessage(
                document.getElementById('predictCameraMessage'),
                '✅ Kamera berhasil dibuka. Posisikan wajah Anda dan klik "Ambil Foto"',
                'success'
            );
        }
    } catch (err) {
        let errorMessage = '❌ Tidak dapat mengakses kamera: ';
        
        if (err.name === 'NotAllowedError') {
            errorMessage += 'Izin akses kamera ditolak. Silakan izinkan akses kamera di pengaturan browser.';
        } else if (err.name === 'NotFoundError') {
            errorMessage += 'Kamera tidak ditemukan. Pastikan perangkat memiliki kamera.';
        } else if (err.name === 'NotReadableError') {
            errorMessage += 'Kamera sedang digunakan aplikasi lain. Tutup aplikasi tersebut dan coba lagi.';
        } else if (err.name === 'OverconstrainedError') {
            errorMessage += 'Kamera tidak mendukung resolusi yang diminta.';
        } else if (err.name === 'TypeError') {
            errorMessage += 'Akses kamera gagal. Gunakan HTTPS atau localhost.';
        } else {
            errorMessage += err.message || 'Terjadi kesalahan tidak diketahui';
        }
        
        showPredictCameraError(errorMessage);
        console.error('Error accessing camera:', err);
    }
}

// Fungsi untuk menutup kamera prediction
function closePredictCamera() {
    if (predictCameraStream) {
        const tracks = predictCameraStream.getTracks();
        tracks.forEach(track => track.stop());
        predictCameraStream = null;
    }
    
    const video = document.getElementById('predictCameraStream');
    
    if (video && video.srcObject) {
        video.srcObject = null;
    }
    
    // Hide video and controls
    document.getElementById('predictVideoContainer').style.display = 'none';
    document.getElementById('predictCaptureContainer').style.display = 'none';
    document.getElementById('startPredictCameraBtn').style.display = 'inline-block';
    document.getElementById('stopPredictCameraBtn').style.display = 'none';
    
    // Reset state
    isPredictStreaming = false;
    
    showMessage(
        document.getElementById('predictCameraMessage'),
        '',
        ''
    );
}

// Fungsi untuk capture gambar prediction
function capturePredictImage() {
    if (!isPredictStreaming) {
        showMessage(
            document.getElementById('predictCameraMessage'),
            '❌ Kamera belum aktif. Silakan buka kamera terlebih dahulu.',
            'error'
        );
        return;
    }
    
    const video = document.getElementById('predictCameraStream');
    const canvas = document.getElementById('predictCaptureCanvas');
    
    if (!canvas || !video) {
        showPredictCameraError('❌ Element kamera tidak ditemukan');
        return;
    }
    
    const context = canvas.getContext('2d');
    
    // Check if video is ready
    if (video.readyState !== video.HAVE_ENOUGH_DATA) {
        showMessage(
            document.getElementById('predictCameraMessage'),
            '❌ Kamera belum siap. Tunggu sebentar dan coba lagi.',
            'error'
        );
        return;
    }
    
    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Validate dimensions
    if (canvas.width === 0 || canvas.height === 0) {
        showMessage(
            document.getElementById('predictCameraMessage'),
            '❌ Stream kamera tidak valid. Coba tutup dan buka kamera lagi.',
            'error'
        );
        return;
    }
    
    // Draw video frame to canvas
    context.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );
    
    // Get image data as base64
    const imageData = canvas.toDataURL('image/png');
    predictCapturedImageData = imageData;
    
    // Show preview
    const preview = document.getElementById('predictCameraPreview');
    preview.innerHTML = `
        <div class="captured-image-container">
            <img src="${imageData}" alt="Foto yang diambil" class="captured-image">
            <p class="capture-success">✅ Foto berhasil diambil!</p>
        </div>
    `;
    
    // Show predict form
    document.getElementById('predictCameraForm').style.display = 'block';
    
    showMessage(
        document.getElementById('predictCameraMessage'),
        '✅ Foto siap diprediksi! Klik "Prediksi Wajah" atau "Ambil Ulang"',
        'success'
    );
}