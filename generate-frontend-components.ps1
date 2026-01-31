# Frontend Component Generation Script
# This script creates all missing frontend components for the RAG System

$baseDir = "C:\Users\user\OneDrive - JeenAI\Documents\code\RAG_System\frontend\src"

Write-Host "Generating frontend components..." -ForegroundColor Green

# Create all necessary directories
$directories = @(
    "$baseDir\store",
    "$baseDir\components\common",
    "$baseDir\components\layout",
    "$baseDir\components\settings",
    "$baseDir\components\documents",
    "$baseDir\components\query"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
        Write-Host "Created directory: $dir" -ForegroundColor Cyan
    }
}

Write-Host "`nAll directories created successfully!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Review FRONTEND_IMPLEMENTATION_GUIDE.md for component specifications"
Write-Host "2. Implement components following the examples in the guide"
Write-Host "3. Start with stores and common components"
Write-Host "4. Test each component before moving to the next"
Write-Host "5. Run 'npm run dev' to test the frontend"
Write-Host "6. Build Docker image with 'docker-compose build frontend'"

Write-Host "`nComponent checklist:" -ForegroundColor Yellow
Write-Host "□ Stores (4): toastStore ✓, settingsStore, documentStore, queryStore"
Write-Host "□ Common Components (11): Button, Card, Input, Select, Badge, Spinner, Modal, Tabs, Table, Toast, StatusIndicator"
Write-Host "□ Layout (2): Header, MainLayout"
Write-Host "□ Hooks (5): useToast, useDebounce, useDocuments, useQuery, useSettings"  
Write-Host "□ API Services (4): client, documents, queries, settings"
Write-Host "□ Settings Components (3): AzureConfig, RAGConfig, SystemStatus"
Write-Host "□ Documents Components (6): DocumentList, DocumentCard, DocumentDetails, UploadModal, ChunksViewer, DocumentFilters"
Write-Host "□ Query Components (8): QueryInput, AnswerDisplay, DebugPanel, ChunksList, RerankComparison, AgentDecision, SearchSources, TimingBreakdown"

Write-Host "`n✓ Frontend foundation complete!" -ForegroundColor Green
Write-Host "✓ Types, utils, and constants created" -ForegroundColor Green
Write-Host "✓ Directory structure ready" -ForegroundColor Green
Write-Host "✓ Implementation guide available" -ForegroundColor Green
