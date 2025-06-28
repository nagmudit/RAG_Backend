# Document Upload Feature

The RAG Backend now supports uploading and processing documents in addition to web scraping. This feature allows you to upload documents directly and ask questions about their content.

## Supported File Formats

- **PDF** (`.pdf`) - Portable Document Format files
- **Microsoft Word** (`.docx`) - Word documents
- **Excel** (`.xlsx`) - Excel spreadsheets
- **Markdown** (`.md`) - Markdown text files

## File Size Limits

- Maximum file size: **50MB**
- Files must contain readable text content

## API Endpoints

### Upload Document

**POST** `/api/v1/upload`

Upload a document to be processed and added to the knowledge base.

**Request:**
- Content-Type: `multipart/form-data`
- Body: File upload with field name `file`

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "file=@path/to/your/document.pdf"
```

**Example using Python:**
```python
import requests

with open('document.pdf', 'rb') as file:
    files = {'file': ('document.pdf', file)}
    response = requests.post('http://localhost:8000/api/v1/upload', files=files)
    
print(response.json())
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully processed document.pdf",
  "filename": "document.pdf",
  "documents_added": 15,
  "file_type": ".pdf"
}
```

### Ask Questions

**POST** `/api/v1/ask`

Ask questions about uploaded documents and scraped web content.

**Request:**
```json
{
  "query": "What are the main topics discussed in the uploaded documents?"
}
```

**Response:**
```json
{
  "answer": "Based on the uploaded documents...",
  "citations": [
    {
      "url": "Uploaded file: document.pdf",
      "title": "document",
      "relevance_score": 0.85,
      "source_type": "document"
    }
  ],
  "query": "What are the main topics discussed in the uploaded documents?"
}
```

## How It Works

1. **Upload**: Send a document to the `/upload` endpoint
2. **Processing**: The system extracts text from the document
3. **Chunking**: Text is split into manageable chunks
4. **Embedding**: Each chunk is converted to vector embeddings
5. **Storage**: Embeddings are stored in the FAISS vector database
6. **Querying**: Use the `/ask` endpoint to query both uploaded documents and scraped web content

## Document Processing Details

### PDF Files
- Extracts text from all pages
- Handles multi-page documents
- Preserves page structure with page markers

### Word Documents (.docx)
- Extracts text from paragraphs
- Includes content from tables
- Preserves document structure

### Excel Files (.xlsx)
- Processes all worksheets
- Extracts data from cells
- Formats data as pipe-separated values

### Markdown Files (.md)
- Preserves original markdown formatting
- Supports UTF-8 encoding
- Fallback to latin-1 encoding if needed

## Error Handling

The API provides detailed error messages for common issues:

- **Unsupported file format**: File extension not in allowed list
- **File too large**: Exceeds 50MB limit
- **Empty file**: File contains no data
- **Processing error**: Unable to extract text from file
- **No content**: File contains no readable text

## Testing

Use the provided test scripts:

1. **Basic testing**: `python test_document_upload.py`
2. **Comprehensive testing**: `python test_api.py`

## Integration Examples

### Frontend Upload Form
```html
<form enctype="multipart/form-data">
  <input type="file" name="file" accept=".pdf,.docx,.xlsx,.md">
  <button type="submit">Upload Document</button>
</form>
```

### JavaScript Upload
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('/api/v1/upload', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

## Best Practices

1. **File Size**: Keep files under 50MB for optimal performance
2. **Text Quality**: Ensure documents contain readable text
3. **File Naming**: Use descriptive filenames for better citations
4. **Batch Processing**: Upload multiple documents separately for better error handling
5. **Content Organization**: Group related documents for coherent responses

## Troubleshooting

### Common Issues

1. **"Unsupported file format"**
   - Check file extension is one of: .pdf, .docx, .xlsx, .md
   - Ensure filename has correct extension

2. **"File size too large"**
   - Compress or split large files
   - Maximum size is 50MB

3. **"No content could be extracted"**
   - File may be corrupted or password-protected
   - PDF files might be image-only (scanned documents)
   - Word documents might be in older .doc format

4. **"Processing failed"**
   - Check server logs for detailed error information
   - Ensure all required dependencies are installed
