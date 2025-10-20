# WinTree Order Screenshot Uploader

A lightweight web application for capturing WinTree order screenshots and uploading them to a Node.js server. Drop, paste, or browse for an image to preview it instantly before sending it to the server.

## Features

- 🎯 Drag-and-drop, paste, or browse to select a screenshot
- 🖼️ Instant inline preview with filename, dimensions, and filesize metadata
- ☁️ Upload endpoint powered by Express and Multer for future processing workflows
- ✨ Polished, responsive UI built with modern HTML, CSS, and vanilla JavaScript

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) 18 or newer

### Installation

```bash
npm install
```

### Run the development server

```bash
npm start
```

The app will be available at [http://localhost:3000](http://localhost:3000).

### Upload API

The Express server exposes a single endpoint:

```
POST /api/upload
Content-Type: multipart/form-data
Field name: screenshot
```

Upon success the server responds with the filename, MIME type, and file size. You can extend this handler to perform OCR, store the image, or forward the data to other services.

## Project Structure

```
public/
  index.html      # Upload interface
  styles.css      # UI styling
  app.js          # Client-side logic for drag-drop, paste, and uploads
server.js         # Express server serving the UI and upload endpoint
package.json      # Node.js project configuration
```

## Next Steps

- Integrate OCR to extract order details from the uploaded screenshot
- Persist uploads to cloud storage or a database
- Connect to Trello’s API to automatically create cards from processed orders

## License

This project is released under the MIT License.
