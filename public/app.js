const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileButton = document.getElementById('file-button');
const preview = document.getElementById('preview');
const previewImage = document.getElementById('preview-image');
const previewFilename = document.getElementById('preview-filename');
const previewDimensions = document.getElementById('preview-dimensions');
const previewSize = document.getElementById('preview-size');
const clearButton = document.getElementById('clear-button');
const uploadForm = document.getElementById('upload-form');
const uploadStatus = document.getElementById('upload-status');

let currentFile = null;
let currentDataUrl = '';

const formatBytes = (bytes) => {
  if (!Number.isFinite(bytes)) return '—';
  if (bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const exponent = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${(bytes / Math.pow(1024, exponent)).toFixed(1)} ${units[exponent]}`;
};

const resetPreview = () => {
  currentFile = null;
  currentDataUrl = '';
  preview.hidden = true;
  previewImage.src = '';
  previewFilename.textContent = '—';
  previewDimensions.textContent = '—';
  previewSize.textContent = '—';
  uploadStatus.value = '';
  uploadStatus.textContent = '';
};

const showPreview = (file, dataUrl) => {
  preview.hidden = false;
  previewFilename.textContent = file.name || 'pasted-image.png';
  previewSize.textContent = formatBytes(file.size || dataUrl.length * 0.75);
  previewImage.src = dataUrl;
  previewImage.onload = () => {
    previewDimensions.textContent = `${previewImage.naturalWidth} × ${previewImage.naturalHeight}`;
  };
};

const handleFile = (file) => {
  if (!file) return;
  if (!file.type.startsWith('image/')) {
    uploadStatus.textContent = 'Please upload an image file.';
    uploadStatus.value = 'error';
    return;
  }

  const reader = new FileReader();
  reader.onload = () => {
    currentFile = file;
    currentDataUrl = reader.result;
    showPreview(file, reader.result);
  };
  reader.onerror = () => {
    uploadStatus.textContent = 'Failed to read the file.';
    uploadStatus.value = 'error';
  };
  reader.readAsDataURL(file);
};

fileButton.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (event) => {
  const [file] = event.target.files;
  handleFile(file);
});

dropZone.addEventListener('dragover', (event) => {
  event.preventDefault();
  dropZone.classList.add('drop-zone--active');
});

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('drop-zone--active');
});

dropZone.addEventListener('drop', (event) => {
  event.preventDefault();
  dropZone.classList.remove('drop-zone--active');
  const file = event.dataTransfer.files[0];
  handleFile(file);
});

dropZone.addEventListener('paste', (event) => {
  const file = Array.from(event.clipboardData.files).find((item) => item.type.startsWith('image/'));
  if (file) {
    handleFile(file);
  }
});

document.addEventListener('paste', (event) => {
  const file = Array.from(event.clipboardData.files).find((item) => item.type.startsWith('image/'));
  if (file) {
    handleFile(file);
  }
});

clearButton.addEventListener('click', () => {
  resetPreview();
  fileInput.value = '';
});

uploadForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!currentFile) {
    uploadStatus.textContent = 'Select or paste a screenshot before uploading.';
    uploadStatus.value = 'error';
    return;
  }

  const formData = new FormData();
  formData.append('screenshot', currentFile, currentFile.name || 'pasted-image.png');

  uploadStatus.textContent = 'Uploading…';
  uploadStatus.value = 'pending';

  try {
    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Upload failed' }));
      throw new Error(error.error || 'Upload failed');
    }

    const result = await response.json();
    uploadStatus.textContent = `Uploaded ${result.filename} (${formatBytes(result.size)})`;
    uploadStatus.value = 'success';
  } catch (error) {
    uploadStatus.textContent = error.message;
    uploadStatus.value = 'error';
  }
});

resetPreview();
