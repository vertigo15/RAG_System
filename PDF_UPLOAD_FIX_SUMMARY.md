# PDF Upload Issue - Analysis & Fixes

## Summary
The PDF upload functionality was not working due to **two critical backend/configuration issues** that have been identified and fixed:

### Issues Found

#### 1. Backend Code Error - `ChunksResponse` Not Imported ❌
**Location:** `backend/src/api/routes/documents.py:76`

**Problem:**  
The `ChunksResponse` schema was used in the route decorator but wasn't imported at the top of the file, causing the backend to crash on startup with:
```
NameError: name 'ChunksResponse' is not defined
```

**Fix Applied:** ✅
Added `ChunksResponse` to the imports on line 9:
```python
from src.models.schemas import DocumentUploadResponse, DocumentResponse, DocumentListResponse, ChunksResponse
```

And removed the redundant import from inside the function (line 84).

---

#### 2. Nginx Proxy Configuration Error ❌
**Location:** `frontend/nginx.conf:9`

**Problem:**  
The nginx reverse proxy was configured to forward API requests to `http://backend:8001/`, but the backend container runs on port **8000** internally. Port 8001 is only the external host mapping. This caused all API calls to fail with **502 Bad Gateway** errors.

**Fix Applied:** ✅
Changed the proxy_pass directive from:
```nginx
proxy_pass http://backend:8001/;
```
to:
```nginx
proxy_pass http://backend:8000/;
```

---

## Test Results (from Selenium)

### UI Elements Working ✅
- ✅ Documents page loads correctly
- ✅ File input element present with correct accept types (.pdf, .docx, .pptx, .png, .jpg, .jpeg, .tiff)
- ✅ Upload button is visible and clickable
- ✅ File selection works (tested with PDF from Downloads folder)

### API Communication Issues (Before Fix) ❌
- ❌ 502 Bad Gateway on `/api/documents` (GET)
- ❌ 502 Bad Gateway on `/api/documents/upload` (POST)
- ⚠️  No spinner/loading indicator shown
- ⚠️  No success/error toast messages
- ❌ Document table not rendering (waiting for API data)

---

## Required Actions to Apply Fixes

Since the containers don't have source code mounted as volumes, you need to rebuild them:

```powershell
# Stop all containers
docker-compose down

# Rebuild backend and frontend with fixes
docker-compose build backend frontend

# Start all services
docker-compose up -d

# Wait for services to be healthy (30-60 seconds)
timeout /t 60

# Check backend is running
docker logs --tail 20 rag-backend

# Check frontend is running
docker logs --tail 20 rag-frontend

# Verify services are up
docker ps --filter "name=rag"
```

---

## Verification Steps

After applying the fixes, test the PDF upload:

1. Open browser to `http://localhost:3100/documents`
2. Click "Upload Documents" button
3. Select a PDF file from your Downloads folder
4. Upload should:
   - Show loading spinner
   - Display success toast message
   - Show the document in the table with "pending" or "processing" status

Or run the automated test:
```powershell
python test_document_upload.py
```

---

## Additional Improvements Needed (Optional)

### Settings Page Display
As mentioned in your requirements, the Settings page should display:

**Azure OpenAI Configuration:**
- Endpoint
- API Key (masked)
- Embedding Model
- LLM Model

**Azure Document Intelligence:**
- Endpoint
- API Key (masked)

**RAG Configuration:**
- Top K Results
- Rerank Top N
- Max Iterations
- Enable Hybrid Search
- Enable Q&A Matching

**System Status:**
- 🟢 PostgreSQL: Connected
- 🟢 Qdrant: Connected (X vectors)
- 🟢 RabbitMQ: Connected (X pending jobs)
- 🟢 Azure OpenAI: Healthy (latency: Xms)
- 🟢 Doc Intel: Healthy

These features need to be implemented in the Settings page component.

---

## Files Modified

1. `backend/src/api/routes/documents.py` - Fixed ChunksResponse import
2. `frontend/nginx.conf` - Fixed backend proxy port

---

## Testing Tools Created

1. **`test_document_upload.py`** - Selenium test for PDF upload functionality
   - Automatically finds PDF in Downloads
   - Takes screenshots at each step
   - Checks for errors in browser console
   - Reports detailed test results

2. **`check_selenium_setup.py`** - Diagnostic tool for Selenium environment
   - Verifies Chrome installation
   - Checks Selenium dependencies
   - Tests basic browser automation
   - Lists available PDF files

3. **`test_requirements.txt`** - Dependencies for testing
   - selenium>=4.0.0
   - webdriver-manager>=4.0.0
   - reportlab>=3.6.0

---

## Next Steps

1. Apply the fixes by rebuilding containers (see Required Actions above)
2. Test PDF upload functionality manually or with automated test
3. Implement Settings page UI enhancements (optional)
4. Consider adding health check endpoint that returns system status for the Settings page

